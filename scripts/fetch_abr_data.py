import requests
import yaml
import json
from datetime import datetime, timedelta

# Load followed ABR user IDs from config
CONFIG_FILE = "config/following.yml"

try:
    with open(CONFIG_FILE, "r") as f:
        config = yaml.safe_load(f)
        followed_abr_users = set(
            config.get("followed_tournament_organizers", {}).get("abr", [])
        )
except Exception as e:
    print(f"Failed to load config file: {e}")
    exit(1)

if not followed_abr_users:
    print("No followed ABR users configured. Exiting.")
    exit(0)

# Define valid event date range
NOW = datetime.now()
START_DATE = NOW - timedelta(days=60)
END_DATE = NOW + timedelta(days=400)


# Function to get the next date for a given day of the week
def get_next_date(day_name):
    days_of_week = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    day_index = days_of_week.index(day_name)
    today_index = NOW.weekday()
    delta_days = (day_index - today_index + 7) % 7
    return (NOW + timedelta(days=delta_days)).strftime("%Y-%m-%d")


# Fetch tournaments for each followed ABR user
all_tournaments = []
for user_id in followed_abr_users:
    api_url = f"https://alwaysberunning.net/api/tournaments?creator={user_id}"
    response = requests.get(api_url)

    if response.status_code == 200:
        tournaments = response.json()

        for t in tournaments:
            try:
                # Remove the 'rendered_in' field if it exists
                t.pop("rendered_in", None)

                # If `date` is present, validate if it falls in range
                if "date" in t and t["date"]:
                    event_date = datetime.strptime(
                        t["date"], "%Y.%m.%d."
                    )  # Convert 'YYYY.MM.DD.' to datetime
                    if START_DATE <= event_date <= END_DATE:
                        t["normalized_date"] = event_date.strftime("%Y-%m-%d")
                        all_tournaments.append(t)

                # If `recurring_day` exists, always include the event and add `normalized_date`
                elif "recurring_day" in t and t["recurring_day"]:
                    t["normalized_date"] = get_next_date(t["recurring_day"])
                    all_tournaments.append(t)

            except ValueError:
                print(
                    f'Skipping event {t.get("id", "Unknown")} due to invalid date format: {t.get("date", "N/A")}'
                )

    else:
        print(f"Failed to fetch data for user {user_id}")

# Sort tournaments by:
# 1. Regular events by normalized_date
# 2. Recurring events alphabetically by `recurring_day`
all_tournaments.sort(
    key=lambda x: (
        x.get("normalized_date", "9999-12-31"),
        x.get("recurring_day", ""),
        x["title"],
    )
)

# Save filtered tournaments to JSON file
with open("data/abr_data.json", "w") as f:
    json.dump(all_tournaments, f, indent=2)

print(f"Saved {len(all_tournaments)} filtered ABR tournaments to data/abr_data.json")
