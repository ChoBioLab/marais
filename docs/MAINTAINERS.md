<!-- docs/MAINTAINERS.md -->
# Maintainer notes

## How a session fits together

1. `chuangai engineer` (Minerva) renders `templates/serve.lsf.in`, writes the script to `~/.local/state/chuangai/scripts/`, and runs `bsub`. The job name is `chuangai_<served>_<gpu>_<n>x`.
2. The job computes a port from `cksum("<user>:<served>")` and binds vLLM to `127.0.0.1:<port>` on the compute node. When vLLM first answers, it publishes a one-line JSON record (model, gpu, ctx, parser, host, port, user) to the shared state dir; the job's `trap` removes the record on exit.
3. `bin/connect` (laptop) reads the published records over `ssh minerva`, opens one tunnel per compute node with the port **mirrored** (local port == remote port, 20000–31999), writes a project `opencode.json` with one provider per published server, and starts `opencode --standalone` with `MINERVA_VLLM_KEY` set. Users switch between published models with `/models`. `bjobs` + the port formula remain as a fallback when no record exists yet.

The server-side and fallback port formulas must stay identical:

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

- `registry/hosts.yaml`: `images.blackwell` and `images.cpu` are still `<confirm>` placeholders. Until they are set, `frontier --allow-b200` and the `index` row refuse to render.
- `--kv-cache-dtype fp8` is hard-coded in `templates/serve.lsf.in` for every model. Move it to `models.yaml` (a per-model `kv_dtype`) when a model needs a different one.
- `python3` on a fresh account needs PyYAML. Confirm `chuangai help` works there, or load a module in `bin/chuangai`.
- Add `--limit-mm-per-prompt '{"image":0,"video":0}'` to `qwen27-fp8`'s `vllm_extra` if you want the memory saving.
- The `finetune` row renders, but `templates/train.lsf.in` still assumes the 4-GPU single-node shape (`--nproc-per-node=4`, one rendezvous endpoint) and has no data input; there is also no training image in `hosts.yaml` yet.
- `index` builds an index but nothing queries it yet; the corpus path is hard-coded in `templates/index.lsf.in`.

## Adding a model

1. Add it to `registry/models.yaml` with a **unique** `served` name — job names, ports and opencode model ids all key on it. (`chuangai list` validates uniqueness.)
2. Add a row in `registry/tasks.yaml` if users should launch it by name.
3. `bsub < scripts/pull_models.lsf` to cache the weights.

No code changes: the planner and renderer read the registry, and `bin/connect` reads whatever the servers publish (model, ctx, parser all travel in the record).

## Security notes

- vLLM binds `127.0.0.1` only, and the API key is required. The tunnel is the only path in.
- `--api-key` appears in the process list on the compute node. If that matters, pass the key through the `VLLM_API_KEY` environment variable instead. I haven't verified that your vLLM version honors it.
- The `burst` lane is not PHI-safe (`phi_safe: false` in `registry/hosts.yaml`).

