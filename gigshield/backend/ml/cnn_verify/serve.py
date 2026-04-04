"""
CNN Verify — FastAPI inference endpoint (port 8003).
Classifies satellite weather tiles for fraud L2 cross-verification.
"""

import logging
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel

logger = logging.getLogger(__name__)

app = FastAPI(title="GigShield CNN Verify Service", version="1.0.0")


class VerifyResponse(BaseModel):
    classification: str
    confidence: float
    probabilities: dict
    agrees_with_api: bool
    inference_ms: int


@app.post("/verify", response_model=VerifyResponse)
async def verify_satellite_tile(image: UploadFile = File(...)):
    """Classify a satellite weather tile image."""
    # Phase 3: Load trained model and run inference
    # For now, return mock heavy_rain classification
    import time
    start = time.time()

    # Mock response — will be replaced with real model inference
    result = VerifyResponse(
        classification="heavy_rain",
        confidence=0.91,
        probabilities={
            "clear": 0.02,
            "light_rain": 0.05,
            "heavy_rain": 0.91,
            "flood_risk": 0.02,
        },
        agrees_with_api=True,
        inference_ms=int((time.time() - start) * 1000) + 145,
    )
    return result


@app.get("/health")
async def health():
    return {"status": "healthy", "model": "mobilenet_v3", "mode": "mock"}
