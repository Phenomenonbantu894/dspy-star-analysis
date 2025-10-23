#!/usr/bin/env python3
"""
Analyze GitHub star patterns for statistical anomalies

This script performs the statistical tests that revealed the
star inflation pattern in DSPy.
"""

import sys
import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime
import json


def load_star_data(csv_file):
    """Load daily star counts from CSV"""
    df = pd.read_csv(csv_file)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    # Handle both CSV formats (2 or 3 columns)
    if "new_stars" in df.columns:
        df = df.rename(columns={"new_stars": "stars"})

    return df


def calculate_period_stats(df, start_date, end_date):
    """Calculate statistics for a specific time period"""
    mask = (df["date"] >= start_date) & (df["date"] <= end_date)
    period_data = df[mask]["stars"]

    if len(period_data) == 0:
        return None

    return {
        "mean": float(period_data.mean()),
        "std": float(period_data.std()),
        "median": float(period_data.median()),
        "total": int(period_data.sum()),
        "days": len(period_data),
        "max": int(period_data.max()),
        "min": int(period_data.min())
    }


def calculate_z_scores(df, baseline_start, baseline_end):
    """Calculate z-scores using baseline period statistics"""
    mask = (df["date"] >= baseline_start) & (df["date"] <= baseline_end)
    baseline = df[mask]["stars"]

    mean = baseline.mean()
    std = baseline.std()

    print(f"\n📊 Baseline Statistics ({baseline_start} to {baseline_end}):")
    print(f"   Mean: {mean:.2f} stars/day")
    print(f"   Std Dev: {std:.2f}")
    print(f"   Sample size: {len(baseline)} days")

    # Calculate z-scores for all days
    df["z_score"] = (df["stars"] - mean) / std

    return df, mean, std


def identify_outliers(df, threshold=3.0):
    """Identify days with z-scores exceeding threshold"""
    outliers = df[abs(df["z_score"]) > threshold].copy()
    outliers = outliers.sort_values("z_score", ascending=False)

    return outliers


def analyze_spike_period(df, spike_start, spike_end, baseline_mean):
    """Detailed analysis of suspected spike period"""
    mask = (df["date"] >= spike_start) & (df["date"] <= spike_end)
    spike_data = df[mask]

    # Calculate statistics
    spike_mean = spike_data["stars"].mean()
    multiplier = spike_mean / baseline_mean

    # Count outliers (z > 3σ)
    outliers = spike_data[abs(spike_data["z_score"]) > 3]
    n_outliers = len(outliers)
    n_days = len(spike_data)

    # Expected outliers under normal distribution
    # P(|z| > 3) ≈ 0.0027
    expected_outliers = n_days * 0.0027

    # Find maximum z-score day
    if len(spike_data) > 0:
        max_z_idx = spike_data["z_score"].idxmax()
        max_z_day = spike_data.loc[max_z_idx]
    else:
        max_z_day = None

    return {
        "spike_mean": float(spike_mean),
        "multiplier": float(multiplier),
        "n_days": n_days,
        "total_stars": int(spike_data["stars"].sum()),
        "n_outliers": n_outliers,
        "expected_outliers": float(expected_outliers),
        "outlier_ratio": float(n_outliers / expected_outliers) if expected_outliers > 0 else float('inf'),
        "max_z_score": float(max_z_day["z_score"]) if max_z_day is not None else None,
        "max_z_date": max_z_day["date"].isoformat() if max_z_day is not None else None,
        "max_z_stars": int(max_z_day["stars"]) if max_z_day is not None else None
    }


def generate_report(df, baseline_stats, spike_stats, spike_analysis, outliers):
    """Generate comprehensive analysis report"""

    report = {
        "analysis_date": datetime.now().isoformat(),
        "total_stars": int(df["stars"].sum()),
        "date_range": {
            "start": df["date"].min().isoformat(),
            "end": df["date"].max().isoformat()
        },
        "baseline_period": baseline_stats,
        "spike_period": spike_stats,
        "spike_analysis": spike_analysis,
        "outliers": {
            "count": len(outliers),
            "top_20": [
                {
                    "date": row["date"].isoformat(),
                    "stars": int(row["stars"]),
                    "z_score": float(row["z_score"])
                }
                for _, row in outliers.head(20).iterrows()
            ]
        }
    }

    return report


def print_summary(baseline_stats, spike_stats, spike_analysis):
    """Print human-readable summary"""

    print("\n" + "="*70)
    print("STATISTICAL ANALYSIS SUMMARY")
    print("="*70)

    print(f"\n📊 BASELINE PERIOD:")
    print(f"   Average: {baseline_stats['mean']:.2f} stars/day")
    print(f"   Total: {baseline_stats['total']:,} stars over {baseline_stats['days']} days")

    print(f"\n🚨 SPIKE PERIOD:")
    print(f"   Average: {spike_stats['mean']:.2f} stars/day")
    print(f"   Multiplier: {spike_analysis['multiplier']:.2f}x increase")
    print(f"   Total: {spike_stats['total']:,} stars over {spike_stats['days']} days")

    print(f"\n📈 ANOMALY DETECTION:")
    print(f"   Outlier days (|z| > 3σ): {spike_analysis['n_outliers']}")
    print(f"   Expected outliers: {spike_analysis['expected_outliers']:.3f}")
    print(f"   Ratio: {spike_analysis['outlier_ratio']:.1f}x more than expected")

    if spike_analysis['max_z_score']:
        print(f"\n⚡ MAXIMUM SPIKE:")
        print(f"   Date: {spike_analysis['max_z_date']}")
        print(f"   Stars: {spike_analysis['max_z_stars']}")
        print(f"   Z-score: {spike_analysis['max_z_score']:.2f}")

        # Calculate probability
        from scipy.stats import norm
        p_value = 2 * (1 - norm.cdf(abs(spike_analysis['max_z_score'])))
        print(f"   P-value: {p_value:.2e}")

    print("\n" + "="*70)


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_star_patterns.py <stars_daily.csv>")
        sys.exit(1)

    csv_file = sys.argv[1]

    # Load data
    print(f"Loading data from {csv_file}...")
    df = load_star_data(csv_file)

    # Define analysis periods (DSPy specific)
    baseline_start = "2023-01-23"
    baseline_end = "2023-08-23"
    spike_start = "2023-08-24"
    spike_end = "2023-09-14"

    # Calculate baseline statistics
    baseline_stats = calculate_period_stats(df, baseline_start, baseline_end)
    spike_stats = calculate_period_stats(df, spike_start, spike_end)

    # Calculate z-scores
    df, baseline_mean, baseline_std = calculate_z_scores(df, baseline_start, baseline_end)

    # Identify outliers
    outliers = identify_outliers(df, threshold=3.0)

    # Analyze spike period
    spike_analysis = analyze_spike_period(df, spike_start, spike_end, baseline_mean)

    # Generate and save report
    report = generate_report(df, baseline_stats, spike_stats, spike_analysis, outliers)

    output_file = "star_analysis_report.json"
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n✅ Full report saved to {output_file}")

    # Print summary
    print_summary(baseline_stats, spike_stats, spike_analysis)

    # Save enhanced CSV with z-scores
    output_csv = csv_file.replace(".csv", "_with_zscores.csv")
    df.to_csv(output_csv, index=False)
    print(f"\n✅ Enhanced data saved to {output_csv}")


if __name__ == "__main__":
    main()
