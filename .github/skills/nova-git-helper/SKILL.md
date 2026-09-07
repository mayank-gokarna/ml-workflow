---
name: nova-git-helper
description: Use when I invoke @branch or @commit commands, or when you need to create a feature branch, make focused commits, or push changes following team conventions.
---

<required>
*CRITICAL* Add the following steps to your Todo list using `todo` tool:

1. **Confirm repository**: Check if cwd contains `.git`. If not, or if workspace has multiple repos, ask which one to work in. Change to that directory.
2. Identify command type: **branch** (create feature branch) or **commit** (stage & commit changes).
3. Load the matching workflow reference:
   - For **branch**: Read [branch-workflow.md](references/branch-workflow.md)
   - For **commit**: Read [commit-workflow.md](references/commit-workflow.md)
4. Add each step from the workflow file (Step 1, Step 2, etc.) to your Todo list.
5. Execute steps sequentially, marking each complete before proceeding.
</required>

# Nova Git Helper

Standardize git workflows for branch creation and focused commits with JIRA integration.

## When to Use This Skill

- I invoke `@branch` or need to create a feature branch
- I invoke `@commit` or need to commit/push changes
- I need help following team git conventions

## Quick Reference - Branch Workflow

⚠️ **MUST READ:** [branch-workflow.md](references/branch-workflow.md)

**Naming convention:** `<JIRA-ID>-<type>/<feature-name>`
| Type | Example |
|------|---------|
| Feature | `AI-343-feat/chunk-versioning` |
| Bugfix | `NOVA-101-fix/opensearch-auth-bug` |

```bash
# Create feature branch
git checkout -b AI-123-feat/user-authentication

# Verify branch
git branch --show-current
```

## Quick Reference - Commit Workflow

⚠️ **MUST READ:** [commit-workflow.md](references/commit-workflow.md)

**Format:** `<type>(<scope>): [<JIRA-ID>] <subject>`

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

```bash
# Check status
git status

# Stage and commit
git add <files>
git commit -m "feat(auth): [AI-123] add JWT validation"

# Push
git push origin $(git branch --show-current)
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No JIRA ID provided | Ask me for the JIRA ticket ID before proceeding |
| On protected branch | Warn me and confirm before any commits |
| Uncommitted changes remain | Show remaining changes and ask how to proceed |
| Branch already exists | Ask if I want to switch or create with different name |