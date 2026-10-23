---
title: GA3 Agents
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# GA3 agents (Q2 A2A invoice, Q3 mailroom, Q4 incident) + Q6 face GLB

| Question | URL to paste |
|---|---|
| Q2 A2A base URL | `https://<space-host>/a2a/` |
| Q3 Mailroom endpoint | `https://<space-host>/mailroom` |
| Q4 Incident base URL | `https://<space-host>/incident` |
| Q6 GLB (backup host) | `https://<space-host>/face.glb` |

Space secrets / variables:

- `LLM_API_KEY` (required): AI Pipe token from https://aipipe.org/login (or an OpenAI key)
- `LLM_BASE_URL` (optional, default `https://aipipe.org/openai/v1`; use `https://api.openai.com/v1` for an OpenAI key)
- `LLM_MODEL` (optional, default `gpt-4.1-mini`)
- `EVIDENCE_WITH_BRACKETS` (optional, Q2 only): `1` returns evidence refs as `[REF]` instead of `REF`
