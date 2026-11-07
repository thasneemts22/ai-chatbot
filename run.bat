@echo off
echo ========================================================
echo   Starting ChatGPT AI Assistant (Python + Streamlit)
echo ========================================================
echo.
cd /d "%~dp0"
python -m streamlit run app.py
pause
