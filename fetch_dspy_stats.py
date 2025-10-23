#!/usr/bin/env python3
"""
Fetch GitHub star history and PyPI download statistics for DSPy
"""

import requests
import json
from datetime import datetime, timedelta
import time
import os
import subprocess

# Configuration
REPO_OWNER = "stanfordnlp"
REPO_NAME = "dspy"
PYPI_PACKAGE = "dspy-ai"

def get_github_token():
    """Get GitHub token from gh CLI"""
    try:
        result = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except:
        return None

def fetch_star_history_via_stargazers(token):
    """
    Fetch complete star history using the stargazers endpoint.
    This gives us the exact timestamp of when each star was added.
    """
    print("Fetching star history from GitHub API...")

    headers = {
        "Accept": "application/vnd.github.v3.star+json",
    }

    if token:
        headers["Authorization"] = f"token {token}"
        print("Using authenticated requests")
    else:
        print("WARNING: No GitHub token found. Rate limits will be strict.")

    stars = []
    page = 1
    per_page = 100

    while True:
        url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/stargazers"
        params = {"page": page, "per_page": per_page}

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            if not data:
                break

            for item in data:
                stars.append({
                    "starred_at": item["starred_at"],
                    "user": item["user"]["login"]
                })

            print(f"Fetched page {page}, total stars: {len(stars)}")

            # Check rate limit
            remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
            if remaining < 10:
                reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                wait_time = max(reset_time - time.time(), 0) + 1
                print(f"Rate limit low. Waiting {wait_time:.0f} seconds...")
                time.sleep(wait_time)

            page += 1
            time.sleep(0.1)  # Be nice to the API

        elif response.status_code == 403:
            print("Rate limit exceeded!")
            print(f"Headers: {response.headers}")
            break
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            break

    return stars

def aggregate_stars_by_date(stars):
    """Aggregate stars into daily counts"""
    daily_counts = {}

    for star in stars:
        date = star["starred_at"].split("T")[0]
        daily_counts[date] = daily_counts.get(date, 0) + 1

    # Create cumulative data
    sorted_dates = sorted(daily_counts.keys())
    cumulative = 0
    result = []

    for date in sorted_dates:
        cumulative += daily_counts[date]
        result.append({
            "date": date,
            "new_stars": daily_counts[date],
            "total_stars": cumulative
        })

    return result

def fetch_repo_metadata(token):
    """Fetch current repo statistics"""
    print("\nFetching repository metadata...")

    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"

    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return {
            "name": data["full_name"],
            "description": data["description"],
            "created_at": data["created_at"],
            "stars": data["stargazers_count"],
            "forks": data["forks_count"],
            "watchers": data["watchers_count"],
            "open_issues": data["open_issues_count"],
            "language": data["language"],
            "last_updated": data["updated_at"]
        }

    return None

def fetch_pypi_downloads():
    """
    Fetch PyPI download statistics using pypistats.org API
    """
    print("\nFetching PyPI download statistics...")

    # Try pypistats API for recent downloads
    url = f"https://pypistats.org/api/packages/{PYPI_PACKAGE}/recent"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            recent_data = response.json()
        else:
            recent_data = None
    except:
        recent_data = None

    # Try to get overall stats
    url_overall = f"https://pypistats.org/api/packages/{PYPI_PACKAGE}/overall"

    try:
        response = requests.get(url_overall)
        if response.status_code == 200:
            overall_data = response.json()
        else:
            overall_data = None
    except:
        overall_data = None

    return {
        "recent": recent_data,
        "overall": overall_data
    }

def main():
    print("=" * 60)
    print("DSPy Repository Statistics Fetcher")
    print("=" * 60)

    # Get GitHub token
    token = get_github_token()

    # Fetch repository metadata
    metadata = fetch_repo_metadata(token)

    if metadata:
        print(f"\nRepository: {metadata['name']}")
        print(f"Stars: {metadata['stars']:,}")
        print(f"Forks: {metadata['forks']:,}")
        print(f"Created: {metadata['created_at']}")

    # Fetch star history
    stars = fetch_star_history_via_stargazers(token)

    if stars:
        print(f"\nTotal stars fetched: {len(stars)}")
        daily_data = aggregate_stars_by_date(stars)

        # Save raw star data
        with open("dspy_stars_raw.json", "w") as f:
            json.dump(stars, f, indent=2)
        print("Saved raw star data to dspy_stars_raw.json")

        # Save aggregated daily data
        with open("dspy_stars_daily.json", "w") as f:
            json.dump(daily_data, f, indent=2)
        print("Saved daily star data to dspy_stars_daily.json")

        # Save as CSV
        with open("dspy_stars_daily.csv", "w") as f:
            f.write("date,new_stars,total_stars\n")
            for entry in daily_data:
                f.write(f"{entry['date']},{entry['new_stars']},{entry['total_stars']}\n")
        print("Saved daily star data to dspy_stars_daily.csv")

    # Fetch PyPI downloads
    pypi_data = fetch_pypi_downloads()

    if pypi_data:
        with open("dspy_pypi_downloads.json", "w") as f:
            json.dump(pypi_data, f, indent=2)
        print("\nSaved PyPI download data to dspy_pypi_downloads.json")

    # Save metadata
    if metadata:
        metadata["fetch_timestamp"] = datetime.now().isoformat()
        with open("dspy_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        print("Saved metadata to dspy_metadata.json")

    print("\n" + "=" * 60)
    print("Data collection complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
