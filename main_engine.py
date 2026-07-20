import os
import sys
import json
import math
import numpy as np
import pandas as pd

COMPETITION_MATRIX = {
    "england": {"tier_1": "Premier League", "baseline_goals": 2.84, "tier_2": "Championship", "tier_2_baseline_goals": 2.68, "cups": ["FA Cup", "EFL Cup"]},
    "spain": {"tier_1": "La Liga", "baseline_goals": 2.55, "tier_2": "Segunda División", "tier_2_baseline_goals": 2.42, "cups": ["Copa del Rey", "Supercopa de España"]},
    "france": {"tier_1": "Ligue 1", "baseline_goals": 2.60, "tier_2": "Ligue 2", "tier_2_baseline_goals": 2.38, "cups": ["Coupe de France", "Trophée des Champions"]},
    "germany": {"tier_1": "Bundesliga", "baseline_goals": 3.18, "tier_2": "2. Bundesliga", "tier_2_baseline_goals": 3.02, "cups": ["DFB-Pokal", "DFL-Supercup"]},
    "italy": {"tier_1": "Serie A", "baseline_goals": 2.58, "tier_2": "Serie B", "tier_2_baseline_goals": 2.46, "cups": ["Coppa Italia", "Supercoppa Italiana"]},
    "iran": {"tier_1": "Persian Gulf Pro League", "baseline_goals": 2.10, "cups": ["Hazfi Cup"]},
    "south_africa": {"tier_1": "Premier Soccer League", "baseline_goals": 2.20, "cups": ["Nedbank Cup", "Carling Knockout Cup", "MTN 8"]},
    "morocco": {"tier_1": "Botola Pro", "baseline_goals": 2.15, "cups": ["Moroccan Throne Cup"]},
    "tunisia": {"tier_1": "Tunisian Ligue Professionnelle 1", "baseline_goals": 1.95, "cups": ["Tunisian Cup"]},
    "china": {"tier_1": "Chinese Super League", "baseline_goals": 2.65, "cups": ["Chinese FA Cup", "Chinese FA Super Cup"]},
    "portugal": {"tier_1": "Primeira Liga", "baseline_goals": 2.70, "cups": ["Taça de Portugal", "Taça da Liga"]},
    "scotland": {"tier_1": "Scottish Premiership", "baseline_goals": 2.80, "cups": ["Scottish Cup", "Scottish League Cup"]},
    "greek": {"tier_1": "Super League Greece", "baseline_goals": 2.50, "cups": ["Greek Football Cup"]},
    "south_korea": {"tier_1": "K League 1", "baseline_goals": 2.55, "cups": ["Korean FA Cup"]},
    "iceland": {"tier_1": "Best deild karla", "baseline_goals": 3.20, "cups": ["Icelandic Cup", "Icelandic League Cup"]},
    "ireland": {"tier_1": "League of Ireland Premier Division", "baseline_goals": 2.50, "cups": ["FAI Cup", "President's Cup"]},
    "estonia": {"tier_1": "Meistriliiga", "baseline_goals": 3.00, "cups": ["Estonian Cup"]},
    "latvia": {"tier_1": "Virsliga", "baseline_goals": 2.85, "cups": ["Latvian Cup"]},
    "croatia": {"tier_1": "Croatian Football League", "baseline_goals": 2.60, "cups": ["Croatian Football Cup"]},
    "egypt": {"tier_1": "Egyptian Premier League", "baseline_goals": 2.30, "cups": ["Egypt Cup", "Egyptian Super Cup"]},
    "netherlands": {"tier_1": "Eredivisie", "baseline_goals": 3.10, "cups": ["KNVB Cup", "Johan Cruyff Shield"]},
    "serbia": {"tier_1": "Serbian SuperLiga", "baseline_goals": 2.60, "cups": ["Serbian Cup"]},
    "russia": {"tier_1": "Russian Premier League", "baseline_goals": 2.65, "cups": ["Russian Cup", "Russian Super Cup"]},
    "slovenia": {"tier_1": "Slovenian PrvaLiga", "baseline_goals": 2.70, "cups": ["Slovenian Cup"]},
    "uruguay": {"tier_1": "Uruguayan Primera División", "baseline_goals": 2.45, "cups": ["Copa Uruguay"]},
    "turkey": {"tier_1": "Süper Lig", "baseline_goals": 2.80, "cups": ["Turkish Cup", "Turkish Super Cup"]},
    "belgium": {"tier_1": "Belgian Pro League", "baseline_goals": 2.85, "cups": ["Belgian Cup", "Belgian Super Cup"]},
    "austria": {"tier_1": "Austrian Football Bundesliga", "baseline_goals": 2.90, "cups": ["Austrian Cup"]},
    "switzerland": {"tier_1": "Swiss Super League", "baseline_goals": 2.95, "cups": ["Swiss Cup"]},
    "czech": {"tier_1": "Czech First League", "baseline_goals": 2.75, "cups": ["Czech Cup"]},
    "denmark": {"tier_1": "Danish Superliga", "baseline_goals": 2.75, "cups": ["Danish Cup"]},
    "brazil": {"tier_1": "Campeonato Brasileiro Série A", "baseline_goals": 2.40, "cups": ["Copa do Brasil"]}
}

