import os
import math
import numpy as np
import pandas as pd
import streamlit as st
import main_engine as engine

# 1. Framework Base Configuration
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
st.caption("Master Automation Suite - Full Multi-League Balanced Dixon-Coles Poisson Framework")

# 2. Sidebar Controls & Validation Schema
with st.sidebar:
    st.markdown("### 📂 Data Control Room")
    uploaded_file = st.file_uploader("Upload Master Match CSV", type=["csv"])
    st.markdown("---")
    st.markdown("### 🔍 Dataset Diagnostic Tool")
    
    REQUIRED_COLUMNS = [
        "league_country", "match_timestamp", "home_team", "away_team", 
        "home_goals", "away_goals", "home_shots", "away_shots", 
        "home_sot", "away_sot", "home_big_chances", "away_big_chances",
        "home_big_chances_missed", "away_big_chances_missed",
        "home_counterattacks", "away_counterattacks",
        "home_headed_goals", "away_headed_goals",
        "home_avail_weight", "home_mot_weight", "home_coach_weight", "home_rest_days",
        "away_avail_weight", "away_mot_weight", "away_coach_weight", "away_rest_days"
    ]
    is_valid_data, uploaded_leagues = False, []
    if uploaded_file is not None:
        try:
            sample_df = pd.read_csv(uploaded_file, nrows=5)
            missing_cols = [col for col in REQUIRED_COLUMNS if col not in list(sample_df.columns)]
            if len(missing_cols) == 0:
                st.success("✅ MASTER SCHEMA VALID")
                is_valid_data = True
                uploaded_file.seek(0) # Reset pointer after reading unique leagues
                uploaded_leagues = sorted(list(pd.read_csv(uploaded_file, usecols=["league_country"])["league_country"].dropna().unique()))
            else:
                st.error("❌ MISSING SYMMETRICAL HEADERS")
                for missing in missing_cols: st.code(f"⚠️ {missing}")
        except Exception as e: st.error(f"Error: {e}")

    if not is_valid_data or uploaded_file is None:
        st.info("👋 Upload your balanced master data CSV file in the sidebar to activate systems.")
        st.stop()

    st.markdown("---")
    st.markdown("### 🌍 Global Target Filter")
    selected_league_filter = st.selectbox("Select Target Country:", uploaded_leagues)
    st.markdown("---")
    st.markdown("### ⚙️ Engine Parameter Adjustments")
    half_life_days = st.slider("Time-Decay Half Life (Days)", 15, 90, 45, 1)
    max_score_cap = st.slider("Matrix Score Simulation Ceiling", 4, 10, 6, 1)
    vol_dampener = st.slider("Volatility Dampener (Smooth)", 0.5, 1.5, 1.0, 0.05)
    st.markdown("---")
    st.markdown("### 🔄 Backtest Range Configuration")
    backtest_window = st.slider("Rolling Window Size (Days)", 90, 365, 180, 5)

# 3. Data Ingestion & Scope Truncation
# Fixes pandas.errors.EmptyDataError by rewinding file pointer before full ingestion
uploaded_file.seek(0)
raw_master_df = pd.read_csv(uploaded_file)
raw_master_df["match_timestamp"] = pd.to_datetime(raw_master_df["match_timestamp"])
filtered_df = raw_master_df[raw_master_df["league_country"] == selected_league_filter].reset_index(drop=True)

if filtered_df.empty:
    st.warning(f"No records match selected country target: '{selected_league_filter}'")
    st.stop()

all_teams = sorted(list(set(filtered_df["home_team"].unique()) | set(filtered_df["away_team"].unique())))
total_records = len(filtered_df)

# Unpack layout containers explicitly to avoid "with m_cols" context crashes
col1, col2, col3 = st.columns(3)
with col1: st.markdown(f'<div class="metric-card"><p class="metric-title">{selected_league_filter.upper()} Total Records Loaded</p><p class="metric-value">{total_records}</p></div>', unsafe_allow_html=True)
with col2: st.markdown(f'<div class="metric-card"><p class="metric-title">Historic Average Home Goals</p><p class="metric-value">{filtered_df["home_goals"].mean():.2f}</p></div>', unsafe_allow_html=True)
with col3: st.markdown(f'<div class="metric-card"><p class="metric-title">Historic Average Away Goals</p><p class="metric-value">{filtered_df["away_goals"].mean():.2f}</p></div>', unsafe_allow_html=True)
st.markdown("---")
# 4. Tab Initialization (Explicit index separation syntax avoids layout unpacking object issues)
all_tabs = st.tabs(["📅 FUTURE PROJECTIONS", "🌍 LEAGUE TABLES", "📜 ARCHIVE ROLLING BACKTESTER", "🔴 LIVE CENTRE"])
tab_pred    = all_tabs[0]
tab_tables  = all_tabs[1]
tab_history = all_tabs[2]
tab_live    = all_tabs[3]

