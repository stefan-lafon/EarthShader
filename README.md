# EarthShader

**Project Goal:** Train a Vision-Language Model to look at an image of a texture and reverse-engineer the executable GLSL shader code required to procedurally generate it.

## Phase 1: Primitives (Status: Finalized)

We have established the core "vision-to-syntax" foundation by training a Qwen2-VL-7B model to reverse-engineer fundamental geometric shapes into executable GLSL Signed Distance Fields (SDFs). This stage focused on establishing a rock-solid literacy in GLSL syntax and spatial mapping.

### **Summary of Results:**
* **Objective:** Established a 1:1 mapping between visual geometric features and the mathematical code required to render them.
* **Dataset Strategy:** Generated a high-quality, validated dataset of **2,000 synthetic samples** (Circles, Squares, and Annuli) using deterministic seeding.
* **Audit Performance:**
    * **Compilation Success:** 100.0% (Zero syntax errors across 100 unseen test samples).
    * **Visual Precision (MSE):** 0.0167 (High spatial accuracy in positioning and sizing).
    * **Shape Identity Accuracy:** 100% (Perfect classification across all primitive types: Circle, Square, Annulus).
    * **Complexity Reasoning:** 98% accuracy in distinguishing single vs. double-shape compositions.
* **Architecture:** Deployed a **4-bit QLoRA** training pipeline on a Google Colab T4 environment.
* **Optimization:** Implemented a **Weighted Cross-Entropy Loss** to prioritize GLSL syntax accuracy (5.0x weight) over natural language reasoning (0.2x weight).

## Phase 2: Composition (Status: In Development)

We are now transitioning to **Boolean Operations**, teaching the model to combine multiple SDFs into complex scenes using Union, Subtraction, and Intersection logic.

**Key Goals for Phase 2:**
* **Multi-Shape Scenes:** Scaling complexity to 2–5 overlapping shapes per scene.
* **Boolean Logic:** Implementing `min()`, `max()`, and subtraction math for shape interaction.
* **Precision Refinement:** Utilizing a **Cosine Decay Learning Rate Scheduler** to fine-tune coordinate precision as composition complexity increases.

---

### **Repo Structure**
* `lib/gl_renderer.py`: Standalone ModernGL renderer for headless GLSL validation.
* `lib/generators/primitives.py`: Procedural SDF generation logic for Stage 1.
* `notebooks/`: 
    * `datagen_primitives.ipynb`: Dataset creation and validation.
    * `train.ipynb`: LoRA fine-tuning and checkpointing.
    * `test_suite.ipynb`: Quantitative performance audit tools.

---
*Note: This document tracks active development.*