def calculate_time_decay_weight(days_ago, half_life_days=68):
    return math.exp(-0.69314718056 * (days_ago / half_life_days))

def calculate_rest_multiplier(days_rest):
    if days_rest <= 2: return 0.88
    elif days_rest == 3: return 0.94
    elif days_rest >= 4 and days_rest <= 6: return 1.00
    elif days_rest >= 7 and days_rest <= 10: return 1.04
    else: return 0.97
def parse_live_team_data(historical_matches, target_team, current_timestamp, half_life_days=68):
    if len(historical_matches) == 0:
        return {"goals": 1.2, "goals_conceded": 1.2, "shots": 12.0, "sot": 4.5, "shots_conceded": 12.0, "games_played": 1.0}
    
    total_weight = 0.0
    weighted_goals, weighted_conceded, weighted_shots, weighted_sot, weighted_shots_con = 0.0, 0.0, 0.0, 0.0, 0.0
    
    target_ts = pd.to_datetime(current_timestamp)
    sorted_matches = historical_matches.copy().sort_values(by="match_timestamp", ascending=False)
    
    for idx, match in sorted_matches.iterrows():
        match_ts = pd.to_datetime(match["match_timestamp"])
        if match_ts >= target_ts:
            continue
        days_ago = max(0, (target_ts - match_ts).days)
        weight = calculate_time_decay_weight(days_ago, half_life_days)
        
        is_home = match["home_team"] == target_team
        role_prefix, opp_prefix = ("home_", "away_") if is_home else ("away_", "home_")
        
        weighted_goals += match[f"{role_prefix}goals"] * weight
        weighted_shots += match[f"{role_prefix}shots"] * weight
        weighted_sot += match[f"{role_prefix}sot"] * weight
        weighted_conceded += match[f"{opp_prefix}goals"] * weight
        weighted_shots_con += match[f"{opp_prefix}shots"] * weight
        total_weight += weight

    div = max(0.01, total_weight)
    return {
        "goals": weighted_goals / div, "goals_conceded": weighted_conceded / div,
        "shots": weighted_shots / div, "sot": weighted_sot / div,
        "shots_conceded": weighted_shots_con / div, "games_played": float(div)
    }

def calculate_advanced_metrics(stats):
    shots = max(1.0, stats.get("shots", 12.0))
    sot = max(0.5, stats.get("sot", 4.5))
    goals = stats.get("goals", 1.2)
    gc = stats.get("goals_conceded", 1.2)
    s_con = max(1.0, stats.get("shots_conceded", 12.0))
    
    shot_quality = (goals * 0.4 + sot * 0.6) / shots
    def_resilience = 1.0 - ((gc * 0.4 + (s_con * 0.08)) / s_con)
    
    return max(0.05, shot_quality), max(0.05, def_resilience)

def generate_dynamic_league_table(df):
    table = {}
    def init_team(team):
        if team not in table:
            table[team] = {"P": 0, "W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0, "GD": 0, "PTS": 0}
            
    for idx, row in df.iterrows():
        h, a = row["home_team"], row["away_team"]
        hg, ag = int(row["home_goals"]), int(row["away_goals"])
        init_team(h)
        init_team(a)
        
        table[h]["P"] += 1
        table[a]["P"] += 1
        table[h]["GF"] += hg
        table[h]["GA"] += ag
        table[a]["GF"] += ag
        table[a]["GA"] += hg
        
        if hg > ag:
            table[h]["W"] += 1
            table[h]["PTS"] += 3
            table[a]["L"] += 1
        elif ag > hg:
            table[a]["W"] += 1
            table[a]["PTS"] += 3
            table[h]["L"] += 1
        else:
            table[h]["D"] += 1
            table[h]["PTS"] += 1
            table[a]["D"] += 1
            table[a]["PTS"] += 1

    for team in table:
        table[team]["GD"] = table[team]["GF"] - table[team]["GA"]
        
    table_df = pd.DataFrame.from_dict(table, orient='index').reset_index()
    table_df.rename(columns={"index": "Club Team"}, inplace=True)
    table_df = table_df.sort_values(by=["PTS", "GD", "GF"], ascending=False).reset_index(drop=True)
    table_df.index += 1
    table_df.index.name = "Pos"
    return table_df

def calculate_bivariate_poisson_probability(lam1, lam2, lam3, x, y):
    if lam1 <= 0 or lam2 <= 0:
        return 1.0 if (x == 0 and y == 0) else 0.0
    
    sum_prob = 0.0
    for k in range(min(x, y) + 1):
        num = (lam3 ** k) * (lam1 ** (x - k)) * (lam2 ** (y - k))
        den = math.factorial(k) * math.factorial(x - k) * math.factorial(y - k)
        sum_prob += num / den
        
    return math.exp(-(lam1 + lam2 + lam3)) * sum_prob
