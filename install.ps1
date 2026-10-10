# TidyMate - one-line installer for Windows (PowerShell).
#
#   irm https://raw.githubusercontent.com/YOUR-GITHUB-USER/tidymate/main/install.ps1 | iex
#
# It creates a private Python environment (so nothing else on your computer is touched),
# installs the tool in it, and creates two commands - tidymate and start_here - that work
# immediately in any new terminal. No admin rights needed. Re-run it any time to update.
# Remove it with:  tidymate setup --uninstall ; then delete  %LOCALAPPDATA%\TidyMate

function Install-TidyMate {
    $ErrorActionPreference = "Stop"
    $Repo = "YOUR-GITHUB-USER/tidymate"
    $Spec = if ($env:TIDYMATE_SPEC) { $env:TIDYMATE_SPEC } else { "https://github.com/$Repo/archive/refs/heads/main.zip" }
    $Root = Join-Path $env:LOCALAPPDATA "TidyMate"
    $Venv = Join-Path $Root "venv"

    # --- find a real Python 3.8+ (skips the Microsoft Store "python" stub) ---
    $pyExe = $null
    $pyArgs = @()
    foreach ($candidate in @(@("py", "-3"), @("python"), @("python3"))) {
        try {
            $exe = $candidate[0]
            $extra = @()
            if ($candidate.Length -gt 1) { $extra = $candidate[1..($candidate.Length - 1)] }
            $out = & $exe @extra --version 2>&1
            if ($LASTEXITCODE -eq 0 -and "$out" -match "Python 3\.(\d+)" -and [int]$Matches[1] -ge 8) {
                $pyExe = $exe
                $pyArgs = $extra
                break
            }
        } catch { }
    }
    if (-not $pyExe) {
        Write-Host ""
        Write-Host " Python 3.8 or newer was not found." -ForegroundColor Yellow
        Write-Host " 1. Install it from https://www.python.org/downloads/ (tick 'Add Python to PATH')"
        Write-Host " 2. Open a new PowerShell window and run this installer again."
        return
    }

    Write-Host "==> Using $pyExe $($pyArgs -join ' ')"
    New-Item -ItemType Directory -Force -Path $Root | Out-Null
    $VenvPy = Join-Path $Venv "Scripts\python.exe"
    if (-not (Test-Path $VenvPy)) {
        & $pyExe @pyArgs -m venv $Venv
        if ($LASTEXITCODE -ne 0) { throw "Could not create the private Python environment." }
    }
    Write-Host "==> Installing TidyMate ..."
    & $VenvPy -m pip install --quiet --upgrade $Spec
    if ($LASTEXITCODE -ne 0) { throw "pip install failed (check your internet connection)." }
    Write-Host "==> Creating the tidymate command ..."
    & $VenvPy -m tidymate setup
}

Install-TidyMate
