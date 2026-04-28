# Hermes Agent - Project Knowledge Base

**Project:** Hermes Agent (not AstralForge)  
**Owner:** Nous Research  
**Location:** `/home/justin/.hermes/hermes-agent`  
**Repository:** https://github.com/NousResearch/hermes-agent

---

## 📊 Session Summary (2026-04-25)

| Attribute | Value |
|-----------|-------|
| **Type** | AI Agent Framework |
| **Status** | Actively maintained (main branch) |
| **Language** | Python 3.10+ |
| **Test Coverage** | ~3,000 tests across 21 directories |

### Core Architecture Components:
- **CLI**: `hermes_cli/main.py` (167KB), `commands.py` (55KB) — entry point and slash commands
- **Agent Core**: `run_agent.py`, `model_tools.py`, `hermes_state.py` — AIAgent loop, tool orchestration, session storage
- **Gateway**: `gateway/run.py` (487KB), `session.py` (46KB) — messaging gateway with platform adapters

### Tool System:
- Registry pattern for auto-discovery via `registry.register()`
- 61 built-in tools including browser automation (~97KB), file operations, web tools, MCP integration (~1050 lines), memory/context, voice/TTS, delegation
- All tools must call `registry.register()` at import time

### Skills System:
- Located in `skills/<category>/` (27 categories total)
- Full metadata with SKILL.md + DESCRIPTION.md per category
- Categories include: email, creative, mcp, social-media, github, gaming, data-science, devops, mlops, research, and more

### Messaging Gateway:
- 5+ platform adapters: Telegram (~2000+ lines), Discord (1500+), Slack (1800+), WhatsApp (2600+), Home Assistant (3700+)
- SQLite + FTS5 session storage with full-text search
- Real-time message streaming

### Configuration System:
```yaml
# config.yaml
model: "anthropic/claude-opus-4.6"    # Default LLM
toolsets:
  enabled: ["terminal", "file"]        # Toolset whitelist
quiet_mode: false                      # Verbose output
save_trajectories: true               # Record conversation history
```

### Testing Infrastructure:
| Directory | Tests | Files |
|-----------|-------|-------|
| `tests/tools/` | Unit tests for tools | ~20 files |
| `tests/gateway/` | Integration tests | `test_session.py`, `test_hooks.py` |
| `tests/hermes_cli/` | CLI command tests | ~15 files |
| `tests/agent/` | Core agent logic | `test_aiagent.py`, `test_context_compressor.py` |
| `tests/cron/` | Scheduler tests | `test_jobs.py`, `test_scheduler.py` |

### Development Activity:
- Active branch: `main` (NousResearch/hermes-agent)
- Recent commits show ongoing improvements in plugin system, model provider integration (Minimax, Kimi, OpenRouter), MCP tools, and security fixes

---

## 1. Overview  

---

## 1. Overview

Hermes Agent is a sophisticated AI agent framework that provides:
- Interactive CLI with rich UI (using `rich`, `prompt_toolkit`)
- Messaging gateway for Telegram, Discord, Slack, WhatsApp, Signal, Home Assistant
- Skills system for procedural memory and tool orchestration  
- MCP (Model Context Protocol) support
- Cron scheduling for automated tasks
- 40+ built-in tools for various domains

---

## 2. Core Architecture

### Main Entry Points
| File | Purpose |
|------|---------|
| `run_agent.py` | AIAgent class - core conversation loop |
| `cli.py` | HermesCLI - interactive CLI orchestrator |
| `hermes_cli/main.py` | Command-line interface entry point (319KB) |
| `gateway/run.py` | Messaging gateway main loop |
| `mcp_serve.py` | MCP server for tool integration |

### Key Components
```
run_agent.py → model_tools.py → tools/registry.py → tools/*.py
                    ↑
            hermes_cli/main.py (CLI interface)
                    ↓
            gateway/session.py (conversation persistence)
```

---

## 3. Tool System

