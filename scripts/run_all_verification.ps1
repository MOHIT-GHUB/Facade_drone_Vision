Write-Host "Running Facade UAV verification inside Ubuntu-22.04-LTS..."
wsl.exe -d Ubuntu-22.04-LTS -- bash -lc "cd /mnt/c/Users/mohit/OneDrive/Documents/Facade_drone_Vision && bash scripts/run_all_verification.sh"
if ($LASTEXITCODE -ne 0) {
    throw "Verification failed with exit code $LASTEXITCODE"
}
Write-Host "Verification complete."
