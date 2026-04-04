"""
FT-Transformer Inference Service — FastAPI server on port 8001.
POST /predict → returns premium_paise + attention_weights (XAI factors).
"""

import numpy as np
import torch
from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="GigShield Premium ML Service", version="1.0.0")

# Feature names for XAI labels
FEATURE_NAMES = [
    'zone_risk_score',
    'aqi_exposure_score',
    'work_hours_per_day',
    'work_days_per_week',
    'season_multiplier',
    'claim_history_count',
    'daily_earning_bucket',
]

XAI_LABELS = {
    'zone_risk_score': 'aqi_zone_history',
    'aqi_exposure_score': 'aqi_zone_history',
    'work_hours_per_day': 'zone_risk_score',
    'work_days_per_week': 'zone_risk_score',
    'season_multiplier': 'monsoon_season',
    'claim_history_count': 'claim_history',
    'daily_earning_bucket': 'zone_risk_score',
}

# Load model at startup
model = None
norm_params = None

# Zone risk scores mapping
ZONE_RISK = {
    'BTM_LAYOUT': 0.87, 'KORAMANGALA': 0.82, 'INDIRANAGAR': 0.91,
    'WHITEFIELD': 0.79, 'JAYANAGAR': 0.85, 'MARATHAHALLI': 0.76,
    'HSR_LAYOUT': 0.88, 'ELECTRONIC_CITY': 0.72, 'HEBBAL': 0.80, 'JP_NAGAR': 0.83,
}


class PredictionRequest(BaseModel):
    zone_id: str = "BTM_LAYOUT"
    aqi_exposure_score: float = 0.42
    work_hours_per_day: int = 12
    work_days_per_week: int = 6
    season_multiplier: float = 1.0
    claim_history_count: int = 0
    daily_earning_bucket: int = 2


class PredictionResponse(BaseModel):
    premium_paise: int
    attention_weights: dict


@app.on_event("startup")
async def load_model():
    """Load trained model on startup."""
    global model, norm_params

    model_path = Path(__file__).parent / "model_weights.pt"
    norm_path = Path(__file__).parent / "norm_params.npz"

    if model_path.exists():
        from model import create_model
        model = create_model()
        model.load_state_dict(torch.load(model_path, map_location="cpu"))
        model.eval()
        print("✅ FT-Transformer model loaded")
    else:
        print("⚠️ No trained model found — using fallback")

    if norm_path.exists():
        norm_params = np.load(norm_path)
        print("✅ Normalization params loaded")


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """Predict premium and return attention weights (XAI factors)."""

    zone_risk = ZONE_RISK.get(request.zone_id, 0.80)

    features = np.array([
        zone_risk,
        request.aqi_exposure_score,
        float(request.work_hours_per_day),
        float(request.work_days_per_week),
        request.season_multiplier,
        float(request.claim_history_count),
        float(request.daily_earning_bucket),
    ], dtype=np.float32)

    if model is not None and norm_params is not None:
        # Normalize
        X = (features - norm_params['mean']) / (norm_params['std'] + 1e-8)
        X_tensor = torch.FloatTensor(X).unsqueeze(0)

        with torch.no_grad():
            premium_pred, attn_weights = model(X_tensor)

        premium_paise = int(premium_pred.item())
        premium_paise = max(2900, min(9900, premium_paise))

        weights = attn_weights[0].numpy()
    else:
        # Fallback: rule-based
        base = 5000
        premium_paise = int(base * (
            0.30 * zone_risk +
            0.25 * request.aqi_exposure_score +
            0.20 * request.season_multiplier +
            0.15 * (request.work_hours_per_day / 16) +
            0.10 * (request.work_days_per_week / 7)
        ))
        premium_paise = max(2900, min(9900, premium_paise))
        weights = np.array([0.30, 0.04, 0.15, 0.10, 0.20, 0.06, 0.15])

    # Map to XAI factor labels
    attention_weights = {
        "aqi_zone_history": round(float(weights[0] + weights[1]), 2),
        "monsoon_season": round(float(weights[4]), 2),
        "zone_risk_score": round(float(weights[2] + weights[3] + weights[6]), 2),
        "claim_history": round(float(weights[5]), 2),
    }

    # Normalize
    total = sum(attention_weights.values())
    if total > 0:
        attention_weights = {k: round(v / total, 2) for k, v in attention_weights.items()}

    return PredictionResponse(
        premium_paise=premium_paise,
        attention_weights=attention_weights,
    )


@app.get("/health")
async def health():
    return {"status": "healthy", "model_loaded": model is not None}
