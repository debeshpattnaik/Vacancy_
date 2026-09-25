@echo off
setlocal
cd /d "%~dp0.."
set "PATH=%LOCALAPPDATA%\MinGit\cmd;%PATH%"

echo ====================================================
echo      Uploading Legal Vacancy Tracker to GitHub
echo ====================================================
echo.
echo Target Repository: https://github.com/debeshpattnaik/Vacancy_.git
echo.
echo Please enter your GitHub Personal Access Token (PAT):
echo (You can create one at https://github.com/settings/tokens with 'repo' scope)
echo.
set /p GITHUB_TOKEN="Enter Token: "

if "%GITHUB_TOKEN%"=="" (
    echo Token cannot be empty.
    pause
    exit /b 1
)

echo.
echo Pushing to GitHub...
git push https://%GITHUB_TOKEN%@github.com/debeshpattnaik/Vacancy_.git main -u --force

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ====================================================
    echo [SUCCESS] Project successfully uploaded to GitHub!
    echo Visit: https://github.com/debeshpattnaik/Vacancy_
    echo ====================================================
) else (
    echo.
    echo [ERROR] Push failed. Please verify your token has 'repo' permissions.
)

pause
