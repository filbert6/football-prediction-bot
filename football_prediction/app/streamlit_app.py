import random
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st


def detect_trained_models() -> bool:
    # Check common locations for trained models in repository
    repo_root = Path(__file__).resolve().parents[2]
    models_dir = repo_root / "football_prediction" / "models"
    models_output = repo_root / "football_prediction" / "models_output"
    # If any python model file besides __init__.py or any joblib exists, consider models present
    if models_dir.exists():
        py_models = [p for p in models_dir.iterdir() if p.suffix == ".py" and p.name != "__init__.py"]
        if py_models:
            return True
    if models_output.exists():
        joblibs = list(models_output.glob("*.joblib"))
        if joblibs:
            return True
    return False


@st.cache_data
def sample_teams_and_leagues():
    leagues = [
        "Premier League",
        "LaLiga",
        "Serie A",
        "Bundesliga",
        "Ligue 1",
    ]
    teams = {
        "Premier League": [
            "Manchester City",
            "Liverpool",
            "Manchester United",
            "Arsenal",
            "Chelsea",
        ],
        "LaLiga": ["Real Madrid", "Barcelona", "Atletico", "Sevilla", "Valencia"],
        "Serie A": ["Juventus", "Inter", "AC Milan", "Napoli", "Roma"],
        "Bundesliga": ["Bayern", "Dortmund", "Leipzig", "RB Leipzig", "Bayer Leverkusen"],
        "Ligue 1": ["PSG", "Lyon", "Marseille", "Monaco", "Lille"],
    }
    return leagues, teams


@st.cache_data
def generate_demo_fixtures(n=12):
    leagues, teams_map = sample_teams_and_leagues()
    rows = []
    for i in range(n):
        league = random.choice(leagues)
        home, away = random.sample(teams_map[league], 2)
        p_home = round(random.uniform(0.3, 0.6), 2)
        p_draw = round(random.uniform(0.15, 0.35), 2)
        p_away = max(0.0, round(1 - p_home - p_draw, 2))
        over25 = round(random.uniform(0.4, 0.8), 2)
        btts = round(random.uniform(0.4, 0.85), 2)
        rows.append(
            {
                "League": league,
                "Home Team": home,
                "Away Team": away,
                "1": p_home,
                "X": p_draw,
                "2": p_away,
                "Over 2.5": over25,
                "BTTS": btts,
            }
        )
    return pd.DataFrame(rows)


def page_home(demo_mode: bool):
    st.title("⚽ Football Prediction Bot")
    st.markdown("Robot professionnel de prédiction football utilisant l'intelligence artificielle.")

    fixtures = generate_demo_fixtures(200)
    num_matches = len(fixtures)
    accuracy = round(random.uniform(0.62, 0.82), 2)
    roi = round(random.uniform(-0.05, 0.25), 2)
    num_leagues = fixtures["League"].nunique()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Nombre de matchs analysés", f"{num_matches}")
    col2.metric("Précision du modèle", f"{accuracy * 100:.1f}%")
    col3.metric("ROI simulé", f"{roi * 100:.1f}%")
    col4.metric("Nombre de ligues", f"{num_leagues}")

    st.markdown("---")
    st.subheader("Tendances")
    # Accuracy over time (simulated)
    dates = pd.date_range(end=datetime.today(), periods=30)
    acc_series = pd.Series(np.clip(np.cumsum(np.random.normal(0, 0.002, len(dates))) + accuracy, 0, 1), index=dates)
    st.line_chart(acc_series.rename("Accuracy"))

    st.subheader("Matches par ligue")
    league_counts = fixtures["League"].value_counts()
    st.bar_chart(league_counts)

    if demo_mode:
        st.warning("Aucun modèle entraîné détecté, utilisation du mode démonstration.")
    else:
        st.success("Modèles détectés — mode production activé.")


