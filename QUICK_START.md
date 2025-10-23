# Quick Start Guide

Get the DSPy star analysis running in 5 minutes.

## Prerequisites Check

```bash
# Verify you have everything
./verify_setup.sh
```

## Installation (First Time Only)

### 1. Install GitHub CLI

**macOS:**
```bash
brew install gh
```

**Linux:**
```bash
sudo apt install gh
```

**Windows:**
```bash
scoop install gh
```

### 2. Authenticate

```bash
gh auth login
```

Follow the prompts to authenticate with your GitHub account.

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or if you prefer a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running the Analysis

### Option 1: Full Automated Pipeline (Recommended)

```bash
./run_full_analysis.sh
```

This will:
1. Fetch all GitHub star data (~5 minutes)
2. Run statistical analysis (~1 second)
3. Generate visualizations (~5 seconds)

**Total time:** ~5-10 minutes

### Option 2: Step by Step

```bash
# Step 1: Collect data
python3 fetch_dspy_stats.py

# Step 2: Analyze
python3 analyze_star_patterns.py dspy_stars_daily.csv

# Step 3: Visualize
python3 visualize_results.py dspy_stars_daily_with_zscores.csv
```

### Option 3: Just Parse Existing Raw Data

If you already have `dspy_stars_raw.json`:

```bash
python3 parse_stars.py > dspy_stars_daily.csv
python3 analyze_star_patterns.py dspy_stars_daily.csv
python3 visualize_results.py dspy_stars_daily_with_zscores.csv
```

## Expected Output

After running, you should have:

**Data files:**
- ✅ `dspy_stars_raw.json` (33 MB) - All stars with timestamps
- ✅ `dspy_stars_daily.csv` (19 KB) - Daily aggregated data
- ✅ `dspy_stars_daily_with_zscores.csv` - Enhanced with statistical metrics
- ✅ `dspy_metadata.json` - Repository metadata
- ✅ `dspy_pypi_downloads.json` - PyPI statistics

**Analysis files:**
- ✅ `star_analysis_report.json` - Complete statistical report

**Visualizations:**
- ✅ `dspy_star_analysis.png` - Main analysis plot (3 panels)
- ✅ `ratio_comparison.png` - Downloads-per-star comparison

## Verify Results

Check that your results match the expected findings:

```bash
# Should show baseline mean around 7.46
grep "baseline_period" star_analysis_report.json

# Should show spike mean around 52.0
grep "spike_period" star_analysis_report.json

# Should show 10 outliers
grep "count" star_analysis_report.json | head -1
```

## Expected Console Output

```
============================================================
DSPy Repository Statistics Fetcher
============================================================
✓ GitHub token obtained

Fetching repository metadata...
Repository: stanfordnlp/dspy
Total Stars: 29,446
Created: 2023-01-09

Fetching complete star history...
[Progress bars showing pages 1-295...]
Total stars fetched: 29,446

============================================================
STATISTICAL ANALYSIS SUMMARY
============================================================

📊 BASELINE PERIOD:
   Average: 7.46 stars/day
   Total: 1,477 stars over 198 days

🚨 SPIKE PERIOD:
   Average: 52.0 stars/day
   Multiplier: 6.97x increase
   Total: 1,144 stars over 22 days

📈 ANOMALY DETECTION:
   Outlier days (|z| > 3σ): 10
   Expected outliers: 0.059
   Ratio: 167.4x more than expected

⚡ MAXIMUM SPIKE:
   Date: 2023-09-07
   Stars: 223
   Z-score: 21.75
   P-value: 2.63e-105
```

If you see these numbers, you've successfully replicated the analysis! 🎉

## Troubleshooting

### "Rate limit exceeded"
- The script handles this automatically
- It will wait and retry
- Use authenticated requests (the script does this via `gh`)

### "Module not found"
```bash
pip install -r requirements.txt
```

### "gh: command not found"
```bash
# macOS
brew install gh

# Linux
sudo apt install gh
```

### "Authentication required"
```bash
gh auth login
```

### Scripts not executable
```bash
chmod +x *.sh *.py
```

## What's Next?

1. **Explore the data** - Open CSV files in Excel/Numbers
2. **Modify the analysis** - Change baseline/spike periods
3. **Create new visualizations** - Edit `visualize_results.py`
4. **Analyze other repos** - Modify `REPO_OWNER` and `REPO_NAME` in scripts

## Need Help?

- Check [README.md](README.md) for detailed documentation
- Run `./verify_setup.sh` to diagnose issues
- See [DEPLOYMENT.md](DEPLOYMENT.md) for GitHub publishing
- Open an issue on GitHub (after deploying)

---

**That's it! You're ready to run reproducible research.** 🚀
