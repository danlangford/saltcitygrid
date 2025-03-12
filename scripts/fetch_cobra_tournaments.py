import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

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
tournaments = []
for a_tag in soup.select("a[href^='/tournaments/']"):
    try:
        tournament_id = a_tag["href"].split("/")[-1]
        title = a_tag.select_one(".card-title").text.strip()
        details_text = a_tag.select_one(".card-subtitle").text.strip()

        # Extracting date, player count, and TO from subtitle
        parts = details_text.split(" - ")
        date_str = parts[0].strip()
        player_count = int(parts[1].split()[0])  # Extract player count
        tournament_organizer = parts[2].strip()  # Extract TO name

        # Convert date to YYYY-MM-DD format
        date_parsed = datetime.strptime(date_str, "%d %b %Y").strftime("%Y-%m-%d")

        # Store structured data
        tournaments.append({
            "id": tournament_id,
            "title": title,
            "date": date_parsed,
            "player_count": player_count,
            "tournament_organizer": tournament_organizer,
            "url": f"https://tournaments.nullsignal.games/tournaments/{tournament_id}"
        })
    except Exception as e:
        print(f"Skipping entry due to error: {e}")

# Sort tournaments by date and title
tournaments.sort(key=lambda x: (x["date"], x["title"]))

# Save as formatted JSON
with open("cobra_tournaments.json", "w") as f:
    json.dump(tournaments, f, indent=2)

print(f"Saved {len(tournaments)} tournaments to cobra_tournaments.json")
