# Workspace + Remote Search

**Task**: "Find similar implementations to what's in my current file"

```
1. Read current file to understand the pattern

2. Search locally for key function/class names in workspace

3. discover_index()
   → See which other repos are indexed beyond current workspace

4. search(query="[pattern from step 1]", 
          filters={"scope": ["other-repo/main"]})
   → Find implementations in repos NOT in the workspace

5. Compare approaches between local and remote
```
