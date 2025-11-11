from sleeper_wrapper import League

# Replace with your actual league ID
league_id = '378845311639904256'

league = League(league_id)
rosters = league.get_rosters()

print(f"Found {len(rosters)} rosters in league {league_id}:\n")
for roster in rosters:
    print(f"Roster ID: {roster['roster_id']}, Owner ID: {roster['owner_id']}")
