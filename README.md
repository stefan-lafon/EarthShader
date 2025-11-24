# EarthShader: Neuro-Symbolic Inverse Procedural Modeling

**EarthShader** is an experimental  **Neuro-Symbolic AI** research project exploring the "Discrete-to-Continuous" problem in Generative AI. The project's objective is to bridge the gap between **Neural Perception** (analyzing continuous data) and **Symbolic Reasoning** (generating discrete, executable logic).

The goal is to reverse-engineer natural images into executable, procedural fragment shaders. Specifically, the goal is to output rednering logic, e.g. Signed Distance Functions (SDF) or raymarching loops, that renders the image deterministically. This approach treats the generative process as an inverse rendering problem. 

We'll start with Vision-Language Models (VLMs), but we'll likely explore other options. 

## Architecture

The system is architected as a three-stage pipeline designed to decouple syntax acquisition from visual generalization:

### 1. Synthetic Ground Truth Factory (Phase 1 - Completed)
To generate high-signal training data without human labeling, we built a headless rendering engine.
* **Headless EGL Pipeline:** Leverages `ModernGL` and `EGL` to perform headless GPU rendering of GLSL code in a cloud environment (Colab), converting text (code) into vision (pixels) without a display manager.
* **Entropy Filtering:** Implements automated **Visual Entropy Filtering** to reject execution failures (black screens) or empty shaders, ensuring 100% of the training data is functional.

### 2. Neuro-Symbolic Translation (Phase 1.5 - planned)
* **Model:** Qwen2-VL-7B-Instruct (Quantized 4-bit).
* **Strategy:** **"Grammar School" Overfitting.** We utilize a small, high-quality benchmark dataset (`Shadereval`) to force the model to memorize GLSL syntax and geometric primitives.
* **Goal:** To validate the tokenizer's ability to handle shader math and prove the Vision-Language bridge can map geometric features to logic before scaling to noisy data.

### 3. Procedural Generalization (Phase 2 & 3 - Planned)
* **Texture Synthesis:** Scaling the pipeline to a larger dataset to learn 2D procedural textures.
* **Volumetric Transfer:** Transfer learning from syntax memorization to generalized 3D SDF (Signed Distance Function) generation for terrains and landscapes.

## Dataset & Attribution

This project utilizes data derived from the **Shadertoy** ecosystem.

* **Primary Source:** [Vipitis/Shadereval-inputs](https://huggingface.co/datasets/Vipitis/Shadereval-inputs).
    * *Note:* This dataset contains canonical GLSL functions (primitives, noise) originally used for code-completion benchmarks. We repurpose it here as "Ground Truth" for inverse rendering.
* **License:** The training data is largely licensed under **CC BY-NC-SA 3.0** (Creative Commons Attribution-NonCommercial-ShareAlike).
* **Usage:** This project is strictly for **Educational and Non-Commercial Research**. It is not intended for commercial deployment. We gratefully acknowledge the contributions of the Shadertoy community.

## Tech Stack

* **Core Model:** Qwen2-VL, PyTorch
* **Training Engine:** Unsloth (Optimized LoRA/QLoRA)
* **Data Pipeline:** ModernGL (Headless OpenGL), Hugging Face Datasets
* **Infrastructure:** Google Colab (T4 GPU), Google Drive (Persistence)

## License

The source code for the EarthShader training pipeline is released under the MIT License. The model weights (adapters) are subject to the license terms of the training data (CC BY-NC-SA 3.0).