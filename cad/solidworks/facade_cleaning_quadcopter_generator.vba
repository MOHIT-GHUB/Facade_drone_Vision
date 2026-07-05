Option Explicit

' SolidWorks VBA macro for an interview-ready facade-cleaning quadcopter.
' Units are meters. The model is a simplified multibody part intended for
' architecture review, mass/CG discussion, and simulation-to-CAD traceability.

Const ARM_LENGTH_M As Double = 0.42
Const ROTOR_DIAMETER_M As Double = 0.254
Const BODY_LENGTH_M As Double = 0.32
Const BODY_WIDTH_M As Double = 0.24
Const BODY_HEIGHT_M As Double = 0.075
Const RESERVOIR_DIAMETER_M As Double = 0.18
Const RESERVOIR_LENGTH_M As Double = 0.22
Const ARM_WIDTH_M As Double = 0.035
Const ARM_THICKNESS_M As Double = 0.024
Const MOTOR_RADIUS_M As Double = 0.045
Const MOTOR_DEPTH_M As Double = 0.045
Const PROP_DISC_DEPTH_M As Double = 0.006
Const SPRAY_BAR_WIDTH_M As Double = 0.28
Const SPRAY_BAR_HEIGHT_M As Double = 0.018
Const BLOWER_RADIUS_M As Double = 0.04
Const BLOWER_DEPTH_M As Double = 0.07

Dim swApp As Object
Dim swModel As Object

Sub main()
    Set swApp = Application.SldWorks
    Dim templatePath As String
    templatePath = swApp.GetUserPreferenceStringValue(1)
    Set swModel = swApp.NewDocument(templatePath, 0, 0, 0)
    If swModel Is Nothing Then
        MsgBox "Could not create a new SolidWorks part. Check default part template."
        Exit Sub
    End If

    swModel.SetTitle2 "facade_cleaning_quadcopter_payload"
    BuildFrame
    BuildPropulsion
    BuildCleaningPayload
    BuildSensorsAndSkids
    AddCustomProperties
    swModel.ViewZoomtofit2
    MsgBox "Facade cleaning quadcopter payload model generated. Save as facade_cleaning_quadcopter_payload.SLDPRT."
End Sub

Sub BuildFrame()
    AddExtrudedBox "central_carbon_body_plate", 0#, 0#, BODY_LENGTH_M, BODY_HEIGHT_M, BODY_WIDTH_M, 0.15, 0.15, 0.16
    AddRotatedArm "front_right_carbon_arm", ARM_LENGTH_M / 2#, ARM_LENGTH_M / 2#, 45#
    AddRotatedArm "front_left_carbon_arm", -ARM_LENGTH_M / 2#, ARM_LENGTH_M / 2#, -45#
    AddRotatedArm "rear_right_carbon_arm", ARM_LENGTH_M / 2#, -ARM_LENGTH_M / 2#, -45#
    AddRotatedArm "rear_left_carbon_arm", -ARM_LENGTH_M / 2#, -ARM_LENGTH_M / 2#, 45#
End Sub

Sub BuildPropulsion()
    AddMotorAndProp "front_right", ARM_LENGTH_M, ARM_LENGTH_M
    AddMotorAndProp "front_left", -ARM_LENGTH_M, ARM_LENGTH_M
    AddMotorAndProp "rear_right", ARM_LENGTH_M, -ARM_LENGTH_M
    AddMotorAndProp "rear_left", -ARM_LENGTH_M, -ARM_LENGTH_M
End Sub

Sub BuildCleaningPayload()
    AddExtrudedCircle "cg_centered_water_reservoir", 0#, 0.01, RESERVOIR_DIAMETER_M / 2#, RESERVOIR_LENGTH_M, 0.05, 0.42, 0.95
    AddExtrudedBox "front_high_pressure_pump", 0#, -0.19, 0.13, 0.07, 0.08, 0.12, 0.12, 0.12
    AddExtrudedBox "front_water_jet_spray_bar", 0#, -0.245, SPRAY_BAR_WIDTH_M, SPRAY_BAR_HEIGHT_M, 0.03, 0.05, 0.18, 0.95
    AddExtrudedCircle "left_air_blower_duct", -0.105, -0.265, BLOWER_RADIUS_M, BLOWER_DEPTH_M, 0.12, 0.12, 0.12
    AddExtrudedCircle "right_air_blower_duct", 0.105, -0.265, BLOWER_RADIUS_M, BLOWER_DEPTH_M, 0.12, 0.12, 0.12
    AddExtrudedBox "quick_connect_water_hose_dock", 0#, 0.22, 0.16, 0.035, 0.05, 0.05, 0.35, 0.95
    AddExtrudedBox "replaceable_nozzle_manifold", 0#, -0.285, 0.23, 0.012, 0.025, 0.02, 0.08, 0.92
End Sub

Sub BuildSensorsAndSkids()
    AddExtrudedBox "gimbal_rgb_thermal_lidar_pod", 0#, -0.115, 0.1, 0.075, 0.065, 0.02, 0.02, 0.02
    AddExtrudedBox "left_landing_skid", -0.115, 0#, 0.035, 0.46, 0.025, 0.05, 0.05, 0.05
    AddExtrudedBox "right_landing_skid", 0.115, 0#, 0.035, 0.46, 0.025, 0.05, 0.05, 0.05
End Sub

