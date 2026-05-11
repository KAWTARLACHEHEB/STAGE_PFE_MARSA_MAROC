@echo off
title MARSA MAROC - Terminal Optimization System
echo ===================================================
echo   DEMARRAGE DU SYSTEME D'OPTIMISATION MARSA MAROC
echo ===================================================

echo [1/3] Nettoyage et Initialisation des donnees (ETL)...
python app/etl/pipeline.py
if %ERRORLEVEL% NEQ 0 (
    echo Erreur lors du pipeline ETL. Verifiez vos fichiers de donnees.
    pause
    exit /b
)

echo [2/3] Demarrage du Serveur Backend (FastAPI)...
start "Backend API" cmd /k "cd app && uvicorn main:app --reload --port 8000"

echo [3/3] Demarrage de l'Interface Utilisateur (React)...
start "Frontend UI" cmd /k "cd frontend && npm run dev"

echo ===================================================
echo   SYSTEME PRET ! 
echo   - Dashboard : http://localhost:5173
echo   - API Docs  : http://localhost:8000/docs
echo ===================================================
pause
