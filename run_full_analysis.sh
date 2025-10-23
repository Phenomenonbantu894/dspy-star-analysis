#!/bin/bash

# Full analysis pipeline for DSPy star inflation research

set -e  # Exit on error

echo "========================================"
echo "DSPy Star Analysis - Full Pipeline"
echo "========================================"

# Check for GitHub CLI
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) not found. Please install:"
    echo "   brew install gh  (macOS)"
    echo "   sudo apt install gh  (Linux)"
    exit 1
fi

# Check authentication
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub. Run: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI authenticated"

# Step 1: Data Collection
echo ""
echo "Step 1: Collecting GitHub star history..."
python3 fetch_dspy_stats.py

if [ ! -f "dspy_stars_daily.csv" ]; then
    echo "❌ Failed to create dspy_stars_daily.csv"
    exit 1
fi

echo "✅ Data collection complete"

# Step 2: Statistical Analysis
echo ""
echo "Step 2: Running statistical analysis..."
python3 analyze_star_patterns.py dspy_stars_daily.csv

if [ ! -f "dspy_stars_daily_with_zscores.csv" ]; then
    echo "❌ Failed to create analysis output"
    exit 1
fi

echo "✅ Statistical analysis complete"

# Step 3: Visualization
echo ""
echo "Step 3: Creating visualizations..."
python3 visualize_results.py dspy_stars_daily_with_zscores.csv

echo ""
echo "========================================"
echo "✅ ANALYSIS COMPLETE!"
echo "========================================"
echo ""
echo "Output files:"
echo "  📄 dspy_stars_daily.csv"
echo "  📄 dspy_stars_daily_with_zscores.csv"
echo "  📄 star_analysis_report.json"
echo "  📊 dspy_star_analysis.png"
echo "  📊 ratio_comparison.png"
echo ""
