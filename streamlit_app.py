import datetime
import numpy as np
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Football Prediction Bot",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def get_sample_matches():
    today = datetime.date.today()
    matches = [
        {
            "Date": today + datetime.timedelta(days=i),
            "League": league,
            "Home Team": home,
            "Away Team": away,
            "Home Odds": home_odds,
            "Draw Odds": draw_odds,
            "Away Odds": away_odds,
            "Prediction": prediction,
            "Win % Home": win_home,
            "Draw %": draw_prob,
            "Win % Away": win_away,
            "Confidence": confidence,
        }
        for i, (league, home, away, home_odds, draw_odds, away_odds, prediction, win_home, draw_prob, win_away, confidence) in enumerate([
            ("Ligue 1", "Paris FC", "Lyon", 2.10, 3.40, 3.10, "Paris FC", 45, 27, 28, 82),
            ("Premier League", "Arsenal", "Liverpool", 2.35, 3.30, 2.80, "Liverpool", 38, 30, 32, 78),
            ("La Liga", "Barcelona", "Sevilla", 1.65, 4.00, 5.20, "Barcelona", 58, 22, 20, 91),
            ("Serie A", "Juventus", "Inter", 2.40, 3.20, 2.90, "Juventus", 41, 31, 28, 76),
            ("Bundesliga", "Bayern", "Dortmund", 1.75, 3.80, 4.70, "Bayern", 53, 24, 23, 88),
        ])
    ]
    return pd.DataFrame(matches)


@st.cache_data
def get_sample_history():
    history = [
        {
            "Date": datetime.date.today() - datetime.timedelta(days=i * 3),
            "Home Team": home,
            "Away Team": away,
            "Score": score,
            "Prediction": pred,
            "Result": result,
            "Model Confidence": confidence,
        }
        for i, (home, away, score, pred, result, confidence) in enumerate([
            ("Paris FC", "Lyon", "2-1", "Paris FC", "Win", 82),
            ("Arsenal", "Liverpool", "1-1", "Liverpool", "Draw", 78),
            ("Barcelona", "Sevilla", "3-0", "Barcelona", "Win", 91),
            ("Juventus", "Inter", "1-2", "Juventus", "Loss", 76),
            ("Bayern", "Dortmund", "2-2", "Bayern", "Draw", 88),
        ])
    ]
    return pd.DataFrame(history)


@st.cache_data
def get_sample_statistics():
    summary = {
        "Average Prediction Accuracy": 79,
        "Total Sample Matches": 25,
        "Win Rate (Home Predictions)": 64,
        "Draw Rate": 22,
        "Away Prediction Success": 58,
    }
    return summary


def render_home():
    st.title("Football Prediction Bot")
    st.write(
        "Bienvenue dans l’interface de démonstration du bot de prédiction de football. "
        "Cette application montre une interface moderne avec des analyses de match, des prédictions, un historique et des statistiques."
    )

    st.markdown("---")

    stats = get_sample_statistics()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Précision moyenne", f"{stats['Average Prediction Accuracy']}%")
    col2.metric("Matches d’exemple", stats["Total Sample Matches"])
    col3.metric("Taux de victoire domicile", f"{stats['Win Rate (Home Predictions)']}%")
    col4.metric("Succès predictions away", f"{stats['Away Prediction Success']}%")

    st.markdown("### Aperçu des prochains matchs")
    upcoming = get_sample_matches()
    st.dataframe(upcoming.style.format({"Home Odds": "{:.2f}", "Draw Odds": "{:.2f}", "Away Odds": "{:.2f}"}))

    st.markdown("### Tendances de performance")
    sample_trend = pd.DataFrame(
        {
            "Date": [datetime.date.today() - datetime.timedelta(days=i) for i in range(7)][::-1],
            "Précision du modèle": [72, 75, 78, 80, 79, 83, 85],
            "Taux de bonne prédiction": [60, 62, 65, 68, 69, 72, 74],
        }
    )
    sample_trend = sample_trend.set_index("Date")
    st.line_chart(sample_trend)

    st.markdown("---")
    st.info(
        "Les données affichées sont des exemples générés automatiquement pour rendre l’interface visible immédiatement même si les modèles ne sont pas encore entraînés."
    )


def render_match_analysis():
    st.title("Analyse de match")
    matches = get_sample_matches()
    selected = st.selectbox("Sélectionnez un match à analyser", matches["Home Team"] + " vs " + matches["Away Team"])
    match = matches.loc[matches["Home Team"] + " vs " + matches["Away Team"] == selected].iloc[0]

    st.subheader(f"Analyse détaillée : {match['Home Team']} vs {match['Away Team']}")
    st.write(f"**Compétition:** {match['League']}  •  **Date:** {match['Date'].strftime('%d/%m/%Y')}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Probabilité domicile", f"{match['Win % Home']}%")
    col2.metric("Probabilité match nul", f"{match['Draw %']}%")
    col3.metric("Probabilité extérieur", f"{match['Win % Away']}%")

    st.markdown("### Raisons de la prédiction")
    st.write(
        "- **Forme récente** : le modèle analyse les 5 derniers matchs et les performances offensives/défensives.\n"
        "- **Avantage domicile** : les équipes jouent mieux chez elles dans les compétitions majeures.\n"
        "- **Motivation** : état de la saison et enjeu de classement.\n"
        "- **Cotes du marché** : le modèle combine ses scores avec les probabilités implicites pour améliorer l’affinage."
    )

    st.markdown("### Indicateurs clés")
    metrics = {
        "Puissance offense": np.random.randint(70, 95),
        "Solidité défense": np.random.randint(65, 90),
        "Forme récente": np.random.randint(60, 96),
        "Chance globale": match["Confidence"],
    }

    score_df = pd.DataFrame.from_dict(metrics, orient="index", columns=["Score"])
    st.bar_chart(score_df)

    st.markdown("### Détails de prédiction")
    st.write(
        f"Le modèle recommande **{match['Prediction']}** avec une confiance de **{match['Confidence']}%**. "
        "Une analyse de l’écart de buts attendus donne priorité à l’équipe la plus stable et la plus dangereuse en attaque."
    )

    st.expander("Voir le commentaire complet de l’analyse").write(
        "Cette analyse utilise des données d’exemple pour illustrer le processus. Les tendances montrent que l’équipe à domicile est légèrement favorisée, mais un résultat nul reste plausible lorsque la différence de probabilité est faible."
    )


