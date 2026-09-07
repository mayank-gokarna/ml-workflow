---
date: [ISO timestamp]
topic: "[Research Question]"
status: complete
---

# Research: [Research Question]

**Date**: [ISO timestamp]
**Scopes Searched**: [repo/branch, repo2/branch, ...]
**Approach**: [filesystem-only | nova-rag-only | hybrid]
**Recency**: [workspace-latest | index-snapshot-ok]
**Assumptions / Clarifications**: [brief bullets]

## Summary
[High-level answer to the research question]

## Search Context
Queries and filters used (for reproducibility):
- `search(query="...", filters={...})` → [what it found]
- Built-in search for "..." in workspace → [what it found]

## Detailed Findings

### [Component/Area 1]
- **Source**: [workspace | Nova RAG index]
- **Location**: [path/to/file.py](link) lines X-Y
- Description and how it connects to other components

### [Component/Area 2]
...

## Cross-References
| File | Source | Description |
|------|--------|-------------|
| `path/to/file.py:123` | workspace | ... |
| `other/repo/file.ts:45` | Nova RAG | ... |

## Architecture Patterns
[Higher-level patterns, conventions, and design decisions discovered across the codebase]
- How components interact
- Common patterns used across repos
- Design decisions and their rationale (if documented)

## Open Questions
[Areas needing further investigation]