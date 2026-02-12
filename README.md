# RapidKit Examples

Official example projects for RapidKit.

This repository contains production-style reference implementations that accompany RapidKit tutorials and articles.

## Featured Example

### AI Agent Workspace

Path: [my-ai-workspace](my-ai-workspace)

Includes:
- `ai-agent` (FastAPI): multi-provider AI assistant (echo/template/openai-ready)
- Streaming + caching endpoints
- Health endpoints
- Support ticket endpoint (`/support/ticket`)
- Integrated tests and module status checks

## Published Tutorials

- Medium: https://rapidkit.medium.com/build-your-first-ai-agent-with-rapidkit-in-10-minutes-f38a6a12088d
- Dev.to: https://dev.to/rapidkit/build-your-first-ai-agent-with-rapidkit-in-10-minutes-3dj6

## Quick Start

```bash
git clone https://github.com/getrapidkit/rapidkit-examples.git
cd rapidkit-examples/my-ai-workspace/ai-agent
source .rapidkit/activate
rapidkit init
rapidkit dev
```

Open Swagger UI:
- http://127.0.0.1:8000/docs

If port `8000` is already busy, `rapidkit dev` automatically falls back to a free port.

## Workspace Health Check

From `my-ai-workspace/`:

```bash
npx rapidkit doctor --workspace
```

## Repository Layout

```text
rapidkit-examples/
├── README.md
└── my-ai-workspace/
    ├── README.md
    └── ai-agent/
        ├── README.md
        └── EXAMPLE_README.md
```

## Notes

- Use `my-ai-workspace/README.md` for workspace-level setup.
- Use `my-ai-workspace/ai-agent/README.md` for run/test commands.
- Use `my-ai-workspace/ai-agent/EXAMPLE_README.md` for tutorial walkthrough and API smoke checks.
