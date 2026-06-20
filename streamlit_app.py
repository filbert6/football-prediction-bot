import datetime
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st

# Ajouter le répertoire football_prediction au chemin
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR / "football_prediction") not in sys.path:
    sys.path.insert(0, str(BASE_DIR / "football_prediction"))

from data_loader import load_upcoming_matches, load_match_history, load_statistics
from prediction_service import predict_matches

st.set_page_config(
    page_title="Football Prediction Bot",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(ttl=3600)
def get_upcoming_matches():
    """Charge les matches à venir avec prédictions réelles."""
    try:
        matches = load_upcoming_matches()
        # Ajouter les prédictions pour chaque match
        predictions = predict_matches(matches)
        
        # Convertir en DataFrame pour affichage
        df_data = []
        for pred in predictions:
            df_data.append({
                "Date": pred.get("date"),
                "League": pred.get("league", ""),
                "Home Team": pred.get("home_team", ""),
                "Away Team": pred.get("away_team", ""),
                "Home Odds": pred.get("home_odds", 0),
                "Draw Odds": pred.get("draw_odds", 0),
                "Away Odds": pred.get("away_odds", 0),
                "Prediction": pred.get("prediction", ""),
                "Win % Home": pred.get("home_win_pct", 0),
                "Draw %": pred.get("draw_pct", 0),
                "Win % Away": pred.get("away_win_pct", 0),
                "Confidence": pred.get("confidence", 0),
            })
        
        return pd.DataFrame(df_data)
    except Exception as e:
        st.error(f"Erreur lors du chargement des matches: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def get_match_history():
    """Charge l'historique réel des matches."""
    try:
        history = load_match_history()
        df_data = []
        for item in history:
            df_data.append({
                "Date": item.get("date"),
                "Home Team": item.get("home_team", ""),
                "Away Team": item.get("away_team", ""),
                "Score": item.get("score", ""),
                "Prediction": item.get("prediction", ""),
                "Result": item.get("result", ""),
                "Model Confidence": item.get("confidence", 0),
            })
        
        return pd.DataFrame(df_data)
    except Exception as e:
        st.error(f"Erreur lors du chargement de l'historique: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def get_statistics_data():
    """Charge les statistiques réelles."""
    try:
        stats = load_statistics()
        return stats
    except Exception as e:
        st.error(f"Erreur lors du chargement des statistiques: {e}")
        return {}


def render_home():
    st.title("Football Prediction Bot")
    st.write(
        "Bienvenue dans le bot de prédiction de football. "
        "Cette application utilise des modèles d'apprentissage machine pour prédire les résultats des matchs."
    )

    st.markdown("---")

    stats = get_statistics_data()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Précision moyenne", f"{stats.get('accuracy', 0)}%")
    col2.metric("Prédictions totales", stats.get("total_predictions", 0))
    col3.metric("Prédictions correctes", stats.get("correct_predictions", 0))
    col4.metric("Modèles actifs", stats.get("models_active", 0))

    st.markdown("### Aperçu des prochains matchs")
    upcoming = get_upcoming_matches()
    if not upcoming.empty:
        st.dataframe(upcoming.style.format({"Home Odds": "{:.2f}", "Draw Odds": "{:.2f}", "Away Odds": "{:.2f}", "Confidence": "{:.0f}"}))
    else:
        st.warning("Aucun match à venir trouvé.")

    st.markdown("### Tendances de performance")
    try:
        history = get_match_history()
        if not history.empty:
            # Créer un graphique de tendance simple
            history_sorted = history.sort_values("Date")
            trend_data = history_sorted.groupby("Date")["Model Confidence"].mean()
            st.line_chart(trend_data)
        else:
            st.info("Aucune donnée historique disponible.")
    except Exception as e:
        st.error(f"Erreur lors du chargement des tendances: {e}")

    st.markdown("---")
    st.info(
        "Les modèles utilisent les données réelles lorsqu'elles sont disponibles. "
        "Si aucun modèle n'est entraîné, les prédictions sont basées sur les probabilités implicites des cotes."
    )


def render_match_analysis():
    st.title("Analyse de match")
    matches = get_upcoming_matches()
    
    if matches.empty:
        st.warning("Aucun match disponible pour l'analyse.")
        return
    
    match_options = matches["Home Team"] + " vs " + matches["Away Team"]
    selected = st.selectbox("Sélectionnez un match à analyser", match_options)
    match = matches.loc[matches["Home Team"] + " vs " + matches["Away Team"] == selected].iloc[0]

    st.subheader(f"Analyse détaillée : {match['Home Team']} vs {match['Away Team']}")
    st.write(f"**Compétition:** {match['League']}  •  **Date:** {match['Date']}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Probabilité domicile", f"{match['Win % Home']:.1f}%")
    col2.metric("Probabilité match nul", f"{match['Draw %']:.1f}%")
    col3.metric("Probabilité extérieur", f"{match['Win % Away']:.1f}%")

    st.markdown("### Raisons de la prédiction")
    st.write(
        "- **Analyse des modèles** : utilisation de multiples algorithmes ML pour améliorer les prédictions.\n"
        "- **Avantage domicile** : les équipes jouent mieux chez elles dans les compétitions majeures.\n"
        "- **Facteurs statistiques** : forme récente, Elo, attaque/défense, confrontations directes.\n"
        "- **Cotes du marché** : intégration des cotes pour améliorer la calibration des probabilités."
    )

    st.markdown("### Confiance du modèle")
    st.metric("Confiance globale", f"{match['Confidence']:.1f}%")

    st.markdown("### Détails de prédiction")
    st.write(
        f"Le modèle recommande **{match['Prediction']}** avec une confiance de **{match['Confidence']:.1f}%**. "
        "Cette prédiction est basée sur l'analyse des données historiques et des facteurs statistiques."
    )


def render_predictions():
    st.title("Prédictions")
    matches = get_upcoming_matches()
    
    if matches.empty:
        st.warning("Aucun match à prédire.")
        return
    
    leagues = matches["League"].unique().tolist()
    selected_league = st.selectbox("Filtrer par ligue", ["Toutes"] + sorted(leagues))

    if selected_league != "Toutes":
        matches = matches[matches["League"] == selected_league]

    st.markdown("### Prédictions des prochains matchs")
    display_df = matches.copy()
    st.dataframe(display_df.style.format(
        {"Home Odds": "{:.2f}", "Draw Odds": "{:.2f}", "Away Odds": "{:.2f}", 
         "Win % Home": "{:.1f}%", "Draw %": "{:.1f}%", "Win % Away": "{:.1f}%", 
         "Confidence": "{:.1f}%"}
    ))

    if len(matches) > 0:
        st.markdown("### Top 3 des prédictions les plus fiables")
        top3 = matches.sort_values(by="Confidence", ascending=False).head(3)
        for idx, (_, row) in enumerate(top3.iterrows(), 1):
            st.write(f"**{idx}. {row['Home Team']} vs {row['Away Team']}** — Prédiction : {row['Prediction']} ({row['Confidence']:.1f}% confiance)")

    st.markdown("### Distribution des prédictions")
    outcome_counts = matches["Prediction"].value_counts().rename_axis("Prédiction").reset_index(name="Nombre")
    if not outcome_counts.empty:
        st.bar_chart(outcome_counts.set_index("Prédiction"))


def render_history():
    st.title("Historique")
    history = get_match_history()
    
    if history.empty:
        st.warning("Aucune donnée historique disponible.")
        return
    
    st.markdown("### Résultats récents et performance du modèle")
    st.dataframe(history)

    st.markdown("### Évolution de la confiance")
    history_sorted = history.sort_values("Date")
    history_chart = history_sorted.copy()
    history_chart["Match"] = history_chart["Home Team"] + " vs " + history_chart["Away Team"]
    history_chart = history_chart.set_index("Match")
    st.line_chart(history_chart[["Model Confidence"]])

    st.markdown("### Résumé")
    if len(history) > 0:
        correct = (history["Result"] == "Correct").sum()
        partial = (history["Result"] == "Partial").sum()
        avg_confidence = history["Model Confidence"].mean()
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Confiance moyenne", f"{avg_confidence:.1f}%")
        col2.metric("Prédictions correctes", f"{correct}/{len(history)}")
        col3.metric("Prédictions partielles", partial)
        col4.metric("Taux de succès", f"{((correct + partial*0.5)/len(history)*100):.1f}%")


def render_statistics():
    st.title("Statistiques")
    matches = get_upcoming_matches()
    
    if matches.empty:
        st.warning("Aucune donnée disponible pour les statistiques.")
        return

    st.markdown("### Résumé des probabilités")
    summary_df = matches[["Home Team", "Away Team", "Win % Home", "Draw %", "Win % Away"]].copy()
    st.dataframe(summary_df.style.format(
        {"Win % Home": "{:.1f}%", "Draw %": "{:.1f}%", "Win % Away": "{:.1f}%"}
    ))

    st.markdown("### Indicateurs du modèle")
    stat_data = {
        "Confiance moyenne (%)": f"{matches['Confidence'].mean():.1f}",
        "Matchs modélisés": len(matches),
        "Prédictions à plus de 80%": (matches["Confidence"] > 80).sum(),
        "Prédictions à plus de 90%": (matches["Confidence"] > 90).sum(),
    }
    stat_df = pd.DataFrame(list(stat_data.items()), columns=["Métrique", "Valeur"])
    st.table(stat_df)

    st.markdown("### Performance par ligue")
    if "League" in matches.columns and len(matches) > 0:
        league_stats = matches.groupby("League")["Confidence"].mean().round(1).reset_index()
        league_stats.columns = ["Ligue", "Confiance moyenne (%)"]
        st.bar_chart(league_stats.set_index("Ligue"))


def main():
    try:
        render_app()
    except Exception as exc:
        st.error("Une erreur inattendue est survenue lors du chargement de l'application.")
        st.exception(exc)


def render_app():
    with st.sidebar:
        st.markdown("# Navigation")
        page = st.radio(
            "Choisissez une page",
            ["Accueil", "Analyse de match", "Prédictions", "Historique", "Statistiques"],
        )
        st.markdown("---")
        st.write("Application de prédiction de football avec modèles d'apprentissage machine.")

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
