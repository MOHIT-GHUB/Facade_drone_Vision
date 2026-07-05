from dataclasses import dataclass
from typing import Any

from .config import MissionState, SafetyBounds


@dataclass(frozen=True)
class SafetyDecision:
    allowed: bool
    action: str
    reason: str
    command: dict[str, Any]


class SafetyLayer:
    """Independent safety shield for learned or scripted commands."""

    def __init__(self, bounds: SafetyBounds | None = None) -> None:
        self.bounds = bounds or SafetyBounds()

    def evaluate(
        self,
        state: MissionState,
        proposed_command: dict[str, Any] | None = None,
    ) -> SafetyDecision:
        command = proposed_command or {}

        if state.wind_mps >= self.bounds.wind_abort_mps:
            return SafetyDecision(False, "abort", "wind exceeds abort threshold", {"mode": "abort"})

        if not state.lidar_valid:
            return SafetyDecision(False, "hold", "lidar invalid", {"mode": "hold"})

        if state.standoff_m < self.bounds.min_standoff_m:
            return SafetyDecision(False, "hold", "standoff below minimum", {"mode": "hold"})

        if state.standoff_m > self.bounds.max_standoff_m:
            return SafetyDecision(False, "hold", "standoff above maximum", {"mode": "hold"})

        if state.x_m < self.bounds.min_x_m or state.x_m > self.bounds.max_x_m:
            return SafetyDecision(False, "return_to_base", "x geofence violation", {"mode": "rtb"})

        if state.z_m < self.bounds.min_z_m or state.z_m > self.bounds.max_z_m:
            return SafetyDecision(False, "return_to_base", "z geofence violation", {"mode": "rtb"})

        if state.reservoir_l <= self.bounds.min_reservoir_l:
            return SafetyDecision(False, "return_to_base", "reservoir below reserve", {"mode": "rtb"})

        if state.battery_pct <= self.bounds.min_battery_pct:
            return SafetyDecision(False, "return_to_base", "battery below reserve", {"mode": "rtb"})

        return SafetyDecision(True, "continue", "safe", command)
