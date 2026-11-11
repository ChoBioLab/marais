---
description: Run BioMCP health check and report any errors or missing API keys.
agent: analyst
---

# BiomCP Health Check

This command executes `biomcp health --apis-only`, captures the output, and:
1. Displays the full table for reference.
2. Highlights any rows with **error** status.
3. Lists APIs that are **excluded** because required keys are missing.
4. Suggests the environment variable or secret name to set for each excluded API.

```bash
biomcp health --apis-only > results/biomcp_health.txt
```

After running, you can view the report with:

```
cat results/biomcp_health.txt
```

If errors are present, consider:
- Checking network connectivity.
- Verifying that the specific API (e.g., Europe PMC) is reachable.
- Adding missing API keys to `~/.config/opencode/secrets/` and updating the corresponding environment variable (e.g., `NCI_API_KEY`, `ONCOKB_TOKEN`).

Use this command periodically to ensure downstream literature and variant queries work reliably.
