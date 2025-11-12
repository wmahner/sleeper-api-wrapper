from sleeper_wrapper import League

# Configuration
league_id = '1207447597271232512'
league = League(league_id)

# Fetch static league data
rosters = league.get_rosters()
users = league.get_users()

# Build lookup maps
owner_map = {
    user['user_id']: user.get('metadata', {}).get('team_name') or user.get('display_name') or user.get('username', f"User {user['user_id']}")
    for user in users
}
roster_map = {r['roster_id']: r for r in rosters}

# Track cumulative records
team_records = {r['owner_id']: {"name": owner_map.get(r['owner_id'], "Unknown"), "wins": 0, "losses": 0, "ties": 0, "points": 0} for r in rosters}

print("\n📋 League Summary Weeks 1–10:\n")

for week in range(1, 11):
    print(f"\n🗓️ Week {week}:\n")
    matchups = league.get_matchups(week)

    # Group matchups
    matchup_groups = {}
    for m in matchups:
        matchup_groups.setdefault(m['matchup_id'], []).append(m)

    # Awards
    awards = {
        "high_score": ("", 0),
        "low_score": ("", float('inf')),
        "closest_win": ("", float('inf'))
    }

    # Matchup awards
    for group in matchup_groups.values():
        if len(group) != 2:
            continue
        team1, team2 = group
        score1 = team1['points']
        score2 = team2['points']
        rid1 = team1['roster_id']
        rid2 = team2['roster_id']
        owner1 = roster_map[rid1]['owner_id']
        owner2 = roster_map[rid2]['owner_id']
        name1 = team_records[owner1]['name']
        name2 = team_records[owner2]['name']

        print(f"⚔️ Matchup: {name1} ({score1:.2f}) vs {name2} ({score2:.2f})")

        # Update points
        team_records[owner1]['points'] += score1
        team_records[owner2]['points'] += score2

        # Update wins/losses/ties
        if score1 > score2:
            team_records[owner1]['wins'] += 1
            team_records[owner2]['losses'] += 1
        elif score2 > score1:
            team_records[owner2]['wins'] += 1
            team_records[owner1]['losses'] += 1
        else:
            team_records[owner1]['ties'] += 1
            team_records[owner2]['ties'] += 1

        # Awards
        if score1 > awards["high_score"][1]:
            awards["high_score"] = (name1, score1)
        if score2 > awards["high_score"][1]:
            awards["high_score"] = (name2, score2)
        if score1 < awards["low_score"][1]:
            awards["low_score"] = (name1, score1)
        if score2 < awards["low_score"][1]:
            awards["low_score"] = (name2, score2)

        diff = abs(score1 - score2)
        if diff < awards["closest_win"][1]:
            winner = name1 if score1 > score2 else name2
            awards["closest_win"] = (winner, diff)

    # Print awards
    print(f"\n🏆 Week {week} Awards:")
    print(f"🥇 High Score: {awards['high_score'][0]} with {awards['high_score'][1]:.2f} pts")
    print(f"🥄 Low Score: {awards['low_score'][0]} with {awards['low_score'][1]:.2f} pts")
    print(f"⚔️ Closest Win: {awards['closest_win'][0]} won by {awards['closest_win'][1]:.2f} pts")

# Final standings
print("\n📈 Current Standings (Weeks 1–10):")
ranked = sorted(team_records.values(), key=lambda x: (-x['wins'], -x['points']))
for i, team in enumerate(ranked, start=1):
    print(f"{i}. {team['name']} — Record: {team['wins']}-{team['losses']}-{team['ties']}, Total Points: {team['points']:.2f}")

