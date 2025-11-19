@echo off
@REM Batch script to relay YouTube live stream to local image file (latest.jpg) at 3 FPS. Change URL as needed.
powershell -NoLogo -NoExit -Command "yt-dlp -g 'https://www.youtube.com/watch?v=57w2gYXjRic' | ForEach-Object { ffmpeg -hide_banner -loglevel warning -i $_ -vf fps=3 -f image2 -update 1 latest.jpg }"
pause
