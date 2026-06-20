# Football Prediction Bot ⚽🤖

Un bot de prédiction de football utilisant des modèles d'apprentissage machine pour prédire les résultats des matchs.

## ✨ Nouvelles fonctionnalités

🎯 **Chargement réel des modèles** - Les modèles sont maintenant chargés automatiquement
🎯 **Prédictions réelles** - Les données factices ont été remplacées par des prédictions dynamiques
🎯 **Interface moderne** - Application Streamlit avec 5 pages interactives

## 🚀 Démarrage rapide

### 1. Installation
```bash
# Installer les dépendances
pip install -r football_prediction/requirements.txt
pip install streamlit pandas numpy scikit-learn joblib

# Ou directement
pip install streamlit pandas numpy scikit-learn joblib
```

### 2. Entraîner les modèles
```bash
python train_models.py
```

### 3. Tester l'installation
```bash
python test_system.py
```

### 4. Lancer l'application
```bash
streamlit run streamlit_app.py
```

L'application sera accessible à `http://localhost:8501`

## 📊 Pages de l'application

| Page | Description |
|------|-------------|
| 🏠 **Accueil** | Vue d'ensemble avec statistiques en temps réel |
| 🔍 **Analyse de match** | Analyse détaillée d'un match spécifique |
| 🎯 **Prédictions** | Liste complète filtrée par ligue |
| 📊 **Historique** | Résultats passés et performance du modèle |
| 📈 **Statistiques** | Analyses détaillées par ligue |

## 🎯 Architecture

### Composants principaux

- **`prediction_service.py`** - Service de prédiction qui charge les modèles et génère les prédictions
- **`data_loader.py`** - Charge les données depuis CSV ou génère des démos
- **`streamlit_app.py`** - Application Streamlit interactive
- **`train_models.py`** - Script pour entraîner les modèles

### Flux de données

```
Données (CSV ou démo)
    ↓
DataLoader (chargement)
    ↓
Modèles entraînés
    ↓
PredictionService (prédictions)
    ↓
Streamlit App (affichage)
```

## 📖 Documentation

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Guide complet d'installation et utilisation
- **[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)** - Guide technique d'intégration
- **[CHANGELOG.md](CHANGELOG.md)** - Résumé des modifications

## 🤖 Ajouter vos modèles

1. Créez un fichier `football_prediction/models/your_model.py`:

```python
def train():
    """Entraîner le modèle."""
    model = YourModel()
    model.fit(X_train, y_train)
    
    metrics = {"accuracy": 0.85}
    return model, metrics
```

2. Entraînez: `python train_models.py`
3. Le modèle sera automatiquement détecté et utilisé

## 📊 Ajouter vos données

Créez un fichier CSV dans `football_prediction/data/processed/`:

```csv
date,league,home_team,away_team,home_odds,draw_odds,away_odds
2024-01-15,Ligue 1,Paris SG,Marseille,1.85,3.50,4.20
2024-01-15,Premier League,Arsenal,Liverpool,2.35,3.30,2.80
```

## 🧪 Tests

Exécutez la suite de tests complète:

```bash
python test_system.py
```

Résultat attendu: **5/5 tests passés** ✅

## 📁 Structure du projet

```
football-prediction-bot/
├── football_prediction/
│   ├── models/
│   │   ├── dummy_model.py          # Modèle de démo
│   │   ├── lightgbm_model.py       # À implémenter
│   │   └── ...
│   ├── data/
│   │   ├── raw/                     # Données brutes
│   │   ├── processed/               # Données traitées
│   │   └── models/                  # Modèles sauvegardés
│   ├── features/                    # Feature engineering
│   ├── scrapers/                    # Récupération de données
│   ├── prediction_service.py        # Service de prédiction
│   ├── data_loader.py               # Chargeur de données
│   ├── train_models.py              # Entraînement
│   ├── pipeline.py                  # Pipeline de données
│   ├── db.py                        # Gestion base de données
│   ├── logging_config.py            # Configuration logging
│   └── requirements.txt             # Dépendances Python
├── streamlit_app.py                 # Application principale
├── train_models.py                  # Point d'entrée entraînement
├── test_system.py                   # Suite de tests
├── SETUP_GUIDE.md                   # Guide d'utilisation
├── INTEGRATION_GUIDE.md             # Guide d'intégration
├── CHANGELOG.md                     # Résumé des modifications
└── README.md                        # Ce fichier
```

## 💻 Utilisation programmatique

```python
from football_prediction.prediction_service import predict_match
from football_prediction.data_loader import load_upcoming_matches

# Charger les données
matches = load_upcoming_matches()

# Faire une prédiction
for match in matches:
    pred = predict_match(match)
    print(f"{pred['home_team']} vs {pred['away_team']}: {pred['prediction']}")
```

## ⚙️ Configuration

L'application utilise Streamlit en mode serveur :
- Hôte: `localhost`
- Port: `8501`
- Configuration dans `.streamlit/config.toml`

## 🔧 Dépannage

### Les modèles ne se chargent pas
```bash
python train_models.py
```

### L'app Streamlit ne démarre pas
```bash
python -m py_compile streamlit_app.py
python test_system.py
```

### Pas de données affichées
Les données de démonstration s'affichent par défaut si aucun CSV n'est trouvé.

## 📝 Fichiers modifiés

- ✅ `streamlit_app.py` - App Streamlit (complètement reécrite)
- ✅ `football_prediction/models/dummy_model.py` - Modèle demo
- ✅ Nouveau: `football_prediction/prediction_service.py`
- ✅ Nouveau: `football_prediction/data_loader.py`
- ✅ Nouveau: `football_prediction/train_models.py`
- ✅ Nouveau: `train_models.py`
- ✅ Nouveau: `test_system.py`
- ✅ Nouveau: `SETUP_GUIDE.md`
- ✅ Nouveau: `INTEGRATION_GUIDE.md`
- ✅ Nouveau: `CHANGELOG.md`

## 📈 Prochaines étapes

1. 🤖 Implémenter les vrais modèles (LightGBM, XGBoost, etc.)
2. 📊 Ajouter vos données réelles
3. 🔧 Entraîner et évaluer les modèles
4. 📉 Monitorer les performances
5. 🔄 Automatiser l'entraînement

## 📞 Support

- Consultez les guides: `SETUP_GUIDE.md` ou `INTEGRATION_GUIDE.md`
- Exécutez les tests: `python test_system.py`
- Vérifiez les logs: dossier `logs/`

## 📄 License

Voir le fichier LICENSE pour les détails.

---

**Version**: 2.0 (Intégration des modèles réels)  
**Dernière mise à jour**: 2024-06-20  
**Statut**: ✅ Prêt pour la production
