from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "docs" / "20_senior_engineer_teaching_guide.md"
TODOS = ROOT / "docs" / "19_teaching_todos_and_checkpoints.md"


REQUIRED_STAGE_HEADINGS = [
    "## Stage 0 - The Problem",
    "## Stage 1 - Requirement Engineering",
    "## Stage 2 - Solution Ideation",
    "## Stage 3 - System Design",
    "## Stage 4 - Repository Structure",
    "## Stage 5 - File-By-File Walkthrough",
    "## Stage 6 - Function-By-Function",
    "## Stage 7 - Data Flow",
    "## Stage 8 - Execution Flow",
    "## Stage 9 - Libraries",
    "## Stage 10 - Testing",
    "## Stage 11 - Debugging",
    "## Stage 12 - Production Readiness",
    "## Stage 13 - Engineering Review",
    "## Stage 14 - Rebuild Roadmap",
]

REQUIRED_FRAMEWORK_HEADINGS = [
    "### 1. THE PROBLEM",
    "### 2. THE NAIVE SOLUTION",
    "### 3. THE ENGINEERING SOLUTION",
    "### 4. MINIMAL EXAMPLE",
    "### 5. IN MY PROJECT",
    "### 6. COMMON AI-GENERATED MISTAKES",
    "### 7. DEBUGGING",
    "### 8. INTERVIEW DEFENSE",
    "### 9. REBUILD CHALLENGE",
]

REQUIRED_PROJECT_FILES = [
    "src/facade_uav/cleaning_zone_map.py",
    "src/facade_uav/safety_layer.py",
    "src/facade_uav/planning/coverage_path.py",
    "src/facade_uav/integration/closed_loop.py",
    "src/facade_uav/mechanical/quadcopter_payload.py",
    "simulation/gazebo/interview_facade_cleaning_world.sdf",
    "cad/solidworks/facade_cleaning_quadcopter_generator.vba",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> None:
    require(GUIDE.exists(), f"missing guide: {GUIDE}")
    require(TODOS.exists(), f"missing TODO/checkpoint file: {TODOS}")
    guide = GUIDE.read_text(encoding="utf-8")
    todos = TODOS.read_text(encoding="utf-8")

    missing_stages = [heading for heading in REQUIRED_STAGE_HEADINGS if heading not in guide]
    require(not missing_stages, f"teaching guide missing stages: {missing_stages}")

    missing_framework = [heading for heading in REQUIRED_FRAMEWORK_HEADINGS if heading not in guide]
    require(not missing_framework, f"teaching guide missing framework headings: {missing_framework}")

    missing_files = [path for path in REQUIRED_PROJECT_FILES if path not in guide]
    require(not missing_files, f"teaching guide missing project file references: {missing_files}")

    require("Two-Pass Verification Rule" in todos, "TODO file missing two-pass verification rule")
    require("Work Trace Template" in todos, "TODO file missing work trace template")

    print(
        {
            "teaching_docs": "pass",
            "stages": len(REQUIRED_STAGE_HEADINGS),
            "framework_headings": len(REQUIRED_FRAMEWORK_HEADINGS),
            "project_file_references": len(REQUIRED_PROJECT_FILES),
        }
    )


if __name__ == "__main__":
    main()
