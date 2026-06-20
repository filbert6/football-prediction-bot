"""Backtest module

Expect input CSV with columns:
- pred_prob: predicted probability for the bet (float 0..1)
- odds: decimal odds for the bet (float)
- actual: 1 if outcome happened, 0 otherwise

Example usage:
python backtest.py data/processed/predictions.csv

"""
import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import log_loss, brier_score_loss, accuracy_score
from datetime import datetime
from pathlib import Path

try:
    from .db import init_db, get_session, save_backtest
    from .logging_config import setup_logging
except ImportError:
    ROOT_DIR = Path(__file__).resolve().parent
    if str(ROOT_DIR) not in sys.path:
        sys.path.insert(0, str(ROOT_DIR))
    try:
        from db import init_db, get_session, save_backtest
        from logging_config import setup_logging
    except ImportError:
        sys.path.insert(0, str(ROOT_DIR.parent))
        from db import init_db, get_session, save_backtest
        from logging_config import setup_logging

logger = setup_logging()


def compute_metrics(df):
    # Filter valid rows
    df = df.dropna(subset=["pred_prob", "odds", "actual"]) 
    df["stake"] = 1.0
    # Select value bets where expected value positive
    df["expected_value"] = df["pred_prob"] * df["odds"] - 1
    bets = df[df["expected_value"] > 0].copy()
    if bets.empty:
        logger.warning("No value bets found")
        bets = df.copy()

    # returns per bet: profit = (odds - 1) * stake if won else -stake
    bets["profit"] = np.where(bets["actual"] == 1, (bets["odds"] - 1) * bets["stake"], -bets["stake"])

    total_stake = bets["stake"].sum()
    total_profit = bets["profit"].sum()
    roi = total_profit / total_stake if total_stake else 0.0
    yield_pct = total_profit / total_stake if total_stake else 0.0
    accuracy = (bets["actual"] == (bets["pred_prob"] > 0.5)).mean()

    # Probabilities and actuals for metrics
    try:
        ll = log_loss(bets["actual"], bets["pred_prob"], labels=[0,1])
    except Exception:
        ll = float("nan")
    try:
        brier = brier_score_loss(bets["actual"], bets["pred_prob"])
    except Exception:
        brier = float("nan")

    # equity curve and drawdown
    eq = (bets["profit"].cumsum()).rename("equity")
    running_max = eq.cummax()
    drawdown = (eq - running_max)
    max_drawdown = drawdown.min()

    metrics = {
        "n_bets": int(len(bets)),
        "total_stake": float(total_stake),
        "total_profit": float(total_profit),
        "roi": float(roi),
        "yield": float(yield_pct),
        "accuracy": float(accuracy),
        "log_loss": float(ll) if not np.isnan(ll) else None,
        "brier_score": float(brier) if not np.isnan(brier) else None,
        "max_drawdown": float(max_drawdown),
    }
    return metrics, eq, drawdown


def plot_results(eq, drawdown, out_dir="reports", name="backtest"):
    os.makedirs(out_dir, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    fig, ax = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    eq.plot(ax=ax[0], title="Equity Curve")
    ax[0].set_ylabel("Profit")
    drawdown.plot(ax=ax[1], title="Drawdown", color="red")
    ax[1].set_ylabel("Drawdown")
    plt.tight_layout()
    out_path = os.path.join(out_dir, f"{name}_{ts}.png")
    fig.savefig(out_path)
    plt.close(fig)
    logger.info(f"Saved backtest plot to {out_path}")
    return out_path


def run(input_csv, report_name="backtest"):
    df = pd.read_csv(input_csv)
    metrics, eq, drawdown = compute_metrics(df)
    plot_path = plot_results(eq, drawdown, out_dir="reports", name=report_name)

    # Save metrics to DB if available
    try:
        engine = init_db()
        session = get_session(engine)
        save_backtest(session, name=report_name, metrics=metrics)
    except Exception:
        logger.debug("DB not available; skipping save")

    # write a short report
    out_report = os.path.join("reports", f"{report_name}_metrics_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.md")
    with open(out_report, "w") as f:
        f.write("# Backtest Report\n\n")
        for k, v in metrics.items():
            f.write(f"- {k}: {v}\n")
        f.write(f"\nPlot: {plot_path}\n")
    logger.info(f"Saved report to {out_report}")
    return metrics, plot_path, out_report


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python backtest.py path/to/predictions.csv")
        sys.exit(1)
    inp = sys.argv[1]
    run(inp)
