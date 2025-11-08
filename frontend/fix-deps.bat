@echo off
cd /d "%~dp0"
echo Cleaning node_modules...
if exist node_modules rmdir /s /q node_modules
if exist package-lock.json del /f package-lock.json
echo Installing dependencies...
call npm install
echo Done! Run npm run dev

