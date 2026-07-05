from __future__ import annotations

from facade_uav.rl.coverage_env import FacadeCoverageEnv


ACTION_TABLE: list[tuple[int, int]] = [
    (-1, -1),
    (0, -1),
    (1, -1),
    (-1, 0),
    (0, 0),
    (1, 0),
    (-1, 1),
    (0, 1),
    (1, 1),
]


def _load_gym_dependencies():
    try:
        import gymnasium as gym  # type: ignore
        import numpy as np  # type: ignore
        from gymnasium import spaces  # type: ignore
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Gym wrapper requires numpy and gymnasium. "
            "Install dependencies with: python -m pip install -r requirements.txt"
        ) from exc
    return gym, np, spaces


gym, np, spaces = _load_gym_dependencies()


class FacadeGymEnv(gym.Env):
    """Gymnasium wrapper for PPO training.

    Observation vector:
    x, z, standoff, wind, reservoir, battery, coverage, dirty_count,
    obstacle_count, nearest_dirty_dx, nearest_dirty_dz, nearest_dirty_distance,
    current_dirty_confidence
    """

    metadata = {"render_modes": []}

    def __init__(self, width: int = 12, height: int = 8, seed: int | None = None) -> None:
        super().__init__()
        self.core = FacadeCoverageEnv(width=width, height=height, seed=seed)
        self.action_space = spaces.Discrete(len(ACTION_TABLE))
        self.observation_space = spaces.Box(
            low=np.array(
                [0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -width, -height, 0.0, 0.0],
                dtype=np.float32,
            ),
            high=np.array(
                [
                    width,
                    height,
                    5.0,
                    20.0,
                    10.0,
                    100.0,
                    1.0,
                    width * height,
                    width * height,
                    width,
                    height,
                    width + height,
                    1.0,
                ],
                dtype=np.float32,
            ),
            dtype=np.float32,
        )

    def reset(self, seed: int | None = None, options: dict | None = None):
        super().reset(seed=seed)
        if seed is not None:
            self.core = FacadeCoverageEnv(width=self.core.width, height=self.core.height, seed=seed)
        obs = self.core.reset()
        return self._vectorize(obs), {}

    def step(self, action):
        obs, reward, done, info = self.core.step(ACTION_TABLE[int(action)])
        return self._vectorize(obs), float(reward), bool(done), False, info

    def _vectorize(self, obs: dict[str, float]):
        return np.array(
            [
                obs["x"],
                obs["z"],
                obs["standoff_m"],
                obs["wind_mps"],
                obs["reservoir_l"],
                obs["battery_pct"],
                obs["coverage_ratio"],
                obs["dirty_count"],
                obs["obstacle_count"],
                obs["nearest_dirty_dx"],
                obs["nearest_dirty_dz"],
                obs["nearest_dirty_distance"],
                obs["current_dirty_confidence"],
            ],
            dtype=np.float32,
        )
