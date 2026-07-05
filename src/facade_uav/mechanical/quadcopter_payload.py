from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class QuadcopterPayloadSpec:
    arm_length_m: float = 0.42
    rotor_diameter_m: float = 0.254
    body_length_m: float = 0.32
    body_width_m: float = 0.24
    body_height_m: float = 0.075
    reservoir_l: float = 1.2
    dry_frame_kg: float = 1.05
    motor_kg_each: float = 0.095
    prop_kg_each: float = 0.018
    battery_kg: float = 0.62
    pump_kg: float = 0.18
    blower_kg: float = 0.22
    gimbal_sensor_kg: float = 0.16
    hose_nozzle_kg: float = 0.14
    landing_gear_kg: float = 0.18
    water_density_kg_per_l: float = 1.0
    max_motor_thrust_n_each: float = 18.0
    payload_y_offset_m: float = -0.09
    reservoir_y_offset_m: float = 0.02
    battery_y_offset_m: float = 0.07
    max_allowable_cg_offset_m: float = 0.035


def estimate_mass_budget(spec: QuadcopterPayloadSpec) -> dict[str, float | bool]:
    water_kg = spec.reservoir_l * spec.water_density_kg_per_l
    motor_total = 4.0 * spec.motor_kg_each
    prop_total = 4.0 * spec.prop_kg_each
    dry_mass = (
        spec.dry_frame_kg
        + motor_total
        + prop_total
        + spec.battery_kg
        + spec.pump_kg
        + spec.blower_kg
        + spec.gimbal_sensor_kg
        + spec.hose_nozzle_kg
        + spec.landing_gear_kg
    )
    wet_mass = dry_mass + water_kg
    max_thrust_n = 4.0 * spec.max_motor_thrust_n_each
    weight_n = wet_mass * 9.81
    thrust_to_weight = max_thrust_n / weight_n
    cg_y_m = (
        spec.battery_kg * spec.battery_y_offset_m
        + water_kg * spec.reservoir_y_offset_m
        + (spec.pump_kg + spec.blower_kg + spec.hose_nozzle_kg + spec.gimbal_sensor_kg)
        * spec.payload_y_offset_m
    ) / wet_mass
    return {
        "dry_mass_kg": round(dry_mass, 3),
        "water_mass_kg": round(water_kg, 3),
        "wet_mass_kg": round(wet_mass, 3),
        "max_thrust_n": round(max_thrust_n, 3),
        "weight_n": round(weight_n, 3),
        "thrust_to_weight": round(thrust_to_weight, 3),
        "cg_y_m": round(cg_y_m, 4),
        "cg_within_limit": abs(cg_y_m) <= spec.max_allowable_cg_offset_m,
        "reservoir_l": round(spec.reservoir_l, 3),
    }


def default_spec_dict() -> dict[str, float]:
    return asdict(QuadcopterPayloadSpec())


def load_spec_from_dict(values: dict[str, float]) -> QuadcopterPayloadSpec:
    defaults = default_spec_dict()
    defaults.update(values)
    return QuadcopterPayloadSpec(**defaults)
