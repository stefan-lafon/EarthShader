# EarthShader

**Project Goal:** Train a Vision-Language Model to look at an image of a texture and reverse-engineer the executable GLSL shader code required to procedurally generate it.

## Phase 1: Primitives (Status: Complete)

We have established the core "vision-to-syntax" foundation by training a Qwen2-VL-7B model to reverse-engineer fundamental geometric shapes (circles, squares, rings) into executable GLSL Signed Distance Fields (SDFs).

**Summary of Results:**
* **Objective:** Trained a model to translate visual primitives into code, creating a rigorous "syntax-to-vision" correlation.
* **Dataset Strategy:** Generated **8,000 synthetic samples** using strict "Canonical Code" rules (`smoothstep`, `mix`, no branching) to reduce search space and encourage structural learning.
* **Architecture & Hardware:** Deployed a **4-bit QLoRA** training pipeline optimized for Google Colab T4 GPUs (16GB VRAM).
* **Critical Optimizations:** Overcame hardware limitations by implementing aggressive memory constraints—capping image resolution at **256x256** and context length at **512 tokens**—stabilizing training speed.
* **Methodology:** Utilized a **Chain-of-Thought (CoT)** approach, where an intermediate "Analysis" comment block bridges the semantic gap between pixel data and code logic.
* **Performance:** Converged to a loss of **~1.36** after a single epoch. Validation confirms the model generates syntactically valid code that closely approximates the target visuals.

## Phase 2: Composition (Status: Starting)

We are now moving to **Boolean Operations**, teaching the model to combine multiple SDFs using Union, Subtraction, and Intersection logic.

*Note: This document tracks active development.*