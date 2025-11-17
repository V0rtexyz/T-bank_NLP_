#!/bin/bash

# T-Plexity Frontend - Node.js Installation Script (no sudo required)
# This script installs Node.js locally using nvm (Node Version Manager)

set -e

echo "=========================================="
echo "Installing Node.js for T-Plexity Frontend"
echo "=========================================="
echo ""

# Check if nvm is already installed
if [ -d "$HOME/.nvm" ]; then
    echo "✓ NVM already installed"
else
    echo "→ Installing NVM (Node Version Manager)..."
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
    echo "✓ NVM installed"
fi

# Load nvm
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"

echo ""
echo "→ Installing Node.js 20 LTS..."
nvm install 20
nvm use 20
nvm alias default 20

echo ""
echo "→ Verifying installation..."
node --version
npm --version

echo ""
echo "=========================================="
echo "✓ Node.js installed successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Reload your shell or run: source ~/.bashrc"
echo "2. Run: npm install"
echo "3. Run: npm run dev"
echo ""

