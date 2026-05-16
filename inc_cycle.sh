#!/bin/bash

# INCREMENTAL CYCLE - FULL SYSTEM
# Uses safer cleanup strategy to preserve build cache while preventing disk fill-up.

# 0. Ensure shared Python base image exists (no-op if already built).
"$(dirname "$0")/scripts/build_base.sh"

# 1. Build and Run Full System
echo "🚀 [INCREMENTAL CYCLE] Building NebulaX Ecosystem (Full)..."
docker compose --profile full up --build

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