def render_predictions():
    st.title("Prédictions")
    matches = get_sample_matches()
    leagues = matches["League"].unique().tolist()
    selected_league = st.selectbox("Filtrer par ligue", ["Toutes"] + leagues)

    if selected_league != "Toutes":
        matches = matches[matches["League"] == selected_league]

    st.markdown("### Prédictions des prochains matchs")
    st.dataframe(matches.assign(**{"Conférence (%)": matches["Confidence"]}).style.format(
        {"Home Odds": "{:.2f}", "Draw Odds": "{:.2f}", "Away Odds": "{:.2f}", "Win % Home": "{:.0f}%", "Draw %": "{:.0f}%", "Win % Away": "{:.0f}%"}
    ))

    st.markdown("### Top 3 des pronostics")
    top3 = matches.sort_values(by="Confidence", ascending=False).head(3)
    for _, row in top3.iterrows():
        st.write(f"**{row['Home Team']} vs {row['Away Team']}** — Prédiction : {row['Prediction']} ({row['Confidence']}% confiance)")

    st.markdown("### Distribution des prédictions")
    outcome_counts = matches["Prediction"].value_counts().rename_axis("Prédiction").reset_index(name="Nombre")
    st.bar_chart(outcome_counts.set_index("Prédiction"))


def render_history():
    st.title("Historique")
    history = get_sample_history()
    st.markdown("### Résultats récents et performance du modèle")
    st.dataframe(history)

    st.markdown("### Évolution de l’historique")
    history_chart = history.copy()
    history_chart["Match"] = history_chart["Home Team"] + " vs " + history_chart["Away Team"]
    history_chart = history_chart.set_index("Match")
    st.bar_chart(history_chart[["Model Confidence"]])

    st.markdown("### Résumé")
    summary = {
        "Buts moyen par match": 2.4,
        "Taux de pronostics exacts": "58%",
        "Prédictions gagnantes": "3/5",
        "Prédictions nulles correctes": "1/2",
    }
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Buts moyen", summary["Buts moyen par match"])
    col2.metric("Précision historique", summary["Taux de pronostics exacts"])
    col3.metric("Pronostics gagnants", summary["Prédictions gagnantes"])
    col4.metric("Matchs nuls corrects", summary["Prédictions nulles correctes"])


def render_statistics():
    st.title("Statistiques")
    matches = get_sample_matches()

    st.markdown("### Répartition des pronostics par équipe")
    home_stats = matches["Home Team"].value_counts().rename_axis("Équipe").reset_index(name="Matches à domicile")
    away_stats = matches["Away Team"].value_counts().rename_axis("Équipe").reset_index(name="Matches à l’extérieur")
    st.bar_chart(home_stats.set_index("Équipe"))
    st.bar_chart(away_stats.set_index("Équipe"))

    st.markdown("### Résumé des probabilités")
    summary_df = matches[["Home Team", "Away Team", "Win % Home", "Draw %", "Win % Away"]].copy()
    st.dataframe(summary_df.style.format({"Win % Home": "{:.0f}%", "Draw %": "{:.0f}%", "Win % Away": "{:.0f}%"}))

    st.markdown("### Indicateurs du modèle")
    stat_df = pd.DataFrame(
        {
            "Type": ["Confiance moyenne", "Matchs modélisés", "Prédictions à plus de 80%"],
            "Valeur": [matches["Confidence"].mean(), len(matches), (matches["Confidence"] > 80).sum()],
        }
    )
    st.table(stat_df)

    st.markdown("### Performance par ligue")
    league_stats = matches.groupby("League")["Confidence"].mean().round(1).reset_index()
    league_stats.columns = ["Ligue", "Confiance moyenne (%)"]
    st.bar_chart(league_stats.set_index("Ligue"))


def main():
    with st.sidebar:
        st.markdown("# Navigation")
        page = st.radio(
            "Choisissez une page",
            ["Accueil", "Analyse de match", "Prédictions", "Historique", "Statistiques"],
        )
        st.markdown("---")
        st.write("Application de démonstration avec données d’exemple.")

    if page == "Accueil":
        render_home()
    elif page == "Analyse de match":
        render_match_analysis()
    elif page == "Prédictions":
        render_predictions()
    elif page == "Historique":
        render_history()
    elif page == "Statistiques":
        render_statistics()


if __name__ == "__main__":
    main()
