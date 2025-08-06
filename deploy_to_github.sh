#!/bin/bash

echo "🚀 Puto Island GitHub Deployment Script"
echo "========================================"

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Check if we have commits
if [ -z "$(git log --oneline 2>/dev/null)" ]; then
    echo "❌ Error: No commits found. Please make an initial commit first."
    exit 1
fi

echo "✅ Git repository detected with commits"

# Prompt for GitHub username
echo ""
read -p "Enter your GitHub username: " github_username

if [ -z "$github_username" ]; then
    echo "❌ Error: GitHub username is required"
    exit 1
fi

# Create the repository URL
repo_url="https://github.com/${github_username}/puto-island.git"

echo "📋 Repository URL: $repo_url"
echo ""
echo "🔧 Setting up remote and pushing to GitHub..."

# Add remote origin
git remote remove origin 2>/dev/null || true  # Remove if exists
git remote add origin "$repo_url"

# Set main branch and push
git branch -M main

echo "🚀 Pushing code to GitHub..."
echo "   This will:"
echo "   - Upload all your game files"
echo "   - Trigger automatic APK build via GitHub Actions"
echo "   - Build will take ~20-30 minutes"
echo ""

if git push -u origin main; then
    echo ""
    echo "🎉 SUCCESS! Code pushed to GitHub!"
    echo ""
    echo "📱 Next Steps:"
    echo "1. Go to: https://github.com/${github_username}/puto-island"
    echo "2. Click 'Actions' tab to watch APK build progress"
    echo "3. Download APK from 'Artifacts' when build completes"
    echo "4. Install on your Android device and enjoy!"
    echo ""
    echo "🕐 Build ETA: 20-30 minutes"
    echo "📦 APK will be ~50-100MB"
    echo ""
    echo "🎮 Your island adventure awaits on mobile!"
else
    echo ""
    echo "❌ Push failed. This usually means:"
    echo "1. Repository doesn't exist on GitHub yet"
    echo "2. You don't have push permissions"
    echo ""
    echo "📋 Manual steps:"
    echo "1. Go to github.com and create repository 'puto-island'"
    echo "2. Make it public (required for free GitHub Actions)"
    echo "3. Run this script again"
    echo ""
    echo "🔗 Quick create link:"
    echo "https://github.com/new?name=puto-island&description=🏝️%20Puto%20Island%20-%20Pygame%20island%20management%20simulation"
fi