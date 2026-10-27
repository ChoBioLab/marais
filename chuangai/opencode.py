"""Write opencode.json for a planned server. Nothing here starts a process."""

from __future__ import annotations

import json
import pathlib

DEFAULT_PATH = pathlib.Path("opencode.json")


def write(p, path: pathlib.Path | None = None, port: int = 8000) -> pathlib.Path:
    path = path or DEFAULT_PATH
    served = p.model["served"]
    base = p.base_url.replace("/v1", "").rstrip("/")
    base = f"{base.rsplit(':', 1)[0]}:{port}/v1"

    cfg = {
        "$schema": "https://opencode.ai/config.json",
        "provider": {
            "vllm": {
                "npm": "@ai-sdk/openai-compatible",
                "name": "vLLM (chuangai)",
                "options": {
                    "baseURL": base,
                    "apiKey": "{file:~/.vllm_key}",
                },
                "models": {
                    served: {
                        "name": f"{served} ({p.gpu or 'cpu'} x{p.gpus})",
                        "tool_call": p.model.get("parser") not in (None, "none"),
                        "limit": {"context": p.model["ctx"]},
                    }
                },
            }
        },
        "model": f"vllm/{served}",
    }
    path.write_text(json.dumps(cfg, indent=2) + "\n")
    return path
