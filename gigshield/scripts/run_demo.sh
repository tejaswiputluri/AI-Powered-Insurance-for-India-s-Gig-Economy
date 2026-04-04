#!/bin/bash
# run_demo.sh — Start all GigShield services for demo mode.
# Starts: Backend API, Premium ML, Forecast ML, CNN Verify ML
# Usage: ./scripts/run_demo.sh

set -e

echo "================================================================"
echo "  GigShield — Demo Mode Launcher"
echo "================================================================"

cd "$(dirname "$0")/.."

# Ensure DEMO_MODE is set
export DEMO_MODE=true

# Check .env exists
if [ ! -f .env ]; then
    echo "⚠️ No .env found — using defaults"
    export DATABASE_URL="sqlite+aiosqlite:///./gigshield_demo.db"
    export REDIS_URL="redis://localhost:6379/0"
    export SECRET_KEY="demo-secret-key-do-not-use-in-production"
else
    export $(grep -v '^#' .env | xargs)
fi

echo ""
echo "🚀 Starting services..."

# Start ML microservices in background
echo "  [1/4] Premium ML service (port 8001)..."
uvicorn backend.ml.premium.serve:app --host 0.0.0.0 --port 8001 &
ML_PREMIUM_PID=$!

echo "  [2/4] Forecast ML service (port 8002)..."
uvicorn backend.ml.forecast.serve:app --host 0.0.0.0 --port 8002 &
ML_FORECAST_PID=$!

echo "  [3/4] CNN Verify ML service (port 8003)..."
uvicorn backend.ml.cnn_verify.serve:app --host 0.0.0.0 --port 8003 &
ML_CNN_PID=$!

sleep 2

# Start main API
echo "  [4/4] Main API (port 8000)..."
echo ""
echo "================================================================"
echo "  🟢 GigShield running at http://localhost:8000"
echo "  📚 API docs at http://localhost:8000/docs"
echo "  🔬 Demo API: POST /api/v1/demo/fire-event"
echo ""
echo "  ML Services:"
echo "    Premium:  http://localhost:8001"
echo "    Forecast: http://localhost:8002"
echo "    CNN:      http://localhost:8003"
echo ""
echo "  Press Ctrl+C to stop all services."
echo "================================================================"

# Trap cleanup
cleanup() {
    echo ""
    echo "🛑 Stopping all services..."
    kill $ML_PREMIUM_PID $ML_FORECAST_PID $ML_CNN_PID 2>/dev/null || true
    echo "✅ All services stopped."
}
trap cleanup EXIT INT TERM

uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
