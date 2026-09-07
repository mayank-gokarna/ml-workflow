# Branch Workflow

Detailed steps for creating feature branches with proper naming conventions.

## Step 1 — Confirm Base Branch

<system-reminder>
Always propose a base branch based on context, but ask me to confirm. Never proceed without my confirmation.
</system-reminder>

Propose: **"I'll base this off `<detected-branch>`. Is that correct?"**

Common base branches:
- `develop` — standard feature work
- `main`/`master` — hotfixes
- Another feature branch — dependent work

```bash
# Fetch latest and verify base exists
git fetch origin
git branch -a | grep <base-branch>
```

## Step 2 — Get JIRA ID

<system-reminder>
JIRA ID is required. First check if provided in the original request. If found, confirm it. If not found, ask for it.
</system-reminder>

Ask: **"What's the JIRA ticket ID? (e.g., AI-123, NOVA-456)"**

**Validation:**
- Pattern: `[A-Z]+-[0-9]+` (e.g., `AI-123`, `NOVA-456`, `PLATFORM-789`)
- If invalid format, ask again with example

## Step 3 — Determine Branch Type

<system-reminder>
Infer type from context: if request contains "fix", "bug", "patch", "issue" → bugfix. Otherwise → feature. Ask only if truly ambiguous.
</system-reminder>

| Type | Prefix | When to use |
|------|--------|-------------|
| Feature | `feat` | New functionality, enhancements |
| Bugfix | `fix` | Bug fixes, corrections |

## Step 4 — Create Branch Name

<system-reminder>
Auto-convert feature names to kebab-case. "UserAuthentication" → "user-authentication". Do not ask for confirmation on case conversion.
</system-reminder>

<good-example>
AI-343-feat/chunk-versioning
NOVA-101-fix/opensearch-auth-bug
AI-789-feat/user-profile-settings
</good-example>

<bad-example>
feat/fix                    # Not descriptive
ai-123-feat/UserAuth        # Wrong case, should be kebab-case
my-feature                  # Missing JIRA ID
AI-123/feature              # Wrong format
</bad-example>

**Rules:**
- JIRA ID prefix: `<PROJECT>-<NUMBER>` (uppercase)
- Type: `-feat/` or `-fix/`
- Name: kebab-case, descriptive (3-5 words ideal)

## Step 5 — Create and Checkout Branch

```bash
# Ensure on base branch with latest
git checkout <base-branch>
git pull origin <base-branch>

# Create and switch to new branch
git checkout -b <JIRA-ID>-<type>/<feature-name>
```

Example:
```bash
git checkout develop
git pull origin develop
git checkout -b AI-123-feat/user-authentication
```

## Step 6 — Verify Branch

```bash
# Confirm current branch
git branch --show-current

# Verify clean state
git status
```

Report to me:
```
✅ Branch created: AI-123-feat/user-authentication
📍 Based on: develop
🔄 Ready for development
```

## Error Handling

| Error | Solution |
|-------|----------|
| Branch already exists | Ask: "Branch exists. Switch to it, or use a different name?" |
| Base branch not found | Suggest running `git fetch origin` and retry |
| Uncommitted changes | Ask: "You have uncommitted changes. Stash, commit, or discard?" |
| Invalid JIRA format | Show valid format and ask again |