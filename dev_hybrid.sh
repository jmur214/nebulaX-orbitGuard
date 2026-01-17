#!/bin/bash

# ============================================================
# HYBRID DEVELOPMENT MODE
# ============================================================
# Runs backend services in Docker while dashboard runs locally.
# This provides:
# - Fast dashboard compilation (16s locally vs 273s in Docker)
# - Real satellite data from space-tracker
# - No more browser load time issues
# ============================================================

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}🚀 [HYBRID MODE] Starting NebulaX Backend Services...${NC}"
echo -e "${YELLOW}Dashboard will run LOCALLY for faster development${NC}"

# Set timeout to tolerate slow Docker operations
export COMPOSE_HTTP_TIMEOUT=300
export DOCKER_CLIENT_TIMEOUT=300

# Start backend services (NOT dashboard)
echo -e "\n${GREEN}Starting: Database, Core API, Space Tracker, Ground Station, RF Receiver${NC}"
docker compose up -d \
    postgres \
    redis \
    core-api \
    space-tracker \
    ground-station \
    rf-receiver

echo -e "\n${CYAN}⏳ Waiting for services to be ready...${NC}"
sleep 5

# Check if core-api is accessible
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Core API is ready at http://localhost:8000${NC}"
else
    echo -e "${YELLOW}! Core API not responding yet (may still be starting)${NC}"
fi

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}🎯 BACKEND SERVICES RUNNING!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "Now start the dashboard locally in a NEW terminal:"
echo ""
echo -e "  ${YELLOW}cd services/dashboard${NC}"
echo -e "  ${YELLOW}npm run dev${NC}"
echo ""
echo -e "Then open: ${CYAN}http://localhost:3000/space${NC}"
echo ""
echo -e "To view backend logs:"
echo -e "  ${YELLOW}docker compose logs -f space-tracker${NC}"
echo ""
echo -e "To stop all services:"
echo -e "  ${YELLOW}docker compose down${NC}"
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"

# Follow logs from space-tracker
echo ""
echo -e "${CYAN}📡 Following space-tracker logs (Ctrl+C to stop)...${NC}"
docker compose logs -f space-tracker rf-receiver
