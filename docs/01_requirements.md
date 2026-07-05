# Requirements

## Mission

Design and simulate an autonomous UAV that cleans glass or curtain-wall skyscraper facades in dense metropolitan environments.

## Success criteria

- End-to-end loop exists in simulation.
- Perception produces a cleaning-zone map.
- Planner accounts for coverage, overlap, path length, wall proximity, reservoir depletion, and wind.
- Independent safety layer can override unsafe actions.
- PPO policy is compared against a lawnmower baseline.
- Documentation explains assumptions and rejected alternatives.

## System assumptions

- v1 facade is a flat vertical panel with window-frame obstacles.
- Standoff target is 1.5 m.
- Safe standoff range is 1.0 m to 2.5 m.
- Mild wind starts at 0 to 4 m/s.
- Abort wind threshold starts at 8 m/s.
- Reservoir starts at 5.0 L and triggers return/hold below 0.25 L.
- Battery triggers return/hold below 20 percent.

## Key engineering risks

- RL policy may learn unsafe shortcuts without an independent safety shield.
- MiDaS depth is relative unless anchored by LiDAR or geometry.
- Close-wall flight stability is strongly affected by wind and wall-effect aerodynamics.
- Reservoir depletion changes mass and center of gravity through the mission.
- A policy trained on one facade can memorize the layout unless held-out facades are used.

## Target metrics

Initial target over a lawnmower baseline:

- 25 percent lower overlap.
- 15 percent lower path length.
- 50 percent fewer standoff violations.
- Zero safety-layer collision escapes in test scenarios.

These targets should be revised only with written justification.
