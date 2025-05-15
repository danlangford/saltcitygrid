import json
import os
from collections import defaultdict

# Paths to JSON files
DATA_DIR = "data"
ABR_FILE = os.path.join(DATA_DIR, "abr_data.json")
COBRA_FILE = os.path.join(DATA_DIR, "cobra_tournaments.json")
DISCORD_FILE = os.path.join(DATA_DIR, "discord_events.json")
AESOPS_FILE = os.path.join(DATA_DIR, "aesops_tournaments.json")
FACEBOOK_FILE = os.path.join(DATA_DIR, "facebook_data.json")
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
aesops_events = load_json(AESOPS_FILE)
facebook_events = load_json(FACEBOOK_FILE)

# Dictionary to store merged events by normalized date
merged_events = defaultdict(
    lambda: {
        "date": None,
        "title": None,
        "locations": [],
        "sources": [],
        "details": [],
        "images": [],
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

        # concatenate event "store" and "address" into a single string and remove the trailing ", USA" if it exists
        if event.get("store") and event.get("address"):
            event["address"] = event["address"].replace(", USA", "")
            merged_events[date]["locations"].append(f"{event.get('store')}, {event.get('address')}")

        merged_events[date]["sources"].append({"source": "ABR", "link": event["url"]})
        merged_events[date]["details"].append(event["title"])
        for key in ["cardpool", "type", "format"]:
            if event.get(key):
                merged_events[date]["details"].append(f'{key}="{event.get(key)}"')
        merged_events[date]["details"].append(
            f'abr_organizer="{event["creator_name"]}"'
        )
        if event.get("recurring_day"):
            merged_events[date]["details"].append(
                f"recurring_day={event['recurring_day']}"
            )

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
        merged_events[date]["sources"].append({"source": "COBRA", "link": event["url"]})
        merged_events[date]["details"].append(event["title"])
        merged_events[date]["details"].append(
            f"cobra_players={event['player_count']} cobra_organizer={event['tournament_organizer']}"
        )

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
            event.get("entity_metadata", {}).get("location")
        )
        merged_events[date]["sources"].append(
            {
                "source": "DISCORD",
                "link": f"https://discord.com/events/{event['guild_id']}/{event['id']}",
            }
        )
        merged_events[date]["details"].append(event["name"])
        merged_events[date]["details"].append(event["description"])
        merged_events[date]["details"].append(
            f"discord_organizer={event['creator']['username']}"
        )

        if event.get("recurrence_rule"):
            merged_events[date]["details"].append("recurring")

        if event.get("image"):
            merged_events[date]["images"].append(
                f"https://cdn.discordapp.com/guild-events/{event['id']}/{event['image']}.png?size=512"
            )

# Merge Aesops events
for event in aesops_events:
    date = event.get("normalized_date")
    if date:
        merged_events[date]["date"] = date
        merged_events[date]["title"] = (
            event["title"]
            if not merged_events[date]["title"]
            else merged_events[date]["title"]
        )
        merged_events[date]["sources"].append({"source": "AESOPS", "link": event["url"]})
        merged_events[date]["details"].append(event["title"])
        merged_events[date]["details"].append(f"aesops_players={event['player_count']}")

# Merge Facebook events
for event in facebook_events:
    date = event.get("normalized_date")
    if date:
        merged_events[date]["date"] = date
        merged_events[date]["title"] = (
            event["title"]
            if not merged_events[date]["title"]
            else merged_events[date]["title"]
        )
        merged_events[date]["sources"].append({"source": "FACEBOOK", "link": event["url"]})
        merged_events[date]["details"].append(event["title"])

# Convert merged dictionary to a list
final_events = list(merged_events.values())

# Deduplicate the "details" array for each event
for event in final_events:
    event["details"] = list(set(event["details"]))

# Save merged events
with open(MERGED_FILE, "w") as f:
    json.dump(final_events, f, indent=2)

print(f"Saved {len(final_events)} merged events to {MERGED_FILE}")
