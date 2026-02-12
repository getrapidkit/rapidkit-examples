# my-ai-workspace

RapidKit workspace for the published AI Agent tutorial.

- Medium: https://rapidkit.medium.com/build-your-first-ai-agent-with-rapidkit-in-10-minutes-f38a6a12088d
- Dev.to: https://dev.to/rapidkit/build-your-first-ai-agent-with-rapidkit-in-10-minutes-3dj6
- Source repository: https://github.com/getrapidkit/rapidkit-examples/tree/main/my-ai-workspace
- Main runnable project: [ai-agent](ai-agent/README.md)

## Quick Start

```bash
cd ai-agent
source .rapidkit/activate
rapidkit init
rapidkit dev
```

Notes:

- `rapidkit dev` now auto-switches to a free port if your requested/default port is busy.
- API docs: http://127.0.0.1:8000/docs (or the fallback port printed in terminal).

## Health Check

Before running the project, you can validate the whole workspace:

```bash
npx rapidkit doctor --workspace
```

Expected result for this example workspace:

- `Health Score: 100%`
- `All checks passed! Workspace is healthy.`

## Command Reference

When in doubt, print the command catalog:

```bash
npx rapidkit --help
```

Use this to quickly see global commands (create, doctor, modules, etc.) and project commands (init/dev/test/lint).

## Workspace Layout

```text
my-ai-workspace/
├── README.md
└── ai-agent/
    ├── README.md
    └── EXAMPLE_README.md
```

Use:

- `ai-agent/README.md` for day-to-day development commands
- `ai-agent/EXAMPLE_README.md` for tutorial walkthrough and API usage examples
