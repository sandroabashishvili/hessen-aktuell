# Hessen Aktuell Handoff

Date: 2026-06-25
Project path: /home/sandro/portfolio_projects/hessen_aktuell
Windows path: \\wsl$\Ubuntu\home\sandro\portfolio_projects\hessen_aktuell

## Current Goal

Finish Hessen Aktuell as a GitHub Pages-ready regional news portal that can run in the background on Sandro's always-on computer.

## What Was Done

- Added GitHub Pages support file: .nojekyll
- Added publish/build script: scripts/build_publish.sh
- Added Windows Task Scheduler wrapper: scripts/windows_task_update.ps1
- Updated diagnostics sitemap checker for GitHub Pages project base path.
- Updated diagnostics overall status so transient external source timeout/empty states remain visible but do not block publishing when the generated site itself is healthy
- Rewrote README.md as a clean ASCII publish/run guide after previous encoding damage

## Important Files

- README.md
- .nojekyll
- scripts/build_publish.sh
- scripts/windows_task_update.ps1
- shared/py/diagnostics/__main__.py
- shared/py/diagnostics/sitemap.py
- shared/py/news_pipeline/config.py
- shared/py/news_pipeline/sitemap_builder.py

## Verified Command

Run from WSL:

    cd /home/sandro/portfolio_projects/hessen_aktuell
    HESSEN_AKTUELL_BASE_URL="https://sandroabashishvili.github.io/hessen-aktuell" bash scripts/build_publish.sh

Last verified result:

- news pipeline builds homepage, city pages, topic pages, daily archive
- robots.txt uses https://sandroabashishvili.github.io/hessen-aktuell/sitemap.xml
- sitemap.xml uses https://sandroabashishvili.github.io/hessen-aktuell/... URLs
- internal links: 0 broken
- sitemap: 0 missing, robots ok
- SEO meta: 0 missing
- diagnostics: Overall: ok

Notes from latest runs:

- Source freshness may show a notice for polizei-nordhessen-presse because the latest parsed public item can be older than the build day.
- Mainova can occasionally timeout or return empty during diagnostics, but when site checks are healthy this should not block publishing.
- The folder is not a git repository yet. build_publish.sh currently prints: Not a git repository yet; generation and diagnostics completed only.

## Next Steps

1. Initialize git in /home/sandro/portfolio_projects/hessen_aktuell or create a GitHub repo first.
2. Repository name: hessen-aktuell
3. Add remote, commit, push.
4. Enable GitHub Pages for the repo.
5. Confirm the public URL: https://sandroabashishvili.github.io/hessen-aktuell
6. Run the publish command again with HESSEN_AKTUELL_BASE_URL set to the public URL.
7. After repo push works, test AUTO_COMMIT=1 behavior:

       cd /home/sandro/portfolio_projects/hessen_aktuell
       HESSEN_AKTUELL_BASE_URL="https://sandroabashishvili.github.io/hessen-aktuell" AUTO_COMMIT=1 bash scripts/build_publish.sh

8. Set up Windows Task Scheduler to run scripts/windows_task_update.ps1 on a schedule.
9. Check logs under shared/data/automation_logs after scheduler runs.

## Runtime Recommendation

For this project, Codex should run in WSL runtime if possible, because the project lives under /home/sandro and uses Linux paths, bash scripts and Python modules. Running Codex from Windows against \\wsl$ paths caused repeated sandbox/helper errors.

If switching runtime causes chat/context loss, read this HANDOFF.md first and continue from here.

## Caution

Do not hand-edit generated public pages unless absolutely necessary. Change builders/config/shared layers instead, then run the pipeline.

Do not publish copied full article text. The project policy is source-aware, conservative ingestion with original source attribution and no full-text copying.
