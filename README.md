# EarthShader: Neuro-Symbolic Inverse Procedural Modeling

**EarthShader** is an experimental Neuro-Symbolic AI research project exploring the "Discrete-to-Continuous" problem in Generative AI. The project's objective is to bridge the gap between **Neural Perception** (analyzing continuous data) and **Symbolic Reasoning** (generating discrete, executable logic).

The goal is to reverse-engineer natural images into executable, procedural fragment shaders. Specifically, the goal is to output rendering logic, e.g., Signed Distance Functions (SDF) or raymarching loops, that renders the image deterministically. This approach treats the generative process as an inverse rendering problem.

## Architecture & Roadmap

The system is designed as a modular pipeline decoupling data acquisition, synthetic expansion, and visual grounding.

### Phase 1: Data Mining (The Miner)
Acquires raw potential seeds from open repositories.
* **Source:** `bigcode/the-stack` (GLSL subset).
* **Metrics:** Scanned **317,741** GLSL files to identify **1,162** (0.36%) potentially valid samples.
* **Filtering:** Enforces a strict **Permissive License Allowlist** (MIT, Apache 2.0, CC0) and validates Shadertoy syntax (`void mainImage`).
* **Sanitization:** Implements regex-based cleaning to strip desktop wrappers, remove comments, and normalize legacy variable names.
* **Output:** A raw archive of potentially usable code (`raw_stack_shaders.jsonl`).

### Phase 2: Validation & Aggregation (The Gatekeeper)
A new intermediate stage acting as the "Firewall" for the dataset. It aggregates data from automated mining and manual injections, validating every shader before it enters the synthetic pipeline.
* **Inputs:** Raw data from The Stack + Manual Injection folder (`*.glsl`).
* **Function:** Compiles and renders every seed candidate in a headless EGL environment.
* **Triage:**
    * **Verified:** Shaders that compile and produce valid images (passed to Phase 3).
    * **Quarantine:** Broken shaders saved with error logs for manual repair.
    * **Blocklist:** Permanently banned code hashes (e.g., empty screens, crashes).

### Phase 3: Synthetic Data Factory (The Fuzzer)
Scales the verified dataset using high-throughput deterministic mutation.
* **Tool:** `03_Data_Fuzzer.ipynb` (CPU-based).
* **Input:** Strictly `verified_seeds.jsonl` (Zero waste on broken code).
* **Strategy:** **Deterministic Parameter Variation.**
    * **Float Fuzzing:** Identifies floating-point literals via Regex and applies multiplicative noise (e.g., ±10%) to distort geometry and colors while preserving logic.
    * **Time Snapshots:** Injects static time definitions to capture shaders at specific animation states.
* **Objective:** Scaling the dataset from ~1k to ~10k+ samples to force the downstream model to learn continuous parameter control.
* **Note:** An experimental LLM-based generator (`Qwen2.5-Coder`) is available in `experimental/` but is currently secondary due to lower robustness.

### Phase 4: Headless Rendering (The Factory)
Mass-produces the final training dataset.
* **Engine:** `ModernGL` + `EGL` headless rendering.
* **Input:** Merged stream of `verified_seeds.jsonl` and `synthetic_dataset.jsonl`.
* **Outcome:** Conversion of text (code) into vision (pixels) to create the final `(Image, Code)` training pairs.

### Phase 5: Neuro-Symbolic Translation (The Brain)
* **Training Model:** **Qwen2-VL-2B-Instruct** (scaling to **7B**).
* **Strategy:** Fine-tuning a Vision-Language Model to map visual features (texture, shape) to the discrete logic required to generate them.
* **Optimization:** Implementing 4-bit QLoRA and gradient checkpointing to fit training within consumer/colab hardware constraints (T4 GPU).

## Project Structure

The workflow is divided into modular notebooks to manage the data lifecycle:

* `01_Data_Download.ipynb`: **The Miner.** Streams and filters raw GLSL from The Stack. (CPU/Network bound).
* `02_Seed_Gatekeeper.ipynb`: **The Gatekeeper.** Aggregates sources, validates rendering, and sorts into Verified/Quarantine/Blocklist. (GPU/OpenGL bound).
* `03_Data_Fuzzer.ipynb`: **The Multiplier (Phase 3).** Deterministic Regex-based fuzzer for fast dataset expansion. (CPU bound).
* `04_Data_Renderer.ipynb`: **The Factory.** Renders the final training set from valid code. Input: Verified + Synthetic. (GPU/OpenGL bound).
* `05_Training_Pipeline.ipynb`: **The Brain.** Fine-tunes Qwen2-VL on the generated pairs. (GPU/Memory bound).
* `experimental/`: Contains experimental notebooks (e.g., LLM-based Generator).

## Dataset & Attribution

This project prioritizes data hygiene and open-source compliance.

* **Primary Source:** [BigCode/The Stack](https://huggingface.co/datasets/bigcode/the-stack).
* **License Strategy:** We strictly filter for **Permissive Licenses** (MIT, Apache 2.0, BSD, CC0). Unlike standard scrapes which often rely on Non-Commercial (CC-BY-NC-SA) data, this pipeline is designed to be compatible with Open Weights release standards.
* **Usage:** This project is for **Educational and Research Purposes**.

## Tech Stack

* **Core Model:** Qwen2-VL (2B / 7B)
* **Training Engine:** PyTorch, PEFT (LoRA), BitsAndBytes
* **Data Pipeline:** Hugging Face Datasets, ModernGL (Headless)
* **Infrastructure:** Google Colab (T4 GPU), Google Drive (Persistence)

## License

The source code for the EarthShader pipeline is released under the MIT License.