# Football Prediction Bot — Professionalized

Ce dossier contient les scripts pour orchestrer la mise à jour des données, l'entraînement des modèles, les backtests et la gestion opérationnelle.

Quick start

1. Copier `.env.example` -> `.env` et ajuster si besoin.
2. Installer les dépendances:

```bash
python -m pip install --upgrade pip
pip install -r football_prediction/requirements-dev.txt
```

3. Lancer le scheduler (bloquant):

```bash
python -m football_prediction.scheduler
```

4. Exécuter le pipeline manuellement:

```bash
python -m football_prediction.pipeline
```

5. Backtest (exemple):

```bash
python -m football_prediction.backtest data/processed/predictions.csv
```

CI/CD

Le workflow GitHub Actions `.github/workflows/ci.yml` exécute les tests.

Notes

- `pipeline.py` tentera d'appeler `train()` dans chaque module `models/*_model.py` s'il existe.
- Les modèles entraînés sont sauvés dans `football_prediction/models_output`.
- La base SQLite par défaut est `football_prediction.db`.
