from sleeper_wrapper import League

# Configuration
league_id = 'YOUR_LEAGUE_ID'  # Replace with your actual Sleeper league ID
week = 10

# Initialize Sleeper API
league = League(league_id)

# Fetch league data
rosters = league.get_rosters()
users = league.get_users()
matchups = league.get_matchups(week)

# Build lookup maps
owner_map = {user['user_id']: user['display_name'] for user in users}
roster_map = {r['roster_id']: r for r in rosters}

# Group matchups by matchup_id
matchup_groups = {}
for m in matchups:
    matchup_groups.setdefault(m['matchup_id'], []).append(m)

# Track team scores and records
team_scores = []
team_records = {}

# Track awards
awards = {
    "high_score": ("", 0),
    "low_score": ("", float('inf')),
    "closest_win": ("", float('inf')),
    "best_team": ("", 0),
    "worst_team": ("", float('inf'))
}

print(f"\n📋 Week {week} League Summary:\n")

for roster in rosters:
    owner_id = roster['owner_id']
    team_name = owner_map.get(owner_id, f"Unknown Team ({owner_id})")
    settings = roster.get('settings', {})

    wins = settings.get('wins', 0)
    losses = settings.get('losses', 0)
    ties = settings.get('ties', 0)
    streak = settings.get('streak', 0)
    streak_type = "W" if settings.get('streak_type') == "win" else "L"
    streak_display = f"{streak_type}{streak}"
    total_points = settings.get('fpts', 0) + settings.get('fpts_decimal', 0)

    team_records[owner_id] = {
        "name": team_name,
        "wins": wins,
        "losses": losses,
        "ties": ties,
        "points": total_points
    }

    print(f"🏈 Team: {team_name}")
    print(f"   Record: {wins}-{losses}-{ties} | Streak: {streak_display}")
    print(f"   Total Points (Season): {total_points:.2f}\n")

    # Track best/worst team by wins
    if wins > awards["best_team"][1]:
        awards["best_team"] = (team_name, wins)
    if wins < awards["worst_team"][1]:
        awards["worst_team"] = (team_name, wins)

# Matchup scores and awards
for group in matchup_groups.values():
    if len(group) != 2:
        continue
    team1, team2 = group
    score1 = team1['points']
    score2 = team2['points']
    name1 = owner_map.get(roster_map[team1['roster_id']]['owner_id'], "Unknown")
    name2 = owner_map.get(roster_map[team2['roster_id']]['owner_id'], "Unknown")

    print(f"⚔️ Matchup: {name1} ({score1:.2f}) vs {name2} ({score2:.2f})")

    # Track scores
    team_scores.append((name1, score1))
    team_scores.append((name2, score2))

    # High/Low Score
    if score1 > awards["high_score"][1]:
        awards["high_score"] = (name1, score1)
    if score2 > awards["high_score"][1]:
        awards["high_score"] = (name2, score2)
    if score1 < awards["low_score"][1]:
        awards["low_score"] = (name1, score1)
    if score2 < awards["low_score"][1]:
        awards["low_score"] = (name2, score2)

    # Closest Win
    diff = abs(score1 - score2)
    if diff < awards["closest_win"][1]:
        winner = name1 if score1 > score2 else name2
        awards["closest_win"] = (winner, diff)

# Print awards
print(f"\n🏆 Week {week} Awards:")
print(f"🥇 High Score: {awards['high_score'][0]} with {awards['high_score'][1]:.2f} pts")
print(f"🥄 Low Score: {awards['low_score'][0]} with {awards['low_score'][1]:.2f} pts")
print(f"⚔️ Closest Win: {awards['closest_win'][0]} won by {awards['closest_win'][1]:.2f} pts")
print(f"🏆 Best Team: {awards['best_team'][0]} with {awards['best_team'][1]} wins")
print(f"💀 Worst Team: {awards['worst_team'][0]} with {awards['worst_team'][1]} wins")

# Playoff standings
print("\n📈 Playoff Standings:")
ranked = sorted(team_records.values(), key=lambda x: (-x['wins'], -x['points']))
for i, team in enumerate(ranked, start=1):
    print(f"{i}. {team['name']} — Record: {team['wins']}-{team['losses']}-{team['ties']}, Total Points: {team['points']:.2f}")








