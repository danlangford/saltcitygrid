import json
from datetime import datetime, timedelta

# FACEBOOK API and screen scraping was not possible (or just too much work)
# so we are going to pluck the FB URL from the AlwaysBeRunning (ABR) data

# Define valid event date range
NOW = datetime.now()
START_DATE = NOW - timedelta(days=60)
END_DATE = NOW + timedelta(days=400)

# Load existing events to retain past ones
try:
    with open("data/facebook_data.json", "r") as f:
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
except (FileNotFoundError, json.JSONDecodeError):
    abr_data = []

# Process ABR data for Facebook events
for event in abr_data:
    try:
        # Skip events without a Facebook link
        if not event.get("link_facebook"):
            continue

        # Extract relevant fields
        abr_id = event["id"]
        title = event["title"]
        date_str = event["normalized_date"]

        # Convert date string to datetime object
        event_date = datetime.strptime(date_str, "%Y-%m-%d")

        # Skip tournaments outside the valid date range
        if not (START_DATE <= event_date <= END_DATE):
            continue

        # Store structured data
        event_dict[abr_id] = {
            "abr_id": abr_id,
            "title": title,
            "date": date_str,  
            "normalized_date": event_date.strftime(
                "%Y-%m-%d"
            ),  
            "url": event["link_facebook"],  
        }

    except Exception as e:
        print(f"Skipping entry due to error: {e}")

# Combine past and new events, then sort
all_events = list(event_dict.values())
all_events.sort(key=lambda x: (x["normalized_date"], x["title"]))

# Save to JSON
with open("data/facebook_data.json", "w") as f:
    json.dump(all_events, f, indent=2)

print(f"Saved {len(all_events)} total Facebook events to data/facebook_data.json")
