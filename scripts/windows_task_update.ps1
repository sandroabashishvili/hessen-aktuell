$ErrorActionPreference = "Stop"

$ProjectPath = "/home/sandro/portfolio_projects/hessen_aktuell"
$BaseUrl = $env:HESSEN_AKTUELL_BASE_URL
if (-not $BaseUrl) {
    $BaseUrl = "https://sandro-abashishvili.de/hessen-aktuell"
}

$LogDir = "\\wsl$\Ubuntu\home\sandro\portfolio_projects\hessen_aktuell\shared\data\automation_logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$Stamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$LogPath = Join-Path $LogDir "update_$Stamp.log"

$Command = "cd $ProjectPath && HESSEN_AKTUELL_BASE_URL='$BaseUrl' AUTO_COMMIT='1' bash scripts/build_publish.sh"
$PreviousErrorPreference = $ErrorActionPreference
$ErrorActionPreference = "Continue"
$Output = & wsl.exe bash -lc $Command 2>&1
$ExitCode = $LASTEXITCODE
$ErrorActionPreference = $PreviousErrorPreference

$Output | ForEach-Object { Write-Output $_ }
$Output | Out-File -FilePath $LogPath -Encoding utf8

if ($ExitCode -ne 0) {
    throw "Hessen Aktuell update failed with exit code $ExitCode. See $LogPath"
}

exit 0
