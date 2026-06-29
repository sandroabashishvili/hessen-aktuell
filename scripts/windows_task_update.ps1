$ErrorActionPreference = "Stop"

$ProjectPath = "/home/sandro/portfolio_projects/hessen_aktuell"
$BaseUrl = $env:HESSEN_AKTUELL_BASE_URL
if (-not $BaseUrl) {
    $BaseUrl = "https://sandroabashishvili.github.io/hessen-aktuell"
}

$LogDir = "\\wsl$\Ubuntu\home\sandro\portfolio_projects\hessen_aktuell\shared\data\automation_logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$Stamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$LogPath = Join-Path $LogDir "update_$Stamp.log"

$Command = "cd $ProjectPath && HESSEN_AKTUELL_BASE_URL='$BaseUrl' AUTO_COMMIT='1' bash scripts/build_publish.sh"
wsl bash -lc $Command 2>&1 | Tee-Object -FilePath $LogPath