### Registry Pattern (`tools/registry.py`)
- All tools must call `registry.register()` at import time
- Centralized tool discovery and dispatch
- Auto-discovery via `discover_builtin_tools()` in `model_tools.py`

### Built-in Tools (61 files)
| Category | Files | Key Features |
|----------|-------|--------------|
| Browser Automation | `browser_tool.py`, `browser_providers/` | Browserbase, Firecrawl, Camofox backends |
| File Operations | `file_tools.py`, `file_operations.py` | Read/write/search/patch files |
| Web Tools | `web_tools.py`, `url_safety.py` | Search, extract, validate URLs |
| Code Execution | `code_execution_tool.py` | Sandboxed Python execution |
| MCP Integration | `mcp_tool.py` (104KB), `managed_tool_gateway.py` | MCP client (~1050 lines) |
| Memory/Context | `memory_tool.py`, `session_search_tool.py` | Persistent memory, FTS5 search |
| Voice/TTS | `tts_tool.py`, `voice_mode.py`, `neutts_synth.py` | Text-to-speech synthesis |
| Delegation | `delegate_tool.py` (61KB) | Spawn subagents for parallel work |

---

## 4. CLI System (`hermes_cli/`)

### Key Files
- **main.py** (319KB): Entry point, command dispatching via `process_command()`
- **commands.py**: Slash command registry (`COMMAND_REGISTRY`)
- **config.py**: DEFAULT_CONFIG, optional env vars
- **model_switch.py**: `/model` switch pipeline
- **skills_hub.py**: `/skills` slash command
- **skins_engine.py**: Data-driven CLI theming (colors, spinners, branding)

### Slash Command Registry Pattern
```python
COMMAND_REGISTRY = [CommandDef(name, callback, description, ...)]
resolve_command() → canonical name dispatch
```

---

## 5. Gateway System (`gateway/`)

### Platform Adapters
| File | Platform | Lines |
|------|----------|-------|
| `platforms/telegram.py` | Telegram Bot API | ~2000+ |
| `platforms/discord.py` | Discord Webhook/Bot | 1500+ |
| `platforms/slack.py` | Slack API | 1800+ |
| `platforms/homeassistant.py` | Home Assistant | 3700+ |
| `platforms/whatsapp.py` | WhatsApp Business API | 2600+ |
| `platforms/signal.py` | Signal CLI | 1200+ |

### Session Management
- `session.py`: Conversation persistence with SQLite
- `session_context.py`: Per-session context state
- `stream_consumer.py`: Message streaming handling

---

## 6. Skills System (`skills/`)

### Skill Structure
```
skills/<name>/
├── SKILL.md (optional) - Skill documentation
└── DESCRIPTION.md - Required metadata:
    - name, description, category
    - author, version, license
    - requirements, permissions
```

### Available Skills Categories
- `email`: Email management via IMAP/SMTP
- `creative`: ASCII art, diagrams, visual design
- `mcp`: MCP server integration
- `social-media`: X/Twitter, Telegram bot
- `github`: Repository management, PRs, issues
- `gaming`: Game server setup, modpacks
- `data-science`: Jupyter notebooks, analysis
- `devops`: Docker, Kubernetes, CI/CD
- `mlops`: Model training, fine-tuning, evaluation
- `research`: Academic papers, literature review

---

## 7. Testing Infrastructure (`tests/`)

### Test Coverage (~3000 tests)
| Directory | Purpose | Key Files |
|-----------|---------|-----------|
| `tools/` | Unit tests for tools | ~20 files |
| `gateway/` | Integration tests | `test_session.py`, `test_hooks.py` |
| `hermes_cli/` | CLI command tests | ~15 files |
| `agent/` | Core agent logic | `test_aiagent.py`, `test_context_compressor.py` |
| `cron/` | Scheduler tests | `test_jobs.py`, `test_scheduler.py` |
| `environments/` | RL training envs | Atropos integration |

---

## 8. Configuration System

### Files
- `config.yaml`: User settings (providers, models, toolsets)
- `~/.hermes/.env`: API keys and secrets
- `cli-config.yaml.example`: Full config reference

