# Iterative Critique Checklist

Generated on 2026-07-06 IST.

## Current Judge Verdict

The project is now strong enough for an honest interview demo because it has:

- A visible mechanical payload concept.
- A dry-run mass and CG check.
- A richer virtual world with the actual cleaning story represented.
- A verified software loop from map to route to safety to actuation log.
- Documentation that admits weak areas instead of overclaiming.

## What Passed

- SolidWorks macro assets exist and include reservoir, pump, spray bar, blower,
  gimbal, and hose dock features.
- Mechanical dry-run passes with thrust-to-weight `1.747`.
- Interview Gazebo world validates with `gz sdf -k`.
- ROS package builds with `interview_demo.launch.py`.
- Closed-loop mission demo passes with `0` clearance violations.
- Injected gust triggers safety override.

## What Still Needs Refinement

1. Real SolidWorks execution
   - Run the macro inside SolidWorks.
   - Save `.SLDPRT` and screenshots.
   - Export STEP/Parasolid for portfolio proof.

2. PX4/Gazebo dynamic flight
   - Add or import a dynamic quadrotor model.
   - Connect offboard velocity commands to PX4 SITL.
   - Show takeoff, standoff hold, cleaning pass, and abort behavior.

3. Learned perception quality
   - Train SegFormer at higher resolution for multiple epochs.
   - Replace or redesign YOLO obstacle labels because current YOLO failed the
     overfit diagnostic.
   - Add real facade obstacle classes such as AC units, ropes, open windows,
     people, pipes, and ledges.

4. PPO/RL gate
   - Add map/CNN observation.
   - Train curriculum stages.
   - Compare against greedy baseline across multiple held-out seeds.
   - Do not claim RL superiority until it passes.

5. Final presentation assets
   - Record a short screen capture of the Gazebo world.
   - Capture SolidWorks screenshots.
   - Make a one-page architecture slide.
   - Prepare a two-minute explanation script.

## Next Refinement Loop

The next best engineering step is PX4/Gazebo dynamic integration:

```text
interview world -> dynamic UAV model -> offboard velocity bridge -> safety node
-> route command playback -> visible cleaning pass
```

That would turn the current visual simulation and logged software proof into a
motion demo.

