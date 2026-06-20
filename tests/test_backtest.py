import pandas as pd
import numpy as np
from football_prediction.backtest import compute_metrics


def test_compute_metrics_simple():
    # Create synthetic data: 10 bets, 5 wins
    n = 10
    df = pd.DataFrame({
        "pred_prob": np.linspace(0.4, 0.9, n),
        "odds": np.linspace(1.5, 2.5, n),
        "actual": [1 if i < 5 else 0 for i in range(n)]
    })
    metrics, eq, drawdown = compute_metrics(df)
    assert metrics["n_bets"] > 0
    assert "roi" in metrics
    assert isinstance(metrics["accuracy"], float)
