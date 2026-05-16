#!/bin/bash
# Legacy alias: the canonical entry point is now ./dev.sh
# Kept so existing muscle memory (and external scripts) keep working.
# All flags are forwarded.
exec "$(dirname "$0")/dev.sh" "$@"
