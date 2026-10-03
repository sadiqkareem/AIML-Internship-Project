@echo off
setlocal
echo ========================================================
echo       Pushing AI Writer to GitHub
echo       Repository: sadiqkareem/AIML-Internship-Project
echo ========================================================
cd /d "%~dp0"

set "PATH=%LOCALAPPDATA%\Microsoft\WinGet\Packages\Git.MinGit_Microsoft.Winget.Source_8wekyb3d8bbwe\cmd;%PATH%"

echo Attempting git push...
git push -u origin main

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ========================================================
    echo Authentication is required by GitHub.
    echo If you have a Personal Access Token (PAT):
    echo 1. Generate one at: https://github.com/settings/tokens (select 'repo' scope)
    echo 2. Paste it below and press Enter:
    echo ========================================================
    set /p TOKEN="Enter GitHub Token (or press Enter to exit): "
    if defined TOKEN (
        git push https://%TOKEN%@github.com/sadiqkareem/AIML-Internship-Project.git main
    )
)

echo.
echo Done!
pause
