Write-Host "Facade UAV environment check"
Write-Host "PowerShell:" $PSVersionTable.PSVersion
Write-Host "Python:"
python --version

Write-Host "`nPython packages:"
$packages = @("numpy", "cv2", "gymnasium", "stable_baselines3", "torch", "ultralytics")
foreach ($pkg in $packages) {
    python -c "import $pkg; print('$pkg OK')" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "$pkg missing"
    }
}

Write-Host "`nWSL:"
wsl.exe -l -v
