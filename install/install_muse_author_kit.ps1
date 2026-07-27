param(
  [string]$PythonExe = "py -3.12"
)

$ErrorActionPreference = "Stop"

function Invoke-External {
  param(
    [Parameter(Mandatory = $true)]
    [string]$FilePath,
    [string[]]$ArgumentList = @()
  )

  & $FilePath @ArgumentList
  if ($LASTEXITCODE -ne 0) {
    throw "Command failed: $FilePath $($ArgumentList -join ' ')"
  }
}

function Resolve-PythonCommand {
  param([string]$Configured)

  if ($Configured -like "py *") {
    return @{
      FilePath = "py"
      ArgumentList = $Configured.Substring(3).Trim().Split(" ", [System.StringSplitOptions]::RemoveEmptyEntries)
    }
  }

  return @{
    FilePath = $Configured
    ArgumentList = @()
  }
}

$kitRoot = Split-Path -Parent $PSScriptRoot
$venvPath = Join-Path $kitRoot ".venv"
$wheelDir = Join-Path $kitRoot "packages"
$gameRoot = Join-Path $kitRoot "muse-game"

$python = Resolve-PythonCommand -Configured $PythonExe

Write-Host "Creating virtual environment..."
Invoke-External -FilePath $python.FilePath -ArgumentList ($python.ArgumentList + @("-m", "venv", $venvPath))

$venvPython = Join-Path $venvPath "Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
  throw "Could not find virtual environment Python at $venvPython"
}

Write-Host "Upgrading pip..."
Invoke-External -FilePath $venvPython -ArgumentList @("-m", "pip", "install", "--upgrade", "pip")

Write-Host "Installing Evennia..."
Invoke-External -FilePath $venvPython -ArgumentList @("-m", "pip", "install", "evennia")

$wheel = Get-ChildItem -Path $wheelDir -Filter "muselang-*.whl" | Select-Object -First 1
if (-not $wheel) {
  throw "Could not find a MuseLang wheel in $wheelDir"
}

Write-Host "Installing MuseLang from wheel..."
Invoke-External -FilePath $venvPython -ArgumentList @("-m", "pip", "install", $wheel.FullName)

Write-Host "Installing MuseLang runtime into muse-game..."
Invoke-External -FilePath $venvPython -ArgumentList @("-m", "muselang.cli", "runtime-install", "--game-root", $gameRoot)
Invoke-External -FilePath $venvPython -ArgumentList @("-m", "muselang.cli", "doctor", "--game-root", $gameRoot)

Write-Host ""
Write-Host "Muse Author Kit install complete."
Write-Host "MuseLang is installed into .\.venv and the muse-game scaffold is ready."
Write-Host "Next steps:"
Write-Host "  1. .\.venv\Scripts\Activate.ps1"
Write-Host "  2. cd .\muse-game"
Write-Host "  3. evennia migrate"
Write-Host "  4. evennia createsuperuser"
Write-Host "  5. evennia start"
