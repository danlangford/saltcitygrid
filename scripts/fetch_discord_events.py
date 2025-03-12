import requests
import json
import yaml
import os
from datetime import datetime, timedelta, UTC

# Load config file for Discord settings
CONFIG_FILE = "config/following.yml"

try:
    with open(CONFIG_FILE, "r") as f:
        config = yaml.safe_load(f)
        guild_ids = config.get("discord_guilds", [])
except Exception as e:
    print(f"Failed to load config file: {e}")
    exit(1)

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not DISCORD_BOT_TOKEN:
    print(
        "Missing Discord bot token! Set DISCORD_BOT_TOKEN in GitHub Secrets or environment variables."
    )
    exit(1)

headers = {
    "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
    "Content-Type": "application/json",
}

# Define valid event date range
NOW = datetime.now(UTC)
START_DATE = NOW - timedelta(days=60)
END_DATE = NOW + timedelta(days=400)

# Load existing events to retain past ones
try:
    with open("pages/discord_events.json", "r") as f:
        saved_events = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    saved_events = []

# Keep only past events within the last 60 days
PAST_CUTOFF = NOW - timedelta(days=60)
filtered_past_events = [
    event
    for event in saved_events
    if datetime.strptime(event["start_time"], "%Y-%m-%dT%H:%M:%S%z") >= PAST_CUTOFF
]

# Create a dictionary of existing events for quick lookup
event_dict = {event["id"]: event for event in filtered_past_events}

# Fetch new events from Discord
for guild_id in guild_ids:
    url = f"https://discord.com/api/v10/guilds/{guild_id}/scheduled-events"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        events = response.json()
        for event in events:
            start_time = datetime.strptime(
                event["scheduled_start_time"], "%Y-%m-%dT%H:%M:%S%z"
            )
            if START_DATE <= start_time <= END_DATE:
                event["normalized_date"] = start_time.strftime("%Y-%m-%d")
                event_dict[event["id"]] = event
    else:
        print(
            f"Failed to fetch events for guild {guild_id}: {response.status_code} - {response.text}"
        )

# Combine past and new events, then sort
all_events = list(event_dict.values())
all_events.sort(key=lambda x: x["scheduled_start_time"])

# Save to JSON
with open("pages/discord_events.json", "w") as f:
    json.dump(all_events, f, indent=2)

print(f"Saved {len(all_events)} total Discord events to pages/discord_events.json")
