<!-- README.md -->
# chuangai

A private AI coding assistant for the lab. It runs the Tier‑0 **Minerva‑Assistant** models (GPT‑OSS 120B/20B) as the default workhorse. You use it from your own laptop through [opencode](https://opencode.ai/docs).

```
laptop (opencode) ──ssh tunnel──> Minerva login node ──> GPU node (vLLM serving Qwen)
```

> **No patient data (PHI).** By default we run the Tier‑0 **Minerva‑Assistant** models (GPT‑OSS 120B/20B) as the primary workhorse. Tier‑1 GPU‑node models (Qwen‑27B, FlashNext‑125B) and the optional AWS Bedrock provider remain available for niche use cases that need those specific models. The `engineer` row still runs outside the PHI‑safe enclave. If your work involves PHI, run `chuangai help` and talk to Chris.

## Usage tracks

| Track | When to use | Core steps |
|------|-------------|------------|
| **A – Minerva‑Assistant (Tier‑0) – default workhorse** | Most everyday work; no GPU job needed. | 1️⃣ Obtain an Assistant API key from the web UI.<br>2️⃣ Save it to `~/.config/opencode/secrets/minerva-assistant-key`.<br>3️⃣ Copy the shared `/.opencode/` config.<br>4️⃣ Run `opencode --standalone`. |
| **B – Self‑hosted VLLM helper (Tier‑1 / Bedrock)** | Need a custom model or larger context; requires a GPU job. | 1️⃣ Set up SSH config and generate a VLLM key.<br>2️⃣ Start a Minerva job (`chuangai engineer`).<br>3️⃣ Copy the shared config (same as Track A).<br>4️⃣ Run `~/chuangai/bin/connect`. |

## Quick start – Track A (Minerva‑Assistant)

| Where | Step | Command |
|---|---|---|
| Laptop | 1. Obtain API key from the Assistant web UI (Settings → Account) |
| Laptop | 2. Save the key to `~/.config/opencode/secrets/minerva-assistant-key` |
| Laptop | 3. Copy shared OpenCode config | `mkdir -p ~/.config/opencode && cp -r .opencode/* ~/.config/opencode/` |
| Laptop | 4. Open Opencode (e.g., `opencode` or launch the UI) | `opencode` |
| Laptop | 5. Finish: exit opencode (no GPU to free) |

> **Note:** The Minerva‑Assistant API is reachable only from within the MSSM VPN (or on‑campus). Ensure you are connected to the VPN before opening Opencode.

## Quick start – Track B (Self‑hosted VLLM)

| Where | Step | Command |
|---|---|---|
| Minerva | 1. Start the server | `chuangai engineer` |
| Minerva | 2. Wait until the job is `RUN` (+5‑10 min) | `bjobs` |
| Laptop | 3. Log in once (2FA) | `ssh -Nf minerva` |
| Laptop | 4. Open Opencode (e.g., `opencode` or launch the UI) | `opencode` |
| Laptop | 5. Finish: exit opencode, then free the GPU | `bkill <jobid>` |

`connect` is only required for the self‑hosted VLLM helper (Track B); the Minerva‑Assistant workflow (Track A) opens Opencode directly.


## Docs

- **[User guide](docs/USER_GUIDE.md)**: first-time setup, daily use, troubleshooting.
- **[Maintainer notes](docs/MAINTAINERS.md)**: how it fits together, adding models, pre-release checks.

## Repo layout

| Path | Purpose |
|---|---|
| `bin/chuangai` | Runs on Minerva. Picks a GPU, renders the LSF script, submits the job. |
| `bin/connect` | Runs on the laptop. Opens the tunnel and starts opencode. |
| `chuangai/` | Python package behind `bin/chuangai`. |
| `registry/*.yaml` | Models, GPU lanes, task rows. The single source of truth. |
| `templates/` | LSF job templates. |

## Configuration

The repository provides a shared OpenCode configuration in the hidden `/.opencode/` directory. To use it:

```bash
mkdir -p ~/.config/opencode
cp -r .opencode/* ~/.config/opencode/
# The config expects the Assistant API key at
# ~/.config/opencode/secrets/minerva-assistant-key.
# Obtain the key from the Assistant web UI (Settings → Account) and
# save it there (chmod 600). Do NOT copy the `secrets/` folder from the repo.
```

The copied `opencode.json` sets the Tier‑0 **Minerva‑Assistant** models as the default. Edit the file only if you need a Tier‑1 or Bedrock model.

