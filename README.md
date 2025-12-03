# EarthShader

**Project Goal:** Train a Vision-Language Model to look at an image of a texture and reverse-engineer the executable GLSL shader code required to procedurally generate it.

## Phase 1: Primitives (Status: Validation)

We have trained a foundational model on **8,000 synthetic samples** of geometric primitives.

**Technical Strategy:**
The model is learning the core mathematical syntax of **Signed Distance Fields (SDFs)**. Instead of using high-level drawing functions, it generates canonical GLSL code by manipulating UV coordinate fields directly (`length`, `abs`, `smoothstep`). This suggests a potential pathway for learning the rigorous "syntax-to-vision" correlation required for procedural generation.

**Training Stats:**
* **Architecture:** Qwen2-VL-7B-Instruct (4-bit QLoRA)
* **Dataset:** 8k synthetic image-code pairs (Circles, Squares, Rings)
* **Performance:** Converged to **~1.36 loss** after 1 epoch.

*Note: This document will be updated as we make progress.*