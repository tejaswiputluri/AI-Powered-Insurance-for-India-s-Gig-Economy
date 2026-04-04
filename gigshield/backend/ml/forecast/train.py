"""
LSTM Forecast — Training script.
Trains on 3 years of synthetic Bengaluru weather data.

Dataset: data/synthetic_weather.csv
Loss: BCELoss (binary cross-entropy)
Optimizer: Adam, lr=1e-3
Epochs: 100, batch_size=32
"""

import logging
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from pathlib import Path
from model import DisruptionForecaster

logger = logging.getLogger(__name__)

# Config
SEQUENCE_LENGTH = 90
OUTPUT_DAYS = 7
EPOCHS = 100
BATCH_SIZE = 32
LEARNING_RATE = 1e-3
MODEL_SAVE_PATH = Path(__file__).parent / "forecast_model.pt"
DATA_PATH = Path(__file__).parent.parent.parent.parent / "data" / "synthetic_weather.csv"


def prepare_sequences(df: pd.DataFrame, zone_id: str):
    """Create sliding window sequences for a single zone."""
    zone_data = df[df["zone_id"] == zone_id].sort_values("date").reset_index(drop=True)

    features = ["max_rainfall_mm", "mean_aqi", "order_drop_pct",
                 "day_of_week", "month", "is_festival", "historical_claim_count"]
    target = "disrupted"

    X, y = [], []
    values = zone_data[features].values
    targets = zone_data[target].values

    for i in range(len(values) - SEQUENCE_LENGTH - OUTPUT_DAYS + 1):
        X.append(values[i:i + SEQUENCE_LENGTH])
        y.append(targets[i + SEQUENCE_LENGTH:i + SEQUENCE_LENGTH + OUTPUT_DAYS])

    return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32)


def train():
    """Train the LSTM forecast model."""
    if not DATA_PATH.exists():
        logger.error(f"Training data not found: {DATA_PATH}")
        logger.info("Run data/synthetic_weather.py first to generate training data.")
        return

    df = pd.read_csv(DATA_PATH)
    zones = df["zone_id"].unique()

    all_X, all_y = [], []
    for zone in zones:
        X, y = prepare_sequences(df, zone)
        all_X.append(X)
        all_y.append(y)

    X_train = np.concatenate(all_X)
    y_train = np.concatenate(all_y)

    dataset = TensorDataset(
        torch.from_numpy(X_train),
        torch.from_numpy(y_train),
    )
    loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = DisruptionForecaster().to(device)
    criterion = nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

    for epoch in range(EPOCHS):
        total_loss = 0
        for batch_X, batch_y in loader:
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)
            optimizer.zero_grad()
            output = model(batch_X)
            loss = criterion(output, batch_y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        if (epoch + 1) % 10 == 0:
            avg_loss = total_loss / len(loader)
            print(f"Epoch {epoch+1}/{EPOCHS} — Loss: {avg_loss:.4f}")

    torch.save(model.state_dict(), MODEL_SAVE_PATH)
    print(f"Model saved to {MODEL_SAVE_PATH}")


if __name__ == "__main__":
    train()
