<!-- README.md -->
# marais

A private AI coding assistant for the lab. It runs the Tier‑0 **Minerva‑Assistant** models (GPT‑OSS 120B/20B) as the default workhorse. **Before using it, install the OpenCode CLI** (e.g., `npm i -g @opencode/cli` or follow the OpenCode installation guide). You then use it from your own laptop through [opencode](https://opencode.ai/docs).

```
laptop (opencode) ──ssh tunnel──> Minerva login node ──> GPU node (vLLM serving Qwen)
```

> **No patient data (PHI).** By default we run the Tier‑0 **Minerva‑Assistant** models (GPT‑OSS 120B/20B) as the primary workhorse. Tier‑1 GPU‑node models (Qwen‑27B, FlashNext‑125B) and the optional AWS Bedrock provider remain available for niche use cases that need those specific models. The `engineer` row still runs outside the PHI‑safe enclave. If your work involves PHI, run `marais help` and talk to Chris.

## Usage tracks

| Track | When to use | Core steps |
|------|-------------|------------|
| **A – Minerva‑Assistant (Tier‑0) – default workhorse** | Most everyday work; no GPU job needed. | 1️⃣ Obtain an Assistant API key from the web UI.<br>2️⃣ Save it to `~/.config/opencode/secrets/minerva-assistant-key`.<br>3️⃣ Run the repository bootstrap script (symlinks the shared config).<br>4️⃣ Run `opencode --standalone`. |
| **B – Self‑hosted VLLM helper (Tier‑1 / Bedrock)** | Need a custom model or larger context; requires a GPU job. | 1️⃣ Set up SSH config and generate a VLLM key.<br>2️⃣ Start a Minerva job (`marais engineer`).<br>3️⃣ Run the repository bootstrap script (symlinks the shared config).<br>4️⃣ Run `~/marais/bin/connect`. |

## Quick start – Track A (Minerva‑Assistant)

> **Prerequisite:** Install OpenCode ([here](https://opencode.ai/docs)).

| Where | Step | Command |
|---|---|---|
| Laptop | 1. Obtain API key from the Assistant web UI (Settings → Account) |
| Laptop | 2. Save the key to `~/.config/opencode/secrets/minerva-assistant-key` |
| Laptop | 3. Run the repository bootstrap script (symlinks the shared config into ~/.config/opencode) | `./setup-opencode.sh` |
| Laptop | 4. Open Opencode (e.g., `opencode` or launch the UI) | `opencode` |
| Laptop | 5. Finish: exit opencode |

> **Note:** The `setup-opencode.sh` script also backs up any existing OpenCode files and warns if the Assistant API key or `biomcp` is missing.
> **Note:** The Minerva‑Assistant API is reachable only from within the MSSM VPN (or on‑campus). Ensure you are connected to the VPN before opening Opencode.

## Quick start – Track B (Self‑hosted VLLM)

| Where | Step | Command |
|---|---|---|
| Minerva | 1. Start the server | `marais engineer` |
| Minerva | 2. Wait until the job is `RUN` (+5‑10 min) | `bjobs` |
| Laptop | 3. Log in once (2FA) | `ssh -Nf minerva` |
| Laptop | 4. Open Opencode (e.g., `opencode` or launch the UI) | `opencode` |
| Laptop | 5. Finish: exit opencode, then free the GPU | `bkill <jobid>` |

`connect` is only required for the self‑hosted VLLM helper (Track B); the Minerva‑Assistant workflow (Track A) opens Opencode directly.


## Docs

- **[User guide](docs/USER_GUIDE.md)**: first-time setup, daily use, troubleshooting.
- **[Maintainer notes](docs/MAINTAINERS.md)**: how it fits together, adding models, pre‑release checks.
- **[Developer guide](docs/DEVELOPERS.md)**: how to add new agents, commands, skills, and modify permissions.

## Repo layout

| Path | Purpose |
|---|---|
| `bin/marais` | Runs on Minerva. Picks a GPU, renders the LSF script, submits the job. |
| `bin/connect` | Runs on the laptop. Opens the tunnel and starts opencode. |
| `marais/` | Python package behind `bin/marais`. |
| `registry/*.yaml` | Models, GPU lanes, task rows. The single source of truth. |
| `templates/` | LSF job templates. |

## Configuration

The repository provides a shared OpenCode configuration in the hidden `/.opencode/` directory. To use it:

```bash
mkdir -p ~/.config/opencode
./setup-opencode.sh   # symlinks the shared config into ~/.config/opencode, backing up any existing files
# The config expects the Assistant API key at
# ~/.config/opencode/secrets/minerva-assistant-key.
# Obtain the key from the Assistant web UI (Settings → Account) and
# save it there (chmod 600). Do NOT copy the `secrets/` folder from the repo.
```

The copied `opencode.json` sets the Tier‑0 **Minerva‑Assistant** models as the default. Edit the file only if you need a Tier‑1 or Bedrock model.

### What the repository ships by default
**Agents**
- `analyst` – primary agent for data processing, statistics and scripting.
- `designer` – primary read‑only agent for experimental design advice.
- `auditor` – sub‑agent that audits a single script or notebook.
- `literature` – sub‑agent that performs verified literature/database lookups.
- `scout` – sub‑agent for fast narrow file‑search queries.

**Commands**
- `/design-review` – invoke the `design-review` skill via the `designer` agent.
- `/lit` – literature lookup via the `literature` agent.
- `/audit` – audit a script via the `auditor` agent.
- `/new-analysis` – scaffold a reproducible analysis folder (uses `analyst`).
- `/biomcp-health` – run `biomcp health --apis-only` and highlight errors/exclusions.

**Skills**
- `design-review` – systematic critique of experimental designs.
- `literature-verification` – retrieve and format evidence tables from public databases.
- `rnaseq-de-workflow` – bulk RNA‑seq differential‑expression workflow conventions.

**MCP (BioMCP)**
- Provides programmatic access to PubMed, UniProt, GTEx, gnomAD, ClinVar, Reactome, STRING and many other biomedical resources.

**Permissions & Rules**
- Permissions are defined in `opencode.json` (edit = ask, bash = ask with a few safe commands allowed, read = allow except for `*secrets/*` and `*service.json`).
- Lab‑wide rules live in `/.opencode/AGENTS.md` (data privacy, scientific honesty, genomics hygiene, reproducibility, delegation).

These components are symlinked into `~/.config/opencode` by `setup-opencode.sh`; any changes you make in the repository are instantly reflected for all users after a restart of OpenCode.

