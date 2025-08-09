#!/bin/bash

# =============================================================================
# CyberDB AI - Quick Start Script for UTM VM
# =============================================================================

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                    CyberDB AI Platform                       ║"
echo "║                  Development Environment                     ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if already set up
if [ -d "venv" ] && [ -f "start-dev.sh" ]; then
    echo -e "${GREEN}Development environment already set up!${NC}"
    echo
    echo "Quick commands:"
    echo "• Start: ./start-dev.sh"
    echo "• Stop:  ./stop-dev.sh"
    echo "• Monitor: ./monitor.sh"
    echo
    read -p "Do you want to start the development environment now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ./start-dev.sh
    fi
    exit 0
fi

echo "This script will set up your CyberDB AI development environment."
echo "Estimated time: 10-15 minutes"
echo

# Check system requirements
echo -e "${YELLOW}Checking system requirements...${NC}"

# Check RAM
TOTAL_MEM=$(free -m | awk 'NR==2{printf "%.0f", $2/1024}')
if [ "$TOTAL_MEM" -lt 3 ]; then
    echo "❌ Insufficient RAM: ${TOTAL_MEM}GB (minimum 3GB required)"
    exit 1
fi

# Check disk space
AVAILABLE_SPACE=$(df -BG . | awk 'NR==2{print $4}' | sed 's/G//')
if [ "$AVAILABLE_SPACE" -lt 10 ]; then
    echo "❌ Insufficient disk space: ${AVAILABLE_SPACE}GB (minimum 10GB required)"
    exit 1
fi

echo "✅ System requirements OK: ${TOTAL_MEM}GB RAM, ${AVAILABLE_SPACE}GB free space"

# Ask for installation type
echo
echo "Choose installation type:"
echo "1) Lightweight (Recommended for UTM VM) - CPU-only ML, local services"
echo "2) Full Docker - Everything in containers"
echo "3) Hybrid - Local development with Docker services"

read -p "Select option (1-3): " -n 1 -r
echo
case $REPLY in
    1) INSTALL_TYPE="lightweight" ;;
    2) INSTALL_TYPE="full-docker" ;;
    3) INSTALL_TYPE="hybrid" ;;
    *) echo "Invalid option. Using lightweight setup."; INSTALL_TYPE="lightweight" ;;
esac

echo -e "${GREEN}Starting $INSTALL_TYPE installation...${NC}"

# Make setup script executable and run
chmod +x setup-dev-environment.sh

# Run setup based on type
if [ "$INSTALL_TYPE" = "lightweight" ]; then
    echo "export INSTALL_TYPE=lightweight" > /tmp/cyberdb_install_type
    ./setup-dev-environment.sh
elif [ "$INSTALL_TYPE" = "full-docker" ]; then
    echo "export INSTALL_TYPE=full-docker" > /tmp/cyberdb_install_type
    ./setup-dev-environment.sh
else
    echo "export INSTALL_TYPE=hybrid" > /tmp/cyberdb_install_type
    ./setup-dev-environment.sh
fi

echo -e "${GREEN}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                     Setup Complete! 🚀                       ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
