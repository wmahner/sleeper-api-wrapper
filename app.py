from sleeper_wrapper import League, Players
import pandas as pd

LEAGUE_ID = "1207447597271232512"
WEEK = 10
SCORING = "pts_ppr"

league = League(LEAGUE_ID)
players_api = Players()

rosters   = league.get_rosters()
users     = league.get_users()
matchups  = league.get_matchups(WEEK)
all_players = players_api.get_all_players()

owner_to_team = {}
for u in users:
    uid = u["user_id"]
    raw = u.get("metadata", {}).get("team_name")
    if not raw or not raw.strip():
        raw = u.get("display_name") or u.get("username")
    owner_to_team[uid] = raw.strip()               # <-- STRIP

roster_to_team = {}
for r in rosters:
    rid = r["roster_id"]
    oid = r["owner_id"]
    roster_to_team[rid] = owner_to_team.get(oid, f"Team_{rid}")

lineup_rows = []
player_scores = {}
for m in matchups:
    rid = m["roster_id"]
    for pid, pts in m.get("players_points", {}).items():
        player_scores[(rid, pid)] = pts

for r in rosters:
    rid = r["roster_id"]
    team = roster_to_team[rid]
    starters = set(r.get("starters", []))
    for pid in r.get("players", []):
        p = all_players.get(pid, {})
        lineup_rows.append({
            "week": WEEK,
            "team_name": team,
            "player_name": p.get("full_name", pid),
            "position": p.get("position", "??"),
            "slot": "Starter" if pid in starters else "Bench",
            SCORING: player_scores.get((rid, pid), 0.0)
        })

df_lineups = pd.DataFrame(lineup_rows)
df_lineups = df_lineups.sort_values(["team_name", "slot", SCORING], ascending=[True, True, False])
df_lineups.to_csv("lineups_ppr_week10.csv", index=False)


scoreboard_rows = []
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

    scoreboard_rows.append({
        "week": WEEK,
        "team_name": team,
        "score": score,
        "opponent": opp_team,
        "opp_score": opp_score,
        "win": score > opp_score
    })

df_scoreboard = pd.DataFrame(scoreboard_rows)
df_scoreboard.to_csv("scoreboard_week10.csv", index=False)


standings_raw = league.get_standings(rosters, users)
stand_rows = []
for rank, (raw, w, l, pf) in enumerate(standings_raw, 1):
    clean = raw.strip()                                   # <-- STRIP
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

all_teams = set(df_lineups["team_name"]).union(df_scoreboard["team_name"]).union(df_standings["team_name"])
print("Teams (no spaces):", sorted(all_teams))
print("MATCHED?", len(all_teams) == len(df_standings))