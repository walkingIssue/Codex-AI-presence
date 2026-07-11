param()

$ErrorActionPreference = "Stop"
$orbRoot = $PSScriptRoot
$electron = Join-Path $orbRoot "node_modules\electron\dist\electron.exe"
$pidPath = Join-Path $orbRoot "orb.pid"

if (Test-Path -LiteralPath $pidPath -PathType Leaf) {
    try {
        $existingPid = [int](Get-Content -LiteralPath $pidPath -Raw).Trim()
        if (Get-Process -Id $existingPid -ErrorAction SilentlyContinue) {
            exit 0
        }
    } catch {
        # The stale PID file will be replaced by the next launch.
    }
}

if (-not (Test-Path -LiteralPath $electron -PathType Leaf)) {
    throw "Strand Orb dependencies are not installed. Run npm install in $orbRoot"
}

$appArgument = '"' + $orbRoot + '"'
Start-Process -FilePath $electron -ArgumentList $appArgument -WorkingDirectory $orbRoot -WindowStyle Hidden | Out-Null
