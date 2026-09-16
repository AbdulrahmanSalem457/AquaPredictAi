@echo off
chcp 65001 >nul
title AquaPredict AI

color 0B
echo.
echo =======================================================
echo     AquaPredict AI - Water Station Intelligence  
echo       Powered by FastAPI ^| Streamlit ^| ML/AI
echo =======================================================
echo.

:: Step 1: Check Python
echo [1/5] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo  [ERROR] Python not found! Install from https://www.python.org
    pause & exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do echo  [OK] %%i detected.
echo.

:: Step 2: Set directory
echo [2/5] Setting project directory...
cd /d "%~dp0"
echo  [OK] %cd%
echo.

:: Step 3: Upgrade pip
echo [3/5] Upgrading pip...
python -m pip install --upgrade pip --quiet
echo  [OK] pip is ready.
echo.

:: Step 4: Install dependencies
echo [4/5] Installing required packages...
echo  (First run may take a few minutes)
python -m pip install fastapi uvicorn pydantic pydantic-settings --quiet
python -m pip install pandas numpy scikit-learn joblib --quiet
python -m pip install streamlit requests --quiet
python -m pip install fpdf2 folium streamlit-folium --quiet
python -m pip install streamlit-mic-recorder python-dotenv plotly --quiet
echo  [OK] All packages installed.
echo.

:: Step 5: Start FastAPI in background WITH visible logs
echo [5/5] Starting servers...
start /b python -m uvicorn api.main:app --host 127.0.0.1 --port 8000

echo  Waiting for FastAPI to initialize...
timeout /t 5 /nobreak >nul

:: Show links
color 0A
echo.
echo =======================================================
echo         AQUAPREDICT AI  ^|  SYSTEM RUNNING
echo =======================================================
echo.
echo   API Base:      http://127.0.0.1:8000
echo   Swagger UI:    http://127.0.0.1:8000/docs
echo   ReDoc:         http://127.0.0.1:8000/redoc
echo.
echo   [NEW] HTML Frontend:   http://127.0.0.1:8000/app/
echo   [ALT] Streamlit Dash:  http://localhost:8501
echo.
echo   Click any link above to open it in your browser.
echo   Press CTRL+C to stop all servers.
echo =======================================================
echo.
color 07

:: Launch Streamlit in same terminal
python -m streamlit run dashboard/app.py --server.port 8501 --server.address localhost --server.headless true

pause

