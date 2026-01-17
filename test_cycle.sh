#!/bin/bash

# 1. Build and Run the System
echo "🚀 [PHASE 1] Building NebulaX Ecosystem..."
docker compose up --build

# --- The script pauses here while you test ---
# --- It resumes when you press Ctrl+C ---

# 2. The Cleanup (Runs automatically after you stop)
echo ""
echo "🛑 [PHASE 2] Test Complete. Initiating Nuclear Cleanup..."

# Stop containers
docker compose down

# Aggressive System Prune
# -a: Remove all unused images not just dangling ones
# --volumes: Remove all unused volumes
# -f: Force (no confirmation)
echo "🧹 Pruning System (Images, Containers, Networks, Volumes)..."
docker system prune -a --volumes -f

# Final Deep Clean of Build Cache
echo "✨ Scrubbing Build Cache..."
docker builder prune --all --force

echo "✅ CLEANUP COMPLETE. Docker is now empty."