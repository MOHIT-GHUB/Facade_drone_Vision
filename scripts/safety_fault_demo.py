from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from facade_uav.config import MissionState, SafetyBounds
from facade_uav.safety_layer import SafetyLayer


def main() -> None:
    layer = SafetyLayer(SafetyBounds())
    cases = [
        MissionState(2, 1.5, 5, 1.5, 2, 3, 80),
        MissionState(2, 1.5, 5, 0.7, 2, 3, 80),
        MissionState(2, 1.5, 5, 1.5, 9, 3, 80),
        MissionState(2, 1.5, 5, 1.5, 2, 0.1, 80),
        MissionState(2, 1.5, 5, 1.5, 2, 3, 10),
        MissionState(2, 1.5, 5, 1.5, 2, 3, 80, lidar_valid=False),
    ]
    results = [
        {
            "case": idx,
            "state": case.__dict__,
            "decision": layer.evaluate(case, {"vx": 0.2, "vz": 0.0}).__dict__,
        }
        for idx, case in enumerate(cases)
    ]
    out = ROOT / "outputs" / "safety_fault_demo.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
