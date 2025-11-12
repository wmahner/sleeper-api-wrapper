from sleeper_wrapper import League

# Configuration
league_id = '1207447597271232512'
league = League(league_id)

# Fetch static league data
rosters = league.get_rosters()
users = league.get_users()

# Build lookup maps
owner_map = {
    user['user_id']: user.get('display_name') or user.get('metadata', {}).get('team_name') or user.get('username', f"User {user['user_id']}")
    for user in users
}
roster_map = {r['roster_id']: r for r in rosters}

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

    for roster in rosters:
        owner_id = roster['owner_id']
        team_name = owner_map.get(owner_id, f"Unknown Team ({owner_id})")
        print(f"🏈 Team: {team_name}")

    # Matchup awards
    for group in matchup_groups.values():
        if len(group) != 2:
            continue
        team1, team2 = group
        score1 = team1['points']
        score2 = team2['points']
        name1 = owner_map.get(roster_map[team1['roster_id']]['owner_id'], "Unknown")
        name2 = owner_map.get(roster_map[team2['roster_id']]['owner_id'], "Unknown")

        print(f"⚔️ Matchup: {name1} ({score1:.2f}) vs {name2} ({score2:.2f})")

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

