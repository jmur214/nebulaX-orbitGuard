#!/bin/bash
# ============================================================
# NebulaX / OrbitGuard — Hybrid Development Mode (default)
# ============================================================
# Backend services in Docker, dashboard on the host for fast iteration.
# Dashboard cold-build: ~16 s native vs. ~273 s in Docker.
#
# Flags:
#   --no-space        Skip space-tracker + ground-station + rf-receiver
#   --no-tail         Don't follow backend logs at the end
#   --auto-dashboard  Also start "npm run dev" in services/dashboard in the background
#   --minimal         Use the docker-compose "minimal" profile (core + space only)
#   -h, --help        Show this help
#
# Equivalent to the older `dev_hybrid.sh`, which is preserved for back-compat.
# ============================================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

# Defaults
INCLUDE_SPACE=1
FOLLOW_LOGS=1
AUTO_DASHBOARD=0
USE_MINIMAL_PROFILE=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --no-space)        INCLUDE_SPACE=0; shift ;;
        --no-tail)         FOLLOW_LOGS=0; shift ;;
        --auto-dashboard)  AUTO_DASHBOARD=1; shift ;;
        --minimal)         USE_MINIMAL_PROFILE=1; shift ;;
        -h|--help)
            grep -E '^# ' "$0" | sed 's/^# \{0,1\}//'
            exit 0 ;;
        *)
            echo -e "${RED}Unknown flag: $1${NC}"
            exit 1 ;;
    esac
done

echo -e "${CYAN}🚀 NebulaX dev.sh — hybrid mode${NC}"
echo -e "${YELLOW}   Backend in Docker, dashboard runs on the host.${NC}"

export COMPOSE_HTTP_TIMEOUT=300
export DOCKER_CLIENT_TIMEOUT=300

# Ensure shared Python base image is built (no-op if already present).
"$(dirname "$0")/scripts/build_base.sh"

if [[ $USE_MINIMAL_PROFILE -eq 1 ]]; then
    echo -e "\n${GREEN}Starting minimal profile: postgres, redis, core-api, space-tracker, ground-station${NC}"
    docker compose --profile minimal up -d
else
    SERVICES=(postgres redis core-api)
    if [[ $INCLUDE_SPACE -eq 1 ]]; then
        SERVICES+=(space-tracker ground-station rf-receiver)
    fi
    echo -e "\n${GREEN}Starting: ${SERVICES[*]}${NC}"
    docker compose up -d "${SERVICES[@]}"
fi

echo -e "\n${CYAN}⏳ Waiting for core-api to be reachable...${NC}"
for _ in $(seq 1 20); do
    if curl -s http://localhost:8000/ > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Core API ready at http://localhost:8000${NC}"
        break
    fi
    sleep 1
done

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}🎯  BACKEND UP${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo ""

if [[ $AUTO_DASHBOARD -eq 1 ]]; then
    if command -v npm > /dev/null; then
        echo -e "${CYAN}Starting dashboard in background (logs: dashboard.log)...${NC}"
        ( cd services/dashboard && npm run dev > ../../dashboard.log 2>&1 ) &
        echo -e "${GREEN}✓ Dashboard PID $!  — open http://localhost:3000${NC}"
    else
        echo -e "${RED}npm not found on host. Run the dashboard manually:${NC}"
        echo -e "  ${YELLOW}cd services/dashboard && npm run dev${NC}"
    fi
else
    echo -e "Start the dashboard in a new terminal:"
    echo -e "  ${YELLOW}cd services/dashboard && npm run dev${NC}"
    echo -e "  → open ${CYAN}http://localhost:3000${NC}"
fi

echo ""
echo -e "Logs:       ${YELLOW}docker compose logs -f <service>${NC}"
echo -e "Stop all:   ${YELLOW}docker compose down${NC}"
echo ""

if [[ $FOLLOW_LOGS -eq 1 && $INCLUDE_SPACE -eq 1 ]]; then
    echo -e "${CYAN}📡 Following space-tracker logs (Ctrl+C to stop)...${NC}"
    docker compose logs -f space-tracker rf-receiver
fi
