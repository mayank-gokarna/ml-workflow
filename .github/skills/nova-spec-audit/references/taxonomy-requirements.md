# Requirements Taxonomy

Use this taxonomy to scan requirements spec for underspecified areas. For each category, mark status as: **Clear** (sufficient), **Partial** (some gaps), or **Missing** (not addressed).

## Categories

| Category | What to Check | Template Section |
|----------|---------------|------------------|
| **Overview** | Problem statement, why feature exists, target users | Overview |
| **User Stories** | All personas covered, clear user types, distinct stories | User Stories |
| **Acceptance Criteria** | EARS patterns used, testable conditions, complete scenarios | Acceptance Criteria |
| **Definition of Done** | Verification steps, test coverage expectations | Definition of Done |
| **Non-Functional** | Performance targets, security, accessibility (if applicable) | Non-Functional Requirements |
| **Dependencies** | External systems, other features, prerequisites | Dependencies |
| **Out of Scope** | Explicit exclusions, boundary clarity | Out of Scope |
| **Open Questions** | Unresolved decisions, blockers identified | Open Questions |

## Common Ambiguities

- Vague user types ("users" vs specific personas)
- Missing negative scenarios (IF unwanted situation...)
- Implicit assumptions about external systems
- Undefined performance/scale expectations
- No explicit out-of-scope boundaries

## Coverage Map Template

```markdown
| Category | Status | Notes |
|----------|--------|-------|
| Overview | Clear/Partial/Missing | ... |
| User Stories | Clear/Partial/Missing | ... |
| Acceptance Criteria | Clear/Partial/Missing | ... |
| Definition of Done | Clear/Partial/Missing | ... |
| Non-Functional | Clear/Partial/Missing | ... |
| Dependencies | Clear/Partial/Missing | ... |
| Out of Scope | Clear/Partial/Missing | ... |
| Open Questions | Clear/Partial/Missing | ... |
```
