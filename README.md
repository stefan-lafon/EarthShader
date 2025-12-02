# EarthShader

**Project Goal:** Train a Vision-Language Model to look at an image of a texture and reverse-engineer the executable GLSL shader code required to procedurally generate it.

## Phase 1: Primitives (Current Status)

We are currently in the foundational stage of training, focusing on teaching the model the core mathematical syntax of **Signed Distance Fields (SDFs)**.

Instead of using high-level drawing functions, the model is learning to generate canonical GLSL code for fundamental shapes—circles, squares, and rings—by manipulating UV coordinate fields directly (`length`, `abs`, `smoothstep`). This establishes the rigorous "syntax-to-vision" correlation required for procedural generation.

*Note: This document will be updated as we make progress.*