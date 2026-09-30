$ErrorActionPreference = "Stop"

if (-not (Get-Command wix -ErrorAction SilentlyContinue)) {
    throw "WiX v4 is required. Install it with: dotnet tool install --global wix"
}

wix build installer\orbit.wxs -o dist\ORBIT.msi
Write-Output "Built dist\ORBIT.msi"