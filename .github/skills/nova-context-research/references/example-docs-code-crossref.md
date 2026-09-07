# Documentation + Code Cross-Reference

**Task**: "Understand the data ingestion pipeline"

```
1. discover_index()
   → Confirms both "document" and "code" content_types are indexed

2. search(query="data ingestion pipeline", 
          filters={"content_type": ["document"]})
   → Returns architecture docs explaining the design

3. search(query="ingest process transform", 
          filters={"content_type": ["code"]})
   → Returns implementation files

4. Cross-reference to understand intent vs. implementation
```
