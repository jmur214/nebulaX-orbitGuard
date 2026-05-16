#!/bin/bash
# Runs every time the codespace starts (initial create + every resume).
# Brings up the minimal backend so the user just opens port 3000.

set -e

cd "$(dirname "$0")/.."

# Make sure the shared base image is present (in case Docker state was wiped on restart).
if ! docker image inspect nebulax-python-base:latest > /dev/null 2>&1; then
    echo "==> Shared base missing — rebuilding..."
    ./scripts/build_base.sh
fi

echo "==> Starting backend (postgres, redis, core-api, space-tracker, ground-station, rf-receiver)..."
./dev.sh --no-tail || true
# (--no-tail keeps dev.sh from blocking on the docker logs follow at the end)

echo ""
echo "==================================================="
echo "  Backend started."
echo ""
echo "  Run the dashboard:"
echo "    cd services/dashboard && npm run dev"
echo ""
echo "  Then open the forwarded port 3000 (Codespaces"
echo "  will pop the URL automatically)."
echo "==================================================="
