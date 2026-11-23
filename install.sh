#!/usr/bin/env bash
# Standalone one-line installer for evallite
set -e

echo "⚡ Installing evallite (Local-First Agent & Tool-Call Evaluation Engine)..."

if command -v uv >/dev/null 2>&1; then
    uv tool install --force git+https://github.com/BNTiyan/evallite.git
elif command -v pipx >/dev/null 2>&1; then
    pipx install --force git+https://github.com/BNTiyan/evallite.git
elif command -v pip3 >/dev/null 2>&1; then
    pip3 install --user git+https://github.com/BNTiyan/evallite.git
else
    echo "❌ Error: Python 3 and pip or uv are required to install evallite."
    exit 1
fi

echo "✅ evallite successfully installed!"
echo "Run 'evallite demo' to explore the terminal evaluation dashboard."
echo "Run 'evallite demo --ci' to verify CI quality gate enforcement."
