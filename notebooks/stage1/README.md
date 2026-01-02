# Stage 1: Primitive Literacy

**Goal:** Train the model to recognize individual geometric primitives and translate them into syntactically correct GLSL.

## Implementation Details
* **Data:** 2,000 samples of circles, squares, and annuli.
* **Logic:** probabilistic 70/30 split between single shapes and double-shape compositions.
* **Loss Strategy:** Weighted cross-entropy (5.0x on code tokens) to ensure 100% compilation success.

## Final Results (Audit: 2026-01-02)
* **Compilation Rate:** 100.0%
* **Visual Precision (MSE):** 0.0167
* **Shape ID Accuracy:** 100%
* **Complexity Accuracy:** 98%

*Note: These notebooks are frozen. Further development for multi-shape logic occurs in the stage2 directory.*