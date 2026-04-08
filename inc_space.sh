#!/bin/bash

# INCREMENTAL SPACE - SPACE DOMAIN ONLY
# Uses safer cleanup strategy to preserve build cache.

# 1. Build and Run Space Domain
echo "🚀 [INCREMENTAL SPACE] Building NebulaX Space System..."
docker compose --profile core --profile space up --build

# --- The script pauses here while you test ---
# --- It resumes when you press Ctrl+C ---

# 2. The Cleanup
echo ""
echo "🛑 [STOPPING] Test Complete. Initiating Smart Cleanup..."

# Stop containers
docker compose down

# INCREMENTAL PRUNE:
# Only removes dangling images (<none>) created during rebuilds.
# Keeps base images and latest builds for fast next startup.
echo "🧹 Pruning Dangling Images (Old Layers)..."
docker image prune -f

echo "✅ CLEANUP COMPLETE. Space reclaimed, cache preserved."
