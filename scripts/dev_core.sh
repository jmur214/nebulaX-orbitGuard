#!/bin/bash
# NebulaX - Start Core Infrastructure Only
# For local Python development - run modules with 'python main.py'
# Usage: ./scripts/dev_core.sh

set -e

echo "🚀 Starting NebulaX Core Infrastructure..."
echo "   - postgres (database)"
echo "   - redis (event bus)"
echo "   - core-api (FastAPI backend)"
echo ""

docker compose up -d postgres redis core-api

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 8

# Check if core-api is responding
if curl -s --max-time 5 http://localhost:8000/ > /dev/null 2>&1; then
    echo "✅ Core API is ready at http://localhost:8000"
else
    echo "⚠️  Core API may still be starting, please wait..."
fi

echo ""
echo "🔧 Development Environment Ready!"
echo "=============================================="
echo ""
echo "Run any module locally with:"
echo "  cd services/<team>/<module>"
echo "  python main.py"
echo ""
echo "Environment variable for modules:"
echo "  export CORE_HOST=localhost"
echo ""
echo "To stop core infrastructure:"
echo "  docker compose down"
