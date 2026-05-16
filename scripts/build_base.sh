#!/bin/bash
# Build (or rebuild) the shared nebulax-python-base image.
# Every Python service Dockerfile starts with FROM nebulax-python-base:latest,
# so this must be built once before `docker compose build` of any service.
#
# Usage: ./scripts/build_base.sh [--force]
#   --force  Rebuild even if the image already exists.

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

IMAGE="nebulax-python-base:latest"
FORCE=0
[[ "$1" == "--force" ]] && FORCE=1

if [[ $FORCE -eq 0 ]] && docker image inspect "$IMAGE" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ $IMAGE already built (use --force to rebuild).${NC}"
    exit 0
fi

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
echo -e "${YELLOW}Building $IMAGE from $REPO_ROOT/infrastructure/python-base ...${NC}"
docker build -t "$IMAGE" "$REPO_ROOT/infrastructure/python-base"
echo -e "${GREEN}✓ $IMAGE ready.${NC}"
