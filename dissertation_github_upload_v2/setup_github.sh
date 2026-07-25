#!/bin/bash
# ─────────────────────────────────────────────────────────────────
# One-command GitHub repository initialisation and push.
#
# Prerequisites:
#   1. Create an EMPTY repository on github.com. Do NOT initialise it
#      with a README, .gitignore, or LICENSE — this script provides
#      all three.
#   2. Extract this ZIP to your desired local location.
#   3. From the extracted folder root (where README.md lives), run:
#        bash setup_github.sh
#
# You will be asked for the GitHub repo URL. Everything else is
# automatic, with a safety confirmation before the actual push.
# ─────────────────────────────────────────────────────────────────

set -e

echo "==============================================================="
echo "  Dissertation code — GitHub repository initialisation"
echo "==============================================================="
echo ""

# Verify we are in the right place
if [ ! -f "README.md" ]; then
    echo "ERROR: README.md not found in current directory."
    echo "Run this script from the repository root (the folder that"
    echo "contains README.md, LICENSE, and the data_collection/,"
    echo "preprocessing/, analysis/ folders)."
    exit 1
fi

# ─── Ask for the GitHub repo URL ──────────────────────────────
echo "Paste your empty GitHub repo URL below."
echo "It should look like:  https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git"
echo ""
read -p "Repo URL: " REPO_URL

if [ -z "$REPO_URL" ]; then
    echo "ERROR: no URL provided. Cancelled."
    exit 1
fi

# ─── Pre-flight safety scans ──────────────────────────────────
echo ""
echo "Running pre-flight safety scans..."
echo ""

# Scan 1: any accidental API keys?
KEY_HITS=$(grep -RE "sk-ant-[a-zA-Z0-9_-]+" --include="*.py" --include="*.ipynb" --include=".env" . 2>/dev/null | wc -l || echo 0)
if [ "$KEY_HITS" -gt 0 ]; then
    echo "WARNING: found $KEY_HITS possible Anthropic API key(s) in the files."
    echo "Please review before pushing:"
    grep -RE "sk-ant-[a-zA-Z0-9_-]+" --include="*.py" --include="*.ipynb" --include=".env" .
    echo ""
    read -p "Continue anyway? (y/N): " CONFIRM
    if [ "$CONFIRM" != "y" ]; then exit 1; fi
fi

# Scan 2: any real Reddit usernames still present?
USER_HITS=$(grep -RE "/u/[A-Za-z0-9_-]{3,}" --include="*.csv" --include="*.ipynb" . 2>/dev/null | grep -v "redacted" | wc -l || echo 0)
if [ "$USER_HITS" -gt 0 ]; then
    echo "WARNING: found $USER_HITS possible unredacted Reddit username mention(s)."
    echo "Sample:"
    grep -RE "/u/[A-Za-z0-9_-]{3,}" --include="*.csv" --include="*.ipynb" . 2>/dev/null | grep -v "redacted" | head -5
    echo ""
    read -p "Continue anyway? (y/N): " CONFIRM
    if [ "$CONFIRM" != "y" ]; then exit 1; fi
fi

# ─── Git init and status preview ──────────────────────────────
echo ""
echo "Initialising git repository..."
git init -q
git add .

echo ""
echo "Files staged for commit:"
git diff --cached --stat

# ─── Final confirmation ───────────────────────────────────────
echo ""
echo "About to commit and push to: $REPO_URL"
echo ""
read -p "Proceed with commit and push? (y/N): " CONFIRM
if [ "$CONFIRM" != "y" ]; then
    echo "Cancelled. Files remain staged; nothing pushed."
    exit 0
fi

# ─── Commit and push ──────────────────────────────────────────
git commit -q -m "Initial commit: dissertation code repository"
git branch -M main
git remote add origin "$REPO_URL"
git push -u origin main

echo ""
echo "==============================================================="
echo "  Done. Your repository is now published at:"
echo "    $REPO_URL"
echo "==============================================================="
