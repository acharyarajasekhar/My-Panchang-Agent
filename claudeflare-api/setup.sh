#!/bin/bash
# Quick Setup Script for Claudeflare Slack Bridge
# Usage: ./setup.sh

set -e

echo "🚀 Claudeflare Slack Bridge - Setup Script"
echo "============================================"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

echo "✅ Node.js $(node --version) detected"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed."
    exit 1
fi

echo "✅ npm $(npm --version) detected"

# Install Wrangler globally if needed
if ! command -v wrangler &> /dev/null; then
    echo "📦 Installing Wrangler CLI..."
    npm install -g wrangler@latest
fi

echo "✅ Wrangler ready"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
npm install

# Build TypeScript
echo ""
echo "🔨 Building TypeScript..."
npm run build

# Create .env.local from template
if [ ! -f ".env.local" ]; then
    echo ""
    echo "📝 Creating .env.local from template..."
    cp .env.example .env.local
    echo "⚠️  Edit .env.local with your values"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env.local with your credentials"
echo "2. Run 'wrangler login' to authenticate with Cloudflare"
echo "3. Run 'npm run deploy' to deploy to Cloudflare Workers"
echo "4. Update your Slack app's Event Subscription URL"
echo ""
echo "For detailed setup instructions, see README.md"
