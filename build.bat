@echo off
chcp 65001 >nul
echo ========================================
echo   Сборка WinsX с помощью PyInstaller
echo ========================================
echo.

REM Проверка наличия PyInstaller
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [INFO] Установка PyInstaller...
    python -m pip install pyinstaller
)

echo [INFO] Сборка исполняемого файла...
python -m PyInstaller WinsX.spec --clean

if errorlevel 1 (
    echo [ERROR] Ошибка при сборке!
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Сборка завершена успешно!
echo [INFO] Исполняемый файл находится в папке: dist\WinsX.exe
echo.
pause

