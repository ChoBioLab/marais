---
name: literature
description: Run biomcp literature search (PubMed + Semantic Scholar) and return a markdown table of citations.
steps: 3
permission:
  edit: deny
  bash: allow
  webfetch: deny
  task: deny
---
1. Execute the shell command `biomcp search article --source semanticscholar "<QUERY>"` (replace `<QUERY>` with the user's request). This returns a list of matching articles with Semantic Scholar metadata.
2. For each result, extract a concise claim or summary, the title/abstract excerpt, PMID or DOI, and the Semantic Scholar URL (you can build the URL as `https://www.semanticscholar.org/paper/<paper_id>` using the `paper_id` field returned by the API).
3. Return a markdown table with columns `claim | evidence | PMID/DOI | source | confidence`.
