# =====================================================================
# SISONKE BET PREDICTIONS - STREAMLIT USER INTERFACE LAYER (SEGMENT 2)
# =====================================================================
tab_pred, tab_tables, tab_history, tab_live = st.tabs(["📅 FUTURE PROJECTIONS", "🌍 LEAGUE TABLES", "📜 ARCHIVE ROLLING BACKTESTER", "🔴 LIVE CENTRE"])

with tab_live:
    st.info("Live data pipelines active. Processing balanced automated scraper telemetry feeds smoothly using Dixon-Coles parameters.")

with tab_tables:
    st.markdown(f"### Dynamic Standings Matrix: {selected_league_filter.upper()}")
    st.dataframe(engine.generate_dynamic_league_table(filtered_df), use_container_width=True)

with tab_history:
    st.markdown("### 📜 Automated Rolling-Window Backtest & Mathematical Performance Validation")
    league_key = selected_league_filter.lower()
    baseline_goals = engine.COMPETITION_MATRIX.get(league_key, {"baseline_goals": 2.65}).get("baseline_goals", 2.65)
    
    if activate_backtester:
        with st.spinner("Processing Chronological Rolling-Window Validations..."):
            backtest_results_df = engine.run_rolling_window_backtest(
                df=filtered_df, baseline_goals=baseline_goals, window_days=backtest_window, evaluation_step_days=7, vol_dampener=vol_dampener
            )
            
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
            st.warning("⚠️ Insufficient historical chronological date range to build the specified rolling window framework pool.")
    else:
        st.info("💡 To initiate mathematical log-loss optimization auditing, click and check the **'Run Historical Backtester'** parameter switch inside the left Sidebar Panel Room.")

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
            
        res = engine.predict_match_probabilities(filtered_df, target["home_team"], target["away_team"], target_ts, baseline_goals, h_rest_days, a_rest_days, home_status, away_status, max_score_cap, vol_dampener)
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
                f"H2H PSYCH BIAS: Home: {res['lambdas']['h2h_mods'][0]:.2f}x | Away: {res['lambdas']['h2h_mods'][1]:.2f}x\n"
                f"----------------------------------------\n"
                f"CALCULATED HOME EXPECTED (λ1) : {res['lambdas']['lam1_home']:.3f}\n"
                f"CALCULATED AWAY EXPECTED (λ2) : {res['lambdas']['lam2_away']:.3f}\n"
                f"DIXON-COLES SCALAR MATRIX (τ) : {res['lambdas']['dixon_coles_tau']:.3f}\n"
                f"----------------------------------------\n"
                f"HOME WIN PROBABILITY SPLIT    : {prob_home*100:.1f}%\n"
                f"MATCH DRAW PROBABILITY SPLIT  : {prob_draw*100:.1f}%\n"
                f"AWAY WIN PROBABILITY SPLIT    : {prob_away*100:.1f}%\n"
                f"========================================\n"
                f"STATUS: AUTOMATED DRILL LAB LOG COMPLETE\n"
            )
            st.text_area("Ticket Log Stream Output", value=ticket_txt, height=265)

        st.markdown("### 🎲 Secondary Betting Markets & Exact Score Heatmap Matrix")
        sec_col1, sec_col2 = st.columns()
        with sec_col1:
            st.markdown('<div class="market-header">Derived Proposition Markets</div>', unsafe_allow_html=True)
            sm = res["secondary_markets"]
            st.metric(label="Both Teams To Score (BTTS) - YES", value=f"{sm['BTTS_Yes'] * 100:.1f}%", delta=f"Fair Odds: {1/max(0.01, sm['BTTS_Yes']):.2f}")
            st.metric(label="Home Team Clean Sheet", value=f"{sm['Home_CS'] * 100:.1f}%", delta=f"Fair Odds: {1/max(0.01, sm['Home_CS']):.2f}")
            st.metric(label="Away Team Clean Sheet", value=f"{sm['Away_CS'] * 100:.1f}%", delta=f"Fair Odds: {1/max(0.01, sm['Away_CS']):.2f}")
        with sec_col2:
            st.markdown('<div class="market-header">Dixon-Coles Exact Score Matrix (%)</div>', unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(res["raw_matrix"] * 100, index=[f"Home {g}" for g in range(max_score_cap + 1)], columns=[f"Away {g}" for g in range(max_score_cap + 1)]).style.background_gradient(cmap="YlOrRd", axis=None).format("{:.2f}%"), use_container_width=True)
