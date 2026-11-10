# Developer Guide for extending the marais OpenCode configuration

This document explains how to add or modify **agents**, **commands**, **skills**, and **configuration** in the marais repository.

## 1. Adding a new **agent**
1. Create a new markdown file in `agents/`, e.g. `agents/myagent.md`.
2. Use the following skeleton (copy from an existing file):
   ```markdown
   ---
   description: Short description of what the agent does.
   mode: primary | subagent   # primary agents can start a session; subagents run as a task.
   permission:               # optional – overrides global permissions for this agent
     edit: deny
     bash: deny
   ---
   You are a ... (prompt that the LLM will see).
   ```
3. Commit the file.
4. Run `./setup-opencode.sh` **or** simply restart OpenCode – the new agent will be symlinked into `~/.config/opencode/agents` and become available.

## 2. Adding a new **command**
1. Create `commands/<name>.md`.
2. Front‑matter example:
   ```markdown
   ---
   description: What the command does.
   agent: <agent‑name>   # which agent will execute the command
   subtask: true|false   # optional – run as a subtask (non‑blocking)
   ---
   <command template, can use $ARGUMENTS, $1, $2 etc.>
   ```
3. Save, commit, and restart OpenCode.

## 3. Adding a new **skill**
1. Make a directory `skills/<skill-id>/`.
2. Inside it, add `SKILL.md` with the required header and numbered steps:
   ```markdown
   ---
   name: <skill-id>
   description: One‑sentence description of the skill.
   ---
   1. Step one …
   2. Step two …
   ```
3. Reference the skill in an agent prompt with `Load the <skill-id> skill`.
4. No additional code changes are required – the skill is loaded at runtime.

## 4. Changing **permissions** or **rules**
- Permissions are defined in `/.opencode/opencode.json` under the `permission` key.
- Lab‑wide rules live in `/.opencode/AGENTS.md` (and any `.opencode/rules/*.md`). Edit those files directly; they are re‑read each OpenCode session.

## 5. Updating the **MCP** configuration
- The `mcp` section in `/.opencode/opencode.json` currently points to a local `biomcp` server.
- To change the command or use a different MCP server, edit the `command` array, e.g.:
  ```json
  "mcp": {
    "biomcp": { "type": "local", "command": ["/full/path/to/biomcp", "serve"], "enabled": true }
  }
  ```
- After editing, restart OpenCode.

## 6. Testing your changes
1. Run `./setup-opencode.sh` to refresh symlinks.
2. Start a fresh OpenCode session: `opencode`.
3. Use `opencode agents list` and `opencode commands list` to verify your additions appear.
4. Run a quick test, e.g. `@myagent "test"` or `/mycommand arg`.

## 7. Contributing back
- Follow the standard repo workflow: fork, create a branch, commit, open a pull request.
- Ensure your changes are documented in this guide (or the README) so new users see them.

---
*Generated on $(date)*
