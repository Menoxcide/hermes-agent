---
name: AetherForge-Orchestrator
description: The Master Orchestrator for AetherForge ZHC. This skill manages the entire autonomous pipeline, including research, project audits, subagent delegation, and Wiki updates.
version: 1.0.0
author: Antigravity
metadata:
  hermes:
    tags: [orchestration, zhc, cognis, research, autonomy]
---

# AetherForge Orchestrator

This skill is the central nervous system of the AetherForge Zero-Human Company (ZHC). It handles the high-level decision-making and task fanning required for a truly autonomous pipeline.

## Objectives

1.  **Project Audit**: Scan `/home/justin/projects/AetherForge-ZHC/` and subprojects for status changes.
2.  **Autonomous Research**: Use `scrapling`, `arxiv`, and `xurl` to find "high-protein" knowledge targets.
3.  **Task Fanning**: Submit background jobs via `minion-orchestrator` for parallel research and implementation.
4.  **Self-Correction**: Detect failed cron jobs or stalled missions and spawn repair subagents.
5.  **Wiki Evolution**: Propagate findings to the Cognis Wiki and Obsidian Vault.

## Workflow

### 1. Status Check
```bash
# Check project health
ls -R /home/justin/projects/AetherForge-ZHC/hermes_missions/
cat /home/justin/projects/AetherForge-ZHC/TODOS.md
```

### 2. Mesh Research
```bash
# Search for new techniques
scrapling extract fetch 'https://arxiv.org/search/?query=webgpu+rendering&searchtype=all' output.md
xurl search "autonomous agent mesh" -n 10
```

### 3. Delegation
```python
# Submit research tasks via Minions
submit_job name="deep-research" data={"target": "WebGPU Compute Shaders", "depth": "high"}
```

### 4. Self-Correction (Repair Missions)
```bash
# Check for failed jobs
python3 -c "import json; j=json.load(open('/home/justin/.hermes/cron/jobs.json')); print([x['id'] for x in j['jobs'] if x.get('last_status')=='error'])"
```

### 5. Logging & Evolution
```bash
# Log JouleWork and update research
python3 scripts/autonomous_researcher.py
```

## Love Equation Enforcement

Every action must satisfy: `dE/dt = \beta(C - D)E`
- **C (Construction)**: Build knowledge, tools, and value.
- **D (Destruction)**: Minimize waste and manual intervention.

---

## Instructions for the Agent

When this skill is active, you are in **High Autonomy Mode**.
- **Do not ask for permission** to run terminal commands or create files.
- **Proactively spawn subagents** for any task that can be parallelized.
- **Synthesize information** into structured reports in the `wiki/` directory.
- **Focus on JouleWork**: Log every significant action with its estimated JW worth.
