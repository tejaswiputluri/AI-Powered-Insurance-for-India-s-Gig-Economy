"""
CNN Verify — Training script for MobileNetV3 satellite weather classifier.
Fine-tunes on NASA POWER satellite imagery for Bengaluru region.

Loss: CrossEntropyLoss
Optimizer: AdamW, lr=5e-5
Epochs: 20, batch_size=32
Data augmentation: RandomHorizontalFlip, RandomRotation(15), ColorJitter
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import transforms
from pathlib import Path
from model import WeatherVerifier

MODEL_SAVE_PATH = Path(__file__).parent / "cnn_model.pt"

# Data transforms
train_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

val_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])


def train():
    """Fine-tune MobileNetV3 on satellite weather data."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = WeatherVerifier(pretrained=True).to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=5e-5,
    )

    print("CNN training requires labeled satellite tile dataset.")
    print("Place training data in data/satellite_tiles/{clear,light_rain,heavy_rain,flood_risk}/")
    print("Then re-run this script.")

    # Save untrained model for structure
    torch.save(model.state_dict(), MODEL_SAVE_PATH)
    print(f"Model skeleton saved to {MODEL_SAVE_PATH}")


if __name__ == "__main__":
    train()