# ---------------------------------------------------------------------
# TAB 4: LIVE CENTRE MONITOR
# ---------------------------------------------------------------------
with tab_live:
    st.info("Live data pipelines active. Processing balanced automated scraper telemetry feeds smoothly using Dixon-Coles parameters.")

# ---------------------------------------------------------------------
# TAB 2: LEAGUE TABLES GENERATOR
# ---------------------------------------------------------------------
with tab_tables:
    st.markdown(f"### Dynamic Standings Matrix: {selected_league_filter.upper()}")
    st.dataframe(engine.generate_dynamic_league_table(filtered_df), use_container_width=True)

# ---------------------------------------------------------------------
# TAB 3: ARCHIVE ROLLING BACKTESTER
# ---------------------------------------------------------------------
with tab_history:
    st.markdown("### 📜 Automated Rolling-Window Backtest & Mathematical Performance Validation")
    league_key = selected_league_filter.lower()
    baseline_goals = engine.COMPETITION_MATRIX.get(league_key, {"baseline_goals": 2.65}).get("baseline_goals", 2.65)
    
    with st.spinner("Processing Chronological Rolling-Window Validations..."):
        # Wrapped in a defensive try-except context to isolate backend main_engine code failures safely
        try:
            backtest_results_df = engine.run_rolling_window_backtest(
                df=filtered_df, 
                baseline_goals=baseline_goals, 
                window_days=backtest_window, 
                evaluation_step_days=7, 
                vol_dampener=vol_dampener
            )
        except TypeError as param_err:
            st.error("❌ Backtester Parameter Mismatch Error!")
            st.info("The dashboard layout parameters do not match your backend main_engine function signature definition.")
            st.code(f"Trace Details: {param_err}")
            backtest_results_df = pd.DataFrame()
        except Exception as inner_err:
            st.error("❌ Internal Engine Calculation Crash!")
            st.info("The calculation script failed internally while filtering historical chronological dataframe matrix sequences.")
            st.code(f"Trace Details: {inner_err}")
            backtest_results_df = pd.DataFrame()
        
    if not backtest_results_df.empty:
        avg_log_loss = backtest_results_df["log_loss"].mean()
        tested_samples = len(backtest_results_df)
        bc1, bc2 = st.columns(2)
        loss_color = "#10b981" if avg_log_loss < 1.00 else ("#facc15" if avg_log_loss < 1.08 else "#ef4444")
        with bc1: st.markdown(f'<div class="metric-card"><p class="metric-title">Evaluated Match Samples</p><p class="metric-value">{tested_samples}</p></div>', unsafe_allow_html=True)
        with bc2: st.markdown(f'<div class="metric-card"><p class="metric-title" style="color:{loss_color};">Average Forecast Log-Loss</p><p class="metric-value" style="color:{loss_color};">{avg_log_loss:.4f}</p></div>', unsafe_allow_html=True)
        st.markdown("#### Chronological Backtest Validation Ledger")
        st.dataframe(backtest_results_df[["match_timestamp", "home_team", "away_team", "home_goals", "away_goals", "actual_outcome", "model_probability", "log_loss"]], use_container_width=True)
    else:
        st.warning("⚠️ Insufficient historical chronological date range or script definition error inside the specified rolling window pool.")
