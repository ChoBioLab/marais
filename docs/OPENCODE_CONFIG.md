# OpenCode Configuration (`opencode.json`)

The repository ships a default OpenCode configuration in the hidden `/.opencode/` directory. When a user runs `./setup-opencode.sh` the file is copied to `~/.config/opencode/opencode.json` and becomes the active configuration for all OpenCode sessions.

## Why this matters
- **Model selection** – Controls which model(s) are used by default (Tier‑0 Minerva‑Assistant, optional Tier‑1 or Bedrock models).
- **Permissions** – Defines the default `edit`, `bash`, and `skill` permissions for agents and the overall session.
- **Providers & models** – Lists the provider blocks (`minerva-assistant`, `minerva-qwen27`, etc.) with endpoint URLs, API‑key handling, and model limits.
- **Agent definitions** – Overrides or adds agent specifications (`mode`, `description`, `prompt`, `permission`).
- **Instructions** – Points OpenCode to additional rule files (`AGENTS.md`, `*.md` in `.opencode/rules`).

## Key sections
| Section | Purpose |
|---------|---------|
| `model` / `small_model` | Default primary model and a lightweight fallback for cheap tasks. |
| `permission` | Global permissions; can be overridden per‑agent. |
| `instructions` | Files that are automatically loaded as lab‑wide rules. |
| `agent` | Custom definitions that replace or extend the built‑in agents. |
| `provider` | API configuration for each model provider, including `baseURL` and how the API key is supplied (file or env var). |

## Editing the configuration
1. **Locate the file** – Edit the copy in your home directory (`~/.config/opencode/opencode.json`). The repository copy (`/.opencode/opencode.json`) should remain unchanged.
2. **Model changes** – To add a new Tier‑1 model, add a provider block under `provider` and reference it in `model` or `small_model`.
3. **Permission tweaks** – Adjust the `permission` map or individual agent `permission` sub‑objects to tighten or relax edit/bash access. Use `ask` for a prompt, `allow` for unrestricted, or `deny` to block.
4. **Agent customisation** – You can add new agents or modify existing ones via the `agent` section. Remember to restart OpenCode (or run `./setup-opencode.sh`) after changes.
5. **Testing** – Run `opencode agents list` and `opencode commands list` to verify your changes are reflected.

For detailed field specifications see the OpenCode schema linked from https://opencode.ai/config.json.
