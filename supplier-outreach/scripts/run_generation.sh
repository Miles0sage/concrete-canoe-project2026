#!/bin/bash
set -e

echo "=== NAU CONCRETE CANOE EMAIL GENERATOR ==="
echo ""

# Check environment variables
if [ -z "$OPENROUTER_API_KEY" ]; then
  echo "❌ OPENROUTER_API_KEY not set"
  echo ""
  echo "Please set it with:"
  echo "export OPENROUTER_API_KEY='your_key_here'"
  exit 1
fi

if [ -z "$OPENAI_API_KEY" ]; then
  echo "❌ OPENAI_API_KEY not set"
  echo ""
  echo "Please set it with:"
  echo "export OPENAI_API_KEY='your_key_here'"
  exit 1
fi

echo "✅ API keys configured"
echo ""

# Install required packages
echo "📦 Checking Python dependencies..."
pip3 install -q requests

# Create output directory
mkdir -p /root/projects/concrete-canoe-2026/supplier-outreach/emails

# Run generator
cd /root/projects/concrete-canoe-2026/supplier-outreach/scripts
python3 generate_emails.py

echo ""
echo "=== GENERATION COMPLETE ==="
echo ""
echo "📧 Emails saved to: supplier-outreach/emails/"
echo "📊 Tracking sheet: supplier-outreach/TRACKING.md"
echo "🔄 Changes committed to git"
echo ""
echo "NEXT STEPS:"
echo "1. Review emails: ls -lh /root/projects/concrete-canoe-2026/supplier-outreach/emails/"
echo "2. Read first: cat /root/projects/concrete-canoe-2026/supplier-outreach/emails/01_*.txt"
echo "3. Copy to NAU email (miles27.85shah@nau.edu)"
echo "4. Send in priority order!"
echo ""
echo "Ready to secure materials! 🚣"
