#!/bin/bash
# NebulaX - Test Single Module
# Usage: ./scripts/test_module.sh <module-name>
# Example: ./scripts/test_module.sh ids-suricata

set -e

MODULE=$1

if [ -z "$MODULE" ]; then
    echo "Usage: ./scripts/test_module.sh <module-name>"
    echo ""
    echo "Available modules:"
    echo "  Red Team:  attack-engine, password-auditor, vuln-scanner, web-injector, c2-beacon, ransomware-sim, apt-emulator"
    echo "  Blue Team: honeypot, blue-sentinel, ids-suricata, net-watchdog, net-forensics, edr-agent"
    echo "  Target:    target-web, internal-infra, identity-manager"
    echo "  Intel:     cve-feeder, ioc-manager"
    echo "  GRC:       incident-reporter, policy-mapper"
    echo "  Space:     space-tracker, ground-station, rf-receiver"
    exit 1
fi

echo "🚀 Starting core infrastructure..."
docker compose up -d postgres redis core-api

echo "⏳ Waiting for core-api to be ready..."
sleep 10

echo "🔧 Starting module: $MODULE"
docker compose up -d $MODULE

echo ""
echo "📋 Tailing logs for $MODULE (Ctrl+C to stop)..."
echo "=============================================="
docker compose logs -f $MODULE
