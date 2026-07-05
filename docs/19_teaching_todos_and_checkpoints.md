# Teaching TODOs And Checkpoints

Generated on 2026-07-06 IST.

## Purpose

This file exists so the learning work is traceable. The goal is not only to own
the repository. The goal is to become able to rebuild, debug, defend, extend,
and maintain the project without AI.

The teaching master prompt requires this order:

```text
problem -> business need -> requirements -> constraints -> solution options ->
trade-offs -> architecture -> modules -> algorithms -> data flow ->
control flow -> implementation -> testing -> debugging -> deployment ->
maintenance -> future improvements
```

## How To Use This File

For each checkpoint:

1. Read the linked teaching section.
2. Close the file.
3. Explain the idea from memory.
4. Rebuild the small example or diagram.
5. Run the verification command.
6. Mark the checkpoint only when you can defend the "why", not only the code.

## Teaching Artifacts

| Artifact | Purpose | Status |
|---|---|---|
| `docs/20_senior_engineer_teaching_guide.md` | Main senior-engineer teaching guide | Created |
| `scripts/check_teaching_docs.py` | Verifies the guide follows the required stage/framework structure | Created |
| `docs/18_iterative_critique_checklist.md` | Current project critique and next refinement loop | Created |
| `docs/17_solidworks_and_interview_demo_plan.md` | Interview demo, CAD, and Gazebo story | Created |
| `docs/16_closed_loop_mission_demo.md` | End-to-end software loop proof | Created |

## Master Walkthrough Checkpoints

| Stage | Topic | Evidence | Learner checkpoint |
|---|---|---|---|
| 0 | The real-world problem | `docs/20_senior_engineer_teaching_guide.md#stage-0-the-problem` | Explain why facade cleaning is not just "drone plus camera" |
| 1 | Requirement engineering | `docs/20_senior_engineer_teaching_guide.md#stage-1-requirement-engineering` | Derive functional and non-functional requirements |
| 2 | Solution ideation | `docs/20_senior_engineer_teaching_guide.md#stage-2-solution-ideation` | Compare naive, monolithic, and modular architectures |
| 3 | System design | `docs/20_senior_engineer_teaching_guide.md#stage-3-system-design` | Draw the architecture from memory |
| 4 | Repository structure | `docs/20_senior_engineer_teaching_guide.md#stage-4-repository-structure` | Explain why each folder exists |
| 5 | File walkthrough | `docs/20_senior_engineer_teaching_guide.md#stage-5-file-by-file-walkthrough` | Identify inputs, outputs, owners, and failure modes |
| 6 | Function walkthrough | `docs/20_senior_engineer_teaching_guide.md#stage-6-function-by-function` | Explain important functions by purpose and edge cases |
| 7 | Data flow | `docs/20_senior_engineer_teaching_guide.md#stage-7-data-flow` | Trace image/map/route/command data end to end |
| 8 | Execution flow | `docs/20_senior_engineer_teaching_guide.md#stage-8-execution-flow` | Trace program launch and demo execution |
| 9 | Libraries | `docs/20_senior_engineer_teaching_guide.md#stage-9-libraries` | Justify OpenCV, ROS 2, Gazebo, SB3, Torch, and Ultralytics |
| 10 | Testing | `docs/20_senior_engineer_teaching_guide.md#stage-10-testing` | Explain what each verification command proves and does not prove |
| 11 | Debugging | `docs/20_senior_engineer_teaching_guide.md#stage-11-debugging` | Diagnose failures by data, logic, config, dependency, and environment |
| 12 | Production readiness | `docs/20_senior_engineer_teaching_guide.md#stage-12-production-readiness` | Explain missing production pieces honestly |
| 13 | Engineering review | `docs/20_senior_engineer_teaching_guide.md#stage-13-engineering-review` | Critique strengths, weaknesses, debt, and risks |
| 14 | Rebuild roadmap | `docs/20_senior_engineer_teaching_guide.md#stage-14-rebuild-roadmap` | Rebuild the project milestone by milestone |

## Concept Checkpoints

Each concept in the teaching guide follows the required 9-part framework:

1. The problem
2. The naive solution
3. The engineering solution
4. Minimal example
5. In my project
6. Common AI-generated mistakes
7. Debugging
8. Interview defense
9. Rebuild challenge

| Concept | Why it matters | Pass condition |
|---|---|---|
| Cleaning-zone map | Converts raw perception into planner-safe state | Build a 4x3 map by hand and mark clean, skip, blocked |
| Safety layer | Keeps unsafe commands out of the control loop | Explain every abort/hold/return-to-base branch |
| Obstacle-aware route planning | Prevents cleaning through blocked facade regions | Draw BFS around an inflated obstacle |
| Closed-loop executor | Connects route to command, safety, and actuation | Explain one nominal event and one fault event |
| Mechanical payload | Makes the UAV credible as a cleaning machine | Defend mass, CG, reservoir, pump, blower, and thrust assumptions |
| Gazebo interview world | Gives the project a visible demo environment | Point out start pad, refill station, dirt, skip zones, and obstacles |
| RL and baselines | Prevents fake RL claims | Explain why greedy is trusted and PPO is not yet claimed |

## Verification Commands

Run the teaching document structure check:

```bash
python3 scripts/check_teaching_docs.py
```

Run the complete project verification:

```bash
bash scripts/run_all_verification.sh
```

From PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_all_verification.ps1
```

## Two-Pass Verification Rule

Before delivery, run the full verification twice.

Pass criteria:

- Both runs finish with `verification complete`.
- The teaching doc checker passes in both runs.
- The ROS package builds in both runs.
- SDF validation passes in both runs.
- Closed-loop mission still has `0` clearance violations.
- Fault demo still triggers a safety override.

## Work Trace Template

Use this format after every future refinement:

```text
Date:
Work item:
Why it exists:
Naive approach avoided:
Engineering choice:
Files changed:
Verification run:
Result:
Remaining risk:
Next checkpoint:
```

