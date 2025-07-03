@echo off
REM 自动下载前端依赖到 static/libs 目录（Windows环境）
REM 需已安装 PowerShell 5.0+

REM 创建目录
mkdir "bootstrap"
mkdir "fontawesome"
mkdir "webfonts"


REM 下载 Bootstrap 4.6.2（bootcdn）
powershell -Command "Invoke-WebRequest -Uri https://cdn.bootcdn.net/ajax/libs/bootstrap/4.6.2/css/bootstrap.min.css -OutFile bootstrap.min.css"
powershell -Command "Invoke-WebRequest -Uri https://cdn.bootcdn.net/ajax/libs/bootstrap/4.6.2/js/bootstrap.min.js -OutFile bootstrap.min.js"

REM 下载 jQuery 3.5.1（bootcdn）
powershell -Command "Invoke-WebRequest -Uri https://cdn.bootcdn.net/ajax/libs/jquery/3.5.1/jquery.slim.min.js -OutFile jquery.slim.min.js"

REM 下载 Popper.js 1.16.1（bootcdn）
powershell -Command "Invoke-WebRequest -Uri https://cdn.bootcdn.net/ajax/libs/popper.js/1.16.1/umd/popper.min.js -OutFile popper.min.js"

REM 下载 FontAwesome 5.15.4 CSS（bootcdn）
powershell -Command "Invoke-WebRequest -Uri https://cdn.bootcdn.net/ajax/libs/font-awesome/5.15.4/css/all.min.css -OutFile all.min.css"

REM 下载 FontAwesome 5.15.4 webfonts（bootcdn，常用字体）
powershell -Command "Invoke-WebRequest -Uri https://cdn.bootcdn.net/ajax/libs/font-awesome/5.15.4/webfonts/fa-solid-900.woff2 -OutFile webfonts\fa-solid-900.woff2"
powershell -Command "Invoke-WebRequest -Uri https://cdn.bootcdn.net/ajax/libs/font-awesome/5.15.4/webfonts/fa-brands-400.woff2 -OutFile webfonts\fa-brands-400.woff2"
powershell -Command "Invoke-WebRequest -Uri https://cdn.bootcdn.net/ajax/libs/font-awesome/5.15.4/webfonts/fa-regular-400.woff2 -OutFile webfonts\fa-regular-400.woff2"

REM 如需更多字体，可参考 FontAwesome webfonts 目录补充

echo 下载完成！
pause
