# Cross-Repo Pattern Search

**Task**: "Find all error handling patterns across our services"

```
1. discover_index()
   → Shows multiple service repos indexed

2. search(query="try except raise custom exception", 
          filters={"content_type": ["code"], "file_extension": [".py"]})
   → Returns error handling patterns from multiple repos

3. Compare patterns across results
```
