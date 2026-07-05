# SolidWorks Quadcopter Payload Generator

This folder contains the CAD-side proof for the facade-cleaning UAV mechanical
workstream.

## Files

- `facade_cleaning_quadcopter_generator.vba`: SolidWorks VBA macro that creates
  a simplified parametric quadcopter part with X-frame arms, four rotors, water
  reservoir, pump, water-jet spray bar, blower ducts, gimbal/sensor pod, hose
  dock, and landing skids.
- `quadcopter_payload_parameters.json`: shared dimensions and mass assumptions.

## Dry Run

The dry run does not require SolidWorks. It validates the mechanical numbers and
writes a reviewable design spec:

```powershell
python scripts\generate_solidworks_quadcopter.py --dry-run
```

Output:

```text
outputs/cad/quadcopter_payload_spec.json
```

## SolidWorks Run

1. Open SolidWorks on Windows.
2. Open `facade_cleaning_quadcopter_generator.vba` in the VBA macro editor.
3. Run `main`.
4. Review the generated named features and custom properties.
5. Save the part as `facade_cleaning_quadcopter_payload.SLDPRT`.

The macro creates a CAD interview model, not a manufacturing drawing. Its goal
is to show the architecture and payload placement clearly: reservoir near the
CG, pump and water-jet hardware facing the facade, blower ducts near the spray
bar, and sensors under the nose.

