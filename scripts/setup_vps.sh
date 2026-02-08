#!/bin/bash
# NAU Concrete Canoe 2026 - VPS Setup Script
# Run on Ubuntu/Debian VPS after cloning repo

set -e
echo "=== NAU Concrete Canoe 2026 - VPS Setup ==="

# Install system deps if needed
command -v git >/dev/null 2>&1 || sudo apt update && sudo apt install -y git python3 python3-pip python3-venv

# Navigate to repo (adjust path if different)
cd "$(dirname "$0")/.." || exit 1

# Create venv
python3 -m venv venv
source venv/bin/activate

# Install Python deps (no GUI - headless only)
pip install --upgrade pip
pip install -r requirements.txt

# Test calculator
echo ""
echo "Testing hull calculator..."
python3 calculations/concrete_canoe_calculator.py

echo ""
echo "=== Setup complete. Run: source venv/bin/activate && python3 scripts/run_hull_analysis.py ==="
