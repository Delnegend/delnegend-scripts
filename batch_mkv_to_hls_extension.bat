@echo off
cls
ffmpeg -i %1 -codec copy "output.mp4"
ffmpeg -i output.mp4 -codec copy -start_number 0 -hls_time 15 -hls_list_size 0 -f hls p.m3u8
del output.mp4
move %1 ../
@REM git init
@REM git remote add origin %2
@REM echo *.ts -delta > .gitattributes
@REM echo *.bat > .gitignore
@REM git add *
@REM git commit -m "create files"
@REM git push -u origin master
@REM del /f /q *.ts *.m3u8 .gitattributes .gitignore
@REM rmdir /s/q .git
del /f /q batch_mkv_to_hls_extension.bat
