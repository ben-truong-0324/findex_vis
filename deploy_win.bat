@echo off
echo 🪟 Launching terminals for Flask + FastAPI deployment...

:: 🔗 Terminal 1: Minikube mount (must stay open for shared /data)
start "Minikube Mount" cmd /k "cd /d %CD% && minikube mount ./data:/mnt/data"

:: 🚀 Terminal 2: Run the FastAPI deployment script (mlAPI)
start "Deploy FastAPI" cmd /k "cd /d %CD%\scripts && deploy_fastapi.bat"

:: 🚀 Terminal 3: Run the Flask deployment script
start "Deploy Flask" cmd /k "cd /d %CD%\scripts && deploy_flask.bat"

echo ✅ All deployment terminals launched!
