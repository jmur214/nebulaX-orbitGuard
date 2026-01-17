#!/bin/bash

# Lightweight Test Cycle for SPACE DOMAIN Only
# Skips Red/Blue team services to save time/bandwidth.

# Set timeout to 5 minutes to tolerate slow orchestration
export COMPOSE_HTTP_TIMEOUT=300
export DOCKER_CLIENT_TIMEOUT=300

echo "🚀 [SPACE MODE] Building NebulaX Space System..."
echo "STARTING: Database, Core API, Dashboard, Space Tracker, Ground Station, RF Receiver"

# Explicitly list the services we want to start
docker compose up --build \
    postgres \
    redis \
    core-api \
    dashboard \
    space-tracker \
    ground-station \
    rf-receiver

# Cleanup on exit (Ctrl+C)
echo ""
echo "🛑 [SPACE MODE] Test Complete. Initiating Nuclear Cleanup..."

# Stop containers
docker compose down

# STOP! Do NOT prune images on slow internet.
# We want to keep the layers we successfully downloaded so the next run is faster.
# echo "🧹 Pruning System (Images, Containers, Networks, Volumes)..."
# docker system prune -a --volumes -f

# echo "✨ Scrubbing Build Cache..."
# docker builder prune --all --force

echo "✅ CLEANUP COMPLETE. Containers stopped, but images preserved for next run."
