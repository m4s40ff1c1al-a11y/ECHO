# ECHO model development workspace

This directory documents the training workflow; it does not contain trained weights.

A responsible model-development sequence:
1. Define a narrow capability and measurable target.
2. Assemble licensed, age-appropriate, privacy-reviewed training data.
3. Deduplicate, filter, document provenance, and split train/validation/test sets.
4. Establish baseline evaluations before fine-tuning.
5. Fine-tune a legally usable base model on rented/hosted GPU infrastructure.
6. Evaluate factuality, safety, robustness, latency, and regression.
7. Publish a versioned model artifact with a model card and dataset documentation.
8. Deploy behind an adapter so the website can switch models without code rewrites.

Never train on private user memories or uploaded files by default. Obtain clear consent and remove secrets and personal data. Keep evaluation data separate from training data. Model weights and checkpoints must not be committed to GitHub.

A future `training_runner.py` should use a maintained framework such as Hugging Face Transformers/PEFT or another reviewed stack, pinned dependencies, reproducible configs, resource limits, and explicit dataset manifests. A training job must be initiated on an authorized cloud GPU service; this repository cannot provision compute by itself.
