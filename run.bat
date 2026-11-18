@echo off
setlocal
cd /d "%~dp0"
where python >nul 2>nul || (echo Python 3.11 or newer is required. & pause & exit /b 1)
if not exist .venv python -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements-minimal.txt
python assignments\capstone\app.py --demo
echo.
echo Demo finished. To run the full checker: python -m autograde.run --capstone --root . -v
pause
