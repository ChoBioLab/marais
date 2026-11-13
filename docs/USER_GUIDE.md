<!-- docs/USER_GUIDE.md -->
# marais user guide

## What you need

- A Minerva account with access to project `acc_untreatedIBD`.
- A laptop running macOS, Linux, or Windows with WSL. It needs `python3` and OpenSSH.
- [opencode](https://opencode.ai/docs), installed on your laptop.

## First-time setup (once per person, about 10 minutes)

### A. Set up the Minerva‑Assistant (Tier‑0) – default workhorse

1. **Obtain an API key**  
   Open a browser, go to https://assistant.hpc.mssm.edu, click **Continue with Microsoft**, then **Settings → Account** and press **Generate API key**. Copy the displayed key.

2. **Save the key locally**  

   ```bash
   mkdir -p ~/.config/opencode/secrets
   echo "<PASTE_KEY_HERE>" > ~/.config/opencode/secrets/minerva-assistant-key
   chmod 600 ~/.config/opencode/secrets/minerva-assistant-key
   ```

3. **Copy the shared OpenCode configuration** (once per repository)

   ```bash
   mkdir -p ~/.config/opencode
   ./setup-opencode.sh   # copies the shared config into ~/.config/opencode, backs up existing files, auto‑installs uv & biomcp-cli, and prompts for the Minerva API key
   # Do NOT copy the `secrets/` folder; you already placed the key above.
   ```

4. **Open Opencode (standalone)**

    Ensure you are on the MSSM VPN (or on‑campus) before opening Opencode.

   ```bash
   opencode
   ```

   No VLLM job or tunnel is required for this track.

### B. Set up a self‑hosted VLLM helper (optional)

#### 1. Laptop: add Minerva to your SSH config

Open `~/.ssh/config` (create it if missing) and add the block below. Replace `YOURUSER` with your Minerva username.

```text
Host minerva
    HostName minerva.hpc.mssm.edu
    User YOURUSER
    ControlMaster auto
    ControlPath ~/.ssh/cm-%C
    ControlPersist 8h
    ServerAliveInterval 30
    ServerAliveCountMax 3
```

Check it with `ssh minerva`. Log in with your password and token, then leave that session open for the next step.

#### 2. Minerva: create your VLLM API key and a shortcut

Run these in the Minerva session once.

```bash
openssl rand -hex 24 > ~/.vllm_key && chmod 600 ~/.vllm_key
echo "alias marais='/sc/arion/projects/untreatedIBD/marais/bin/marais'" >> ~/.bashrc
```

Log out and back in, then check that `marais help` prints a list of rows.

#### 3. Laptop: let the tunnel reach compute nodes without a password

```bash
[ -f ~/.ssh/id_ed25519 ] || ssh-keygen -t ed25519 -N ""
ssh minerva 'umask 077; mkdir -p ~/.ssh; cat >> ~/.ssh/authorized_keys' < ~/.ssh/id_ed25519.pub
```

#### 4. Laptop: install `connect`

```bash
mkdir -p ~/marais/bin
scp minerva:/sc/arion/projects/untreatedIBD/marais/bin/connect ~/marais/bin/connect
chmod +x ~/marais/bin/connect
```

This is the same `bin/connect` file as in the repo. Re‑run these three lines if Chris tells you it was updated.

#### 5. Laptop: tell opencode about the server

Save this as `~/.config/opencode/opencode.json`. Create the folder first with `mkdir -p ~/.config/opencode`.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "minerva-assistant/gpt-oss-120b",
  "provider": {
    "minerva-assistant": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Minerva Assistant",
      "options": {
        "baseURL": "https://assistant.hpc.mssm.edu/api",
        "apiKey": "{file:~/.config/opencode/secrets/minerva-assistant-key}"
      },
      "models": {
        "gpt-oss-120b": {
          "name": "Assistant: GPT‑OSS 120B (vLLM)",
          "tool_call": true,
          "reasoning": true,
          "limit": { "context": 120000, "output": 16384 }
        }
      }
    }
  }
}
```

You don't set `MINERVA_VLLM_KEY` yourself. `connect` reads your key from Minerva and passes it to opencode.

Setup is done. Don't repeat it.

#### 6. Use the shared OpenCode configuration (once per repository)

The repository ships a hidden `/.opencode/` directory containing a ready‑made OpenCode configuration (Tier‑0 default). Copy it to your personal config once:

```bash
mkdir -p ~/.config/opencode
./setup-opencode.sh   # copies the shared config into ~/.config/opencode, backs up existing files, auto‑installs uv & biomcp-cli, and prompts for the Minerva API key
# Do NOT copy the `secrets/` folder; create your own key there:
# ~/.config/opencode/secrets/minerva-assistant-key (chmod 600)
```

After this, `opencode` will automatically use the Tier‑0 **Minerva‑Assistant** models. Edit `~/.config/opencode/opencode.json` only if you need a Tier‑1 or Bedrock model — see the [OpenCode configuration guide](docs/OPENCODE_CONFIG.md) for details.

## Every session

### 1. Minerva: start the server

Run this from your own folder, not the shared project folder. The command writes a `.lsf` file and an `opencode.json` into the folder you run it from (see the [OpenCode configuration guide](docs/OPENCODE_CONFIG.md)). Ignore both.

```bash
mkdir -p ~/marais-jobs && cd ~/marais-jobs
marais engineer
```

It prints `submitted <jobid>`. If it says a server is already running, you can reuse that one.

### 2. Minerva: wait for the server to boot

```bash
bjobs
```

- `PEND` means you're queued for a GPU. This can take minutes to hours.
- `RUN` means the job has started. The model then needs about 5–10 more minutes to load.

You can go straight to step 3, because `connect` waits for you.

### 3. Laptop: log in so the tunnel can reuse the connection

```bash
ssh -Nf minerva
```

Enter your password and token. The connection lasts 8 hours, so you do this once per working day.

### 4. Laptop: connect

Go to the folder you want to work on, then run `connect` by its full path:

```bash
cd ~/my-project
~/marais/bin/connect
```

It prints progress and then `ready:`, and opencode opens in that folder. Work as usual. The tunnel closes when you exit opencode.

### 5. Finish: free the GPU

Exit opencode (`/exit` or Ctrl-C). Then on Minerva:

```bash
bjobs                 # note the JOBID
bkill <JOBID>
```

GPUs are shared. Please release yours when you're done. A job also stops by itself after 12 hours.

To reconnect later while the job is still running, repeat steps 3 and 4 only.

### First interaction (examples)
- **Design review**: `@designer "I plan a CRISPR knockout of TP53 in human iPSC, 4 replicates, batch‑randomized."` – the `designer` agent provides a design critique using its built‑in reasoning.
- **Literature lookup**: `/lit TP53` – the `literature` agent fetches curated evidence tables (see example in the documentation).
- **Audit a script**: `/audit scripts/analysis.R "check multiple‑testing correction"` – the `auditor` agent reviews the file and reports any defects.
- **Scaffold a new analysis**: `/new-analysis my-rna‑seq` – creates a reproducible folder layout with a README and placeholder files.

### Where the files live
- The **source** definitions are in the repository under `@agents/`, `@commands/`, and `@skills/`.
- Running `./setup-opencode.sh` copies the repository’s `@agents/`, `@commands/`, and `@skills/` directories into `~/.config/opencode`.
- OpenCode always reads from `~/.config/opencode`; any change you make in the repo is instantly reflected after restarting OpenCode (no need to copy files again).

### Adding new agents, commands, or skills
#### New agent
1. Create `@agents/<name>.md` (use existing files as a template).
2. Define `description`, `mode` (`primary` or `subagent`), and an optional `permission` block.
3. Commit the file; run `./setup-opencode.sh` or restart OpenCode to expose the new agent.

#### New command
1. Create `@commands/<name>.md` with a front‑matter block (`description`, `agent`, optional `subtask`).
2. Write the command template (`$ARGUMENTS`, `$1`, `$2`).
3. Restart OpenCode to make the command available.

#### New skill
1. Make a directory `@skills/<skill-id>/` and add `SKILL.md` (include `name`, `description`, numbered steps).
2. Reference the skill in an agent prompt with `Load the <skill-id> skill`.
3. No code changes required – the skill is loaded at runtime.

### FAQ (quick)
- **Why does `setup-opencode.sh` warn about missing keys?**
  The script now automatically installs `uv` (if missing) and `biomcp-cli` via `uv`. It then prompts you to enter the Minerva assistant API key, saving it with mode 600. After the prompt it still warns if the key or `biomcp` is missing, because they are required for downstream commands.
- **Can I edit the configuration files directly?**
  Yes, but changes should be made in the repository (the source) and then re‑run `setup‑opencode.sh` for consistency across teammates.
- **How do I add a custom permission?**
  Edit `/.opencode/opencode.json` → `permission` (see the [OpenCode configuration guide](docs/OPENCODE_CONFIG.md)) and add the desired glob pattern. Restart OpenCode afterwards.

## Troubleshooting

| What you see | What to do |
|---|---|
| `marais: command not found` (Minerva) | Add the alias line from setup step 2 to `~/.bash_profile` too, then log in again. |
| `No such file or directory: .../connect` (laptop) | Redo setup step 4. |
| `Permission denied` running `connect` | Run `chmod +x ~/marais/bin/connect`. |
| Asks for a password or token, or "Cannot reach Minerva" | Run `ssh -Nf minerva`. Your 8-hour login expired. |
| `No 'qwen27' job found` | There's no server. Run `marais engineer` on Minerva. Your job may also have hit its 12 h limit. |
| Stays on "queued, waiting for a GPU" | All matching GPUs are busy. Run `marais status` on Minerva, and wait. |
| `No API key in ~/.vllm_key` | Do setup step 2. If you changed the key, `bkill` the job and start a new one. |
| `No API key in ~/.config/opencode/secrets/minerva-assistant-key` | Follow the “Obtain an API key” steps in Track A. |
| `Local port 8000 busy` | An old tunnel is still running. Run `pkill -f 'ssh .*-L 8000:'`, then retry. |
| `Tunnel failed` | Redo setup step 3, then retry. |
| `Server job ended during startup` | Run `ls -t /sc/arion/projects/untreatedIBD/marais/logs \| head`. Then run `tail -n 30 <newest .stderr file>`. Send that output to Chris. |
| `opencode not found on PATH` | Install opencode, and open a new terminal. |
| opencode says "connection refused" mid-session | The job ended or the tunnel dropped. Run `bjobs`, start a new job if needed, and run `opencode --standalone` again. |
| Replies show `<think>` text | Known cosmetic issue. Tell Chris. |
| Anything else | Run `marais help` and send Chris what you ran, what you expected, and what you got. |

## FAQ

- **Can I use it with patient data?** No. See the PHI warning in the README.
- **Can I use other models?** Not yet through `connect`. It currently supports only `qwen27`, which is started by the `engineer` row.
- **Will my files be sent anywhere?** opencode runs on your laptop and sends prompts and file contents only to your own server on Minerva, through your tunnel.
- **Why does the first start take so long?** The job waits for a GPU, and then the 29 GB model loads. Later reconnects to a running job take seconds.
- **Can I just type `connect`?** Only if you put `~/marais/bin` on your PATH. The full path is more reliable, and a bare `connect` can collide with other tools.
