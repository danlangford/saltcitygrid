import requests
from bs4 import BeautifulSoup
import json
import yaml
from datetime import datetime, timedelta

# Load config file with followed TOs
CONFIG_FILE = "config/following.yml"

try:
    with open(CONFIG_FILE, "r") as f:
        config = yaml.safe_load(f)
        followed_tos = set(
            config.get("followed_tournament_organizers", {}).get("cobra", [])
        )
except Exception as e:
    print(f"Failed to load config file: {e}")
    exit(1)

if not followed_tos:
    print("No followed COBRA TOs configured. Exiting.")
    exit(0)

# Define valid event date range
NOW = datetime.now()
START_DATE = NOW - timedelta(days=60)
END_DATE = NOW + timedelta(days=400)

# Load existing events to retain past ones
try:
    with open("pages/cobra_tournaments.json", "r") as f:
        saved_events = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    saved_events = []

# Keep only past events within the last 60 days
PAST_CUTOFF = NOW - timedelta(days=60)
filtered_past_events = [
    event
    for event in saved_events
    if datetime.strptime(event["normalized_date"], "%Y-%m-%d") >= PAST_CUTOFF
]

# Track unique event IDs
event_ids = {event["id"] for event in filtered_past_events}

# URL to fetch data from
URL = "https://tournaments.nullsignal.games/tournaments"

# Fetch HTML content
response = requests.get(URL)
if response.status_code != 200:
    print("Failed to fetch COBRA tournaments")
    exit(1)

# Parse HTML
soup = BeautifulSoup(response.text, "lxml")

# Find all tournament entries
new_events = []
for a_tag in soup.select("a[href^='/tournaments/']"):
    try:
        tournament_id = a_tag["href"].split("/")[-1]
        if tournament_id not in event_ids:
            title = a_tag.select_one(".card-title").text.strip()
            details_text = a_tag.select_one(".card-subtitle").text.strip()

            # Extracting date, player count, and TO from subtitle
            parts = details_text.split(" - ")
            date_str = parts[0].strip()
            player_count = int(parts[1].split()[0])  # Extract player count
            tournament_organizer = parts[2].strip()  # Extract TO name

            # Convert date string to datetime object
            event_date = datetime.strptime(date_str, "%d %b %Y")

            # Skip tournaments outside the valid date range
            if not (START_DATE <= event_date <= END_DATE):
                continue

            # Skip tournaments if TO is not in `following.yml`
            if tournament_organizer.lower() not in [to.lower() for to in followed_tos]:
                continue

            # Store structured data
            new_events.append(
                {
                    "id": tournament_id,
                    "title": title,
                    "date": date_str,  # Retain original date format
                    "normalized_date": event_date.strftime(
                        "%Y-%m-%d"
                    ),  # Add normalized date in ISO 8601 format
                    "player_count": player_count,
                    "tournament_organizer": tournament_organizer,
                    "url": f"https://tournaments.nullsignal.games/tournaments/{tournament_id}",
                }
            )
            event_ids.add(tournament_id)

    except Exception as e:
        print(f"Skipping entry due to error: {e}")

# Combine past and new events, then sort
all_events = filtered_past_events + new_events
all_events.sort(key=lambda x: (x["normalized_date"], x["title"]))

# Save to JSON
with open("pages/cobra_tournaments.json", "w") as f:
    json.dump(all_events, f, indent=2)

print(
    f"Saved {len(all_events)} total COBRA tournaments to pages/cobra_tournaments.json"
)
