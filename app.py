from sleeper_wrapper import League, Players
import requests

league_id = '1207447597271232512'
week = 10

league = League(league_id)
players = Players()

# Fetch league data
rosters = league.get_rosters()
users = league.get_users()
matchups = league.get_matchups(week)
player_dict = players.get_all_players()

owner_map = {user['user_id']: user['display_name'] for user in users}
roster_map = {r['roster_id']: r for r in rosters}

# Group matchups by matchup_id
matchup_groups = {}
for m in matchups:
    matchup_groups.setdefault(m['matchup_id'], []).append(m)

# Track awards
awards = {
    "high_score": ("", 0),
    "low_score": ("", float('inf')),
    "closest_win": ("", float('inf')),
    "bench_blunder": ("", 0),
    "hot_hand": ("", "", 0),
    "best_bench": ("", 0),
    "worst_bench": ("", float('inf')),
    "worst_overall": ("", float('inf'))
}

print(f"\n📋 Week {week} League Summary:\n")

for roster in rosters:
    owner_id = roster['owner_id']
    team_name = owner_map.get(owner_id, f"Unknown Team ({owner_id})")
    starters = set(roster.get('starters', []))
    all_players = roster.get('players', [])
    settings = roster.get('settings', {})
    wins = settings.get('wins', 0)
    losses = settings.get('losses', 0)
    ties = settings.get('ties', 0)
    streak = settings.get('streak', 0)
    streak_type = "W" if settings.get('streak_type') == "win" else "L"
    streak_display = f"{streak_type}{streak}"

    print(f"🏈 Team: {team_name}")
    print(f"   Record: {wins}-{losses}-{ties} | Streak: {streak_display}")
    print("   Roster:")

    best_player = ("", 0)
    worst_player = ("", float('inf'))
    starter_points = 0
    bench_points = 0

    for pid in all_players:
        player_info = player_dict.get(pid)
        name = player_info.get('full_name', f"Unknown ({pid})")
        stats = league.get_player_stats(pid, week)
        ppr = stats.get('pts_ppr', 0)
        is_starter = "Starter" if pid in starters else "Bench"
        print(f"     - {name} ({is_starter}) | PPR: {ppr}")

        if is_starter:
            starter_points += ppr
        else:
            bench_points += ppr

        if ppr > best_player[1]:
            best_player = (name, ppr)
        if ppr < worst_player[1]:
            worst_player = (name, ppr)

    total_points = starter_points + bench_points
    print(f"   Best Player: {best_player[0]} ({best_player[1]} pts)")
    print(f"   Worst Player: {worst_player[0]} ({worst_player[1]} pts)")
    print(f"   Week {week} Starter Points: {starter_points:.2f}")
    print(f"   Week {week} Bench Points: {bench_points:.2f}")
    print(f"   Total Points: {total_points:.2f}\n")

    # Update awards
    if starter_points > awards["high_score"][1]:
        awards["high_score"] = (team_name, starter_points)
    if starter_points < awards["low_score"][1]:
        awards["low_score"] = (team_name, starter_points)
    if bench_points > awards["best_bench"][1]:
        awards["best_bench"] = (team_name, bench_points)
    if bench_points < awards["worst_bench"][1]:
        awards["worst_bench"] = (team_name, bench_points)
    if total_points < awards["worst_overall"][1]:
        awards["worst_overall"] = (team_name, total_points)
    if best_player[1] > awards["hot_hand"][2]:
        awards["hot_hand"] = (team_name, best_player[0], best_player[1])

# Matchup-based awards
for group in matchup_groups.values():
    if len(group) != 2:
        continue
    team1, team2 = group
    score1 = team1['points']
    score2 = team2['points']
    name1 = owner_map.get(roster_map[team1['roster_id']]['owner_id'], "Unknown")
    name2 = owner_map.get(roster_map[team2['roster_id']]['owner_id'], "Unknown")

    print(f"⚔️ Matchup: {name1} ({score1:.2f}) vs {name2} ({score2:.2f})")

    diff = abs(score1 - score2)
    if diff < awards["closest_win"][1]:
        winner = name1 if score1 > score2 else name2
        awards["closest_win"] = (winner, diff)

    # Bench blunder
    for team in [team1, team2]:
        starters = set(team['starters'])
        all_players = team['players']
        bench = [p for p in all_players if p not in starters]
        bench_points = sum([league.get_player_stats(p, week).get('pts_ppr', 0) for p in bench])
        name = owner_map.get(roster_map[team['roster_id']]['owner_id'], "Unknown")
        if bench_points > awards["bench_blunder"][1]:
            awards["bench_blunder"] = (name, bench_points)

# Print awards
print(f"\n🏆 Week {week} Awards:")
print(f"🥇 High Score: {awards['high_score'][0]} with {awards['high_score'][1]:.2f} pts")
print(f"🥄 Low Score: {awards['low_score'][0]} with {awards['low_score'][1]:.2f} pts")
print(f"⚔️ Closest Win: {awards['closest_win'][0]} won by {awards['closest_win'][1]:.2f} pts")
print(f"🛋️ Bench Blunder: {awards['bench_blunder'][0]} left {awards['bench_blunder'][1]:.2f} pts on the bench")
print(f"🔥 Hot Hand: {awards['hot_hand'][1]} from {awards['hot_hand'][0]} scored {awards['hot_hand'][2]:.2f} pts")
print(f"🧠 Best Bench: {awards['best_bench'][0]} with {awards['best_bench'][1]:.2f} pts")
print(f"😴 Worst Bench: {awards['worst_bench'][0]} with {awards['worst_bench'][1]:.2f} pts")
print(f"💀 Worst Overall: {awards['worst_overall'][0]} with {awards['worst_overall'][1]:.2f} total pts")




