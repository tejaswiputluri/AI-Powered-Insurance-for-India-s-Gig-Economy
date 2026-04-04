"""
LSTM Disruption Forecaster — 3-layer LSTM model for predicting next 7 days'
disruption probability per Bengaluru zone.

Input sequence: 90 days of daily features per zone (sliding window)
Features per day: max_rainfall_mm, mean_aqi, order_drop_pct, day_of_week,
                  month, is_festival, historical_claim_count
Total input: 90 × 7 = 630 per zone

Architecture:
  LSTM(input_size=7, hidden_size=128, num_layers=3, dropout=0.2, batch_first=True)
  Linear(128, 7) → outputs disruption probability for next 7 days
  Sigmoid activation on output
"""

import torch
import torch.nn as nn


class DisruptionForecaster(nn.Module):
    """3-layer LSTM model for zone-level disruption forecasting."""

    def __init__(
        self,
        input_size: int = 7,
        hidden_size: int = 128,
        num_layers: int = 3,
        output_days: int = 7,
        dropout: float = 0.2,
    ):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout,
            batch_first=True,
        )
        self.fc = nn.Linear(hidden_size, output_days)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Tensor of shape (batch, seq_len=90, features=7)
        Returns:
            Tensor of shape (batch, 7) — disruption probability per day
        """
        lstm_out, (h_n, _) = self.lstm(x)
        # Use last hidden state
        last_hidden = h_n[-1]  # shape: (batch, hidden_size)
        out = self.fc(last_hidden)
        return self.sigmoid(out)


# Feature names for reference
FEATURE_NAMES = [
    "max_rainfall_mm",
    "mean_aqi",
    "order_drop_pct",
    "day_of_week",
    "month",
    "is_festival",
    "historical_claim_count",
]
