#!/bin/bash
# Super Prompt npm Cache Fix Script
# Resolves npm cache permission issues during installation

echo "🔧 Super Prompt npm Cache Fix"
echo "=============================="

# Clean npm cache completely
echo "🧹 Cleaning npm cache..."
npm cache clean --force 2>/dev/null || true

# Remove problematic cache directories
echo "🗑️  Removing problematic cache files..."
sudo rm -rf /tmp/.npm-cache 2>/dev/null || true
sudo rm -rf ~/.npm/_cacache 2>/dev/null || true

# Create fresh cache directory with proper permissions
echo "📁 Creating fresh cache directory..."
mkdir -p /tmp/npm-cache-clean
chmod 755 /tmp/npm-cache-clean

# Install with custom cache location
echo "📦 Installing Super Prompt with clean cache..."
NPM_CONFIG_CACHE=/tmp/npm-cache-clean npm install -g @cdw0424/super-prompt@latest

echo "✅ Installation completed!"
echo "🚀 Run: super-prompt super:init"