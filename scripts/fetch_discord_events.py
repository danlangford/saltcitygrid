import requests
import json
import yaml
import os
from datetime import datetime, timedelta
import pytz

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
NOW = datetime.now(pytz.UTC)
START_DATE = NOW - timedelta(days=60)
END_DATE = NOW + timedelta(days=400)

# Load existing events to retain past ones
try:
    with open("data/discord_events.json", "r") as f:
        saved_events = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    saved_events = []

# Keep only past events within the last 60 days
PAST_CUTOFF = NOW - timedelta(days=60)
filtered_past_events = [
    event
    for event in saved_events
    if datetime.strptime(event["scheduled_start_time"], "%Y-%m-%dT%H:%M:%S%z")
    >= PAST_CUTOFF
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
            # Parse the main scheduled_start_time
            main_start_time_utc = datetime.strptime(
                event["scheduled_start_time"], "%Y-%m-%dT%H:%M:%S%z"
            )
            all_dates = [main_start_time_utc]

            # Check for exceptions and parse their dates
            if "guild_scheduled_event_exceptions" in event:
                for exception in event["guild_scheduled_event_exceptions"]:
                    exception_start_time_utc = datetime.strptime(
                        exception["scheduled_start_time"], "%Y-%m-%dT%H:%M:%S%z"
                    )
                    all_dates.append(exception_start_time_utc)

            # Find the earliest valid date within the range
            valid_dates = [date for date in all_dates if START_DATE <= date <= END_DATE]
            if valid_dates:
                next_date_utc = min(valid_dates)
                # Convert UTC time to Mountain Time
                mountain_tz = pytz.timezone("America/Denver")
                next_date_mt = next_date_utc.astimezone(mountain_tz)
                event["normalized_date"] = next_date_mt.strftime("%Y-%m-%d")

            # Add the event to the dictionary
            event_dict[event["id"]] = event
    else:
        print(
            f"Failed to fetch events for guild {guild_id}: {response.status_code} - {response.text}"
        )

# Combine past and new events, then sort
all_events = list(event_dict.values())
all_events.sort(key=lambda x: x["scheduled_start_time"])

# Save to JSON
with open("data/discord_events.json", "w") as f:
    json.dump(all_events, f, indent=2)

print(f"Saved {len(all_events)} total Discord events to data/discord_events.json")
