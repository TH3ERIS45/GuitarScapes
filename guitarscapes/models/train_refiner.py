"""Training script for the neural chord refiner model.

Generates synthetic chord data, trains a small MLP classifier, and exports
the model to ONNX format for use by the NeuralRefiner at inference time.

Usage:
    python -m guitarscapes.models.train_refiner
"""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import numpy as np


# ── Constants ──────────────────────────────────────────────────────────────

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

CHORD_TYPES = {
    "": [0, 4, 7],          # major
    "m": [0, 3, 7],         # minor
    "7": [0, 4, 7, 10],     # dominant 7th
    "m7": [0, 3, 7, 10],    # minor 7th
    "maj7": [0, 4, 7, 11],  # major 7th
    "sus2": [0, 2, 7],      # suspended 2nd
    "sus4": [0, 5, 7],      # suspended 4th
    "dim": [0, 3, 6],       # diminished
    "aug": [0, 4, 8],       # augmented
}

CHORD_TYPE_ORDER = ["", "m", "7", "m7", "maj7", "sus2", "sus4", "dim", "aug"]
NUM_CHORDS = len(NOTE_NAMES) * len(CHORD_TYPE_ORDER)  # 108


def _build_chord_names() -> list[str]:
    """Build list of all 108 chord names in canonical order."""
    names = []
    for note in NOTE_NAMES:
        for ctype in CHORD_TYPE_ORDER:
            names.append(f"{note}{ctype}")
    return names


def _build_templates() -> np.ndarray:
    """Build (108, 12) array of L2-normalized chord templates."""
    templates = np.zeros((NUM_CHORDS, 12), dtype=np.float32)
    idx = 0
    for root_idx in range(12):
        for ctype in CHORD_TYPE_ORDER:
            intervals = CHORD_TYPES[ctype]
            for interval in intervals:
                templates[idx, (root_idx + interval) % 12] = 1.0
            # L2 normalize
            norm = np.linalg.norm(templates[idx])
            if norm > 0:
                templates[idx] /= norm
            idx += 1
    return templates


def _cosine_similarity_batch(
    vector: np.ndarray, templates: np.ndarray
) -> np.ndarray:
    """Compute cosine similarity between a vector and all templates."""
    v_norm = np.linalg.norm(vector)
    if v_norm < 1e-10:
        return np.zeros(len(templates))
    v = vector / v_norm
    return templates @ v


# ── Data Generation ────────────────────────────────────────────────────────


def generate_dataset(
    n_samples: int,
    templates: np.ndarray,
    noise_std: float = 0.15,
    rng: np.random.Generator | None = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """Generate synthetic training data.

    For each sample:
    1. Pick a random chord → ideal HPCP from template.
    2. Add Gaussian noise.
    3. Run template matching to get top-3 candidates.
    4. Construct 15-dim input: [12 HPCP + 3 candidate indices].
    5. Label: true chord index.

    Args:
        n_samples: Number of samples to generate.
        templates: (108, 12) chord template matrix.
        noise_std: Standard deviation of Gaussian noise.
        rng: Random number generator.

    Returns:
        (X, y) — features array (n, 15), labels array (n,).
    """
    if rng is None:
        rng = np.random.default_rng(42)

    X = np.zeros((n_samples, 15), dtype=np.float32)
    y = np.zeros(n_samples, dtype=np.int64)

    for i in range(n_samples):
        # Random chord
        chord_idx = rng.integers(0, NUM_CHORDS)
        y[i] = chord_idx

        # Ideal HPCP + noise
        hpcp = templates[chord_idx].copy() + rng.normal(0, noise_std, 12).astype(
            np.float32
        )
        hpcp = np.clip(hpcp, 0, None)
        max_val = np.max(hpcp)
        if max_val > 0:
            hpcp /= max_val

        # Template matching for top-3
        similarities = _cosine_similarity_batch(hpcp, templates)
        top3 = np.argsort(similarities)[-3:][::-1]

        # Build input
        X[i, :12] = hpcp
        X[i, 12:15] = top3.astype(np.float32)

    return X, y


# ── Model Definition ───────────────────────────────────────────────────────


def _build_model():
    """Build a simple MLP model using PyTorch."""
    import torch
    import torch.nn as nn

    class ChordRefinerMLP(nn.Module):
        """Small MLP for chord classification refinement."""

        def __init__(self, input_dim: int = 15, num_classes: int = 108):
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(input_dim, 64),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(64, 32),
                nn.ReLU(),
                nn.Dropout(0.1),
                nn.Linear(32, num_classes),
            )

        def forward(self, x):
            return self.net(x)

    return ChordRefinerMLP()


