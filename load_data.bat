@echo off
REM Double-click this file to load ola_clean.csv into MySQL (database: ola, table: ola_rides)
cd /d "%~dp0"
where python >nul 2>&1
if %errorlevel%==0 (
  python load_to_mysql.py
) else (
  py load_to_mysql.py
)
echo.
pause
