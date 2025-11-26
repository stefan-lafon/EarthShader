# EarthShader: Neuro-Symbolic Inverse Procedural Modeling

**EarthShader** is an experimental Neuro-Symbolic AI research project exploring the "Discrete-to-Continuous" problem in Generative AI. The project's objective is to bridge the gap between **Neural Perception** (analyzing continuous data) and **Symbolic Reasoning** (generating discrete, executable logic).

The goal is to reverse-engineer natural images into executable, procedural fragment shaders. Specifically, the goal is to output rendering logic, e.g. Signed Distance Functions (SDF) or raymarching loops, that renders the image deterministically. This approach treats the generative process as an inverse rendering problem.

## Architecture & Roadmap

The system is architected as a multi-stage pipeline designed to decouple syntax acquisition, infrastructure scaling, and visual generalization.

### Phase 1: Synthetic Ground Truth Factory (Completed)
To generate high-signal training data without human labeling, we built a headless rendering engine.
* **Headless EGL Pipeline:** Leverages `ModernGL` and `EGL` to perform headless GPU rendering of GLSL code in a cloud environment (Colab), converting text (code) into vision (pixels) without a display manager.
* **Entropy Filtering:** Implements automated **Visual Entropy Filtering** to reject execution failures (black screens) or empty shaders, ensuring 100% of the training data is functional.

### Phase 2: Neuro-Symbolic Translation Validation (In Progress)
* **Model:** **Qwen2-VL-2B-Instruct** (Development Target).
* **Strategy:** **"Steel Thread" Validation.** We utilize a lightweight 2B variant and a small benchmark dataset (`Shadereval`) to validate the end-to-end learning loop.
* **Goal:** To validate the tokenizer's ability to handle shader math and prove the Vision-Language bridge can map geometric features to logic before scaling to noisy data. This phase focuses on overfitting (memorization) to prove syntax acquisition capabilities.

### Phase 3: Infrastructure Scaling & Optimization (Planned)
* **Model Upgrade:** upgrading to **Qwen2-VL-7B** to increase reasoning capacity.
* **Optimization:** Implementing **4-bit QLoRA** quantization, **Gradient Checkpointing**, and **Flash Attention 2** to fit the larger model context within consumer hardware constraints (T4/L4 GPUs).
* **Objective:** Achieving a stable training throughput at scale while maintaining the syntax accuracy achieved in Phase 2.

### Phase 4: Texture Synthesis at Scale (Planned)
* **Data Scaling:** Integrating the larger `shaders21k` dataset to move from memorization to generalization.
* **Objective:** Training the model to hallucinate novel 2D procedural textures (noise patterns, materials) from unseen input images.

### Phase 5: Volumetric Transfer (Planned)
* **Domain Transfer:** Transfer learning from 2D texture logic to 3D Volumetric Geometry.
* **Objective:** Generating Signed Distance Functions (SDFs) and raymarching loops to represent 3D terrains and objects.

## Dataset & Attribution

This project utilizes data derived from the **Shadertoy** ecosystem.

* **Primary Source:** [Vipitis/Shadereval-inputs](https://huggingface.co/datasets/Vipitis/Shadereval-inputs).
    * *Note:* This dataset contains canonical GLSL functions (primitives, noise) originally used for code-completion benchmarks. We repurpose it here as "Ground Truth" for inverse rendering validation.
* **License:** The training data is largely licensed under **CC BY-NC-SA 3.0** (Creative Commons Attribution-NonCommercial-ShareAlike).
* **Usage:** This project is strictly for **Educational and Non-Commercial Research**. It is not intended for commercial deployment. We gratefully acknowledge the contributions of the Shadertoy community.

## Tech Stack

* **Core Model:** Qwen2-VL (2B / 7B), PyTorch
* **Training Engine:** Native PyTorch (Custom Loop), PEFT (LoRA)
* **Data Pipeline:** ModernGL (Headless OpenGL), Hugging Face Datasets
* **Infrastructure:** Google Colab (T4 GPU), Google Drive (Persistence)

## License

The source code for the EarthShader training pipeline is released under the MIT License. The model weights (adapters) are subject to the license terms of the training data (CC BY-NC-SA 3.0).