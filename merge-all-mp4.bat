@echo off

@REM == START MINIMIZED
if "%1" == "" start "" /min "%~f0" MY_FLAG && exit

@REM == FIND CORRUPTED FILES
for /R %%F in (*.mp4) do (
ffmpeg -y -i "%%F" -t 2 -r 0.5 "%%~nF.jpg"
if errorlevel 1 echo del /s /f /q "%%F" >> remove_corrupted.bat
del "%%~nF.jpg"
)
del /s /f /q *.tmp

@REM == REMOVE CORRUPTED FILES
IF EXIST remove_corrupted.bat (
  start remove_corrupted.bat
) ELSE (
  ECHO File not found
)

@REM == LIST ALL VIDEOS
for /R %%F in (*.mp4) do (
echo file '%%F' >> data.txt
)

@REM == CONCAT
for %%I in (.) do set CurrDirName=%%~nxI
ffmpeg -f concat -safe 0 -i data.txt -c copy D:/%CurrDirName%.mkv

@REM attrib +r output.mp4
@REM del *.mp4
@REM attrib -r output.mp4
@REM del *.txt


@REM echo %CurrDirName%
@REM rename output.mp4 "%CurrDirName%".mkv
@REM move "%CurrDirName%.mkv" ../
@REM pause
start /min D:\sound.vbs
exit