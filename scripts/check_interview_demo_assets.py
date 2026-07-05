from __future__ import annotations

import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from facade_uav.mechanical.quadcopter_payload import estimate_mass_budget, load_spec_from_dict


REQUIRED_WORLD_MODELS = {
    "facade_cleaning_quadcopter_visual",
    "water_refill_station",
    "washable_glass_facade",
    "dirty_target_patches",
    "skip_zone_concrete_panels",
    "obstacle_ac_units",
    "mission_route_markers",
}

REQUIRED_MACRO_FEATURE_TOKENS = {
    "front_water_jet_spray_bar",
    "left_air_blower_duct",
    "right_air_blower_duct",
    "cg_centered_water_reservoir",
    "gimbal_rgb_thermal_lidar_pod",
    "quick_connect_water_hose_dock",
}


def world_model_names(path: Path) -> set[str]:
    root = ET.parse(path).getroot()
    return {model.attrib["name"] for model in root.findall(".//model") if "name" in model.attrib}


def main() -> None:
    macro = ROOT / "cad" / "solidworks" / "facade_cleaning_quadcopter_generator.vba"
    params = ROOT / "cad" / "solidworks" / "quadcopter_payload_parameters.json"
    sim_world = ROOT / "simulation" / "gazebo" / "interview_facade_cleaning_world.sdf"
    ros_world = ROOT / "ros2_ws" / "src" / "facade_cleaning_uav" / "worlds" / "interview_facade_cleaning_world.sdf"

    missing_files = [path for path in [macro, params, sim_world, ros_world] if not path.exists()]
    if missing_files:
        raise SystemExit(f"missing interview demo files: {missing_files}")

    macro_text = macro.read_text(encoding="utf-8")
    missing_tokens = sorted(token for token in REQUIRED_MACRO_FEATURE_TOKENS if token not in macro_text)
    if missing_tokens:
        raise SystemExit(f"macro is missing payload features: {missing_tokens}")

    sim_models = world_model_names(sim_world)
    ros_models = world_model_names(ros_world)
    missing_models = sorted(REQUIRED_WORLD_MODELS - sim_models)
    if missing_models:
        raise SystemExit(f"simulation world missing models: {missing_models}")
    if sim_models != ros_models:
        raise SystemExit("simulation and ROS interview worlds do not expose the same model names")

    spec = load_spec_from_dict(json.loads(params.read_text(encoding="utf-8")))
    budget = estimate_mass_budget(spec)
    if float(budget["thrust_to_weight"]) < 1.5 or not bool(budget["cg_within_limit"]):
        raise SystemExit(f"mechanical budget failed: {budget}")

    summary = {
        "macro": str(macro),
        "simulation_world": str(sim_world),
        "ros_world": str(ros_world),
        "world_models_checked": sorted(REQUIRED_WORLD_MODELS),
        "mass_budget": budget,
        "status": "pass",
    }
    out = ROOT / "outputs" / "interview_demo" / "asset_check.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
