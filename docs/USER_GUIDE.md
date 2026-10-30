<!-- docs/USER_GUIDE.md -->
# chuangai user guide

## What you need

- A Minerva account with access to project `acc_untreatedIBD`.
- A laptop running macOS, Linux, or Windows with WSL. It needs `python3` and OpenSSH.
- [opencode](https://opencode.ai/docs), installed on your laptop.

## First-time setup (once per person, about 10 minutes)

### 1. Laptop: add Minerva to your SSH config

Open `~/.ssh/config` (create it if missing) and add the block below. Replace `YOURUSER` with your Minerva username.

```
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

### 2. Minerva: create your API key and a shortcut

Run these in the Minerva session from step 1. Run them once.

```bash
openssl rand -hex 24 > ~/.vllm_key && chmod 600 ~/.vllm_key
echo "alias chuangai='/sc/arion/projects/untreatedIBD/chuangai/bin/chuangai'" >> ~/.bashrc
```

Log out and back in, then check that `chuangai help` prints a list of rows.

### 3. Laptop: let the tunnel reach compute nodes without a password

```bash
[ -f ~/.ssh/id_ed25519 ] || ssh-keygen -t ed25519 -N ""
ssh minerva 'umask 077; mkdir -p ~/.ssh; cat >> ~/.ssh/authorized_keys' < ~/.ssh/id_ed25519.pub
```

### 4. Laptop: install `connect`

```bash
mkdir -p ~/chuangai/bin
scp minerva:/sc/arion/projects/untreatedIBD/chuangai/bin/connect ~/chuangai/bin/connect
chmod +x ~/chuangai/bin/connect
```

This is the same `bin/connect` file as in the repo. Re-run these three lines if Chris tells you it was updated.

### 5. No laptop-side config

There is nothing to configure: `connect` writes the `opencode.json` your project needs every time you connect, and it reads your API key from Minerva for you (you never set `MINERVA_VLLM_KEY` yourself). If you followed an older guide and created `~/.config/opencode/opencode.json`, you can delete that file.

Setup is done. Don't repeat it.

## Every session

### 1. Minerva: start the server

Run this from your own folder, not the shared project folder. The rendered job script is kept in `~/.local/state/chuangai/scripts/` — nothing is written into your folder.

```bash
mkdir -p ~/chuangai-jobs && cd ~/chuangai-jobs
chuangai engineer
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
~/chuangai/bin/connect
```

If more than one of your servers is running, it lists them and you pick one by its served name (the ones from `chuangai help`, e.g. `~/chuangai/bin/connect qwen27-bf16`).

It prints progress and then `ready:`, writes an `opencode.json` into that folder, and opencode opens in that folder. Work as usual. If several of your servers are up, switch between them with `/models` inside opencode. The tunnel closes when you exit opencode.

### 5. Finish: free the GPU

Exit opencode (`/exit` or Ctrl-C). Then on Minerva:

```bash
bjobs                 # note the JOBID
bkill <JOBID>
```

GPUs are shared. Please release yours when you're done. A job also stops by itself after 12 hours.

To reconnect later while the job is still running, repeat steps 3 and 4 only.

## Troubleshooting

| What you see | What to do |
|---|---|
| `chuangai: command not found` (Minerva) | Add the alias line from setup step 2 to `~/.bash_profile` too, then log in again. |
| `No such file or directory: .../connect` (laptop) | Redo setup step 4. |
| `Permission denied` running `connect` | Run `chmod +x ~/chuangai/bin/connect`. |
| Asks for a password or token, or "Cannot reach Minerva" | Run `ssh -Nf minerva`. Your 8-hour login expired. |
| `No '<model>' job found` | There's no server for that model. Run the matching `chuangai <row>` on Minerva (see `chuangai help`). Your job may also have hit its 12 h limit. |
| `Several servers are published; pick one` | You have more than one server running. Re-run with a model name: `connect qwen27` (the list it prints shows the names). |
| Stays on "queued, waiting for a GPU" | All matching GPUs are busy. Run `chuangai status` on Minerva, and wait. |
| `No API key in ~/.vllm_key` | Do setup step 2. If you changed the key, `bkill` the job and start a new one. |
| `Local port NNNNN busy` | An old tunnel is still running. Run `pkill -f 'ssh .*-L NNNNN:'`, then retry. |
| `Tunnel failed` | Redo setup step 3, then retry. |
| `Server job ended during startup` | Run `ls -t /sc/arion/projects/untreatedIBD/chuangai/logs \| head`. Then run `tail -n 30 <newest .stderr file>`. Send that output to Chris. |
| `opencode not found on PATH` | Install opencode, and open a new terminal. |
| opencode says "connection refused" mid-session | The job ended or the tunnel dropped. Run `bjobs`, start a new job if needed, and run `~/chuangai/bin/connect` again. |
| Replies show `<think>` text | Known cosmetic issue. Tell Chris. |
| Anything else | Run `chuangai help` and send Chris what you ran, what you expected, and what you got. |

## FAQ

- **Can I use it with patient data?** No. See the PHI warning in the README.
- **Can I use other models?** Yes. Each row runs a model: `engineer`/`batch` serve `qwen27`, `reason` serves `qwen27-bf16`, and `frontier` serves `flashnext`. (`script` uses the always-on server and needs no tunnel.) Start the row on Minerva, then run `connect` (or `connect <model>` if you have several servers up) on the laptop. Switch between running servers live with `/models` inside opencode.
- **Will my files be sent anywhere?** opencode runs on your laptop and sends prompts and file contents only to your own server on Minerva, through your tunnel.
- **Why does the first start take so long?** The job waits for a GPU, and then the 29 GB model loads. Later reconnects to a running job take seconds.
- **Can I just type `connect`?** Only if you put `~/chuangai/bin` on your PATH. The full path is more reliable, and a bare `connect` can collide with other tools.