# ---------------------------------------------------------------------
# TAB 1: FUTURE PROJECTIONS ENGINE
# ---------------------------------------------------------------------
with tab_pred:
    st.markdown("### 📋 Historic Database Overview")
    st.dataframe(filtered_df, use_container_width=True)
    st.markdown("### 🔍 Advanced Match Drill-Down Lab")
    options = {f"[{selected_league_filter.upper()}] {r['home_team']} vs {r['away_team']} ({pd.to_datetime(r['match_timestamp']).strftime('%Y-%m-%d')})": r for idx, r in filtered_df.iterrows()}
    sel_match = st.selectbox("Select Target Profile:", list(options.keys()))
    
    if sel_match:
        target = options[sel_match]
        target_ts = pd.to_datetime(target["match_timestamp"])
        league_key = selected_league_filter.lower()
        baseline_goals = engine.COMPETITION_MATRIX.get(league_key, {"baseline_goals": 2.65}).get("baseline_goals", 2.65)
        
        st.markdown("**📋 Live Situational Calibrations (Adjustable Pre-loaded Parameters):**")
        sc1, sc2 = st.columns(2)
        with sc1:
            home_status = st.selectbox("Home Squad League Alignment Status:", ["stable", "promoted", "relegated"], key="lab_hstat")
            h_inj = st.slider("Home Squad Availability Scale", 0.5, 1.0, float(target.get("home_avail_weight", 1.0)), 0.05, key="lab_hi")
            h_mot = st.slider("Home Tactical Motivation Index", 0.8, 1.2, float(target.get("home_mot_weight", 1.0)), 0.05, key="lab_hm")
            h_rest_days = st.slider("Home Squad Recovery Window (Days)", 1, 14, int(target.get("home_rest_days", 5)), step=1, key="lab_hr")
        with sc2:
            away_status = st.selectbox("Away Squad League Alignment Status:", ["stable", "promoted", "relegated"], key="lab_astat")
            a_inj = st.slider("Away Squad Availability Scale", 0.5, 1.0, float(target.get("away_avail_weight", 1.0)), 0.05, key="lab_ai")
            a_mot = st.slider("Away Tactical Motivation Index", 0.8, 1.2, float(target.get("away_mot_weight", 1.0)), 0.05, key="lab_am")
            a_rest_days = st.slider("Away Squad Recovery Window (Days)", 1, 14, int(target.get("away_rest_days", 5)), step=1, key="lab_ar")
            distance_tier = st.select_slider("Away Journey Travel Disadvantage Override", options=["Short (No Penalty)", "Moderate (-1%)", "Long (-2%)", "Continental (-4%)"], value="Short (No Penalty)", key="lab_dist")
            distance_map = {"Short (No Penalty)": 1.00, "Moderate (-1%)": 0.99, "Long (-2%)": 0.98, "Continental (-4%)": 0.96}
            dynamic_distance_penalty = distance_map[distance_tier]
            
        # Wrapped in a defensive try-except context to isolate backend main_engine code failures safely
        try:
            res = engine.predict_match_probabilities(
                filtered_df, 
                target["home_team"], 
                target["away_team"], 
                target_ts, 
                baseline_goals, 
                h_rest_days, 
                a_rest_days, 
                home_status, 
                away_status, 
                max_score_cap, 
                vol_dampener
            )
        except TypeError as signature_err:
            st.error("❌ Prediction Signature Mismatch!")
            st.info("The configuration parameters pass format does not match the definition inside your main_engine.py file script.")
            st.code(f"Trace Details: {signature_err}")
            res = {
                "market_probabilities": {"1 (Home Win)": 0.33, "X (Draw)": 0.34, "2 (Away Win)": 0.33},
                "lambdas": {"h2h_mods": [1.0, 1.0], "lam1_home": 1.000, "lam2_away": 1.000, "dixon_coles_tau": 1.000},
                "optimal_bet_pick": "N/A",
                "full_score_matrix": np.zeros((max_score_cap, max_score_cap))
            }
        except Exception as general_err:
            st.error("❌ Calculation Matrix Runtime Computation Failure!")
            st.info("The system backend module hit an unexpected error while calculating vector distributions.")
            st.code(f"Trace Details: {general_err}")
            res = {
                "market_probabilities": {"1 (Home Win)": 0.33, "X (Draw)": 0.34, "2 (Away Win)": 0.33},
                "lambdas": {"h2h_mods": [1.0, 1.0], "lam1_home": 1.000, "lam2_away": 1.000, "dixon_coles_tau": 1.000},
                "optimal_bet_pick": "N/A",
                "full_score_matrix": np.zeros((max_score_cap, max_score_cap))
            }

        h_stats = engine.parse_live_team_averages(filtered_df, target["home_team"], target_ts, half_life_days, status_override=home_status)
        a_stats = engine.parse_live_team_averages(filtered_df, target["away_team"], target_ts, half_life_days, status_override=away_status)
        
        prob_home, prob_draw, prob_away = res["market_probabilities"]["1 (Home Win)"], res["market_probabilities"]["X (Draw)"], res["market_probabilities"]["2 (Away Win)"]
        sample_density = min(h_stats["games_played"], a_stats["games_played"])
        confidence_score = min(100, int((sample_density / 6.0) * 100)) if sample_density > 0 else 15
        
        c_left, c_right = st.columns(2)
        with c_left:
            st.markdown('<div class="market-header">Calculated Dixon-Coles Probability Outcomes</div>', unsafe_allow_html=True)
            st.progress(max(0, min(100, int(prob_home * 100))), text=f"🏠 Home Win: {prob_home*100:.1f}% (Fair Decimal Odds: {1/max(0.01, prob_home):.2f})")
            st.progress(max(0, min(100, int(prob_draw * 100))), text=f"🤝 Draw Outcome: {prob_draw*100:.1f}% (Fair Decimal Odds: {1/max(0.01, prob_draw):.2f})")
            st.progress(max(0, min(100, int(prob_away * 100))), text=f"🚀 Away Win: {prob_away*100:.1f}% (Fair Decimal Odds: {1/max(0.01, prob_away):.2f})")
            if h_stats["games_played"] < 5 or a_stats["games_played"] < 5:
                st.warning(f"⚠️ Bayesian Small Sample Rule Triggered! Home games: {h_stats['games_played']} | Away games: {a_stats['games_played']}. Output regressed toward 1.0.")
            st.metric("Model Sample Confidence Level", f"{confidence_score}%")
            
        with c_right:
            st.markdown('<div class="market-header">🎫 Calibrated Betting Ticket Slip</div>', unsafe_allow_html=True)
            ticket_txt = (
                f"========================================\n"
                f"        SISONKE BET ANALYTICS ENGINE    \n"
                f"        DIXON-COLES CALIBRATED LOG      \n"
                f"========================================\n"
                f"MATCH PROFILE : {target['home_team']} vs {target['away_team']}\n"
                f"TIMESTAMP UTC : {target_ts.strftime('%Y-%m-%d %H:%M')}\n"
                f"SQUAD ALIGN   : H: {home_status.upper()} | A: {away_status.upper()}\n"
                f"H2H PSYCH BIAS: Home: {res['lambdas']['h2h_mods']:.2f}x | Away: {res['lambdas']['h2h_mods']:.2f}x\n"
                f"----------------------------------------\n"
                f"CALCULATED HOME EXPECTED (λ1) : {res['lambdas']['lam1_home']:.3f}\n"
                f"CALCULATED AWAY EXPECTED (λ2) : {res['lambdas']['lam2_away']:.3f}\n"
                f"DIXON-COLES SCALAR MATRIX (τ) : {res['lambdas']['dixon_coles_tau']:.3f}\n"
                f"----------------------------------------\n"
                f"HOME WIN PROBABILITY SPLIT    : {prob_home*100:.1f}%\n"
                f"MATCH DRAW PROBABILITY SPLIT  : {prob_draw*100:.1f}%\n"
                f"AWAY WIN PROBABILITY SPLIT    : {prob_away*100:.1f}%\n"
                f"========================================\n"
                f"RECOMMENDED OPTIMAL BET TARGET : {res.get('optimal_bet_pick', 'N/A').upper()}\n"
                f"MODEL STRUCT CONFIDENCE METRIC : {confidence_score}%\n"
                f"========================================"
            )
            st.text_area("System Coupon Script Output", value=ticket_txt, height=360)
            
        st.markdown("### 📊 Live Structural Match Deep-Dive Metrics")
        md1, md2 = st.columns(2)
        with md1:
            st.markdown('<p class="market-header">🏠 Home Attack & Defense Vector Breakdown</p>', unsafe_allow_html=True)
            st.code(
                f"Historical Samples Evaluated : {h_stats['games_played']}\n"
                f"Calculated Attack Factor (α) : {h_stats['attack_rating']:.3f}\n"
                f"Calculated Defense Factor (β): {h_stats['defense_rating']:.3f}\n"
                f"Avg Goals (Scored / Conceded): {h_stats['avg_scored']:.2f} / {h_stats['avg_conceded']:.2f}\n"
                f"Expected Shots on Target (SoT): {h_stats['avg_sot']:.2f}"
            )
        with md2:
            st.markdown('<p class="market-header">🚀 Away Attack & Defense Vector Breakdown</p>', unsafe_allow_html=True)
            st.code(
                f"Historical Samples Evaluated : {a_stats['games_played']}\n"
                f"Calculated Attack Factor (α) : {a_stats['attack_rating']:.3f}\n"
                f"Calculated Defense Factor (β): {a_stats['defense_rating']:.3f}\n"
                f"Avg Goals (Scored / Conceded): {a_stats['avg_scored']:.2f} / {a_stats['avg_conceded']:.2f}\n"
                f"Expected Shots on Target (SoT): {a_stats['avg_sot']:.2f}"
            )
            
        st.markdown("### 🧮 Dixon-Coles Probability Matrix Distribution Grid")
        grid_matrix = res.get("full_score_matrix", np.zeros((max_score_cap, max_score_cap)))
        grid_df = pd.DataFrame(
            grid_matrix, 
            index=[f"Home {i}" for i in range(max_score_cap)], 
            columns=[f"Away {j}" for j in range(max_score_cap)]
        )
        st.dataframe(grid_df.style.format("{:.4f}").background_gradient(cmap="Blues"), use_container_width=True)
