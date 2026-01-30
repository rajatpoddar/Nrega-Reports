#!/bin/bash

# --- CONFIGURATION ---
# IMPORTANT: Apne NAS par jahan Nrega-Reports folder hai, wo path yahan likhein
# Agar folder ka naam alag hai to ise change kar dein
PROJECT_DIR="/volume1/docker/Projects/Nrega-Reports"

echo "=========================================="
echo "🚀 Starting NREGA Reports App Update..."
echo "=========================================="

# 1. Project folder me jao
if [ -d "$PROJECT_DIR" ]; then
  cd "$PROJECT_DIR"
  echo "📂 Navigated to $PROJECT_DIR"
else
  echo "❌ Error: Directory $PROJECT_DIR not found!"
  echo "Please check the PROJECT_DIR path in the script."
  exit 1
fi

# 2. Git Permission Fix (Safe Directory) - Synology NAS fix
git config --global --add safe.directory "$PROJECT_DIR"

# 3. GitHub se naya code khicho
echo "📥 Pulling latest code from GitHub..."
git pull origin main

# Check if git pull worked
if [ $? -ne 0 ]; then
    echo "❌ Git pull failed! Internet check karein ya manual git status dekhein."
    exit 1
fi

# 4. Docker container ko naye code ke sath rebuild karo
echo "🐳 Rebuilding Docker container..."
sudo docker-compose up -d --build

# 5. Purani unused images ko saf karo (Space bachane ke liye)
echo "🧹 Cleaning up old Docker images..."
sudo docker image prune -f

echo "=========================================="
echo "✅ Update Complete! App is running on Port 5233 🌐"
echo "=========================================="