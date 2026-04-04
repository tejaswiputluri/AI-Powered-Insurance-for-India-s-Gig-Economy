"""
FT-Transformer Model Definition — Premium Pricing.
Feature Tokenizer Transformer for tabular data (Gorishniy et al. 2021).
Input: 7 rider profile features → Output: weekly premium (paise) + attention weights.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math


class FTTransformer(nn.Module):
    """
    Feature Tokenizer Transformer for premium pricing.

    Architecture:
    1. FeatureTokenizer: Projects each feature to d_token-dimensional embedding
    2. [CLS] token prepended
    3. Transformer encoder (multi-head self-attention)
    4. [CLS] output → MLP → premium prediction

    The attention weights from the last layer are the XAI factors.
    """

    def __init__(
        self,
        n_features: int = 7,
        d_token: int = 64,
        n_heads: int = 4,
        n_layers: int = 3,
        d_ffn: int = 128,
        dropout: float = 0.1,
    ):
        super().__init__()

        self.n_features = n_features
        self.d_token = d_token

        # Feature tokenizer — one linear projection per feature
        self.feature_tokenizers = nn.ModuleList([
            nn.Linear(1, d_token) for _ in range(n_features)
        ])

        # [CLS] token
        self.cls_token = nn.Parameter(torch.randn(1, 1, d_token))

        # Positional embeddings
        self.pos_embedding = nn.Parameter(torch.randn(1, n_features + 1, d_token))

        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_token,
            nhead=n_heads,
            dim_feedforward=d_ffn,
            dropout=dropout,
            batch_first=True,
        )
        self.transformer = nn.TransformerEncoder(
            encoder_layer, num_layers=n_layers
        )

        # Output head
        self.output_head = nn.Sequential(
            nn.LayerNorm(d_token),
            nn.Linear(d_token, d_ffn),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(d_ffn, 1),  # single premium output
        )

        # Store last attention weights for XAI
        self._last_attention_weights = None

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            x: (batch_size, n_features) — all features as floats

        Returns:
            premium: (batch_size, 1) — predicted premium in paise
            attention_weights: (batch_size, n_features) — normalized attention per feature
        """
        batch_size = x.size(0)

        # Tokenize each feature
        tokens = []
        for i, tokenizer in enumerate(self.feature_tokenizers):
            feature_token = tokenizer(x[:, i:i+1])  # (batch, d_token)
            tokens.append(feature_token.unsqueeze(1))  # (batch, 1, d_token)

        tokens = torch.cat(tokens, dim=1)  # (batch, n_features, d_token)

        # Prepend [CLS] token
        cls = self.cls_token.expand(batch_size, -1, -1)
        tokens = torch.cat([cls, tokens], dim=1)  # (batch, n_features+1, d_token)

        # Add positional embeddings
        tokens = tokens + self.pos_embedding

        # Transformer forward
        encoded = self.transformer(tokens)

        # Extract [CLS] token output
        cls_output = encoded[:, 0, :]  # (batch, d_token)

        # Compute premium
        premium = self.output_head(cls_output)  # (batch, 1)

        # Compute attention weights via dot product similarity
        feature_outputs = encoded[:, 1:, :]  # (batch, n_features, d_token)
        cls_expanded = cls_output.unsqueeze(1).expand_as(feature_outputs)
        similarities = (cls_expanded * feature_outputs).sum(dim=-1)  # (batch, n_features)
        attention_weights = F.softmax(similarities / math.sqrt(self.d_token), dim=-1)

        self._last_attention_weights = attention_weights.detach()

        return premium, attention_weights


def create_model(n_features: int = 7) -> FTTransformer:
    """Create a new FT-Transformer model instance."""
    return FTTransformer(
        n_features=n_features,
        d_token=64,
        n_heads=4,
        n_layers=3,
        d_ffn=128,
        dropout=0.1,
    )
