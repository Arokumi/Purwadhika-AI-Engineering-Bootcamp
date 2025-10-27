@echo off
powershell -NoLogo -NoExit -Command "yt-dlp -g 'https://www.youtube.com/watch?v=Q4VKEMGkvK0' | ForEach-Object { ffmpeg -hide_banner -loglevel warning -i $_ -vf fps=1 -f image2 -update 1 latest.jpg }"
pause
