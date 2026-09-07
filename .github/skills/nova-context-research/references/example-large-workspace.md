# Large Workspace Navigation

**Task**: "Find where user permissions are checked" (in a large monorepo)

```
1. Built-in search returns too many results or times out

2. discover_index()
   → Confirms the monorepo is indexed

3. search(query="check permission user access", 
          filters={"scope": ["monorepo/main"], "file_extension": [".py"]})
   → Returns top relevant files: src/auth/permissions.py, src/api/middleware.py

4. Use built-in tools to read those specific files for current state
```