Sub AddMotorAndProp(prefix As String, x As Double, z As Double)
    AddExtrudedCircle prefix & "_motor_pod", x, z, MOTOR_RADIUS_M, MOTOR_DEPTH_M, 0.08, 0.08, 0.08
    AddExtrudedCircle prefix & "_transparent_prop_disc", x, z, ROTOR_DIAMETER_M / 2#, PROP_DISC_DEPTH_M, 0.7, 0.82, 0.95
End Sub

Sub AddRotatedArm(featureName As String, cx As Double, cz As Double, angleDeg As Double)
    Dim lengthM As Double
    lengthM = Sqr(cx * cx + cz * cz) * 2#
    AddRotatedExtrudedRectangle featureName, cx / 2#, cz / 2#, lengthM, ARM_WIDTH_M, ARM_THICKNESS_M, angleDeg, 0.06, 0.06, 0.06
End Sub

Sub AddExtrudedBox(featureName As String, centerX As Double, centerZ As Double, widthX As Double, heightZ As Double, depthY As Double, r As Double, g As Double, b As Double)
    SelectFrontPlane
    swModel.SketchManager.InsertSketch True
    swModel.SketchManager.CreateCenterRectangle centerX, centerZ, 0#, centerX + widthX / 2#, centerZ + heightZ / 2#, 0#
    swModel.SketchManager.InsertSketch True
    Dim feat As Object
    Set feat = swModel.FeatureManager.FeatureExtrusion2(True, False, False, 6, 0, depthY / 2#, depthY / 2#, False, False, False, False, 0#, 0#, False, False, False, False, True, True, True, 0, 0, False)
    If Not feat Is Nothing Then
        feat.Name = featureName
        ApplyMaterialColor feat, r, g, b
    End If
End Sub

Sub AddRotatedExtrudedRectangle(featureName As String, centerX As Double, centerZ As Double, lengthX As Double, widthZ As Double, depthY As Double, angleDeg As Double, r As Double, g As Double, b As Double)
    Dim a As Double
    a = angleDeg * 3.14159265358979 / 180#
    Dim ux As Double, uz As Double, vx As Double, vz As Double
    ux = Cos(a) * lengthX / 2#: uz = Sin(a) * lengthX / 2#
    vx = -Sin(a) * widthZ / 2#: vz = Cos(a) * widthZ / 2#
    SelectFrontPlane
    swModel.SketchManager.InsertSketch True
    swModel.SketchManager.CreateLine centerX - ux - vx, centerZ - uz - vz, 0#, centerX + ux - vx, centerZ + uz - vz, 0#
    swModel.SketchManager.CreateLine centerX + ux - vx, centerZ + uz - vz, 0#, centerX + ux + vx, centerZ + uz + vz, 0#
    swModel.SketchManager.CreateLine centerX + ux + vx, centerZ + uz + vz, 0#, centerX - ux + vx, centerZ - uz + vz, 0#
    swModel.SketchManager.CreateLine centerX - ux + vx, centerZ - uz + vz, 0#, centerX - ux - vx, centerZ - uz - vz, 0#
    swModel.SketchManager.InsertSketch True
    Dim feat As Object
    Set feat = swModel.FeatureManager.FeatureExtrusion2(True, False, False, 6, 0, depthY / 2#, depthY / 2#, False, False, False, False, 0#, 0#, False, False, False, False, True, True, True, 0, 0, False)
    If Not feat Is Nothing Then
        feat.Name = featureName
        ApplyMaterialColor feat, r, g, b
    End If
End Sub

Sub AddExtrudedCircle(featureName As String, centerX As Double, centerZ As Double, radius As Double, depthY As Double, r As Double, g As Double, b As Double)
    SelectFrontPlane
    swModel.SketchManager.InsertSketch True
    swModel.SketchManager.CreateCircleByRadius centerX, centerZ, 0#, radius
    swModel.SketchManager.InsertSketch True
    Dim feat As Object
    Set feat = swModel.FeatureManager.FeatureExtrusion2(True, False, False, 6, 0, depthY / 2#, depthY / 2#, False, False, False, False, 0#, 0#, False, False, False, False, True, True, True, 0, 0, False)
    If Not feat Is Nothing Then
        feat.Name = featureName
        ApplyMaterialColor feat, r, g, b
    End If
End Sub

Sub SelectFrontPlane()
    swModel.Extension.SelectByID2 "Front Plane", "PLANE", 0, 0, 0, False, 0, Nothing, 0
End Sub

Sub ApplyMaterialColor(feat As Object, r As Double, g As Double, b As Double)
    Dim colorData(8) As Double
    colorData(0) = r
    colorData(1) = g
    colorData(2) = b
    colorData(3) = 1#
    colorData(4) = 1#
    colorData(5) = 0.5
    colorData(6) = 0.35
    colorData(7) = 0#
    colorData(8) = 0#
    feat.MaterialPropertyValues = colorData
End Sub

Sub AddCustomProperties()
    Dim props As Object
    Set props = swModel.Extension.CustomPropertyManager("")
    props.Add3 "Project", 30, "Autonomous Facade Cleaning UAV", 2
    props.Add3 "Payload", 30, "Water jet + air blower + RGB/thermal/LiDAR sensor pod", 2
    props.Add3 "Reservoir_L", 30, "1.2", 2
    props.Add3 "DesignIntent", 30, "Interview CAD model generated from repository macro", 2
    props.Add3 "SimulationTrace", 30, "Matches simulation/gazebo/interview_facade_cleaning_world.sdf visual payload layout", 2
End Sub
