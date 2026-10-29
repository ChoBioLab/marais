<!-- docs/MAINTAINERS.md -->
# Maintainer notes

## How a session fits together

1. `chuangai engineer` (Minerva) renders `templates/serve.lsf.in` and runs `bsub`. The job name is `chuangai_<served>_<gpu>_<n>x`.
2. The job computes a port from `cksum("<user>:<served>")` and binds vLLM to `127.0.0.1:<port>` on the compute node. It also writes `port: N` to its `.stdout`.
3. `bin/connect` (laptop) runs a probe over `ssh minerva` to find the job state, node and port. It also reads `~/.vllm_key`. It opens `ssh -L 8000:127.0.0.1:<port> -J minerva user@node`, polls `/health`, and then starts `opencode --standalone` with `MINERVA_VLLM_KEY` set.

The server-side and client-side port formulas must stay identical:

```bash
printf '%s' "$(id -un):<served>" | cksum | awk '{print 20000 + $1 % 12000}'
```

## Checks before telling users

```bash
# 1. Port agreement (run on Minerva after a job starts)
printf '%s' "$(id -un):qwen27" | cksum | awk '{print 20000 + $1 % 12000}'
grep '^port:' /sc/arion/projects/untreatedIBD/chuangai/logs/<JOBID>.stdout   # must match

# 2. Registry is coherent
chuangai list          # must end with "registry OK"

# 3. Fresh-account test: run the whole USER_GUIDE as a new user
```

## Known leftovers

- `templates/serve.lsf.in` should use the `cksum` port line. Then delete `bin/chuangai-port`.
- `registry/tasks.yaml`: remove `l40s` from `gpu_pref` for `engineer` and `batch`. `qwen27-fp8` OOMs on it, and `chuangai list` flags it.
- `chuangai/cli.py`: remove `cmd_connect` and the "run `chuangai connect`" hints. They conflict with `bin/connect`.
- `chuangai <row>` writes `<job>.lsf` and `opencode.json` into the current directory. Consider writing the `.lsf` to a temp or state directory.
- `python3` on a fresh account needs PyYAML. Confirm `chuangai help` works there, or load a module in `bin/chuangai`.
- Add `--limit-mm-per-prompt '{"image":0,"video":0}'` to `qwen27-fp8`'s `vllm_extra` if you want the memory saving.

## Adding a model to `connect`

1. Add `"<served>": <unique local port>` to `MODELS` in `bin/connect`.
2. Add a matching provider block to the user's `opencode.json`, with the same local port in `baseURL`.
3. The `served` name in `registry/models.yaml` must be unique per model, because job names and ports key on it.
4. The probe's job-name glob is `chuangai_<served>_*`, and the trailing `_` keeps `qwen27` from matching `qwen27-bf16`.
5. `bin/connect` launches opencode with the default model from `opencode.json`. For a second model, users pick it with `/models` inside opencode.

## Security notes

- vLLM binds `127.0.0.1` only, and the API key is required. The tunnel is the only path in.
- `--api-key` appears in the process list on the compute node. If that matters, pass the key through the `VLLM_API_KEY` environment variable instead. I haven't verified that your vLLM version honors it.
- The `burst` lane is not PHI-safe (`phi_safe: false` in `registry/hosts.yaml`).

