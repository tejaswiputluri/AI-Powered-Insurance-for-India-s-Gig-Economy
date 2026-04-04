#!/bin/bash
# train_all_models.sh — Train all 3 GigShield ML models
# 1. FT-Transformer (premium pricing)
# 2. LSTM (disruption forecast)
# 3. CNN (satellite weather verification)

set -e

echo "================================================================"
echo "  GigShield — Training All ML Models"
echo "================================================================"

cd "$(dirname "$0")/.."

# 1. Generate synthetic data
echo ""
echo "🔧 [1/5] Generating synthetic rider data..."
python -m backend.ml.premium.synthetic_data

echo ""
echo "🔧 [2/5] Generating synthetic weather data..."
python -m backend.ml.forecast.data_prep

# 2. Train FT-Transformer (Premium)
echo ""
echo "🧠 [3/5] Training FT-Transformer premium model..."
python -m backend.ml.premium.train

# 3. Train LSTM (Forecast)
echo ""
echo "🧠 [4/5] Training LSTM forecast model..."
python -m backend.ml.forecast.train

# 4. Train CNN (Weather Verify)
echo ""
echo "🧠 [5/5] Training CNN weather verification model..."
python -m backend.ml.cnn_verify.train

echo ""
echo "================================================================"
echo "  ✅ All models trained successfully!"
echo "================================================================"
echo ""
echo "Model locations:"
echo "  - Premium:  backend/ml/premium/premium_model.pt"
echo "  - Forecast: backend/ml/forecast/forecast_model.pt"
echo "  - CNN:      backend/ml/cnn_verify/cnn_model.pt"
