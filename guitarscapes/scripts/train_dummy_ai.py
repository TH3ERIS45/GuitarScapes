"""Script to generate a synthetic AI model (ONNX) for NeuralRefiner.

This script trains a simple Multi-Layer Perceptron (MLP) on the mathematical 
chord templates, augmented with noise, to create a functional "AI" that
refines the template matching.

Run with: python -m guitarscapes.scripts.train_dummy_ai
"""

import sys
from pathlib import Path
import numpy as np

try:
    from sklearn.neural_network import MLPClassifier
    from skl2onnx import convert_sklearn
    from skl2onnx.common.data_types import FloatTensorType
except ImportError:
    print("Error: Missing ML dependencies. Run:")
    print("pip install scikit-learn skl2onnx onnx")
    sys.exit(1)

from guitarscapes.utils.config import DetectionConfig, PathConfig
from guitarscapes.detection.templates import ChordTemplateBank

def main():
    print("Initializing Template Bank...")
    config = DetectionConfig()
    bank = ChordTemplateBank(config)
    templates = bank._templates
    
    num_classes = len(templates)
    samples_per_class = 200
    
    print(f"Generating synthetic dataset ({num_classes} chords x {samples_per_class} variations)...")
    
    X = []
    y = []
    
    for class_idx, template in enumerate(templates):
        for _ in range(samples_per_class):
            # Add random noise to the template
            noise = np.random.normal(0, 0.15, size=12)
            hpcp = template + noise
            hpcp = np.clip(hpcp, 0, None)
            
            # Normalize
            norm = np.linalg.norm(hpcp)
            if norm > 0:
                hpcp /= norm
                
            # Get top 3 template candidates (just like in the real pipeline)
            candidates = bank.match(hpcp)
            
            # Build 15-dim input vector
            x_vec = np.zeros(15, dtype=np.float32)
            x_vec[:12] = hpcp
            for i in range(min(3, len(candidates))):
                x_vec[12 + i] = candidates[i].chord_index
            for i in range(len(candidates), 3):
                x_vec[12 + i] = -1.0
                
            X.append(x_vec)
            y.append(class_idx)
            
    X = np.array(X, dtype=np.float32)
    y = np.array(y, dtype=np.int64)
    
    print(f"Training MLP Classifier on {len(X)} samples...")
    mlp = MLPClassifier(
        hidden_layer_sizes=(64, 64),
        activation='relu',
        max_iter=50,
        random_state=42,
        learning_rate_init=0.01
    )
    mlp.fit(X, y)
    
    score = mlp.score(X, y)
    print(f"Training Accuracy: {score:.1%}")
    
    print("Exporting model to ONNX format...")
    paths = PathConfig()
    models_dir = paths.models_dir
    models_dir.mkdir(parents=True, exist_ok=True)
    
    model_path = paths.chord_refiner_model
    
    # Convert to ONNX with zipmap=False to return raw probabilities tensor
    initial_type = [('float_input', FloatTensorType([None, 15]))]
    onx = convert_sklearn(mlp, initial_types=initial_type, options={'zipmap': False})
    
    with open(model_path, "wb") as f:
        f.write(onx.SerializeToString())
        
    print(f"\n[SUCESSO] IA Ativada! Modelo salvo em: {model_path}")
    print("Você pode abrir o GuitarScapes Pro agora e a IA estará ativa.")

if __name__ == "__main__":
    main()
