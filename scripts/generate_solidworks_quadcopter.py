from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from facade_uav.mechanical.quadcopter_payload import (
    QuadcopterPayloadSpec,
    estimate_mass_budget,
    load_spec_from_dict,
)


def load_spec(path: Path) -> QuadcopterPayloadSpec:
    if not path.exists():
        return QuadcopterPayloadSpec()
    return load_spec_from_dict(json.loads(path.read_text(encoding="utf-8")))


def validate_budget(budget: dict[str, float | bool]) -> list[str]:
    issues: list[str] = []
    if float(budget["thrust_to_weight"]) < 1.5:
        issues.append("thrust_to_weight below 1.5; interview design has too little lift margin")
    if not bool(budget["cg_within_limit"]):
        issues.append("cg_y_m outside allowable payload offset; shift reservoir/battery toward center")
    if float(budget["reservoir_l"]) < 1.0:
        issues.append("reservoir_l below 1.0; cleaning demo may look under-specified")
    return issues


def write_design_spec(spec: QuadcopterPayloadSpec, output_dir: Path) -> Path:
    budget = estimate_mass_budget(spec)
    issues = validate_budget(budget)
    output_dir.mkdir(parents=True, exist_ok=True)
    out = output_dir / "quadcopter_payload_spec.json"
    out.write_text(
        json.dumps(
            {
                "solidworks_macro": str(
                    (ROOT / "cad" / "solidworks" / "facade_cleaning_quadcopter_generator.vba").resolve()
                ),
                "parameters": spec.__dict__,
                "mass_budget": budget,
                "validation_issues": issues,
                "status": "pass" if not issues else "review_required",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return out


def try_launch_solidworks(macro_path: Path) -> None:
    try:
        import win32com.client  # type: ignore
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "pywin32 is not installed. Run the macro manually in SolidWorks or install pywin32."
        ) from exc

    try:
        sw_app = win32com.client.Dispatch("SldWorks.Application")
    except Exception as exc:
        raise RuntimeError("Could not connect to SolidWorks COM. Is SolidWorks installed?") from exc

    sw_app.Visible = True
    print(f"SolidWorks opened. Run this macro from the VBA editor: {macro_path}")
    print("The macro entry point is: main")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default="cad/solidworks/quadcopter_payload_parameters.json",
        help="Mechanical parameter JSON.",
    )
    parser.add_argument("--output-dir", default="outputs/cad")
    parser.add_argument(
        "--run-solidworks",
        action="store_true",
        help="Open SolidWorks through COM if available. The macro is still run from SolidWorks.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate parameters and write the design spec without launching SolidWorks.",
    )
    args = parser.parse_args()

    config_path = ROOT / args.config
    spec = load_spec(config_path)
    out = write_design_spec(spec, ROOT / args.output_dir)
    result = json.loads(out.read_text(encoding="utf-8"))
    print(json.dumps(result, indent=2))
    if result["validation_issues"]:
        raise SystemExit("mechanical design needs review")

    if args.run_solidworks:
        try_launch_solidworks(ROOT / "cad" / "solidworks" / "facade_cleaning_quadcopter_generator.vba")
    elif not args.dry_run:
        print("Dry-run complete. Use --run-solidworks on a machine with SolidWorks installed.")


if __name__ == "__main__":
    main()

