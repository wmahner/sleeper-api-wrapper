from sleeper_wrapper import League
import requests

league_id = '1207447597271232512'
league = League(league_id)

try:
    rosters = league.get_rosters()
    print(f"Found {len(rosters)} rosters:")
    for roster in rosters:
        print(f"Roster ID: {roster['roster_id']}, Owner ID: {roster['owner_id']}")
except requests.exceptions.HTTPError as err:
    print(f"HTTP error occurred: {err}")
except Exception as e:
    print(f"Unexpected error: {e}")
