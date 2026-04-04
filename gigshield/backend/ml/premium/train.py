"""
FT-Transformer Training Script — trains premium pricing model on 50k synthetic riders.
Output: saves model weights to ml/premium/model_weights.pt
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
import pandas as pd
import numpy as np
from pathlib import Path
from model import FTTransformer, create_model


FEATURE_COLS = [
    'zone_risk_score',
    'aqi_exposure_score',
    'work_hours_per_day',
    'work_days_per_week',
    'season_multiplier',
    'claim_history_count',
    'daily_earning_bucket',
]


def train():
    """Train FT-Transformer on synthetic rider data."""
    data_path = Path(__file__).parent.parent.parent.parent / "data" / "synthetic_riders.csv"

    if not data_path.exists():
        print("Generating synthetic data first...")
        from synthetic_data import generate_synthetic_riders
        df = generate_synthetic_riders()
        df.to_csv(data_path, index=False)
    else:
        df = pd.read_csv(data_path)

    print(f"Training data: {len(df)} samples")

    # Prepare tensors
    X = df[FEATURE_COLS].values.astype(np.float32)
    y = df['target_premium_paise'].values.astype(np.float32).reshape(-1, 1)

    # Normalize features
    X_mean = X.mean(axis=0)
    X_std = X.std(axis=0) + 1e-8
    X = (X - X_mean) / X_std

    # Save normalization params
    norm_path = Path(__file__).parent / "norm_params.npz"
    np.savez(norm_path, mean=X_mean, std=X_std)

    # Split
    n_train = int(0.8 * len(X))
    X_train, X_val = X[:n_train], X[n_train:]
    y_train, y_val = y[:n_train], y[n_train:]

    # Create data loaders
    train_ds = TensorDataset(torch.FloatTensor(X_train), torch.FloatTensor(y_train))
    val_ds = TensorDataset(torch.FloatTensor(X_val), torch.FloatTensor(y_val))
    train_loader = DataLoader(train_ds, batch_size=256, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=256)

    # Device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on: {device}")

    # Model
    model = create_model(n_features=7).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-5)
    criterion = nn.MSELoss()

    # Training loop
    best_val_loss = float('inf')
    for epoch in range(50):
        model.train()
        train_loss = 0
        for X_batch, y_batch in train_loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)

            optimizer.zero_grad()
            pred, _ = model(X_batch)
            loss = criterion(pred, y_batch)
            loss.backward()
            optimizer.step()

            train_loss += loss.item()

        train_loss /= len(train_loader)

        # Validation
        model.eval()
        val_loss = 0
        with torch.no_grad():
            for X_batch, y_batch in val_loader:
                X_batch, y_batch = X_batch.to(device), y_batch.to(device)
                pred, _ = model(X_batch)
                val_loss += criterion(pred, y_batch).item()
        val_loss /= len(val_loader)

        if (epoch + 1) % 5 == 0:
            print(f"Epoch {epoch+1:3d} | Train Loss: {train_loss:10.2f} | Val Loss: {val_loss:10.2f}")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            model_path = Path(__file__).parent / "model_weights.pt"
            torch.save(model.state_dict(), model_path)

    print(f"\n✅ Best validation loss: {best_val_loss:.2f}")
    print(f"✅ Model saved to ml/premium/model_weights.pt")


if __name__ == "__main__":
    train()
