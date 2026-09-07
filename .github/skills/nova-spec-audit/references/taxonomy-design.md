# Design Taxonomy

Use this taxonomy to scan design spec for underspecified areas. For each category, mark status as: **Clear** (sufficient), **Partial** (some gaps), or **Missing** (not addressed).

## Categories

| Category | What to Check | Template Section |
|----------|---------------|------------------|
| **Overview** | Purpose, key decisions, requirement cross-references | Overview |
| **Architecture Diagrams** | Component relationships, layer boundaries, Mermaid diagrams | High-Level Architecture |
| **Request Flows** | Sequence diagrams, key interactions, async vs sync | Request Flow |
| **Components** | Single responsibility, clear interfaces, technology choices | Components and Interfaces |
| **API Contracts** | Endpoints, request/response schemas, versioning | API Endpoints |
| **Data Models** | Entities, relationships, field types, constraints | Data Models |
| **Error Handling** | Error categories, propagation strategy, recovery | Error Handling |
| **Testing Strategy** | Unit/integration/E2E approach, coverage expectations | Testing Strategy |

## Common Ambiguities

- Missing component boundaries or overlapping responsibilities
- Undefined API versioning strategy
- Error handling strategy not specified per component
- No sequence diagram for critical flows
- Data model relationships unclear (1:1, 1:N, N:M)
- Testing approach not tied to components

## Coverage Map Template

```markdown
| Category | Status | Notes |
|----------|--------|-------|
| Overview | Clear/Partial/Missing | ... |
| Architecture Diagrams | Clear/Partial/Missing | ... |
| Request Flows | Clear/Partial/Missing | ... |
| Components | Clear/Partial/Missing | ... |
| API Contracts | Clear/Partial/Missing | ... |
| Data Models | Clear/Partial/Missing | ... |
| Error Handling | Clear/Partial/Missing | ... |
| Testing Strategy | Clear/Partial/Missing | ... |
```
