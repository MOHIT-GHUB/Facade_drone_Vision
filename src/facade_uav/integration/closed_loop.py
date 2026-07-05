from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from facade_uav.cleaning_zone_map import CleaningZoneMap
from facade_uav.config import MissionState, SafetyBounds
from facade_uav.control.offboard_interface import VelocityCommand, clamp_velocity
from facade_uav.safety_layer import SafetyLayer


@dataclass(frozen=True)
class MissionExecutorConfig:
    cell_size_m: float = 1.0
    cruise_speed_mps: float = 0.6
    cleaning_reservoir_l: float = 0.06
    transit_battery_pct: float = 0.04
    clean_battery_pct: float = 0.08
    nominal_wind_mps: float = 2.0
    injected_gust_step: int | None = None
    injected_gust_mps: float = 9.5


def _command_from_step(
    current_x: int,
    current_z: int,
    target_x: int,
    target_z: int,
    cruise_speed_mps: float,
) -> dict[str, float | str]:
    dx = target_x - current_x
    dz = target_z - current_z
    command = clamp_velocity(
        VelocityCommand(
            vx_mps=max(-cruise_speed_mps, min(cruise_speed_mps, float(dx) * cruise_speed_mps)),
            vy_mps=0.0,
            vz_mps=max(-cruise_speed_mps, min(cruise_speed_mps, float(dz) * cruise_speed_mps)),
        ),
        max_speed_mps=cruise_speed_mps,
    )
    return {
        "mode": "velocity",
        "vx_mps": command.vx_mps,
        "vy_mps": command.vy_mps,
        "vz_mps": command.vz_mps,
        "yaw_rate_rps": command.yaw_rate_rps,
    }


def execute_closed_loop_route(
    zone_map: CleaningZoneMap,
    route: dict[str, Any],
    bounds: SafetyBounds | None = None,
    config: MissionExecutorConfig | None = None,
) -> dict[str, Any]:
    """Run planner steps through safety, offboard command, and actuation logic."""

    cfg = config or MissionExecutorConfig()
    safety = SafetyLayer(bounds or SafetyBounds())
    current_x = int(route.get("start", {}).get("x", 0))
    current_z = int(route.get("start", {}).get("z", 0))
    reservoir_l = 5.0
    battery_pct = 100.0
    event_log: list[dict[str, Any]] = []
    clean_events = 0
    transit_events = 0
    safety_overrides = 0

    for index, step in enumerate(route.get("steps", [])):
        if not isinstance(step, dict):
            continue
        target_x = int(step["x"])
        target_z = int(step["z"])
        cell = zone_map.cell(target_x, target_z)
        wind_mps = cfg.injected_gust_mps if cfg.injected_gust_step == index else cfg.nominal_wind_mps
        state = MissionState(
            x_m=float(target_x) * cfg.cell_size_m,
            y_m=cell.depth_m,
            z_m=float(target_z) * cfg.cell_size_m,
            standoff_m=cell.depth_m,
            wind_mps=wind_mps,
            reservoir_l=reservoir_l,
            battery_pct=battery_pct,
            lidar_valid=True,
        )
        proposed = _command_from_step(
            current_x,
            current_z,
            target_x,
            target_z,
            cfg.cruise_speed_mps,
        )
        decision = safety.evaluate(state, proposed)
        if not decision.allowed:
            safety_overrides += 1
            event_log.append(
                {
                    "index": index,
                    "step": step,
                    "state": asdict(state),
                    "decision": asdict(decision),
                    "actuation": "disabled",
                }
            )
            break

        action = str(step.get("action", "transit"))
        actuation = "off"
        if action == "clean":
            did_clean = zone_map.mark_cleaned(target_x, target_z)
            if did_clean:
                clean_events += 1
                reservoir_l = max(0.0, reservoir_l - cfg.cleaning_reservoir_l)
                battery_pct = max(0.0, battery_pct - cfg.clean_battery_pct)
                actuation = "water_jet_on"
        else:
            transit_events += 1
            battery_pct = max(0.0, battery_pct - cfg.transit_battery_pct)

        event_log.append(
            {
                "index": index,
                "step": step,
                "state": asdict(state),
                "decision": asdict(decision),
                "actuation": actuation,
                "reservoir_after_l": round(reservoir_l, 3),
                "battery_after_pct": round(battery_pct, 3),
            }
        )
        current_x = target_x
        current_z = target_z

    return {
        "pipeline": "perception_map_to_route_to_safety_to_offboard_to_actuation",
        "events": event_log,
        "metrics": {
            "route_steps_requested": len([step for step in route.get("steps", []) if isinstance(step, dict)]),
            "events_executed": len(event_log),
            "clean_events": clean_events,
            "transit_events": transit_events,
            "safety_overrides": safety_overrides,
            "coverage_ratio": round(zone_map.coverage_ratio(), 3),
            "reservoir_remaining_l": round(reservoir_l, 3),
            "battery_remaining_pct": round(battery_pct, 3),
        },
        "skipped_targets": route.get("skipped_targets", []),
    }
