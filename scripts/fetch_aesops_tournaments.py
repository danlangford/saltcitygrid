import requests
from bs4 import BeautifulSoup
import json
import yaml
from datetime import datetime, timedelta

# Define valid event date range
NOW = datetime.now()
START_DATE = NOW - timedelta(days=60)
END_DATE = NOW + timedelta(days=400)

# Load existing events to retain past ones
try:
    with open("data/aesops_tournaments.json", "r") as f:
        saved_events = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    saved_events = []

# Keep only past events within the last 60 days
START_DATE = NOW - timedelta(days=60)
filtered_past_events = [
    event
    for event in saved_events
    if datetime.strptime(event["normalized_date"], "%Y-%m-%d") >= START_DATE
]

# Create a dictionary of existing events for quick lookup
event_dict = {event["id"]: event for event in filtered_past_events}

# Load event titles from abr_data.json
try:
    with open("data/abr_data.json", "r") as f:
        abr_data = json.load(f)
    abr_event_titles = [event["title"] for event in abr_data]
except (FileNotFoundError, json.JSONDecodeError):
    abr_event_titles = []

# URL to fetch data from
URL = "https://www.aesopstables.net/index?page=1"

# Fetch HTML content
response = requests.get(URL)

if response.status_code != 200:
    print("Failed to fetch Aesops tournaments")
    exit(1)

# Parse HTML
soup = BeautifulSoup(response.text, "lxml")

# Find all tournament entries
for a_tag in soup.select("a[href$='/standings']"):
    try:
        tournament_id = a_tag["href"].split("/")[-2]
        title = a_tag.text.strip()

        # Skip if the title does not match any ABR events
        if title not in abr_event_titles:
            continue

        # Extract the parent <tr> element
        tr_tag = a_tag.find_parent("tr")
        if not tr_tag:
            continue

        # Extract data from <tr>
        columns = tr_tag.find_all("th")
        if len(columns) < 4:
            continue

        rounds = int(columns[1].text.strip())
        player_count = int(columns[2].text.strip())
        date_str = columns[3].text.strip()

        # Convert date string to datetime object
        event_date = datetime.strptime(date_str, "%Y-%m-%d")

        # Skip tournaments outside the valid date range
        if not (START_DATE <= event_date <= END_DATE):
            continue

        # Store structured data
        event_dict[tournament_id] = {
            "id": tournament_id,
            "title": title,
            "date": date_str,  # Retain original date format
            "normalized_date": event_date.strftime(
                "%Y-%m-%d"
            ),  # Add normalized date in ISO 8601 format
            "player_count": player_count,
            "url": f"https://www.aesopstables.net/{tournament_id}/standings",
        }

    except Exception as e:
        print(f"Skipping entry due to error: {e}")

# Combine past and new events, then sort
all_events = list(event_dict.values())
all_events.sort(key=lambda x: (x["normalized_date"], x["title"]))

# Save to JSON
with open("data/aesops_tournaments.json", "w") as f:
    json.dump(all_events, f, indent=2)

print(
    f"Saved {len(all_events)} total Aesops tournaments to data/aesops_tournaments.json"
)
