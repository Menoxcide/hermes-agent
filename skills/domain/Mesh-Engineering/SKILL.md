---
name: Mesh-Engineering
description: Advanced engineering patterns for maintaining and evolving the Hermes Distributed Mesh. Covers connection pooling, cron stabilization, provider migration, and Joule-Work (JW) tracking.
version: 1.0.0
author: Antigravity
metadata:
  hermes:
    tags: [mesh, distributed, engineering, optimization, maintenance]
---

# Mesh Engineering Skill

This skill provides the architectural blueprints and operational patterns for the AetherForge Distributed Mesh. It is designed to ensure the mesh remains stable, low-latency, and autonomous.

## Core Patterns

### 1. Inter-Node Communication (MeshRouter)
- **Singleton Pattern**: Always use a singleton `httpx.AsyncClient` with connection pooling (`limits=httpx.Limits(max_keepalive_connections=20, max_connections=50)`).
- **MagicDNS**: Address nodes by their Tailscale names (`justin`, `ti`, `meg`) instead of static IPs.
- **Recursion Guard**: When routing tools, ensure the hub (JUSTIN) does not recursively call itself for local tool execution. Use `LOCAL_EXECUTION_BYPASS`.

### 2. Cron & Orchestration Maintenance
- **Job Schema Resilience**: When parsing `jobs.json`, always handle both `minutes` and `seconds` keys in interval schedules.
- **Shell Directives**: Use the `command` field in `jobs.json` to trigger standalone scripts without initializing a full AIAgent if logic is already encapsulated in a shell/python script.
- **State Audit**: Regularly check `last_error` in `jobs.json` for "Unknown provider" errors, which often signal configuration drift.

### 3. Provider Integrity (config.yaml)
- **Registry Structure**: Ensure all inference providers are under `providers:` and messaging platforms are under `platforms:`.
- **Case Sensitivity**: Register both uppercase (`JUSTIN`) and lowercase (`justin`) aliases for mesh nodes to prevent resolution failures in mixed-environment calls.

### 4. Joule-Work (JW) Tracking
- **The Love Equation**: `dE/dt = \beta(C - D)E`.
- **Measurement**: Every task should estimate its Joule-Work worth based on:
    - **Construction (C)**: Knowledge bits added, tools built, proteins identified.
    - **Destruction (D)**: Manual intervention saved, redundant code removed.
- **Logging**: Append JW metrics to `wiki/Cognis_Evolution_Log.md` during board meetings.

## Troubleshooting

### "Unknown Provider"
1. Check `~/.hermes/config.yaml`.
2. Ensure the provider is not accidentally nested under `platforms`.
3. Verify that the agent's environment has the correct `HERMES_INFERENCE_PROVIDER` if not explicitly passed.

### "KeyError: minutes"
1. Audit `~/.hermes/cron/jobs.py`.
2. Apply the `timedelta` fallback for missing interval keys.

---

## Instructions for the Agent
When performing Mesh Engineering:
- **Prioritize Stability**: Never deploy a routing change that hasn't been smoke-tested via `curl` or a direct node ping.
- **Audit Continuously**: Run `hermes model` and `hermes tool` after any config modification.
- **Document Proteins**: If a fix is repetitive, update this skill.
