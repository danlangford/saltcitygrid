import requests
import yaml
import json
from datetime import datetime, timedelta

# Load followed ABR user IDs from config
CONFIG_FILE = "config/following.yml"

try:
    with open(CONFIG_FILE, "r") as f:
        config = yaml.safe_load(f)
        followed_abr_users = set(config.get("followed_tournament_organizers", {}).get("abr", []))
except Exception as e:
    print(f"Failed to load config file: {e}")
    exit(1)

if not followed_abr_users:
    print("No followed ABR users configured. Exiting.")
    exit(0)

# Define valid event date range
NOW = datetime.now()
START_DATE = NOW - timedelta(days=30)
END_DATE = NOW + timedelta(days=400)

# Fetch tournaments for each followed ABR user
all_tournaments = []
for user_id in followed_abr_users:
    api_url = f"https://alwaysberunning.net/api/tournaments?creator_id={user_id}" 
    response = requests.get(api_url)
    
    if response.status_code == 200:
        tournaments = response.json()

        # Filter tournaments based on date range
        for t in tournaments:
            try:
                event_date = datetime.strptime(t["date"], "%Y.%m.%d.")  # Convert "YYYY.MM.DD." to datetime
                if START_DATE <= event_date <= END_DATE:
                    all_tournaments.append(t)
            except ValueError:
                print(f"Skipping event {t['id']} due to invalid date format: {t['date']}")
    else:
        print(f"Failed to fetch data for user {user_id}")

# Sort tournaments by date and title
all_tournaments.sort(key=lambda x: (x["date"], x["title"]))

# Save filtered tournaments to JSON file
with open("abr_data.json", "w") as f:
    json.dump(all_tournaments, f, indent=2)

print(f"Saved {len(all_tournaments)} filtered ABR tournaments to abr_data.json")
