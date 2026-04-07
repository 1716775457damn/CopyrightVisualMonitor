@echo off
chcp 65001 >nul
echo 开始为您打包 CopyrightVisualMonitor 为独立exe单文件...
echo 请确认您已经 pip install pyinstaller 以及完成相关模型下载！

REM 建议先使用虚拟环境安装完毕需求库，然后在该虚拟环境中运行此 bat。

pyinstaller ^
    --noconfirm ^
    --onefile ^
    --windowed ^
    --name "CopyrightVisualMonitor_v2" ^
    --add-data "tessdata;tessdata" ^
    --add-data "templates;templates" ^
    --exclude-module tensorflow ^
    --exclude-module keras ^
    --exclude-module torch ^
    --exclude-module matplotlib ^
    --exclude-module scipy ^
    --exclude-module sqlalchemy ^
    --hidden-import=win10toast ^
    main.py

echo.
echo ===============================================================
echo 打包完毕！输出文件在 \dist\CopyrightVisualMonitor_v2\ 目录下。
echo 注意：为防误杀请提前将其加入杀毒软件白名单。
echo ===============================================================
pause
