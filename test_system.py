#!/usr/bin/env python
"""Script de test complet du système de prédiction."""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR / "football_prediction"))

def test_imports():
    """Teste que tous les modules peuvent être importés."""
    print("📋 Test 1: Vérification des imports...")
    try:
        from prediction_service import get_prediction_service
        from data_loader import load_upcoming_matches, load_match_history, load_statistics
        print("✅ Tous les modules importés avec succès")
        return True
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False


def test_models():
    """Teste le chargement des modèles."""
    print("\n📋 Test 2: Vérification des modèles...")
    try:
        from prediction_service import get_prediction_service
        service = get_prediction_service()
        
        if not service.models:
            print("⚠️  Aucun modèle chargé (utilisation de fallback)")
        else:
            print(f"✅ Modèles chargés: {list(service.models.keys())}")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_data_loading():
    """Teste le chargement des données."""
    print("\n📋 Test 3: Vérification du chargement des données...")
    try:
        from data_loader import (
            load_upcoming_matches,
            load_match_history,
            load_statistics
        )
        
        matches = load_upcoming_matches()
        history = load_match_history()
        stats = load_statistics()
        
        print(f"✅ Matches à venir: {len(matches)}")
        print(f"✅ Historique: {len(history)} entrées")
        print(f"✅ Statistiques chargées")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_predictions():
    """Teste la génération de prédictions."""
    print("\n📋 Test 4: Test des prédictions...")
    try:
        from prediction_service import predict_match
        from data_loader import load_upcoming_matches
        
        matches = load_upcoming_matches()
        if matches:
            pred = predict_match(matches[0])
            print(f"✅ Prédiction générée: {pred['prediction']} (confiance: {pred['confidence']:.1f}%)")
            return True
        else:
            print("❌ Aucun match disponible")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_streamlit_integration():
    """Teste l'intégration Streamlit."""
    print("\n📋 Test 5: Test de l'intégration Streamlit...")
    try:
        import ast
        
        with open(BASE_DIR / "streamlit_app.py", 'r') as f:
            code = f.read()
        
        ast.parse(code)
        print("✅ Code Streamlit syntaxiquement correct")
        
        # Vérifier les imports
        required_imports = [
            'from data_loader import',
            'from prediction_service import'
        ]
        
        for required in required_imports:
            if required in code:
                print(f"✅ Import trouvé: {required}")
            else:
                print(f"❌ Import manquant: {required}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def main():
    """Lance tous les tests."""
    print("=" * 50)
    print("🧪 Tests du système de prédiction")
    print("=" * 50)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Modèles", test_models()))
    results.append(("Données", test_data_loading()))
    results.append(("Prédictions", test_predictions()))
    results.append(("Streamlit", test_streamlit_integration()))
    
    print("\n" + "=" * 50)
    print("📊 Résumé des tests")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name}: {status}")
    
    print(f"\nRésultat final: {passed}/{total} tests passés")
    
    if passed == total:
        print("\n🎉 Tous les tests sont passés! L'application est prête.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) ont échoué.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
