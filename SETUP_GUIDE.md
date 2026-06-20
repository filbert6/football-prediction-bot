# 🎯 Football Prediction Bot - Guide Complet

## 📌 Vue d'ensemble

Le Football Prediction Bot utilise des modèles d'apprentissage machine pour prédire les résultats des matchs de football. Le système est maintenant entièrement intégré avec :

- ✅ **Chargement réel des modèles** depuis `models_output/`
- ✅ **Prédictions générées dynamiquement** basées sur les modèles ou les cotes
- ✅ **Données réelles** chargées depuis les fichiers CSV
- ✅ **Interface Streamlit moderne** affichant toutes les prédictions

## 🚀 Démarrage rapide

### 1. Installation des dépendances
```bash
pip install -r football_prediction/requirements.txt
pip install streamlit pandas numpy scikit-learn joblib
```

### 2. Entraîner les modèles
```bash
python train_models.py
```
Cela entraîne et sauvegarde tous les modèles dans `football_prediction/models_output/`.

### 3. Lancer l'application
```bash
streamlit run streamlit_app.py
```
L'application démarrera sur `http://localhost:8501`

### 4. Vérifier l'installation
```bash
python test_system.py
```

## 📁 Structure du projet

### Composants principaux

#### 1. **Service de Prédiction** 
```
football_prediction/prediction_service.py
```
- Charge tous les modèles entraînés
- Génère des prédictions pour les matches
- Agrège les prédictions de plusieurs modèles
- Fallback sur les cotes de marché

**Utilisation programmatique:**
```python
from football_prediction.prediction_service import predict_match

match = {
    'home_team': 'Paris SG',
    'away_team': 'Marseille',
    'home_odds': 1.85,
    'away_odds': 4.20,
    'draw_odds': 3.50,
    'home_elo': 1850,
    'away_elo': 1620,
}

prediction = predict_match(match)
# {
#     'prediction': 'Paris SG',
#     'home_win_pct': 52.3,
#     'draw_pct': 25.1,
#     'away_win_pct': 22.6,
#     'confidence': 52.3
# }
```

#### 2. **Data Loader**
```
football_prediction/data_loader.py
```
- Charge les données réelles depuis les CSV
- Génère des données de démonstration
- Fournit matches, historique et statistiques

**Utilisation:**
```python
from football_prediction.data_loader import (
    load_upcoming_matches,
    load_match_history,
    load_statistics
)

matches = load_upcoming_matches()
history = load_match_history()
stats = load_statistics()
```

#### 3. **Modèles**
```
football_prediction/models/
├── dummy_model.py       # Modèle de démonstration
├── lightgbm_model.py    # À implémenter
├── xgboost_model.py     # À implémenter
└── ...
```

#### 4. **Application Streamlit**
```
streamlit_app.py
```
Pages disponibles:
- 🏠 **Accueil** - Vue d'ensemble avec statistiques
- 🔍 **Analyse de match** - Détails d'un match spécifique
- 🎯 **Prédictions** - Liste de tous les matchs à prédire
- 📊 **Historique** - Résultats passés et performance
- 📈 **Statistiques** - Analyses par ligue

## 🔧 Ajouter vos propres données

### Format des données de matches
Créez un fichier CSV dans `football_prediction/data/processed/` :

```csv
date,league,home_team,away_team,home_odds,draw_odds,away_odds,home_elo,away_elo,home_form,away_form,home_attack,away_attack,home_defense,away_defense
2024-01-15,Ligue 1,Paris SG,Marseille,1.85,3.50,4.20,1850,1620,0.72,0.58,0.78,0.65,0.82,0.68
```

Colonnes optionnelles:
- `home_elo`, `away_elo` - Cotes Elo
- `home_form`, `away_form` - Forme récente (0-1)
- `home_attack`, `away_attack` - Force offensive (0-1)
- `home_defense`, `away_defense` - Force défensive (0-1)

### Format de l'historique
Fichier avec `*history*` dans le nom :

```csv
date,home_team,away_team,score,prediction,result,confidence
2024-01-10,PSG,Nantes,3-1,PSG,Correct,87
2024-01-08,Arsenal,Fulham,4-1,Arsenal,Correct,91
```

## 🤖 Créer un nouveau modèle

1. Créez un fichier dans `football_prediction/models/` :

```python
# football_prediction/models/my_model.py

import numpy as np
from sklearn.ensemble import RandomForestClassifier

def train():
    """Entraîner et retourner le modèle."""
    # Générer les données (à remplacer par vos vraies données)
    X_train = np.random.randn(1000, 10)
    y_train = np.random.randint(0, 3, 1000)
    
    # Créer et entraîner le modèle
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Calculer les métriques
    metrics = {
        "accuracy": model.score(X_train, y_train),
        "precision": 0.75,
        "recall": 0.72,
        "f1": 0.73
    }
    
    return model, metrics
```

