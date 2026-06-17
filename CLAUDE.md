# headroom_sanitizer

Multi-user auth and access control system for the Headroom LLM proxy.

## Workflow conventions

### OpenSpec changes

This project uses OpenSpec (`spec-driven` schema) for all changes. The standard workflow:

```
/opsx:propose → /opsx:apply → /opsx:sync → /opsx:archive
```

After `/opsx:propose` completes all 4 artifacts (proposal, design, specs, tasks),
**always invoke the `dummy-docs` skill** to generate `DUMMY.MD` at the change root:

```
Skill tool: skill="dummy-docs", args="change=<name> target=<changeRoot>/DUMMY.MD"
```

`DUMMY.MD` is mandatory — it provides a plain-language English explanation of
all design decisions with everyday analogies, concrete persona names, real CLI
usage examples, and an "At a glance" summary table. The skill will ask whether
to also generate a translated copy (e.g., Portuguese) in the `dummy/` directory.

### Language policy

- **Code, CLI output, error messages, docstrings, comments, documentation**: English
- **DUMMY.MD and user-facing explanations**: Portuguese (Brazilian) — layman-friendly

### Branch naming

```
feat/<change-name>
```

Branch from the previous PRD's branch to carry accumulated work forward.

## PRD context

PRDs live at `.compozy/tasks/multi-user-auth-control/`:

| PRD | Change | Branch | Status |
|-----|--------|--------|--------|
| PRD 1 | `admin-cli-user-management` | `feat/admin-cli-user-management` | Archived |
| PRD 2 | `auth-proxy-gateway` | `feat/auth-proxy-gateway` | Archived |
| PRD 2.1 | `websocket-auth` | `feat/websocket-auth` | Proposed (deferred) |
| PRD 3 | `audit-analytics` | `feat/audit-analytics` | Proposed |

## Architecture

```
headroom/auth/          # PRD 1: models, crypto (Fernet), store (Neo4j)
plugins/headroom-auth/  # PRD 2: auth middleware plugin (headroom.proxy_extension)
headroom/usage/         # PRD 3: audit logging + CLI (pending)
headroom/cli/           # CLI commands (auth.py, usage.py)
```

Key patterns:
- Extension system: `headroom.proxy_extension` entry-point group, `install(app, config) -> None`
- Reference plugin: `plugins/headroom-oauth2/`
- Per-request identity: `contextvars` in `headroom/proxy/project_context.py`
- Rate limiter: `headroom/proxy/rate_limiter.py` (TokenBucketRateLimiter)
- Neo4j access: `GraphDatabase.driver` via `Neo4jAuthStore`

## Dependencies

All already in `pyproject.toml`:
- `neo4j>=5.0` — graph database
- `cryptography` — Fernet encryption
- `fastembed` — local embeddings (ONNX)
- `qdrant-client` — vector search
- `click>=8.1.0` — CLI
- `rich>=13.0.0` — terminal output
