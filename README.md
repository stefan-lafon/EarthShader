# EarthShader: Neuro-Symbolic Inverse Procedural Modeling

**EarthShader** is an experimental Neuro-Symbolic AI research project exploring the "Discrete-to-Continuous" problem in Generative AI. The project's objective is to bridge the gap between **Neural Perception** (analyzing continuous data) and **Symbolic Reasoning** (generating discrete, executable logic).

The goal is to reverse-engineer natural images into executable, procedural fragment shaders. Specifically, the goal is to output rendering logic, e.g., Signed Distance Functions (SDF) or raymarching loops, that renders the image deterministically. This approach treats the generative process as an inverse rendering problem.

## Architecture & Roadmap

The system is designed as a modular pipeline decoupling data acquisition, synthetic expansion, and visual grounding.

### Phase 1: Data Mining & Filtration (Current)
To build a legally compliant "Ground Truth" dataset, we moved away from scraping to selective filtering of open repositories.
* **Source:** `bigcode/the-stack` (GLSL subset).
* **Metrics:** Scanned **317,741** GLSL files to identify **1,162** (0.36%) valid samples.
* **Filtering:** Enforces a strict **Permissive License Allowlist** (MIT, Apache 2.0, CC0) and validates Shadertoy syntax (`void mainImage`).
* **Sanitization:** Implements regex-based cleaning to strip desktop wrappers, remove comments (token optimization), and normalize legacy variable names.
* **Procedural Constraint:** Enforces a **"Pure Procedural"** rule by rejecting shaders with external dependencies (textures, channels) to ensure 100% renderability in a headless environment.

### Phase 2: Synthetic Data Factory (In Progress)
To solve the data scarcity problem (scaling from ~1.1k samples), we utilize Large Language Models for semantic augmentation.
* **Generator Model:** **Qwen2.5-Coder-7B**.
* **Strategy:** **Semantic Fuzzing.** The model acts as a multiplier, rewriting existing valid shaders with specific mutation strategies (e.g., "Change the color palette," "Invert the geometry," "Alter the speed") while preserving the compilation structure.
* **Objective:** Scaling the dataset from 1,162 to **~10,000+** samples to force the downstream model to learn continuous parameter control rather than memorization.

### Phase 3: Headless Rendering & Grounding (Planned)
* **Engine:** Custom `ModernGL` + `EGL` pipeline running in a headless cloud environment.
* **Validation:** The renderer acts as the "Ground Truth Oracle." Synthetic shaders that fail to compile or render black frames are automatically rejected, ensuring 100% of the training data is functional.
* **Outcome:** Conversion of text (code) into vision (pixels) to create the final `(Image, Code)` training pairs.

### Phase 4: Neuro-Symbolic Translation (Planned)
* **Training Model:** **Qwen2-VL-2B-Instruct** (scaling to **7B**).
* **Strategy:** Fine-tuning a Vision-Language Model to map visual features (texture, shape) to the discrete logic required to generate them.
* **Optimization:** Implementing 4-bit QLoRA and gradient checkpointing to fit training within consumer/colab hardware constraints (T4 GPU).

## Project Structure

The workflow is divided into modular notebooks to manage cloud resource constraints:

* `01_Data_Download.ipynb`: **The Miner.** Streams, filters, and sanitizes raw GLSL from The Stack. (CPU/Network bound).
* `02_Data_Generator.ipynb`: **The Multiplier.** Uses LLMs to synthesize variations of valid shaders. (GPU/Compute bound).
* `03_Data_Renderer.ipynb`: **The Renderer.** Validates code by executing it and saving the output frames. (GPU/OpenGL bound).
* `04_Training_Pipeline.ipynb`: **The Brain.** Fine-tunes Qwen2-VL on the generated pairs. (GPU/Memory bound).

## Dataset & Attribution

This project prioritizes data hygiene and open-source compliance.

* **Primary Source:** [BigCode/The Stack](https://huggingface.co/datasets/bigcode/the-stack).
* **License Strategy:** We strictly filter for **Permissive Licenses** (MIT, Apache 2.0, BSD, CC0). Unlike standard scrapes which often rely on Non-Commercial (CC-BY-NC-SA) data, this pipeline is designed to be compatible with Open Weights release standards.
* **Usage:** This project is for **Educational and Research Purposes**.

## Tech Stack

* **Core Model:** Qwen2-VL (2B / 7B)
* **Synthetic Generator:** Qwen2.5-Coder
* **Training Engine:** PyTorch, PEFT (LoRA), BitsAndBytes
* **Data Pipeline:** Hugging Face Datasets, ModernGL (Headless)
* **Infrastructure:** Google Colab (T4 GPU), Google Drive (Persistence)

## License

The source code for the EarthShader pipeline is released under the MIT License.