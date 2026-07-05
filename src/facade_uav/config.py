from dataclasses import dataclass


@dataclass(frozen=True)
class SafetyBounds:
    min_x_m: float = -1.0
    max_x_m: float = 20.0
    min_z_m: float = 0.0
    max_z_m: float = 30.0
    min_standoff_m: float = 1.0
    max_standoff_m: float = 2.5
    target_standoff_m: float = 1.5
    wind_abort_mps: float = 8.0
    min_reservoir_l: float = 0.25
    min_battery_pct: float = 20.0


@dataclass(frozen=True)
class MissionState:
    x_m: float
    y_m: float
    z_m: float
    standoff_m: float
    wind_mps: float
    reservoir_l: float
    battery_pct: float
    lidar_valid: bool = True


@dataclass(frozen=True)
class RewardWeights:
    coverage_gain: float = 10.0
    target_progress: float = 1.5
    overlap_penalty: float = 2.0
    path_length_penalty: float = 0.1
    standoff_penalty: float = 5.0
    reservoir_penalty: float = 1.0
    obstacle_penalty: float = 20.0