# ── Training ───────────────────────────────────────────────────────────────


def train_model(
    output_path: Path | None = None,
    n_train: int = 10000,
    n_val: int = 2000,
    epochs: int = 50,
    lr: float = 0.001,
    batch_size: int = 64,
) -> None:
    """Train the chord refiner model and export to ONNX.

    Args:
        output_path: Path to save the ONNX model. Defaults to
                     models/chord_refiner.onnx in the project directory.
        n_train: Number of training samples.
        n_val: Number of validation samples.
        epochs: Training epochs.
        lr: Learning rate.
        batch_size: Batch size.
    """
    import torch
    import torch.nn as nn
    from torch.utils.data import DataLoader, TensorDataset

    if output_path is None:
        output_path = Path(__file__).parent / "chord_refiner.onnx"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("  GuitarScapes Pro — Neural Refiner Training")
    print("=" * 60)

    # Build templates
    templates = _build_templates()
    chord_names = _build_chord_names()
    print(f"Chord templates: {len(chord_names)} chords")

    # Generate data
    print(f"Generating {n_train} training + {n_val} validation samples...")
    rng_train = np.random.default_rng(42)
    rng_val = np.random.default_rng(123)
    X_train, y_train = generate_dataset(n_train, templates, noise_std=0.2, rng=rng_train)
    X_val, y_val = generate_dataset(n_val, templates, noise_std=0.2, rng=rng_val)

    # Convert to tensors
    train_ds = TensorDataset(
        torch.tensor(X_train, dtype=torch.float32),
        torch.tensor(y_train, dtype=torch.long),
    )
    val_ds = TensorDataset(
        torch.tensor(X_val, dtype=torch.float32),
        torch.tensor(y_val, dtype=torch.long),
    )
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size)

    # Build model
    model = _build_model()
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    print(f"\nModel: {sum(p.numel() for p in model.parameters())} parameters")
    print(f"Training for {epochs} epochs...\n")

    best_val_acc = 0.0

    for epoch in range(1, epochs + 1):
        # Train
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0

        for batch_X, batch_y in train_loader:
            optimizer.zero_grad()
            logits = model(batch_X)
            loss = criterion(logits, batch_y)
            loss.backward()
            optimizer.step()

            train_loss += loss.item() * len(batch_y)
            preds = logits.argmax(dim=1)
            train_correct += (preds == batch_y).sum().item()
            train_total += len(batch_y)

        # Validate
        model.eval()
        val_correct = 0
        val_total = 0

        with torch.no_grad():
            for batch_X, batch_y in val_loader:
                logits = model(batch_X)
                preds = logits.argmax(dim=1)
                val_correct += (preds == batch_y).sum().item()
                val_total += len(batch_y)

        train_acc = train_correct / train_total
        val_acc = val_correct / val_total
        avg_loss = train_loss / train_total

        if epoch % 5 == 0 or epoch == 1:
            print(
                f"  Epoch {epoch:3d}/{epochs}  "
                f"Loss: {avg_loss:.4f}  "
                f"Train Acc: {train_acc:.1%}  "
                f"Val Acc: {val_acc:.1%}"
            )

        if val_acc > best_val_acc:
            best_val_acc = val_acc

    print(f"\nBest validation accuracy: {best_val_acc:.1%}")

    # Export to ONNX
    print(f"\nExporting to ONNX: {output_path}")
    model.eval()
    dummy_input = torch.randn(1, 15, dtype=torch.float32)
    torch.onnx.export(
        model,
        dummy_input,
        str(output_path),
        input_names=["input"],
        output_names=["output"],
        dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}},
        opset_version=13,
    )
    print(f"Model saved to {output_path}")
    print("Done!")


# ── Entry Point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    train_model()
