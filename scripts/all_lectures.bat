@echo off
rem Transcribes lectures 1..7 one after another; already finished ones are skipped.
setlocal
set NOPAUSE=1
for %%N in (1 2 3 4 5 6 7) do call "%~dp0run_gpu.bat" %%N
echo.
echo ALL DONE. Results are in the transcripts folder.
pause
