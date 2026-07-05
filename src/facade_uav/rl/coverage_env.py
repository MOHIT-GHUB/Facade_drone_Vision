from __future__ import annotations

import random

from facade_uav.cleaning_zone_map import CleaningZoneMap
from facade_uav.config import MissionState, RewardWeights, SafetyBounds
from facade_uav.safety_layer import SafetyLayer


class FacadeCoverageEnv:
    """Pure-Python facade coverage environment.

    This environment is intentionally simple and dependency-free. It provides
    the same reward terms expected by the later Gymnasium/PPO wrapper.
    """

    def __init__(
        self,
        width: int = 12,
        height: int = 8,
        seed: int | None = None,
        weights: RewardWeights | None = None,
    ) -> None:
        self.width = width
        self.height = height
        self.rng = random.Random(seed)
        self.weights = weights or RewardWeights()
        self.safety = SafetyLayer(SafetyBounds(max_x_m=float(width), max_z_m=float(height)))
        self.zone_map = CleaningZoneMap(width, height)
        self.x = 0
        self.z = 0
        self.standoff_m = 1.5
        self.wind_mps = 0.0
        self.reservoir_l = 5.0
        self.battery_pct = 100.0
        self.steps = 0
        self.max_steps = width * height * 3

    def reset(self) -> dict[str, float]:
        self.zone_map = CleaningZoneMap(self.width, self.height)
        for z in range(self.height):
            for x in range(self.width):
                self.zone_map.set_dirty(x, z, self.rng.uniform(0.55, 1.0))
        self._add_obstacles()
        self.x = 0
        self.z = 0
        self.standoff_m = 1.5
        self.wind_mps = self.rng.uniform(0.0, 2.0)
        self.reservoir_l = 5.0
        self.battery_pct = 100.0
        self.steps = 0
        return self.observation()

    def step(self, action: tuple[int, int]) -> tuple[dict[str, float], float, bool, dict[str, object]]:
        previous_target_distance = self._nearest_dirty_distance()
        dx = max(-1, min(1, int(action[0])))
        dz = max(-1, min(1, int(action[1])))
        next_x = max(0, min(self.width - 1, self.x + dx))
        next_z = max(0, min(self.height - 1, self.z + dz))

        path_length = abs(next_x - self.x) + abs(next_z - self.z)
        self.x = next_x
        self.z = next_z
        self.steps += 1
        self.reservoir_l = max(0.0, self.reservoir_l - 0.03)
        self.battery_pct = max(0.0, self.battery_pct - 0.08)
        self.wind_mps = max(0.0, self.wind_mps + self.rng.uniform(-0.20, 0.20))

        cell = self.zone_map.cell(self.x, self.z)
        hit_obstacle = cell.obstacle
        was_already_clean = cell.cleaned
        new_clean = self.zone_map.mark_cleaned(self.x, self.z)

        standoff_error = abs(self.standoff_m - 1.5)
        state = MissionState(
            x_m=float(self.x),
            y_m=self.standoff_m,
            z_m=float(self.z),
            standoff_m=self.standoff_m,
            wind_mps=self.wind_mps,
            reservoir_l=self.reservoir_l,
            battery_pct=self.battery_pct,
        )
        safety_decision = self.safety.evaluate(state, {"dx": dx, "dz": dz})
        target_progress = previous_target_distance - self._nearest_dirty_distance()

        reward_terms = {
            "coverage_gain": self.weights.coverage_gain if new_clean else 0.0,
            "target_progress": self.weights.target_progress * target_progress,
            "overlap_penalty": -self.weights.overlap_penalty if was_already_clean else 0.0,
            "path_length_penalty": -self.weights.path_length_penalty * path_length,
            "standoff_penalty": -self.weights.standoff_penalty * standoff_error,
            "reservoir_penalty": -self.weights.reservoir_penalty if self.reservoir_l < 1.0 else 0.0,
            "obstacle_penalty": -self.weights.obstacle_penalty if hit_obstacle else 0.0,
            "safety_penalty": -50.0 if not safety_decision.allowed else 0.0,
        }
        reward = sum(reward_terms.values())
        done = (
            self.zone_map.coverage_ratio() >= 0.98
            or self.steps >= self.max_steps
            or safety_decision.action in {"abort", "return_to_base"}
        )
        info = {
            "reward_terms": reward_terms,
            "safety": safety_decision.reason,
            "coverage_ratio": self.zone_map.coverage_ratio(),
        }
        return self.observation(), reward, done, info

    def observation(self) -> dict[str, float]:
        summary = self.zone_map.summary()
        nearest_dirty_dx, nearest_dirty_dz, nearest_dirty_distance = self._nearest_dirty_delta()
        current = self.zone_map.cell(self.x, self.z)
        return {
            "x": float(self.x),
            "z": float(self.z),
            "standoff_m": self.standoff_m,
            "wind_mps": self.wind_mps,
            "reservoir_l": self.reservoir_l,
            "battery_pct": self.battery_pct,
            "coverage_ratio": summary["coverage_ratio"],
            "dirty_count": summary["dirty_count"],
            "obstacle_count": summary["obstacle_count"],
            "nearest_dirty_dx": nearest_dirty_dx,
            "nearest_dirty_dz": nearest_dirty_dz,
            "nearest_dirty_distance": float(nearest_dirty_distance),
            "current_dirty_confidence": current.dirty_confidence,
        }

    def _add_obstacles(self) -> None:
        frame_columns = {0, self.width - 1}
        if self.width >= 6:
            frame_columns.add(self.width // 2)
        for z in range(self.height):
            for x in frame_columns:
                if self.rng.random() < 0.35:
                    self.zone_map.set_obstacle(x, z, True)

    def _nearest_dirty_delta(self) -> tuple[float, float, float]:
        dirty_cells = self.zone_map.dirty_cells(threshold=0.25)
        if not dirty_cells:
            return 0.0, 0.0, 0.0
        target_x, target_z = min(
            dirty_cells,
            key=lambda pos: abs(pos[0] - self.x) + abs(pos[1] - self.z),
        )
        dx = float(target_x - self.x)
        dz = float(target_z - self.z)
        return dx, dz, abs(dx) + abs(dz)

    def _nearest_dirty_distance(self) -> float:
        return self._nearest_dirty_delta()[2]


def lawnmower_policy(env: FacadeCoverageEnv) -> list[tuple[int, int]]:
    actions: list[tuple[int, int]] = []
    direction = 1
    for row in range(env.height):
        for _ in range(env.width - 1):
            actions.append((direction, 0))
        if row != env.height - 1:
            actions.append((0, 1))
        direction *= -1
    return actions


def greedy_nearest_dirty_action(env: FacadeCoverageEnv) -> tuple[int, int]:
    dx, dz, _ = env._nearest_dirty_delta()
    step_x = 0 if dx == 0 else (1 if dx > 0 else -1)
    step_z = 0 if dz == 0 else (1 if dz > 0 else -1)
    return step_x, step_z
