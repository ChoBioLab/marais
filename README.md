<!-- README.md -->
# chuangai

A private AI coding assistant for the lab. It runs a Qwen 27B model on Minerva GPUs. You use it from your own laptop through [opencode](https://opencode.ai/docs).

```
laptop (opencode) ──ssh tunnel──> Minerva login node ──> GPU node (vLLM serving Qwen)
```

> **No patient data (PHI).** The `engineer` row runs outside the PHI-safe enclave. If your work involves PHI, run `chuangai help` and talk to Chris.

## Quick start (after one-time setup)

| Where | Step | Command |
|---|---|---|
| Minerva | 1. Start the server | `chuangai engineer` |
| Minerva | 2. Wait until the job is `RUN`, plus about 5–10 min to load the model | `bjobs` |
| Laptop | 3. Log in once (2FA); stays valid for 8 h | `ssh -Nf minerva` |
| Laptop | 4. Connect and start opencode, from your project folder | `~/chuangai/bin/connect` |
| Laptop | 5. Finish: exit opencode, then free the GPU on Minerva | `bkill <jobid>` |

`connect` also waits for a queued or loading server, so step 4 works before the server is ready.

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
