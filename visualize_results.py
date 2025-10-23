#!/usr/bin/env python3
"""
Create visualizations of GitHub star analysis
"""

import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime


def create_analysis_plots(df, output_file="star_analysis.png"):
    """Create comprehensive visualization of star patterns"""

    # Set up the plot style
    plt.style.use('seaborn-v0_8-darkgrid')
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(16, 12))

    # Define important periods (DSPy specific)
    baseline_start = pd.to_datetime("2023-01-23")
    baseline_end = pd.to_datetime("2023-08-23")
    spike_start = pd.to_datetime("2023-08-24")
    spike_end = pd.to_datetime("2023-09-14")
    paper_date = pd.to_datetime("2023-10-05")
    databricks_date = pd.to_datetime("2023-09-14")

    # Plot 1: Daily star counts with period highlighting
    ax1.plot(df["date"], df["stars"], linewidth=1.5, color="steelblue", alpha=0.7)

    # Highlight periods
    baseline_mask = (df["date"] >= baseline_start) & (df["date"] <= baseline_end)
    spike_mask = (df["date"] >= spike_start) & (df["date"] <= spike_end)

    ax1.fill_between(df[baseline_mask]["date"], 0, df[baseline_mask]["stars"],
                     alpha=0.2, color="green", label="Baseline Period (Jan-Aug 2023)")
    ax1.fill_between(df[spike_mask]["date"], 0, df[spike_mask]["stars"],
                     alpha=0.3, color="red", label="Spike Period (Aug 24-Sep 14, 2023)")

    # Add key events
    ax1.axvline(databricks_date, color="purple", linestyle="--",
                linewidth=2, alpha=0.8, label="Databricks $43B Announcement")
    ax1.axvline(paper_date, color="orange", linestyle="--",
                linewidth=2, alpha=0.8, label="DSPy Paper Published")

    ax1.set_ylabel("Stars per Day", fontsize=13, fontweight="bold")
    ax1.set_title("DSPy GitHub Stars - Daily Acquisition Pattern",
                  fontsize=16, fontweight="bold", pad=20)
    ax1.legend(loc="upper left", fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(bottom=0)

    # Plot 2: Z-scores with outlier thresholds
    ax2.plot(df["date"], df["z_score"], linewidth=1.5, color="darkblue", alpha=0.7)
    ax2.axhline(3, color="red", linestyle="--", label="3σ threshold", linewidth=2, alpha=0.7)
    ax2.axhline(-3, color="red", linestyle="--", linewidth=2, alpha=0.7)
    ax2.axhline(0, color="gray", linestyle="-", linewidth=0.5, alpha=0.5)

    # Highlight spike period
    ax2.fill_between(df[spike_mask]["date"], -5, 25, alpha=0.15, color="red")

    # Mark outliers
    outliers = df[abs(df["z_score"]) > 3]
    ax2.scatter(outliers["date"], outliers["z_score"],
               color="red", s=100, zorder=5, alpha=0.7, label="Outliers (|z| > 3)")

    ax2.set_ylabel("Z-Score", fontsize=13, fontweight="bold")
    ax2.set_title("Statistical Anomaly Detection (Z-Scores)",
                  fontsize=16, fontweight="bold", pad=20)
    ax2.legend(loc="upper left", fontsize=10)
    ax2.grid(True, alpha=0.3)

    # Plot 3: Cumulative stars over time
    df["cumulative_stars"] = df["stars"].cumsum()
    ax3.plot(df["date"], df["cumulative_stars"], linewidth=2,
            color="darkgreen", label="Total Stars")

    # Mark key milestones
    milestones = [1000, 5000, 10000, 20000]
    for milestone in milestones:
        milestone_date = df[df["cumulative_stars"] >= milestone]["date"].iloc[0]
        ax3.axhline(milestone, color="gray", linestyle=":", alpha=0.3)
        ax3.text(df["date"].min(), milestone, f"{milestone:,}",
                fontsize=9, va="bottom")

    ax3.fill_between(df[spike_mask]["date"],
                     0, df[spike_mask]["cumulative_stars"],
                     alpha=0.2, color="red")

    ax3.set_ylabel("Cumulative Stars", fontsize=13, fontweight="bold")
    ax3.set_xlabel("Date", fontsize=13, fontweight="bold")
    ax3.set_title("Cumulative GitHub Stars Over Time",
                  fontsize=16, fontweight="bold", pad=20)
    ax3.legend(loc="upper left", fontsize=10)
    ax3.grid(True, alpha=0.3)

    # Format x-axis for all plots
    for ax in [ax1, ax2, ax3]:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    print(f"✅ Visualization saved to {output_file}")

    return fig


def create_comparison_plot(ratios_data, output_file="ratio_comparison.png"):
    """Create bar chart comparing downloads-per-star ratios"""
    fig, ax = plt.subplots(figsize=(12, 7))

    projects = list(ratios_data.keys())
    ratios = list(ratios_data.values())

    colors = ['red' if 'DSPy' in p else 'steelblue' for p in projects]

    bars = ax.bar(projects, ratios, color=colors, alpha=0.7, edgecolor='black')

    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')

    ax.set_ylabel("Downloads per Star (Monthly)", fontsize=13, fontweight="bold")
    ax.set_title("LLM Framework: Downloads-per-Star Ratio Comparison",
                 fontsize=16, fontweight="bold", pad=20)
    ax.grid(True, axis='y', alpha=0.3)
    plt.xticks(rotation=45, ha='right')

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    print(f"✅ Comparison plot saved to {output_file}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python visualize_results.py <stars_daily_with_zscores.csv>")
        sys.exit(1)

    csv_file = sys.argv[1]

    # Load data
    print(f"Loading data from {csv_file}...")
    df = pd.read_csv(csv_file)
    df["date"] = pd.to_datetime(df["date"])

    # Create main analysis plots
    create_analysis_plots(df, "dspy_star_analysis.png")

    # Create comparison plot
    ratios = {
        "LangChain": 662,
        "Instructor": 330,
        "LlamaIndex": 93.6,
        "DSPy": 16.9
    }
    create_comparison_plot(ratios, "ratio_comparison.png")

    print("\n✅ All visualizations created successfully!")


if __name__ == "__main__":
    main()
