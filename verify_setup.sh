#!/bin/bash

# Verification script to ensure all dependencies and setup are correct

echo "=========================================="
echo "DSPy Star Analysis - Setup Verification"
echo "=========================================="
echo ""

# Check Python
echo "Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ $PYTHON_VERSION"
else
    echo "❌ Python 3 not found"
    exit 1
fi

# Check GitHub CLI
echo ""
echo "Checking GitHub CLI..."
if command -v gh &> /dev/null; then
    GH_VERSION=$(gh --version | head -n 1)
    echo "✅ $GH_VERSION"

    # Check authentication
    if gh auth status &> /dev/null; then
        echo "✅ GitHub CLI authenticated"
    else
        echo "⚠️  GitHub CLI not authenticated. Run: gh auth login"
    fi
else
    echo "❌ GitHub CLI not found. Install with: brew install gh"
fi

# Check Python packages
echo ""
echo "Checking Python dependencies..."

PACKAGES=("requests" "pandas" "numpy" "scipy" "matplotlib")
MISSING=()

for package in "${PACKAGES[@]}"; do
    if python3 -c "import $package" &> /dev/null; then
        echo "✅ $package"
    else
        echo "❌ $package (missing)"
        MISSING+=("$package")
    fi
done

if [ ${#MISSING[@]} -ne 0 ]; then
    echo ""
    echo "⚠️  Missing packages detected. Install with:"
    echo "   pip install -r requirements.txt"
fi

# Check files
echo ""
echo "Checking repository files..."

FILES=(
    "README.md"
    "requirements.txt"
    "fetch_dspy_stats.py"
    "parse_stars.py"
    "analyze_star_patterns.py"
    "visualize_results.py"
    "run_full_analysis.sh"
    "LICENSE"
    ".gitignore"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file (missing)"
    fi
done

# Check if scripts are executable
echo ""
echo "Checking script permissions..."

SCRIPTS=(
    "fetch_dspy_stats.py"
    "parse_stars.py"
    "analyze_star_patterns.py"
    "visualize_results.py"
    "run_full_analysis.sh"
)

for script in "${SCRIPTS[@]}"; do
    if [ -x "$script" ]; then
        echo "✅ $script (executable)"
    else
        echo "⚠️  $script (not executable)"
    fi
done

# Check git
echo ""
echo "Checking Git repository..."

if [ -d ".git" ]; then
    echo "✅ Git repository initialized"

    COMMIT_COUNT=$(git rev-list --count HEAD)
    echo "✅ $COMMIT_COUNT commit(s)"

    if git remote -v | grep -q origin; then
        echo "✅ Remote 'origin' configured"
        git remote -v | head -n 2
    else
        echo "⚠️  No remote 'origin' configured"
        echo "   See DEPLOYMENT.md for instructions"
    fi
else
    echo "❌ Not a git repository"
fi

echo ""
echo "=========================================="
echo "Verification Complete!"
echo "=========================================="
echo ""

if [ ${#MISSING[@]} -eq 0 ] && command -v gh &> /dev/null && gh auth status &> /dev/null; then
    echo "✅ All systems ready! You can run:"
    echo "   ./run_full_analysis.sh"
else
    echo "⚠️  Some setup required. See messages above."
fi

echo ""
