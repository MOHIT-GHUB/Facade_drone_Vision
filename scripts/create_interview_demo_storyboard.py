from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    out_dir = ROOT / "outputs" / "interview_demo"
    out_dir.mkdir(parents=True, exist_ok=True)

    cad_spec = read_json(ROOT / "outputs" / "cad" / "quadcopter_payload_spec.json")
    closed_loop = read_json(ROOT / "outputs" / "closed_loop_mission" / "summary.json")
    asset_check = read_json(out_dir / "asset_check.json")

    steps = [
        {
            "step": 1,
            "title": "Start and water connection",
            "show": "UAV on the start pad beside the refill station and hose dock.",
            "technical_point": "Dedicated reservoir, pump, quick-connect water dock, and blower ducts are visible in CAD and Gazebo.",
        },
        {
            "step": 2,
            "title": "Takeoff and facade scan",
            "show": "Drone moves from start pad toward the glass facade at safe standoff.",
            "technical_point": "RGB/thermal/LiDAR sensor pod feeds a cleaning-zone map; OpenCV is the trusted baseline and SegFormer is wired for learned segmentation.",
        },
        {
            "step": 3,
            "title": "Analyze what to clean and skip",
            "show": "Dirty glass targets, concrete skip panels, window frames, AC units, and ledges are separated.",
            "technical_point": "Cleanable glass becomes route targets; concrete, frames, and inflated obstacle clearance become skip zones.",
        },
        {
            "step": 4,
            "title": "Plan safe route",
            "show": "Route markers show scan and clean targets while avoiding protrusions.",
            "technical_point": "Greedy nearest-dirty is the trusted v1 planner; PPO is trained/evaluable but has not passed the baseline gate yet.",
        },
        {
            "step": 5,
            "title": "Clean with water jet and air blower",
            "show": "Water spray bar and blower ducts face the facade; actuation logs only trigger on safe clean steps.",
            "technical_point": "Reservoir depletion and battery drain are tracked in the closed-loop execution log.",
        },
        {
            "step": 6,
            "title": "Fault and safety proof",
            "show": "Injected gust case stops the mission independently of the planner.",
            "technical_point": "Safety layer enforces wind, standoff, geofence, reservoir, battery, and LiDAR validity.",
        },
    ]

    storyboard = {
        "demo_launch": "ros2 launch facade_cleaning_uav interview_demo.launch.py",
        "standalone_world": "gz sim -r simulation/gazebo/interview_facade_cleaning_world.sdf",
        "cad_macro": "cad/solidworks/facade_cleaning_quadcopter_generator.vba",
        "cad_mass_budget": cad_spec.get("mass_budget", {}),
        "closed_loop_metrics": {
            "nominal": closed_loop.get("nominal_metrics", {}),
            "fault": closed_loop.get("fault_metrics", {}),
            "clearance_violations": closed_loop.get("clearance_violations", []),
        },
        "asset_check": asset_check.get("status", "not_run"),
        "steps": steps,
        "honest_limits": [
            "SolidWorks macro is generated and dry-run checked here, but final CAD creation requires SolidWorks on Windows.",
            "Gazebo world is visual/interview-ready; PX4 dynamic closed-loop flight remains the next integration gate.",
            "YOLO obstacle detector is a pipeline proof only; do not claim it is safety-ready.",
            "PPO has not beaten the deterministic baseline yet.",
        ],
    }

    json_path = out_dir / "interview_demo_storyboard.json"
    md_path = out_dir / "interview_demo_storyboard.md"
    json_path.write_text(json.dumps(storyboard, indent=2), encoding="utf-8")

    lines = [
        "# Interview Demo Storyboard",
        "",
        f"Launch: `{storyboard['demo_launch']}`",
        f"Standalone world: `{storyboard['standalone_world']}`",
        f"SolidWorks macro: `{storyboard['cad_macro']}`",
        "",
        "## Mechanical proof",
        "",
        f"- Wet mass kg: `{cad_spec.get('mass_budget', {}).get('wet_mass_kg', 'n/a')}`",
        f"- Thrust-to-weight: `{cad_spec.get('mass_budget', {}).get('thrust_to_weight', 'n/a')}`",
        f"- CG Y offset m: `{cad_spec.get('mass_budget', {}).get('cg_y_m', 'n/a')}`",
        "",
        "## Sequence",
        "",
    ]
    for item in steps:
        lines.extend(
            [
                f"{item['step']}. {item['title']}",
                f"   - Show: {item['show']}",
                f"   - Technical point: {item['technical_point']}",
            ]
        )
    lines.extend(["", "## Honest limits", ""])
    for limit in storyboard["honest_limits"]:
        lines.append(f"- {limit}")
    lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"storyboard": str(json_path), "markdown": str(md_path)}, indent=2))


if __name__ == "__main__":
    main()
