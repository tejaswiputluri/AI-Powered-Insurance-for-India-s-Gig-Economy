"""
MobileNetV3 CNN — Satellite weather verification model.
Classifies satellite tiles into 4 weather categories.

Classes:
  0: clear       (no significant cloud cover)
  1: light_rain  (some cloud cover, < 8mm/hr equivalent)
  2: heavy_rain  (dense cloud cover, > 8mm/hr equivalent)
  3: flood_risk  (extreme cloud cover + historical flood zones)

Input: RGB satellite tile image, resized to 224×224
Output: softmax probabilities over 4 classes

Fine-tuning:
  Base: torchvision.models.mobilenet_v3_small(weights='IMAGENET1K_V1')
  Freeze all layers except: classifier[-1] and last 2 conv blocks
  Replace classifier[-1]: Linear(1024, 4) + Softmax
"""

import torch
import torch.nn as nn
from torchvision import models


WEATHER_CLASSES = ["clear", "light_rain", "heavy_rain", "flood_risk"]


class WeatherVerifier(nn.Module):
    """MobileNetV3-Small fine-tuned for satellite weather classification."""

    def __init__(self, num_classes: int = 4, pretrained: bool = True):
        super().__init__()

        # Load pre-trained MobileNetV3-Small
        if pretrained:
            self.model = models.mobilenet_v3_small(weights="IMAGENET1K_V1")
        else:
            self.model = models.mobilenet_v3_small(weights=None)

        # Freeze all except last 2 conv blocks and classifier
        for param in self.model.parameters():
            param.requires_grad = False

        # Unfreeze last 2 inverted residual blocks
        for param in self.model.features[-2:].parameters():
            param.requires_grad = True

        # Replace classifier head
        in_features = self.model.classifier[-1].in_features
        self.model.classifier[-1] = nn.Linear(in_features, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Tensor of shape (batch, 3, 224, 224)
        Returns:
            Tensor of shape (batch, num_classes) — logits
        """
        return self.model(x)

    def predict(self, x: torch.Tensor) -> dict:
        """Run inference and return classification with probabilities."""
        self.eval()
        with torch.no_grad():
            logits = self.forward(x)
            probs = torch.softmax(logits, dim=1)
            class_idx = torch.argmax(probs, dim=1).item()
            return {
                "classification": WEATHER_CLASSES[class_idx],
                "confidence": float(probs[0][class_idx]),
                "probabilities": {
                    cls: float(probs[0][i]) for i, cls in enumerate(WEATHER_CLASSES)
                },
            }
