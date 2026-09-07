---
name: nova-spec-audit
description: Use when I invoke @audit [requirements/design/tasks], or when working on a spec file (requirements.md, design.md, tasks.md) and you detect ambiguous or underspecified areas that need audit before proceeding.
---

<required>
*CRITICAL* Add the following steps to your Todo list using `todo` tool:

1. Identify the active feature (use [nova-feature-management](../nova-feature-management/SKILL.md) `@feature status`) and target spec file (requirements.md, design.md, or tasks.md).
2. Decide spec type, then load the matching taxonomy ([taxonomy-requirements](references/taxonomy-requirements.md), [taxonomy-design](references/taxonomy-design.md), or [taxonomy-tasks](references/taxonomy-tasks.md)) and scan for ambiguities to build a coverage map.
3. Generate a prioritized queue of up to 5 clarifying questions (do NOT show all at once).
4. Run the sequential questioning loop: ask one question at a time, validate my answer, record it.
5. After each accepted answer, update the spec file immediately (integrate into relevant sections).
6. Report completion with coverage summary and suggest next steps.
</required>

# Nova Spec Audit

Detect and reduce ambiguity in feature specifications through targeted clarifying questions, recording answers directly in the spec file.

## When to Use This Skill

- I invoke `@audit requirements`, `@audit design`, or `@audit tasks`
- Working on a spec file and noticing gaps that block the next phase
- Before advancing to the next spec-driven development stage (requirements → design → tasks → code)

## Audit Workflow

### Step 1 — Identify Target Spec

Determine which spec file to audit:
- `@audit requirements` → `specs/<feature>/requirements.md`
- `@audit design` → `specs/<feature>/design.md`
- `@audit tasks` → `specs/<feature>/tasks.md`
- No argument → Ask me which spec type to audit

If no active feature, prompt me to set one via `@feature switch <path>` or `@feature create <path>`.

### Step 2 — Scan for Ambiguities

Load the taxonomy matching the spec type:
- requirements.md → [taxonomy-requirements.md](references/taxonomy-requirements.md)
- design.md → [taxonomy-design.md](references/taxonomy-design.md)
- tasks.md → [taxonomy-tasks.md](references/taxonomy-tasks.md)

For each category, mark: **Clear** / **Partial** / **Missing**.

Skip audit if:
- No critical ambiguities found → Report "No critical ambiguities detected" and suggest proceeding
- Spec file missing → Instruct me to create it first

### Step 3 — Generate Questions (Internal)

Build a prioritized queue of maximum 5 questions. Apply these constraints:

- Each question must be answerable with:
  - Multiple-choice (2-5 options), OR
  - Short answer (≤5 words)
- Only include questions that materially impact: architecture, data modeling, task decomposition, test design, UX behavior, or operational readiness
- Prioritize by: (Impact × Uncertainty) — cover highest-impact unresolved categories first
- Exclude: already answered, trivial preferences, or plan-level details

### Step 4 — Sequential Questioning Loop

Present ONE question at a time:

**For multiple-choice:**
1. State your **recommended option** with reasoning: `**Recommended:** Option [X] — <reasoning>`
2. Show options as a table
3. Add: "Reply with option letter, 'yes' to accept recommendation, or your own short answer."

**For short-answer:**
1. State your **suggested answer**: `**Suggested:** <answer> — <reasoning>`
2. Add: "Reply with your answer (≤5 words), or 'yes' to accept suggestion."

**After I answer:**
- If I say "yes"/"recommended"/"suggested" → use your recommendation
- Validate answer fits constraints; if ambiguous, ask for quick disambiguation
- Record answer and proceed to next question

**Stop when:**
- All critical ambiguities resolved
- I signal completion ("done", "good", "no more")
- 5 questions asked

### Step 5 — Integrate Answers (After Each)

After each accepted answer, immediately update the spec:

1. **Relevant section**: Update the section matching the category from the coverage map (use the "Template Section" column in the taxonomy)
2. **Remove contradictions**: Replace obsolete statements; leave no duplicates
3. **Save immediately** to minimize context loss

### Step 6 — Report Completion

After loop ends, report:
- Questions asked & answered count
- Path to updated spec
- Sections touched
- Coverage summary table (Resolved / Deferred / Clear / Outstanding per category)
- Suggested next action (`@audit` again, proceed to design/planning, etc.)

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No active feature | Run `@feature status` then `@feature switch <path>` |
| Spec file missing | Create via `@feature create` |
| User wants to skip | Warn that downstream rework risk increases, then proceed |
| Coverage already complete | Report "No critical ambiguities" and suggest next step |
