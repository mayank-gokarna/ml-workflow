# Commit Workflow

Detailed steps for creating focused, conventional commits with JIRA attribution.

## Step 1 — Check Current Branch

<system-reminder>
If on `main` or `master`, warn me and ask for explicit confirmation before proceeding.
</system-reminder>

```bash
git branch --show-current
```

**If on protected branch (`main`/`master`):**
```
⚠️ You're on `main`/`master`. Committing directly to this branch is not recommended.
Do you want to:
1. Create a feature branch first (recommended)
2. Proceed anyway (requires confirmation)
```

## Step 2 — Get JIRA ID

<system-reminder>
JIRA ID is required. First check if provided in the original request. If found, confirm it. If not found, ask for it.
</system-reminder>

Ask: **"What's the JIRA ticket ID for these changes? (e.g., AI-123)"**

**Validation:** Pattern `[A-Z]+-[0-9]+`

## Step 3 — Review Uncommitted Changes

```bash
# Get overview of changes
git status

# See detailed diff
git diff
git diff --staged
```

**If no uncommitted changes:**
```
ℹ️ Nothing to commit. Working tree is clean.
```
Stop here and report to me.

**Analysis approach:**
1. Group changes by logical unit (feature, fix, refactor)
2. Identify dependencies between changes
3. Plan commit order (foundations first)

Report to me:
```
📋 Uncommitted changes:
• Modified: src/auth/handler.go (auth logic)
• Modified: src/auth/handler_test.go (tests)
• Added: src/auth/jwt.go (new JWT utilities)
• Modified: go.mod (new dependency)

💡 Suggested commits:
1. "chore(deps): [AI-123] add jwt-go dependency"
2. "feat(auth): [AI-123] add JWT token validation"
3. "test(auth): [AI-123] add JWT validation tests"
```

## Step 4 — Create Focused Commits

### Commit Message Format

```
<type>(<scope>): [<JIRA-ID>] <subject>

[optional body]

[optional footer]
```

<system-reminder>
Infer scope automatically from the files being changed:
- `src/auth/*` → `auth`
- `src/api/users/*` → `api` or `users`
- `docs/*` → `docs`
- Multiple areas → use the primary/most impacted area
- If unclear, omit scope: `feat: [AI-123] subject`
</system-reminder>

<good-example>
feat(auth): [AI-123] add JWT token validation
fix(api): [AI-456] handle null response in user endpoint
docs(readme): [NOVA-789] update installation instructions
refactor(user): [AI-101] extract validation logic to separate module
</good-example>

<bad-example>
fixed stuff                           # No JIRA, no type, not descriptive
AI-123: updates                       # Missing type, vague subject
feat: add feature                     # Missing JIRA ID
feat(auth) [AI-123] add jwt           # Missing colon after scope
</bad-example>

### Commit Types

| Type | Usage |
|------|-------|
| `feat` | New feature or capability (including skills, configs that add functionality) |
| `fix` | Bug fix |
| `docs` | Documentation only (README, comments, API docs — not new functionality) |
| `style` | Formatting, no logic change |
| `refactor` | Code restructuring, no behavior change |
| `test` | Adding or updating tests |
| `chore` | Build, tooling, dependencies |

<system-reminder>
Use `feat` when adding new capabilities, even if files are markdown (e.g., agent skills).
Use `docs` only for pure documentation updates that don't add new functionality.
</system-reminder>

### Creating Commits

```bash
# Stage specific files
git add <file1> <file2>

# Or stage by hunk for mixed changes
git add -p

# Commit with message
git commit -m "feat(auth): [AI-123] add JWT token validation"
```

**For multi-line commit messages:**
```bash
git commit -m "feat(auth): [AI-123] add JWT token validation" \
           -m "- Implement token parsing and validation" \
           -m "- Add expiration checking" \
           -m "- Support RS256 algorithm"
```

## Step 5 — Verify All Changes Committed

```bash
# Check nothing remains
git status

# Review commit history
git log --oneline -5
```

**If changes remain:**
```
⚠️ Some changes are still uncommitted:
• Modified: src/config.go

Should I:
1. Create another commit for these changes
2. Amend the previous commit
3. Leave them uncommitted
```

## Step 6 — Offer to Push

<system-reminder>
Always ask before pushing. Do not push without my confirmation.
</system-reminder>

Ask: **"All changes committed. Ready to push to origin?"**

```bash
git push origin $(git branch --show-current)
```

Report completion:
```
✅ Commits pushed successfully
📍 Branch: AI-123-feat/user-authentication
📝 Commits:
   • chore(deps): [AI-123] add jwt-go dependency
   • feat(auth): [AI-123] add JWT token validation
   • test(auth): [AI-123] add JWT validation tests
```

## Error Handling

| Error | Solution |
|-------|----------|
| Merge conflicts | Guide through resolution, then continue |
| Push rejected | Suggest `git pull --rebase` then retry |
| Pre-commit hook fails | Show error, suggest fixes |
| Large binary files | Warn about repo size, suggest LFS |