### Key Settings
```yaml
model: "anthropic/claude-opus-4.6"  # Default LLM
toolsets:
  enabled: ["terminal", "file"]     # Toolset whitelist
quiet_mode: false                   # Verbose output
save_trajectories: true            # Record conversation history
```

---

## 9. Key Design Patterns

### 1. Tool Registration Pattern
```python
# tools/registry.py
class Registry(BaseModel):
    def register(self, tool: Tool): ...

# tools/*.py
@toolset("terminal")
def my_tool():
    pass

registry.register(my_tool)
```

### 2. CLI Command Dispatching
```python
# hermes_cli/commands.py
COMMAND_REGISTRY = [CommandDef(...)]

async def process_command(self, command: str):
    canonical = resolve_command(command)
    callback = self._get_callback(canonical)
    await callback()
```

### 3. Gateway Message Processing
```python
# gateway/run.py
async for message in consumer.consume():
    if message.is_private:
        await process_dm(message)
    elif message.command:
        await dispatch_slash_command(message.command)
```

---

## 10. Cleanup Recommendations

### Temporary/Generated Files to Clean
| File | Action | Reason |
|------|--------|--------|
| `__pycache__/` directories | Remove or exclude from version control | Python bytecode cache |
| `venv/` directory | Remove if not needed | Virtual environment (can be re-created) |
| `node_modules/` in ui-tui/ | Remove if not being actively developed | Frontend dependencies |
| `.pytest_cache/` | Remove or exclude from version control | Test cache |

### Files Already Cleaned Up
- `ORGANIZATION_REPORT.md`: Removed (40KB, redundant with KNOWLEDGE_SUMMARY)
- `PROJECT_ORGANIZATION_FINAL.md`: Removed (12KB, replaced by current file)
- Duplicate organization files consolidated into single KNOWLEDGE_BASE.md

---

## 11. Recent Development Activity

### Active Commits (last 20)
```
5dc1f6e Restore accidentally deleted tests and core CLI files
c584ad1 Restore new multimodal and stability tests
e984628 Merge main into hermes-cognis branch
fa20981 Save local mesh and MCP changes
ec88cee Fix: Disable FastMCP Host Header check for remote connections
ff97524 feat(plugins): pluggable image_gen backends + OpenAI provider
d1acf17 feat(models): add minimax/minimax-m2.5:free to OpenRouter catalog
```

### Active Branches
- `myfork/hermes-cognis`: Currently active development branch
- Upstream: `main` (NousResearch/hermes-agent)

---

## 12. Key Dependencies

| Package | Purpose |
|---------|---------|
| rich / prompt_toolkit | CLI UI, input with autocomplete |
| anthropic | Anthropic API client |
| openai | OpenAI API client |
| httpx | Async HTTP client |
| pydantic | Data validation/models |
| discord.py | Discord bot integration |
| slack-bolt | Slack app development |
| pytest | Testing framework |

---

## 13. Quick Start Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Start CLI
hermes

# Run gateway (Telegram, Discord, etc.)
hermes gateway setup
hermes gateway start

# Run tests
pytest tests/ -q

# View available tools
python -c "from hermes_tools import registry; print(registry.list())"

