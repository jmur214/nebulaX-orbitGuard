#!/bin/bash
# One-time setup when a new codespace is created.
# Builds the shared Python base image and installs dashboard deps so the
# first ./dev.sh is fast.

set -e

echo "==================================================="
echo "  NebulaX Codespace post-create setup"
echo "==================================================="

cd "$(dirname "$0")/.."

echo ""
echo "==> Building shared Python base image (one-time)..."
./scripts/build_base.sh

echo ""
echo "==> Installing dashboard node_modules..."
( cd services/dashboard && npm install --no-audit --no-fund )

echo ""
echo "==> Pre-pulling postgres + redis images..."
docker pull postgres:15-alpine
docker pull redis:7-alpine

echo ""
echo "==================================================="
echo "  Setup complete."
echo ""
echo "  To start the system, run:"
echo "    ./dev.sh --no-tail"
echo ""
echo "  Then in a separate terminal:"
echo "    cd services/dashboard && npm run dev"
echo ""
echo "  Codespaces will auto-forward ports 3000 + 8000."
echo "==================================================="
