# Memory Optimization for Render (512MB Limit)

## Current Optimizations

1. **Lazy Loading**: Embeddings model loads only on first request
2. **Memory-Efficient Embeddings**:
   - Model: `paraphrase-MiniLM-L3-v2` (~80MB, smaller than L6-v2's ~130MB)
   - CPU device (no GPU memory)
   - Batch size: 8 (reduced from default)
   - Tokenizer parallelism disabled
3. **Chunk Limiting**: Maximum 20 chunks per resume
4. **Smaller Chunks**: Chunk size capped at 800 characters
5. **Immediate Cleanup**: Vectorstore deleted after use
6. **Garbage Collection**: Explicit GC calls after processing

## Memory Usage Breakdown

- **Embeddings Model**: ~80-100MB (paraphrase-MiniLM-L3-v2, loaded once, cached)
- **FAISS Vectorstore**: ~50-100MB (per request, cleaned up)
- **PDF Processing**: ~20-50MB (temporary)
- **Python Runtime**: ~100-150MB
- **Total**: ~250-400MB (should fit within 512MB limit)

## If Still Exceeding Memory

### Option 1: Upgrade Render Plan
- Render Starter: $7/month, 512MB RAM
- Render Standard: $25/month, 2GB RAM (recommended)

### Option 2: Further Optimizations
1. Reduce max chunks to 15 or 10
2. Use even smaller chunk sizes (500 chars max)
3. Process in batches and clear between batches
4. Consider using a cloud embedding service instead

### Option 3: Alternative Deployment
- Railway.app: 512MB free tier, better memory management
- Fly.io: 256MB free tier, can scale
- AWS/GCP: More control over resources

## Monitoring

Check Render logs for memory usage:
- Look for "used over 512MB" errors
- Monitor memory spikes during embedding generation
- Watch for memory leaks (gradual increase over time)
