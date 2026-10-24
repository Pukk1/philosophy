@echo off
rem Usage: run_gpu.bat N [model]   (N = lecture number 1..7)
rem Set NOPAUSE=1 to skip the final pause (used by all_lectures.bat)
setlocal
set "SCRIPTS=%~dp0"
cd /d "%SCRIPTS%.."
if not exist work mkdir work
set PYTHONIOENCODING=utf-8
set PYTHONUNBUFFERED=1
set "PY=C:\venvs\whisper38\Scripts\python.exe"
set "N=%~1"
if "%N%"=="" (
  echo Usage: run_gpu.bat N [model]
  pause
  exit /b 1
)
set "LOG=work\gpu_run_%N%.log"

echo ==== START %date% %time% lecture %N% ==== > "%LOG%"
echo Lecture %N%: transcribing on GPU. Log: %CD%\%LOG%
"%PY%" "%SCRIPTS%run_gpu.py" %N% %2 >> "%LOG%" 2>&1
set RC=%errorlevel%
echo [exit] %RC% >> "%LOG%"
echo ==== END %date% %time% ==== >> "%LOG%"
if "%RC%"=="0" (echo Lecture %N%: DONE) else (echo Lecture %N%: FAILED or skipped, see %LOG%)
if not "%NOPAUSE%"=="1" pause
exit /b %RC%
