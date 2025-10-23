import json
import sys
from collections import defaultdict
from datetime import datetime

# Read the JSON file
with open('dspy_stars_raw.json', 'r') as f:
    data = json.load(f)

# Aggregate by date
daily_counts = defaultdict(int)

for item in data:
    if 'starred_at' in item:
        date = item['starred_at'].split('T')[0]
        daily_counts[date] += 1

# Sort by date and create cumulative counts
sorted_dates = sorted(daily_counts.keys())
cumulative = 0

print("date,new_stars,total_stars")
for date in sorted_dates:
    cumulative += daily_counts[date]
    print(f"{date},{daily_counts[date]},{cumulative}")