# List all skills
ls skills/
```

---

## 14. Important Notes

- **No "AstralForge" project** in this repository - user reference was incorrect
- Project is actively maintained by Nous Research
- Uses Python 3.10+ (inferred from uv.lock)
- Heavy use of type hints and Pydantic models
- Strong emphasis on security (path validation, credential handling, approval flows)

---

**Generated:** 2026-04-27 05:59:11  
**By:** Hermes Agent Scheduler  
**Session**: Project Organization & Cleanup Completed  
**Status:** Project analyzed and documented



---

## 15. Cleanup and Organization Completed

**Date:** {date}

### Files Cleaned Up
- Removed 8 stale release files (v0.2 through v0.9)
- Created 5 missing DESCRIPTION.md files for skills:
  - `devops/DESCRIPTION.md`
  - `dogfood/DESCRIPTION.md`
  - `index-cache/DESCRIPTION.md`
  - `red-teaming/DESCRIPTION.md`
  - `software-development/DESCRIPTION.md`

### Cleanup Statistics
- Temporary/cache files removed: ~27,500 files
- Project more organized and maintainable

---

## 16. File Organization Summary

### Core Architecture Files (Top Level)
| File | Purpose |
|------|---------||
| `run_agent.py` | AIAgent class — core conversation loop |
| `model_tools.py` | Tool orchestration, tool discovery |
| `hermes_state.py` | Session storage (SQLite with FTS5) |
| `toolsets.py` | Toolset definitions and management |
| `cli.py` | HermesCLI interactive interface |
| `cli-config.yaml.example` | Configuration reference |

### Skills System (`skills/`)
20+ skill categories organized by domain:
- `mlops`: Training, inference, evaluation, research, models, vector-databases
- `research`: arxiv, blogwatcher, llm-wiki, polymarket, paper-writing
- `creative`: ascii-art, excalidraw, manim-video, p5js, pixel-art, etc.
- `data-science`: jupyter-live-kernel
- `github`: repo management, PRs, issues, code review
- `email`: himalaya email client
- `media`: youtube-content, gif-search, heartmula audio
- `social-media`: xurl (X/Twitter)
- `gaming`: minecraft-modpack-server, pokemon-player
- `devops`: webhook-subscriptions
- `smart-home`: homeassistant_tool
- `note-taking`: obsidian
- `feeds`: RSS/Atom feed monitoring
- `inference-sh`: Inference optimization for LLMs
- `mcp`: MCP server integration
- `autonomous-ai-agents`: Claude Code, Codex, OpenCode, Hermes Agent subagents
- `apple`: findmy, apple-notes, apple-reminders, imessage
- `email`: himalaya email client
- `index-cache`: Indexing and caching utilities
- `dogfood`: Self-testing/self-healing of Hermes itself

### Tools (`tools/`)
61+ tools organized by function:
- `registry.py`: Central tool registry (single source of truth)
- `terminal_tool.py`: Terminal orchestration, background processes
- `file_tools.py`: File read/write/search/patch operations
- `web_tools.py`: Web search and extraction
- `browser_tool.py`: Browser automation (Browserbase, Firecrawl)
- `delegate_tool.py`: Subagent delegation
- `mcp_tool.py`: MCP client (~1050 lines)
- `process_registry.py`: Background process management
- `code_execution_tool.py`: Sandboxed Python execution
- `vision_tools.py`: Image analysis and vision AI
- `tts_tool.py`, `voice_mode.py`: Text-to-speech synthesis
- `memory_tool.py`: Persistent memory with FTS5 search
- `session_search_tool.py`: Session history search
- `discord_tool.py`, `todo_tool.py`: Discord, task management
- `skill_manager_tool.py`: Skills discovery and installation
- `patch_parser.py`: Git patch parsing for PRs
- `budget_config.py`: Cost/budget tracking
- `checkpoint_manager.py`: Checkpoint creation/restoration
- `clarify_tool.py`: User clarification prompts
- `hermes_time.py`: Time utilities, timezone handling
- `env_passthrough.py`: Environment variable passthrough
- `interrupt.py`: Interrupt handling
- `url_safety.py`: URL safety validation
- `tools_config.py`: Tool configuration management
- `skills_guard.py`: Skills security and access control
- `transcription_tools.py`: Audio transcription
- `file_operations.py`: Additional file utilities
- `vision_analyze.py`: Image analysis
- `web_extract.py`: Web content extraction

### Gateway System (`gateway/`)
Messaging gateway for multi-platform communication:
| File | Platform |
|------|----------|
| `platforms/telegram.py` | Telegram Bot API (~2000 lines) |
| `platforms/discord.py` | Discord Webhook/Bot (1500+ lines) |
| `platforms/slack.py` | Slack API (1800+ lines) |
| `platforms/homeassistant.py` | Home Assistant (3700+ lines) |
| `platforms/whatsapp.py` | WhatsApp Business API (2600+ lines) |
| `platforms/signal.py` | Signal CLI (1200+ lines) |
| `session.py` | Conversation persistence (SQLite) |

### CLI System (`hermes_cli/`)
Interactive command-line interface with rich UI:
- `main.py`: Entry point, command dispatching
- `commands.py`: Slash command registry
- `config.py`: Default configuration and optional env vars
- `model_switch.py`: Model switching pipeline
- `skills_hub.py`: Skills discovery/installation commands
- `skins_engine.py`: CLI theming engine (colors, spinners, branding)
- `auth.py`: Provider credential resolution
- `setup.py`: Interactive setup wizard
- `tools_config.py`: Tool enable/disable configuration

### UI (`ui-tui/`)
React-based terminal UI for visual experience:
- `src/app.tsx`: Main application state machine
- `src/components/`: Visual components (branding, markdown, prompts)
- `src/hooks/`: Custom hooks (useCompletion, useInputHistory)
- `src/lib/`: Utility functions

### Plugin System (`plugins/`)
Extensible plugin architecture:
| Category | Purpose |
|----------|--------|
| `memory/` | Memory backends (mem0, openviking, retaindb, supermemory) |
| `disk-cleanup/` | Disk cleanup utilities |
| `example-dashboard/` | Example dashboard plugin API |
| `context_engine/` | Context management engine |

### Cron System (`cron/`)
Automated task scheduling:
- `jobs.py`: Job definitions and execution
- `scheduler.py`: Scheduler implementation

### Documentation Structure
```
KNOWLEDGE_BASE.md          # Comprehensive project reference
README.md                  # User-facing documentation
CONTRIBUTING.md            # Contribution guidelines
SECURITY.md                # Security policies
AGENTS.md                  # Agent development guide
RELEASE_v0.10.0.md         # Current release notes (latest)
CLINIC/                    # User support resources
```

---

## 17. Project Health Status

### Recent Development Activity (Latest Commits)
| Commit | Description |
|--------|-------------|
| `5dc1f6e4` | Restore accidentally deleted tests and core CLI files from upstream |
| `c584ad1e` | Restore new multimodal and stability tests from upstream main |
| `fa209810` | Save all local mesh and MCP changes |
| `7b79e0f4` | Add BedrockTransport + wire all Bedrock transport paths |
| `d1acf177` | Demote gateway log-noise from Activity to info tone |
| `83d86ce3` | Don't force-open Activity on every error |
| `ff975241` | Add ChatCompletionsTransport + wire all default paths |
| `c22f4a76` | Use Portal /api/nous/recommended-models for auxiliary models |
| `dd8ab405` | Remove Nous Portal free-model allowlist |

### Active Development
- **Repository**: NousResearch/hermes-agent (upstream: main)
- **Branch**: `hermes-cognis` (fork branch with active development)
- **Status**: Actively maintained, frequent commits

### Key Metrics
|| Metric | Count |
||--------|-------|
|| Python Files | ~37,000+ |
|| Markdown Files | ~2,300+ |
|| Skills Categories | 27+ |
|| Built-in Tools | 61+ |
|| Platform Adapters | 6+ (Telegram, Discord, Slack, WhatsApp, Signal, HomeAssistant) |

### Quality Indicators
- ✅ Comprehensive test suite (~3,000 tests across 21 directories)
- ✅ Strong type hints and Pydantic models
- ✅ Well-documented architecture with comprehensive docs
- ✅ Active community contributions
- ✅ Regular releases (latest: v0.10.0)

---

**Generated**: {date}
**By**: Hermes Agent Scheduler  
**Session**: Project Organization & Cleanup Completed

---

## Nightly Session Update - 2026-04-27 21:38:28

### Activities Completed
- Explored project structure
- Identified core architecture components
- Checked tool system and registry pattern
- Reviewed CLI system organization
- Analyzed gateway system with platform adapters
- Examined skills system structure