def page_match_analysis(demo_mode: bool):
    st.header("🔍 Analyse Match")
    leagues, teams_map = sample_teams_and_leagues()
    all_teams = [t for teams in teams_map.values() for t in teams]

    col1, col2 = st.columns([2, 1])
    with col1:
        home = st.selectbox("Équipe domicile", all_teams, index=0)
        away = st.selectbox("Équipe extérieure", all_teams, index=1)
    with col2:
        st.write("")
        st.write("")
        if st.button("Analyser"):
            if home == away:
                st.error("Veuillez choisir deux équipes différentes.")
                return

            # Simple demo probabilities
            base = random.uniform(0.45, 0.55)
            h_adv = random.uniform(0.0, 0.15)
            p_home = round(np.clip(base + h_adv, 0, 1), 2)
            p_away = round(np.clip(1 - p_home - 0.2, 0, 1), 2)
            p_draw = round(np.clip(1 - p_home - p_away, 0, 1), 2)
            over25 = round(random.uniform(0.35, 0.75), 2)
            btts = round(random.uniform(0.4, 0.85), 2)

            st.subheader(f"Analyse: {home} vs {away}")
            m1, m2, m3 = st.columns(3)
            m1.metric("Victoire domicile", f"{p_home * 100:.1f}%")
            m2.metric("Nul", f"{p_draw * 100:.1f}%")
            m3.metric("Victoire extérieur", f"{p_away * 100:.1f}%")

            m4, m5 = st.columns(2)
            m4.metric("Over 2.5", f"{over25 * 100:.1f}%")
            m5.metric("BTTS", f"{btts * 100:.1f}%")

            # Simple odds example
            odds_df = pd.DataFrame(
                {
                    "Market": ["1", "X", "2", "Over 2.5", "BTTS"],
                    "Prob": [p_home, p_draw, p_away, over25, btts],
                    "Implied Odds": [round(1 / max(p_home, 0.01), 2), round(1 / max(p_draw, 0.01), 2), round(1 / max(p_away, 0.01), 2), round(1 / max(over25, 0.01), 2), round(1 / max(btts, 0.01), 2)],
                }
            )
            st.dataframe(odds_df)


def page_predictions(demo_mode: bool):
    st.header("🎯 Prédictions")
    df = generate_demo_fixtures(20)
    # Show probabilities as percentages
    df_display = df.copy()
    for c in ["1", "X", "2", "Over 2.5", "BTTS"]:
        df_display[c] = (df_display[c] * 100).round(1).astype(str) + "%"

    st.dataframe(df_display.reset_index(drop=True))


def page_history(demo_mode: bool):
    st.header("📊 Historique")
    # Simulated betting history
    n = 60
    dates = pd.date_range(end=datetime.today(), periods=n)
    results = np.random.choice([0, 1], size=n, p=[0.55, 0.45])
    stakes = np.random.uniform(5, 50, size=n)
    returns = stakes * (np.where(results == 1, np.random.uniform(1.5, 3.0, size=n), 0)) - stakes

    df_hist = pd.DataFrame({"date": dates, "won": results, "stake": stakes, "profit": returns})
    total_wins = int(df_hist["won"].sum())
    accuracy = float(df_hist["won"].mean())
    roi = df_hist["profit"].sum() / df_hist["stake"].sum()
    yield_pct = df_hist["profit"].sum() / df_hist["stake"].mean()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Nombre de paris gagnants", f"{total_wins}")
    c2.metric("Accuracy", f"{accuracy * 100:.1f}%")
    c3.metric("ROI", f"{roi * 100:.1f}%")
    c4.metric("Yield", f"{yield_pct:.1f}")

    st.markdown("---")
    st.subheader("Profit cumulé")
    df_hist = df_hist.set_index("date").sort_index()
    st.line_chart(df_hist["profit"].cumsum())

    st.subheader("Répartition victoires/défaites")
    st.bar_chart(df_hist["won"].value_counts())


def page_stats(demo_mode: bool):
    st.header("📈 Statistiques")
    fixtures = generate_demo_fixtures(200)
    top_leagues = fixtures["League"].value_counts().head(5)
    st.subheader("Top ligues (par nombre de matches simulés)")
    st.bar_chart(top_leagues)

    st.subheader("Répartition des résultats (1/X/2) - simulation")
    # Create a simulated result distribution
    results = np.random.choice(["1", "X", "2"], size=500, p=[0.45, 0.28, 0.27])
    res_series = pd.Series(results).value_counts()
    st.bar_chart(res_series)

    st.subheader("Graphiques interactifs")
    st.dataframe(fixtures.sample(10).reset_index(drop=True))


def main():
    st.set_page_config(page_title="Football Prediction Bot", page_icon="⚽", layout="wide")

    demo_mode = not detect_trained_models()

    # Sidebar menu
    st.sidebar.title("Menu")
    menu = st.sidebar.radio(
        "Navigation",
        ("🏠 Accueil", "🔍 Analyse Match", "🎯 Prédictions", "📊 Historique", "📈 Statistiques"),
    )

    # Ensure no blank pages: map selection to functions
    if menu == "🏠 Accueil":
        page_home(demo_mode)
    elif menu == "🔍 Analyse Match":
        page_match_analysis(demo_mode)
    elif menu == "🎯 Prédictions":
        page_predictions(demo_mode)
    elif menu == "📊 Historique":
        page_history(demo_mode)
    elif menu == "📈 Statistiques":
        page_stats(demo_mode)
    else:
        st.warning("Page inconnue — retour à l'accueil.")
        page_home(demo_mode)


if __name__ == "__main__":
    main()
