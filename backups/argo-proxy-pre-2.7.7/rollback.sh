#!/bin/bash
# Emergency Rollback Script for Argo-Proxy 2.7.6
# Run this script if argo-proxy 2.7.7 causes issues

set -e

echo "🔄 Rolling back to argo-proxy 2.7.6..."

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Uninstall current version
echo "📦 Uninstalling current argo-proxy..."
pip uninstall argo-proxy -y

# Reinstall from backup
echo "🔧 Reinstalling from backup source..."
cd "$SCRIPT_DIR/current_source_code"
pip install -e .

# Verify
echo "✅ Verifying installation..."
if argo-proxy --version | grep -q "2.7.6"; then
    echo "🎉 Rollback successful! argo-proxy 2.7.6 restored."
    argo-proxy --version
else
    echo "❌ Rollback may have failed. Check manually."
    exit 1
fi

echo ""
echo "📝 To test your setup:"
echo "  1. argo-proxy --help"
echo "  2. Test your BAML integration"
echo "  3. Check your config: argo-proxy --show"