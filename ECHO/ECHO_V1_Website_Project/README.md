# ECHO V1 — hosted multimodal AI website

ECHO V1 is a cloud-hosted website. Users open its HTTPS URL; they do not need to run a terminal or install a local AI model. There is no offline mode. The hybrid multi-agent team system is intentionally reserved for a later release, but the service boundaries leave room for it.

## Included in this build

- Responsive web workspace, owner account setup, password login, secure session cookies, CSRF checks, and security headers.
- Encrypted short-, medium-, and long-term memory records with user-controlled deletion.
- External AI chat through an OpenAI-compatible chat-completions endpoint.
- Web research through a Brave Search-compatible endpoint.
- Private file upload with type and size limits.
- Voice input through browser microphone recording plus a speech-to-text endpoint; spoken assistant replies through text-to-speech.
- Image generation, image analysis, and image editing through a configured image API.
- Video understanding by extracting up to 12 frames at five-second intervals and sending those samples to a vision-capable model. It is sampled-frame analysis, not continuous real-time video perception.
- Interactive Mermaid flowchart generation.
- Evolution Engine proposal tracking and a CI test workflow foundation.
- AI Factory: create and save specialized AI project specifications, then export provider-neutral WAI handoff ZIPs containing configuration, system prompt, manifest, and setup/validation instructions. API keys are never packaged.

## What is not magically complete

The repository is real application code, but the external capabilities become live only after the hosting owner configures compatible API credentials, model names, and provider permissions. A chat model must support image input for image/video analysis. Image generation/editing must be enabled by the selected provider and account. Browser microphone access requires HTTPS and user permission. Costs, quotas, supported models, and API terms depend on the selected provider.

ECHO is not a newly trained foundation model in this ZIP. It is an AI application that calls externally hosted models. The training folder is a place to develop a real dataset/evaluation/fine-tuning pipeline; actual training needs approved data, GPU compute, and a selected training provider. No model has been trained by packaging this project.

The AI Factory export is a provider-neutral starter package, not a verified one-click WAI import format. Check WAI’s current import requirements and map the included manifest/configuration to its supported fields. It does not train a new foundation model or provision paid model access.

The Evolution Engine currently stores proposals and includes CI checks plus a deployment-policy design. It does not yet possess credentials to modify the repository, deploy itself, or roll back production. Those functions require a selected Git provider/hosting provider and an audited deployment controller. Security controls, authentication, permission boundaries, and the update policy must remain protected from self-modification.

## Deploy as a website (Render blueprint included)

1. An adult account owner creates the GitHub repository and imports this project.
2. The owner creates a Render web service from `render.yaml` (the blueprint uses a persistent disk; it is not a free ephemeral deployment).
3. In the hosting dashboard, set a unique `DATA_ENCRYPTION_KEY` generated with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`. Keep a separate secure backup. Losing it makes saved encrypted memories unreadable.
4. Set `AI_API_KEY` and `AI_MODEL`. `AI_BASE_URL` defaults to the OpenAI API endpoint. Choose a model that supports the features you plan to enable.
5. Add `IMAGE_API_KEY`, `STT_API_KEY`, and `TTS_API_KEY` as needed. Optional model variables are listed in `.env.example`.
6. Deploy and open the HTTPS URL. Create the owner account on first visit.

The Render blueprint stores persistent application data at `/srv/echo/persist`. Review current hosting prices, data retention, region, and provider terms before deploying. A parent/guardian should own provider accounts and review API billing/age requirements.

## Local development only

Local running is for development/testing; production use is through the hosted website URL.

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Copy .env.example to .env and set APP_SECRET + DATA_ENCRYPTION_KEY
uvicorn app.main:app --reload
```

Video analysis requires `ffmpeg` installed on the machine. The production Dockerfile installs it automatically.

## Security baseline

- Never commit `.env`, API keys, database files, uploaded user files, or model checkpoints.
- Never place provider secrets in frontend JavaScript.
- Keep `APP_SECRET` and `DATA_ENCRYPTION_KEY` private and backed up separately.
- Use a unique owner password and HTTPS.
- Treat model output, search results, and uploaded files as untrusted input.
- Do not give agents unrestricted production shell access or credentials.
- Require owner approval for security, authentication, permission, data migration, destructive, billing, or policy changes.
