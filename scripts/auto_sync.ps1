param(
    [int]$IntervalSeconds = 60,
    [string]$Remote = "origin",
    [string]$Branch = "main",
    [switch]$RunOnce
)

function Write-Stamp {
    param([string]$Message)
    $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$stamp] $Message"
}

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

Write-Stamp "Auto sync started for $Remote/$Branch. Checking every $IntervalSeconds seconds."

while ($true) {
    git fetch $Remote $Branch | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Stamp "Fetch failed. Auto sync stopped."
        break
    }

    $localHead = (git rev-parse HEAD).Trim()
    $remoteHead = (git rev-parse "$Remote/$Branch").Trim()
    if ($LASTEXITCODE -ne 0) {
        Write-Stamp "Could not read branch state. Auto sync stopped."
        break
    }

    if ($localHead -ne $remoteHead) {
        Write-Stamp "Remote update detected. Pulling latest changes..."
        git pull --rebase --autostash $Remote $Branch
        if ($LASTEXITCODE -ne 0) {
            Write-Stamp "Pull failed. Resolve conflicts, then restart auto sync."
            break
        }
        Write-Stamp "Local workspace updated."
    } else {
        Write-Stamp "Already up to date."
    }

    if ($RunOnce) {
        break
    }

    Start-Sleep -Seconds $IntervalSeconds
}