2. Le script `train_models.py` découvrira automatiquement votre modèle
3. Entraînez avec `python train_models.py`

## 📊 Architecture du flux

```
┌─────────────────────┐
│  Données réelles    │
│  ou Démo            │
└──────────┬──────────┘
           │
           ▼
┌──────────────────────────┐
│   DataLoader             │
│  - CSV files             │
│  - Demo data generator   │
└──────────┬───────────────┘
           │
      ┌────┴────────────────────┐
      │                         │
      ▼                         ▼
┌─────────────┐        ┌──────────────────┐
│  Matches    │        │   Statistics     │
│  History    │        │   Analysis       │
└─────┬───────┘        └──────────────────┘
      │
      ▼
┌───────────────────────────────┐
│  PredictionService            │
│ - Load models from joblib     │
│ - Aggregate predictions       │
│ - Fallback to market odds     │
└───────────┬───────────────────┘
            │
            ▼
    ┌───────────────┐
    │   Predictions │
    │  - Home Win % │
    │  - Draw %     │
    │  - Away Win % │
    │  - Confidence │
    └───────┬───────┘
            │
            ▼
┌───────────────────────────────┐
│   Streamlit Application       │
│  - Home Page                  │
│  - Match Analysis             │
│  - Predictions                │
│  - History                    │
│  - Statistics                 │
└───────────────────────────────┘
```

## 🧪 Test du système

Exécutez le suite de tests complète :

```bash
python test_system.py
```

Tests inclus:
- ✅ Vérification des imports
- ✅ Chargement des modèles
- ✅ Chargement des données
- ✅ Génération des prédictions
- ✅ Intégration Streamlit

## 📈 Exemple d'utilisation complète

```python
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR / "football_prediction"))

from prediction_service import predict_matches
from data_loader import load_upcoming_matches, load_statistics

# Charger les données
matches = load_upcoming_matches()
stats = load_statistics()

print(f"Précision moyenne: {stats['accuracy']}%")
print(f"Total de prédictions: {stats['total_predictions']}")

# Générer les prédictions
predictions = predict_matches(matches)

# Afficher les résultats
for pred in predictions:
    print(f"\n{pred['home_team']} vs {pred['away_team']}")
    print(f"  Prédiction: {pred['prediction']} ({pred['confidence']:.1f}%)")
    print(f"  Victoire domicile: {pred['home_win_pct']:.1f}%")
    print(f"  Match nul: {pred['draw_pct']:.1f}%")
    print(f"  Victoire extérieur: {pred['away_win_pct']:.1f}%")
```

## 🔐 Sécurité et Performance

- ✅ **Cache Streamlit** - Les données sont mises en cache avec TTL 1h
- ✅ **Gestion d'erreurs** - Fonctionnement gracieux même sans modèles
- ✅ **Optimisation** - Chargement lazy des modèles
- ✅ **Logging** - Suivi complet des opérations

## 🐛 Dépannage

### Les modèles ne se chargent pas
```bash
# Vérifier que les modèles sont entraînés
ls football_prediction/models_output/

# Réentraîner si nécessaire
python train_models.py
```

### L'application Streamlit ne démarre pas
```bash
# Vérifier les erreurs
python -m py_compile streamlit_app.py

# Exécuter les tests
python test_system.py
```

### Pas de données affichées
- Vérifiez que les fichiers CSV sont dans `football_prediction/data/processed/`
- Les données de démonstration s'affichent par défaut si aucun fichier n'est trouvé

## 📝 Fichiers modifiés/créés

- ✅ `football_prediction/prediction_service.py` - Service de prédiction
- ✅ `football_prediction/data_loader.py` - Chargeur de données
- ✅ `football_prediction/models/dummy_model.py` - Modèle de démo
- ✅ `football_prediction/train_models.py` - Script de formation
- ✅ `train_models.py` - Point d'entrée
- ✅ `streamlit_app.py` - Application mise à jour
- ✅ `test_system.py` - Suite de tests
- ✅ `INTEGRATION_GUIDE.md` - Guide d'intégration

## 🎯 Prochaines étapes

1. **Implémenter les modèles réels** - LightGBM, XGBoost, etc.
2. **Ajouter vos données** - CSV dans `data/processed/`
3. **Entraîner les modèles** - `python train_models.py`
4. **Ajuster les paramètres** - Tuning des hyperparamètres
5. **Monitorer les performances** - Suivi des statistiques

## 📞 Support

Pour toute question ou problème, consultez:
- `INTEGRATION_GUIDE.md` - Guide d'intégration détaillé
- `test_system.py` - Aide au dépannage
- Logs dans `logs/` - Suivi détaillé
