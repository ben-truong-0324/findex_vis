#!/bin/bash

echo "🍎 Launching terminals for Flask + FastAPI deployment..."

# Get the current directory
CURRENT_DIR=$(pwd)

# 🪟 Terminal 1: Minikube mount (must stay open for shared /data)
osascript <<EOF
tell application "Terminal"
    do script "cd \"$CURRENT_DIR\" && minikube mount ./data:/mnt/data"
    set custom title of front window to "Minikube Mount"
end tell
EOF

# 🚀 Terminal 2: Run the FastAPI deployment script
osascript <<EOF
tell application "Terminal"
    do script "cd \"$CURRENT_DIR/scripts\" && ./deploy_fastapi.sh"
    set custom title of front window to "Deploy FastAPI"
end tell
EOF

# 🚀 Terminal 3: Run the Flask deployment script
osascript <<EOF
tell application "Terminal"
    do script "cd \"$CURRENT_DIR/scripts\" && ./deploy_flask.sh"
    set custom title of front window to "Deploy Flask"
end tell
EOF

echo "✅ All deployment terminals launched!"

