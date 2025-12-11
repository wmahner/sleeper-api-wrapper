from sleeper_wrapper import League, Players
import pandas as pd

LEAGUE_ID = "1207447597271232512"
SCORING = "pts_ppr"
WEEK = 14   # <-- Only week 14

league = League(LEAGUE_ID)
players_api = Players()

rosters   = league.get_rosters()
users     = league.get_users()
all_players = players_api.get_all_players()

# Build owner → team name map
owner_to_team = {}
for u in users:
    uid = u["user_id"]
    raw = u.get("metadata", {}).get("team_name")
    if not raw or not raw.strip():
        raw = u.get("display_name") or u.get("username")
    owner_to_team[uid] = raw.strip()

roster_to_team = {r["roster_id"]: owner_to_team.get(r["owner_id"], f"Team_{r['roster_id']}") for r in rosters}

# Collect week 14 results
lineup_rows = []
scoreboard_rows = []
stand_rows = []

print("\n📋 League Summary Week 14:\n")

matchups = league.get_matchups(WEEK)

# Player scores per roster
player_scores = {}
for m in matchups:
    rid = m["roster_id"]
    for pid, pts in m.get("players_points", {}).items():
        player_scores[(rid, pid)] = pts

# Build lineups
for r in rosters:
    rid = r["roster_id"]
    team = roster_to_team[rid]
    starters = set(r.get("starters", []))
    for pid in r.get("players", []):
        p = all_players.get(pid, {})
        pts = player_scores.get((rid, pid), 0.0)
        slot = "Starter" if pid in starters else "Bench"
        lineup_rows.append({
            "week": WEEK,
            "team_name": team,
            "player_name": p.get("full_name", pid),
            "position": p.get("position", "??"),
            "slot": slot,
            SCORING: pts
        })

# Weekly awards
awards = {
    "high_score": ("", 0),
    "low_score": ("", float('inf')),
    "closest_win": ("", float('inf')),
    "best_team": ("", 0),
    "worst_team": ("", float('inf'))
}

# Build scoreboard and track awards
print(f"\n🗓️ Week {WEEK} Results:\n")
for m in matchups:
    rid = m["roster_id"]
    team = roster_to_team[rid]
    score = m.get("points", 0.0)
    opp_rid = next(
        (mm["roster_id"] for mm in matchups
         if mm["matchup_id"] == m["matchup_id"] and mm["roster_id"] != rid),
        None
    )
    opp_team = roster_to_team.get(opp_rid, "Bye")
    opp_score = next((mm.get("points", 0.0) for mm in matchups if mm["roster_id"] == opp_rid), 0.0)

    print(f"⚔️ {team} ({score:.2f}) vs {opp_team} ({opp_score:.2f})")

    scoreboard_rows.append({
        "week": WEEK,
        "team_name": team,
        "score": score,
        "opponent": opp_team,
        "opp_score": opp_score,
        "win": score > opp_score
    })

    # Awards
    if score > awards["high_score"][1]:
        awards["high_score"] = (team, score)
    if score < awards["low_score"][1]:
        awards["low_score"] = (team, score)
    if score > awards["best_team"][1]:
        awards["best_team"] = (team, score)
    if score < awards["worst_team"][1]:
        awards["worst_team"] = (team, score)

    diff = abs(score - opp_score)
    if diff < awards["closest_win"][1]:
        winner = team if score > opp_score else opp_team
        awards["closest_win"] = (winner, diff)

# Print weekly awards
print(f"\n🏆 Week {WEEK} Awards:")
print(f"🥇 High Score: {awards['high_score'][0]} with {awards['high_score'][1]:.2f} pts")
print(f"🥄 Low Score: {awards['low_score'][0]} with {awards['low_score'][1]:.2f} pts")
print(f"⚔️ Closest Win: {awards['closest_win'][0]} won by {awards['closest_win'][1]:.2f} pts")
print(f"🏆 Best Team: {awards['best_team'][0]} with {awards['best_team'][1]:.2f} pts")
print(f"💀 Worst Team: {awards['worst_team'][0]} with {awards['worst_team'][1]:.2f} pts")

# Export lineups and scoreboard for week 14
df_lineups = pd.DataFrame(lineup_rows)
df_lineups.to_csv("lineups_ppr_week14.csv", index=False)

df_scoreboard = pd.DataFrame(scoreboard_rows)
df_scoreboard.to_csv("scoreboard_week14.csv", index=False)

# Standings
standings_raw = league.get_standings(rosters, users)
for rank, (raw, w, l, pf) in enumerate(standings_raw, 1):
    clean = raw.strip()
    owner_id = next((oid for oid, t in owner_to_team.items() if t == clean), None)
    team = owner_to_team.get(owner_id, clean) if owner_id else clean
    stand_rows.append({
        "rank": rank,
        "team_name": team,
        "record": f"{w}-{l}",
        "pf": float(pf)
    })

df_standings = pd.DataFrame(stand_rows)
df_standings.to_csv("standings.csv", index=False)

print("\n📈 Final Standings exported to standings.csv")







