# Finding an Implementation

**Task**: "How is authentication implemented?"

```
1. discover_index()  
   → Shows scopes: ["auth-service/main", "api-gateway/main", ...]

2. [CHECKPOINT] Multiple repos have auth code. Ask user:
   "I see auth-service and api-gateway both indexed. 
    Which should I search, or both?"
   → User says: "Start with auth-service"

3. search(query="authentication middleware verify token", 
          filters={"scope": ["auth-service/main"], "content_type": ["code"]})
   → Returns chunk from src/auth/middleware.py (Chunk 3/8)

4. get_chunks(scope="auth-service/main", 
              identifier="src/auth/middleware.py",
              chunk_orders=[0, 1, 2, 3, 4])
   → Returns full context of the authentication implementation
```
