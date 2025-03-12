import json
import os
from collections import defaultdict

# Paths to JSON files
DATA_DIR = "data"
ABR_FILE = os.path.join(DATA_DIR, "abr_data.json")
COBRA_FILE = os.path.join(DATA_DIR, "cobra_tournaments.json")
DISCORD_FILE = os.path.join(DATA_DIR, "discord_events.json")
MERGED_FILE = os.path.join("pages", "merged_events.json")


# Load JSON safely
def load_json(filepath):
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


# Load event data
abr_events = load_json(ABR_FILE)
cobra_events = load_json(COBRA_FILE)
discord_events = load_json(DISCORD_FILE)

# Dictionary to store merged events by normalized date
merged_events = defaultdict(
    lambda: {
        "date": None,
        "title": None,
        "locations": [],
        "sources": [],  # Now stores source + link together
        "details": [],
    }
)

# Merge ABR events
for event in abr_events:
    date = event.get("normalized_date")
    if date:
        merged_events[date]["date"] = date
        merged_events[date]["title"] = (
            event["title"]
            if not merged_events[date]["title"]
            else merged_events[date]["title"]
        )
        merged_events[date]["locations"].append(event.get("store", "Unknown"))
        merged_events[date]["sources"].append({"source": "ABR", "link": event["url"]})
        merged_events[date]["details"].append(event["title"])

# Merge Cobra events
for event in cobra_events:
    date = event.get("normalized_date")
    if date:
        merged_events[date]["date"] = date
        merged_events[date]["title"] = (
            event["title"]
            if not merged_events[date]["title"]
            else merged_events[date]["title"]
        )
        merged_events[date]["locations"].append("Unknown")  # Cobra lacks location info
        merged_events[date]["sources"].append({"source": "COBRA", "link": event["url"]})
        merged_events[date]["details"].append(event["title"])

# Merge Discord events
for event in discord_events:
    date = event.get("normalized_date")
    if date:
        merged_events[date]["date"] = date
        merged_events[date]["title"] = (
            event["name"]
            if not merged_events[date]["title"]
            else merged_events[date]["title"]
        )
        merged_events[date]["locations"].append(
            event.get("entity_metadata", {}).get("location", "Unknown")
        )
        merged_events[date]["sources"].append(
            {
                "source": "DISCORD",
                "link": f"https://discord.com/events/{event['guild_id']}/{event['id']}",
            }
        )
        merged_events[date]["details"].append(event["name"])

# Convert merged dictionary to a list
final_events = list(merged_events.values())

# Save merged events
with open(MERGED_FILE, "w") as f:
    json.dump(final_events, f, indent=2)

print(f"Saved {len(final_events)} merged events to {MERGED_FILE}")
