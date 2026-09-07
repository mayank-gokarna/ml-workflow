---
name: nova-context-research
description: Use when I invoke @research [topic], or when you must explore unfamiliar code/architecture before implementing (e.g., you need to locate the right entry point, understand the end-to-end flow, or compare patterns across repos) and you want the output captured as a short research notepad with key files, findings, and next steps.
---

<required>
*CRITICAL* Add the following steps to your Todo list using `todo` tool:

1. Clarify with me on the research scope and constraints (topic, repo(s), recency requirements, file types, desired depth) and restate the goal in one sentence.
2. Check whether Nova RAG is available:
	- Check if Nova RAG MCP is installed (server name contains "nova-rag").
	- If installed, call `healthcheck()` to verify connectivity.
	- If not installed or unhealthy, fall back to filesystem-only research.
3. Choose the approach (hybrid vs Nova RAG-only vs filesystem-only).
4. Run the research loop (repeat until confident): search broadly, narrow to likely entry points/canonical implementations, expand context, and verify against the local workspace when possible.
5. Use the [research notepad template](assets/research-notepad-template.md) for output and ask me whether and where to save it.
</required>

# Nova Context Research

Research codebases and gather comprehensive context using a reproducible, multi-step workflow.

## When to Use This Skill

- Exploring unfamiliar codebase or architecture
- Gathering context before implementing a feature
- Finding patterns across multiple repositories

## Research Workflow

### Step 1 — Reflect and Clarify

Before searching, restate my intent in one sentence and confirm:

- **Goal**: what decision/output do I want?
- **Scope**: which repository/repositories, branch, folder(s) (or “unknown / explore”)
- **Recency**: is “latest local workspace state” required, or is “indexed snapshot OK”?
- **Depth**: quick pointer vs deep architecture walkthrough
- **Constraints**: code-only vs docs-only vs both

If any are unclear, don’t start searching blind and ask me questions.

Prompts (use only when needed):

- Scope unclear → “Which repository or scope should I search in?”
- Filters unclear → “Search code only, specific file types, or everything (docs + code)?”
- Recency unclear → “Do you need the latest workspace state, or is indexed snapshot OK?”

### Step 2 — Determine the Search Approach

Pick one of the approaches below, and state the choice explicitly.

| Approach | Use When | Strengths | Risks / Mitigations |
|---|---|---|---|
| Hybrid (default) | Nova RAG available, scope unclear, or you need both breadth + accuracy | Best balance of speed + accuracy | Requires disciplined note-taking + verification |
| Nova RAG-only | Repo not in workspace, or cross-repo pattern search | Fast narrowing, cross-repo | Snapshot may be stale → verify locally if possible |
| Filesystem-only | Nova RAG unavailable (fallback) | Most accurate/current | Slow on larger workspaces |

### Step 3 — Conduct Multi-step Research (Iterate)

Run research as a loop until you can answer the question confidently.

**Tool usage by approach:**

| Approach | Broad search | Deep read / Expand |
|---|---|---|
| Hybrid | Nova RAG | Nova RAG (`get_chunks`) → Filesystem (once narrowed) |
| Nova RAG-only | Nova RAG | Nova RAG (`get_chunks`) |
| Filesystem-only | Filesystem | Filesystem |

1. **Search (broad)**
	- Identify candidate files/locations matching the research topic.
	- *Syntax by tool:*
		- Nova RAG: `discover_index()` (if needed) → `search()` with filters (scope/content_type/file_extension).
		- Filesystem: filename glob or text/regex search → open likely files and follow imports/usages.
2. **Narrow (target files/components)**
	- Prefer “entry points” (routers, CLI entry, main pipeline orchestration) then follow imports/usages.
3. **Expand context**
	- Read surrounding functions/classes to understand the full picture.
	- *Syntax by tool:*
		- Nova RAG: `get_chunks()` around the best chunk(s).
		- Filesystem: open and read the surrounding functions/classes.
4. **Verify / reconcile**
	- If using Nova RAG and the repo exists locally: verify in workspace to avoid snapshot drift.
5. **Refine query**
	- Adjust keywords toward code-shaped patterns (“try/except”, decorator names, class names, config keys).
	- Examples:
		- error handling → `try`, `except`, `raise`
		- auth → `verify`, `token`, `middleware`, `jwt`
		- endpoints → `router`, `@app.route`, `@router`, `FastAPI`

6. **Stop condition**
	- Stop searching when you have sufficient information to support the research topic and answer the user’s question.
	- Usually this means you have:
		- the primary implementation location(s)
		- a minimal end-to-end flow description
		- relevant cross-repo conventions or differences (only if the question spans repos)

Mini-cheats (use sparingly):

- Nova RAG broadening: `discover_index()` → `search(query="...", filters={"content_type": ["code"]})`
- Nova RAG expand context: `get_chunks(scope="...", identifier="...", chunk_orders=[...])`
- Filesystem narrowing: filename glob → text/regex → open file and follow imports/usages

### Step 4 — Create Structured Output

Write results using the research-notepad format in the template:
[research notepad template](assets/research-notepad-template.md)

Checkpoint: ask me:
**“I will format this as a research notepad. Shall I save it?”**

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No results | Broaden query, remove filters, check `discover_index()` for valid scopes |
| Outdated results | Index is a snapshot; read file directly if in workspace |
| Wrong chunk context | Use broader `chunk_orders` range or omit to get all chunks |

## Examples

- [Finding an Implementation](references/example-finding-implementation.md) — Discover → Search → Expand flow
- [Cross-Repo Pattern Search](references/example-cross-repo-search.md) — Find patterns across services
- [Workspace + Remote Search](references/example-workspace-plus-remote.md) — Compare local and indexed code
- [Large Workspace Navigation](references/example-large-workspace.md) — Nova RAG to narrow down, built-in for details
- [Documentation + Code Cross-Reference](references/example-docs-code-crossref.md) — Understand intent and implementation
