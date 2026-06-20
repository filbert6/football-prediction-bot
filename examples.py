#!/usr/bin/env python
"""
Exemple complet d'utilisation du Football Prediction Bot.
Montre comment:
1. Charger les données
2. Faire des prédictions
3. Analyser les résultats
"""

import sys
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR / "football_prediction"))

def example_1_basic_usage():
    """Exemple 1: Utilisation basique."""
    print("=" * 60)
    print("EXEMPLE 1: Utilisation basique")
    print("=" * 60)
    
    from prediction_service import predict_match
    
    # Créer un match
    match = {
        'home_team': 'Paris SG',
        'away_team': 'Marseille',
        'home_odds': 1.85,
        'away_odds': 4.20,
        'draw_odds': 3.50,
    }
    
    # Faire une prédiction
    prediction = predict_match(match)
    
    print(f"\nMatch: {match['home_team']} vs {match['away_team']}")
    print(f"Prédiction: {prediction['prediction']}")
    print(f"Confiance: {prediction['confidence']:.1f}%")
    print(f"  - Victoire domicile: {prediction['home_win_pct']:.1f}%")
    print(f"  - Match nul: {prediction['draw_pct']:.1f}%")
    print(f"  - Victoire extérieur: {prediction['away_win_pct']:.1f}%")


def example_2_multiple_predictions():
    """Exemple 2: Prédictions multiples."""
    print("\n" + "=" * 60)
    print("EXEMPLE 2: Prédictions multiples")
    print("=" * 60)
    
    from data_loader import load_upcoming_matches
    from prediction_service import predict_matches
    
    # Charger les matches
    matches = load_upcoming_matches()
    print(f"\nChargement de {len(matches)} matches...")
    
    # Faire des prédictions pour tous
    predictions = predict_matches(matches)
    
    # Afficher les résultats
    print("\n" + "─" * 60)
    print("PRÉDICTIONS")
    print("─" * 60)
    
    for pred in predictions:
        print(f"\n📍 {pred['league']} | {pred['date']}")
        print(f"   {pred['home_team']:20} vs {pred['away_team']:20}")
        print(f"   → Prédiction: {pred['prediction']:15} | Confiance: {pred['confidence']:5.1f}%")
        print(f"   → Cotes: {pred['home_odds']:.2f} / {pred['draw_odds']:.2f} / {pred['away_odds']:.2f}")


def example_3_historical_analysis():
    """Exemple 3: Analyse historique."""
    print("\n" + "=" * 60)
    print("EXEMPLE 3: Analyse historique")
    print("=" * 60)
    
    from data_loader import load_match_history, load_statistics
    
    # Charger l'historique
    history = load_match_history()
    stats = load_statistics()
    
    print(f"\nStatistiques globales:")
    print(f"  - Précision moyenne: {stats.get('accuracy', 'N/A')}%")
    print(f"  - Total de prédictions: {stats.get('total_predictions', 'N/A')}")
    print(f"  - Prédictions correctes: {stats.get('correct_predictions', 'N/A')}")
    print(f"  - Modèles actifs: {stats.get('models_active', 'N/A')}")
    
    if history:
        print(f"\n\nHistorique des {len(history)} derniers matches:")
        print("─" * 80)
        
        for item in history:
            result_emoji = "✅" if item['result'] == 'Correct' else "⚠️" if item['result'] == 'Partial' else "❌"
            print(f"{result_emoji} {item['home_team']:15} vs {item['away_team']:15} | "
                  f"Score: {item['score']:6} | "
                  f"Confiance: {item['confidence']:5.0f}%")


def example_4_league_analysis():
    """Exemple 4: Analyse par ligue."""
    print("\n" + "=" * 60)
    print("EXEMPLE 4: Analyse par ligue")
    print("=" * 60)
    
    from data_loader import load_upcoming_matches
    from prediction_service import predict_matches
    
    # Charger et prédire
    matches = load_upcoming_matches()
    predictions = predict_matches(matches)
    
    # Créer un DataFrame
    df = pd.DataFrame(predictions)
    
    if df.size > 0 and 'league' in df.columns:
        print("\nPronotics par ligue:")
        print("─" * 80)
        
        for league in df['league'].unique():
            league_matches = df[df['league'] == league]
            avg_confidence = league_matches['confidence'].mean()
            
            print(f"\n🏆 {league} ({len(league_matches)} matches)")
            print(f"   Confiance moyenne: {avg_confidence:.1f}%")
            
            for _, match in league_matches.iterrows():
                print(f"   • {match['home_team']} ({match['home_odds']:.2f}) vs "
                      f"{match['away_team']} ({match['away_odds']:.2f})")
                print(f"     → {match['prediction']} ({match['confidence']:.1f}%)")


def example_5_programmatic_filtering():
    """Exemple 5: Filtrage programmatique."""
    print("\n" + "=" * 60)
    print("EXEMPLE 5: Filtrage programmatique")
    print("=" * 60)
    
    from data_loader import load_upcoming_matches
    from prediction_service import predict_matches
    
    # Charger et prédire
    matches = load_upcoming_matches()
    predictions = predict_matches(matches)
    
    # Créer un DataFrame
    df = pd.DataFrame(predictions)
    
    # Filtrer par confiance > 80%
    high_confidence = df[df['confidence'] > 80]
    
    print(f"\nMatchs avec confiance > 80% ({len(high_confidence)} matches):")
    print("─" * 80)
    
    if len(high_confidence) > 0:
        for _, match in high_confidence.iterrows():
            print(f"✨ {match['home_team']} vs {match['away_team']}")
            print(f"   Prédiction: {match['prediction']} ({match['confidence']:.1f}% confiance)")
    else:
        print("Aucun match avec confiance > 80%")


def main():
    """Lance tous les exemples."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  🤖 Football Prediction Bot - Exemples d'utilisation".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    
    try:
        example_1_basic_usage()
        example_2_multiple_predictions()
        example_3_historical_analysis()
        example_4_league_analysis()
        example_5_programmatic_filtering()
        
        print("\n" + "=" * 60)
        print("✅ TOUS LES EXEMPLES EXÉCUTÉS AVEC SUCCÈS!")
        print("=" * 60)
        
        return 0
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
