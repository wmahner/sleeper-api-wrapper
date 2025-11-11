from sleeper_wrapper import League, Players

# Replace with your actual league ID
league_id = '1207447597271232512'

# Initialize League and Players
league = League(league_id)
players = Players()

# Get all rosters and users in the league
rosters = league.get_rosters()
users = league.get_users()
player_dict = players.get_all_players()

# Create a mapping from owner_id to display_name
owner_map = {user['user_id']: user['display_name'] for user in users}

print(f"\n📋 Found {len(rosters)} rosters in league {league_id}:\n")

for roster in rosters:
    owner_id = roster['owner_id']
    team_name = owner_map.get(owner_id, f"Unknown Team ({owner_id})")
    roster_id = roster['roster_id']
    player_ids = roster.get('players', [])

    # Convert player IDs to names
    player_names = []
    for pid in player_ids:
        player_info = player_dict.get(pid)
        if player_info:
            name = player_info.get('full_name') or f"{player_info.get('first_name', '')} {player_info.get('last_name', '')}".strip()
            player_names.append(name)
        else:
            player_names.append(f"Unknown Player ({pid})")
for name in player_names:
    stats = fantasy_stats.get(name)
    if stats:
        print(f"     - {name} | PPR Avg: {stats['avg_points']} | Pos Rank: {stats['pos_rank']}")


    print(f"🏈 Team: {team_name} | Roster ID: {roster_id}")
    print(f"   Players: {', '.join(player_names) if player_names else 'No players listed'}\n")
def get_fantasypros_stats():
    url = "http://localhost:8000/players?scoring=PPR"
    response = requests.get(url)
    return {p['name']: p for p in response.json()}

fantasy_stats = get_fantasypros_stats()


