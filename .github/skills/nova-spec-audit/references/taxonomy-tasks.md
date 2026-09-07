# Tasks Taxonomy

Use this taxonomy to scan tasks spec for underspecified areas. For each category, mark status as: **Clear** (sufficient), **Partial** (some gaps), or **Missing** (not addressed).

## Categories

| Category | What to Check | Template Section |
|----------|---------------|------------------|
| **Phase Structure** | Logical grouping, incremental delivery, naming clarity | Phase N headers |
| **Task Granularity** | 1-2 day chunks, specific enough to implement | Task items (X.Y) |
| **Technical Details** | File paths, components, methods specified | Task descriptions |
| **Requirement Links** | Each task traces to US-XXX, coverage complete | _Requirements: US-XXX_ |
| **Test Requirements** | Unit test expectations per task | Unit test requirements |
| **Dependencies** | Task ordering, blocking relationships, parallelization | Implicit in ordering |
| **Deliverables** | Concrete outputs, acceptance criteria per task | Specific deliverables |

## Common Ambiguities

- Tasks too large (>2 days) or too vague
- Missing requirement traceability (no US-XXX reference)
- No unit test requirements specified
- Unclear task dependencies (which tasks can run in parallel)
- Phase boundaries don't align with deliverable milestones
- Technical details missing (just "implement X" without specifics)

## Coverage Map Template

```markdown
| Category | Status | Notes |
|----------|--------|-------|
| Phase Structure | Clear/Partial/Missing | ... |
| Task Granularity | Clear/Partial/Missing | ... |
| Technical Details | Clear/Partial/Missing | ... |
| Requirement Links | Clear/Partial/Missing | ... |
| Test Requirements | Clear/Partial/Missing | ... |
| Dependencies | Clear/Partial/Missing | ... |
| Deliverables | Clear/Partial/Missing | ... |
```
