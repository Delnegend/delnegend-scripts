@echo off

if "%1" == "" start "" /min "%~f0" MY_FLAG && exit

for /R %%F in (*.mp4) do (
ffmpeg -y -i "%%F" -t 2 -r 0.5 "%%~nF.jpg"
if errorlevel 1 echo del /s /f /q %%F >> remove_corrupted.bat
del "%%~nF.jpg"
)
del /s /f /q *.tmp

IF EXIST remove_corrupted.bat (
  start remove_corrupted.bat
) ELSE (
  ECHO File not found
)

for /R %%F in (*.mp4) do (
echo file '%%F' >> data.txt
)
ffmpeg -f concat -safe 0 -i data.txt -c:v copy -c:a aac output.mp4
attrib +r output.mp4
@REM del *.mp4
attrib -r output.mp4
del *.txt

for %%I in (.) do set CurrDirName=%%~nxI
@REM echo %CurrDirName%
rename output.mp4 "%CurrDirName%".mp4
move "%CurrDirName%.mp4" ../
@REM pause
exit
