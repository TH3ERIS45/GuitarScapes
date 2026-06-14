"""Neural chord refinement using ONNX Runtime inference.

Provides optional neural network refinement of chord candidates using a
pre-trained ONNX model. Falls back gracefully to template-based candidates
when the model is unavailable.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

from guitarscapes.utils.logger import get_logger

if TYPE_CHECKING:
    import onnxruntime as ort

from guitarscapes.detection.templates import ChordCandidate


logger = get_logger("detection.neural_refiner")


class NeuralRefiner:
    """ONNX Runtime-based chord refinement model.

    Accepts an HPCP vector and template-matched candidates, producing
    refined probability estimates over all 108 chord classes. If the model
    file is missing or loading fails, the refiner gracefully falls back to
    returning candidates unchanged.

    Args:
        model_path: Path to the ONNX model file. If ``None`` or the file
            doesn't exist, the refiner operates in passthrough mode.
    """

    def __init__(self, model_path: Path | None = None) -> None:
        self._model_path = model_path
        self._session: ort.InferenceSession | None = None
        self._input_name: str = ""
        self._output_name: str = ""
        self._load_attempted: bool = False

        if model_path is not None and model_path.is_file():
            self._load_model(model_path)
        else:
            reason = "no path provided" if model_path is None else f"file not found: {model_path}"
            logger.info("NeuralRefiner disabled: %s", reason)

    def _load_model(self, model_path: Path) -> None:
        """Attempt to load the ONNX model with optimized settings.

        Args:
            model_path: Path to the .onnx model file.
        """
        self._load_attempted = True
        try:
            import onnxruntime as ort

            # Configure session with all graph optimizations enabled
            session_options = ort.SessionOptions()
            session_options.graph_optimization_level = (
                ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            )
            session_options.inter_op_num_threads = 1
            session_options.intra_op_num_threads = 1

            self._session = ort.InferenceSession(
                str(model_path),
                sess_options=session_options,
                providers=["CPUExecutionProvider"],
            )

            # Cache input/output names for inference
            self._input_name = self._session.get_inputs()[0].name
            self._output_name = self._session.get_outputs()[0].name

            logger.info(
                "NeuralRefiner loaded: %s (input=%s, output=%s)",
                model_path.name,
                self._input_name,
                self._output_name,
            )

        except ImportError:
            logger.warning(
                "onnxruntime not installed; NeuralRefiner disabled"
            )
            self._session = None
        except Exception:
            logger.exception(
                "Failed to load ONNX model from %s; NeuralRefiner disabled",
                model_path,
            )
            self._session = None

    @property
    def is_available(self) -> bool:
        """Whether the neural refiner model is loaded and ready."""
        return self._session is not None

    def refine(
        self,
        hpcp: np.ndarray,
        candidates: list[ChordCandidate],
        all_chord_names: list[str],
    ) -> list[ChordCandidate]:
        """Refine chord candidates using neural network inference.

        Constructs a 15-dimensional input vector (12 HPCP values + 3 candidate
        chord indices) and runs it through the ONNX model to produce a
        probability distribution over all 108 chord classes.

        If the model is unavailable, returns the original candidates unchanged.

        Args:
            hpcp: 12-element HPCP vector.
            candidates: Template-matched chord candidates (typically top 3).
            all_chord_names: Ordered list of all 108 chord names matching the
                model's output dimension.

        Returns:
            Refined list of top chord candidates with updated confidence scores,
            or the original candidates if the model is unavailable.
        """
        if not self.is_available:
            return candidates

        if len(candidates) == 0:
            return candidates

        try:
            # Build 15-dim input: 12 HPCP + 3 candidate indices
            hpcp = np.asarray(hpcp, dtype=np.float32)
            input_vector = np.zeros(15, dtype=np.float32)
            input_vector[:12] = hpcp[:12]

            # Fill candidate indices (pad with -1 if fewer than 3)
            for i in range(min(3, len(candidates))):
                input_vector[12 + i] = float(candidates[i].chord_index)
            for i in range(len(candidates), 3):
                input_vector[12 + i] = -1.0

            # Run inference: shape (1, 15) -> multiple outputs
            input_batch = input_vector.reshape(1, -1)
            outputs = self._session.run(
                None,  # Request all outputs
                {self._input_name: input_batch},
            )

            # The skl2onnx classifier typically returns [labels, probabilities]
            # Find the output that has the probability distribution (size >= 108)
            probabilities = None
            for out in outputs:
                if hasattr(out, "size") and out.size >= len(all_chord_names):
                    probabilities = out.flatten()
                    break
            
            if probabilities is None:
                probabilities = outputs[-1].flatten()

            # Softmax if not already normalized
            if not np.isclose(probabilities.sum(), 1.0, atol=0.01):
                exp_probs = np.exp(probabilities - np.max(probabilities))
                probabilities = exp_probs / exp_probs.sum()

            # Get top K refined candidates
            top_k = min(len(candidates), len(probabilities))
            top_indices = np.argpartition(probabilities, -top_k)[-top_k:]
            top_indices = top_indices[np.argsort(probabilities[top_indices])[::-1]]

            # The NN is not trained on a noise class, so it can be overconfident on out-of-distribution noise.
            # To prevent this, we scale the NN probability by the original template match confidence.
            # A strong template match means the input is actually a chord.
            base_confidence = candidates[0].confidence if candidates else 0.0

            refined = [
                ChordCandidate(
                    chord_name=all_chord_names[idx],
                    # Scale confidence: we don't want 99% confidence if base match was 15%.
                    confidence=min(1.0, float(probabilities[idx]) * base_confidence * 1.5),
                    chord_index=int(idx),
                )
                for idx in top_indices
            ]

            logger.debug(
                "Neural refinement: %s (%.3f) -> %s (%.3f)",
                candidates[0].chord_name,
                candidates[0].confidence,
                refined[0].chord_name if refined else "N/A",
                refined[0].confidence if refined else 0.0,
            )

            return refined

        except Exception:
            logger.exception("Neural refinement failed; returning original candidates")
            return candidates
