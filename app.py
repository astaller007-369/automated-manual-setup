import os
import math
import numpy as np
import pandas as pd
import streamlit as st
import main_engine as engine

st.set_page_config(page_title="Sisonke Bet Predictions", page_icon="⚽", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; color: #f1f5f9; }
    h1 { color: #facc15; font-weight: 900 !important; font-size: 42px !important; margin: 0; padding-bottom: 5px; }
    h3 { color: #facc15; font-weight: 700 !important; margin-top: 25px !important; border-bottom: 1px solid #1e293b; padding-bottom: 5px; }
    .metric-card { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 20px; border-radius: 12px; border: 1px solid #334155; text-align: center; }
    .metric-title { font-size: 13px; font-weight: 600; text-transform: uppercase; color:#94a3b8; }
    .metric-value { font-size: 28px; font-weight: 800; line-height: 1; margin-top: 5px; }
    .market-header { color: #38bdf8; font-weight: 700; font-size: 15px; text-transform: uppercase; border-bottom: 2px solid #0284c7; margin-bottom: 12px; }
    .ticket-box { background-color: #1e293b; border: 2px dashed #facc15; border-radius: 8px; padding: 15px; color: #f8fafc; font-family: monospace; }
    </style>
""", unsafe_allow_html=True)

st.write("<h1>Sis⚽nke Bet Predictions</h1>", unsafe_allow_html=True)
st.caption("Master Manual CSV Engine - Multi-League Bivariate Poisson Framework")

with st.sidebar:
    st.markdown("### 📂 Data Control Room")
    uploaded_file = st.file_uploader("Upload Master Match CSV", type=["csv"])
    
    st.markdown("---")
    st.markdown("### 🔍 Dataset Diagnostic Tool")
    
    REQUIRED_COLUMNS = [
        "league_country", "match_timestamp", "home_team", "away_team", 
        "home_goals", "away_goals", "home_shots", "away_shots", 
        "home_sot", "away_sot", "home_big_chances", "home_big_chances_missed",
        "home_counterattacks", "home_cross_attack_goals"
    ]
    
    is_valid_data = False
    uploaded_leagues = []
    
    if uploaded_file is not None:
        try:
            sample_df = pd.read_csv(uploaded_file, nrows=5)
            uploaded_cols = list(sample_df.columns)
            missing_cols = [col for col in REQUIRED_COLUMNS if col not in uploaded_cols]
            
            if len(missing_cols) == 0:
                st.success("✅ MASTER SCHEMA VALID")
                is_valid_data = True
                full_scan = pd.read_csv(uploaded_file, usecols=["league_country"])
                uploaded_leagues = sorted(list(full_scan["league_country"].dropna().unique()))
            else:
                st.error("❌ MISSING HEADERS")
                for missing in missing_cols: st.code(f"⚠️ {missing}")
        except Exception as e:
            st.error(f"Error: {e}")

    if not is_valid_data or uploaded_file is None:
        st.info("👋 Upload your master data CSV file in the sidebar to activate the systems.")
        st.stop()

    st.markdown("---")
    st.markdown("### 🌍 Global Target Filter")
    selected_league_filter = st.selectbox("Select Target Country:", uploaded_leagues)
    
    st.markdown("---")
    st.markdown("### ⚙️ Volatility Control")
    vol_dampener = st.slider("Volatility Dampener (Smooth)", 0.5, 1.5, 1.0, 0.05)

raw_master_df = pd.read_csv(uploaded_file)
raw_master_df["match_timestamp"] = pd.to_datetime(raw_master_df["match_timestamp"])
filtered_df = raw_master_df[raw_master_df["league_country"] == selected_league_filter].reset_index(drop=True)

if filtered_df.empty:
    st.warning(f"No records match: '{selected_league_filter}'")
    st.stop()
total_records = len(filtered_df)
m_cols = st.columns(3)

m_cols[0].markdown(f'<div class="metric-card"><p class="metric-title">{selected_league_filter.upper()} Rows</p><p class="metric-value">{total_records}</p></div>', unsafe_allow_html=True)
m_cols[1].markdown(f'<div class="metric-card"><p class="metric-title">Avg Home Goals</p><p class="metric-value">{filtered_df["home_goals"].mean():.2f}</p></div>', unsafe_allow_html=True)
m_cols[2].markdown(f'<div class="metric-card"><p class="metric-title">Avg Away Goals</p><p class="metric-value">{filtered_df["away_goals"].mean():.2f}</p></div>', unsafe_allow_html=True)

tab_pred, tab_tables, tab_history, tab_live = st.tabs(["📅 FUTURE PROJECTIONS", "🌍 LEAGUE TABLES", "📜 ARCHIVE LEDGER", "🔴 LIVE CENTRE"])

with tab_live:
    st.info("Live data pipelines paused. System running on filtered master batch CSV processing matrices.")

with tab_tables:
    st.markdown(f"### Dynamic Standings Matrix: {selected_league_filter.upper()}")
    league_table_df = engine.generate_dynamic_league_table(filtered_df)
    st.dataframe(league_table_df, use_container_width=True)

with tab_history:
    st.markdown("### 📜 Automated Backtest Ledger & Performance Audit")
    if "predicted_outcome" in filtered_df.columns and "closing_bookie_odds" in filtered_df.columns:
        settled_df = filtered_df.dropna(subset=["home_goals", "away_goals", "predicted_outcome"]).copy()
        
        def check_bet_result(row):
            hg, ag = int(row["home_goals"]), int(row["away_goals"])
            actual = "HOME" if hg > ag else ("AWAY" if ag > hg else "DRAW")
            return 1.0 if row["predicted_outcome"] == actual else 0.0
            
        settled_df["bet_won"] = settled_df.apply(check_bet_result, axis=1)
        settled_df["stake"] = 100.0  
        settled_df["payout"] = settled_df["bet_won"] * settled_df["stake"] * settled_df["closing_bookie_odds"]
        settled_df["net_profit"] = settled_df["payout"] - settled_df["stake"]
        
        total_bets = len(settled_df)
        winning_bets = int(settled_df["bet_won"].sum())
        strike_rate = (winning_bets / total_bets * 100) if total_bets > 0 else 0.0
        total_investment = settled_df["stake"].sum()
        total_net_return = settled_df["net_profit"].sum()
        roi = (total_net_return / total_investment * 100) if total_investment > 0 else 0.0
        
        ac1, ac2, ac3, ac4 = st.columns(4)
        ac1.markdown(f'<div class="metric-card"><p class="metric-title">Settled Picks</p><p class="metric-value">{total_bets}</p></div>', unsafe_allow_html=True)
        ac2.markdown(f'<div class="metric-card"><p class="metric-title">Strike Rate</p><p class="metric-value">{strike_rate:.1f}%</p></div>', unsafe_allow_html=True)
        
        profit_color = "#10b981" if total_net_return >= 0 else "#ef4444"
        ac3.markdown(f'<div class="metric-card"><p class="metric-title" style="color:{profit_color};">Net Return</p><p class="metric-value" style="color:{profit_color};">{total_net_return:+.2f}u</p></div>', unsafe_allow_html=True)
        ac4.markdown(f'<div class="metric-card"><p class="metric-title" style="color:{profit_color};">ROI</p><p class="metric-value" style="color:{profit_color};">{roi:+.1f}%</p></div>', unsafe_allow_html=True)
        
        st.markdown("#### Detailed Settle Ledger Summary")
        ledger_view = settled_df[["match_timestamp", "home_team", "away_team", "home_goals", "away_goals", "predicted_outcome", "closing_bookie_odds", "net_profit"]].copy()
        st.dataframe(ledger_view.style.format({"closing_bookie_odds": "{:.2f}", "net_profit": "{:+.2f}u"}), use_container_width=True)
    else:
        st.warning("To activate the Archive Ledger audit dashboard, add 'predicted_outcome' (HOME/DRAW/AWAY) and 'closing_bookie_odds' columns to your CSV sheet.")

with tab_pred:
    st.dataframe(filtered_df, use_container_width=True)
    st.markdown("### 🔍 Advanced Match Drill-Down Lab")
    options = {f"[{selected_league_filter.upper()}] {r['home_team']} vs {r['away_team']}": r for idx, r in filtered_df.iterrows()}
    sel_match = st.selectbox("Select Target Profile:", list(options.keys()))
    
    if sel_match:
        target = options[sel_match]
        h_stats = engine.parse_live_team_data(filtered_df, target["home_team"], target["match_timestamp"])
        a_stats = engine.parse_live_team_data(filtered_df, target["away_team"], target["match_timestamp"])
        h_q, h_res = engine.calculate_advanced_metrics(h_stats)
        a_q, a_res = engine.calculate_advanced_metrics(a_stats)
        
        base_goals = engine.COMPETITION_MATRIX.get(selected_league_filter, {"baseline_goals": 2.50})["baseline_goals"]
        fixed_hga, away_psy_subtraction = 1.10, 0.97
        
        st.markdown("**📋 Live Situational Calibrations:**")
        sc1, sc2 = st.columns(2)
        with sc1:
            st.markdown("#### 🏠 Home Adjustments")
            h_inj = st.slider("Home Availability", 0.5, 1.0, 1.0, 0.05, key="hi", help="GUIDE: Scales down the attack proxy when crucial goalscorers are injured.")
            h_mot = st.slider("Home Motivation Index", 0.8, 1.2, 1.0, 0.05, key="hm", help="GUIDE: Increases target expectancy for high-stakes matches.")
            h_rest_days = st.slider("Home Recovery Window (Days)", 1, 14, 5, step=1, key="hr", help="GUIDE: Dictates rest curve multipliers to simulate physical degradation.")
        with sc2:
            st.markdown("#### 🚀 Away Adjustments")
            a_inj = st.slider("Away Availability", 0.5, 1.0, 1.0, 0.05, key="ai", help="GUIDE: Penalizes the away team's scoring projection depending on injury lengths.")
            a_mot = st.slider("Away Motivation Index", 0.8, 1.2, 1.0, 0.05, key="am", help="GUIDE: Scales target urgency settings based on team motivation disparities.")
            a_rest_days = st.slider("Away Recovery Window (Days)", 1, 14, 5, step=1, key="ar", help="GUIDE: Dictates recovery curve parameters.")
            
            distance_tier = st.select_slider(
                "Away Journey Travel Disadvantage Penalty",
                options=["Short (No Penalty)", "Moderate (-1%)", "Long (-2%)", "Continental (-4%)"],
                value="Short (No Penalty)",
                help="GUIDE: Subtracts structural efficiency weights from away side parameters based on flight/travel durations."
            )
            distance_map = {"Short (No Penalty)": 1.00, "Moderate (-1%)": 0.99, "Long (-2%)": 0.98, "Continental (-4%)": 0.96}
            dynamic_distance_penalty = distance_map[distance_tier]
            
        h_rest_mult = engine.calculate_rest_multiplier(h_rest_days)
        a_rest_mult = engine.calculate_rest_multiplier(a_rest_days)
            
        h_exp = max(0.1, (base_goals / 2) * (h_stats["goals"] / max(0.1, a_stats["goals_conceded"])) * fixed_hga * h_inj * h_mot * h_rest_mult * h_q * (2.0 - a_res) * vol_dampener)
        a_exp = max(0.1, (base_goals / 2) * (a_stats["goals"] / max(0.1, h_stats["goals_conceded"])) * (2.0 - fixed_hga) * away_psy_subtraction * dynamic_distance_penalty * a_inj * a_mot * a_rest_mult * a_q * (2.0 - h_res) * vol_dampener)
        
        sample_density = min(h_stats["games_played"], a_stats["games_played"])
        confidence_score = min(100, int((sample_density / 5.0) * 100)) if sample_density > 0 else 20
        
        goals_axis = np.arange(0, 6)
        prob_home, prob_away = 0.0, 0.0
        for h in goals_axis:
            for a in goals_axis:
                p = engine.calculate_bivariate_poisson_probability(h_exp, a_exp, 0.10, h, a)
                if h > a: prob_home += p
                elif a > h: prob_away += p
        prob_draw = max(0.02, 1.0 - (prob_home + prob_away))
        
        c_left, c_right = st.columns(2)
        with c_left:
            st.markdown('<div class="market-header">Calculated Probabilities Splits</div>', unsafe_allow_html=True)
            st.progress(max(0, min(100, int(prob_home * 100))), text=f"🏠 Home Win: {prob_home*100:.1f}% (Fair: {1/prob_home:.2f})")
            st.progress(max(0, min(100, int(prob_draw * 100))), text=f"🤝 Draw: {prob_draw*100:.1f}% (Fair: {1/prob_draw:.2f})")
            st.progress(max(0, min(100, int(prob_away * 100))), text=f"🚀 Away Win: {prob_away*100:.1f}% (Fair: {1/prob_away:.2f})")
            st.metric("Model Confidence Level", f"{confidence_score}%")
            
        with c_right:
            st.markdown('<div class="market-header">🎫 Calibrated Betting Ticket Slip</div>', unsafe_allow_html=True)
            ticket_txt = (
                f"========================================\n"
                f"        SISONKE BET ANALYTICS ENGINE    \n"
                f"========================================\n"
                f"Match    : {target['home_team']} vs {target['away_team']}\n"
                f"Region   : {selected_league_filter.upper()}\n"
                f"Confidence: {confidence_score}%\n"
                f"----------------------------------------\n"
                f"Calculated xG Expectations:\n"
                f"  🏠 Home Expected xG: {h_exp:.2f} (+10% Fixed HGA)\n"
                f"  🚀 Away Expected xG: {a_exp:.2f} (Subtracted -3% Psy | {distance_tier})\n"
                f"----------------------------------------\n"
                f"Advanced Model Quality Indicators:\n"
                f"  🏠 Home Attack (Shot Quality) / Def Res: {h_q:.2f} / {h_res:.2f}\n"
                f"  🚀 Away Attack (Shot Quality) / Def Res: {a_q:.2f} / {a_res:.2f}\n"
                f"========================================\n"
            )
            st.markdown(f'<div class="ticket-box"><pre>{ticket_txt}</pre></div>', unsafe_allow_html=True)
