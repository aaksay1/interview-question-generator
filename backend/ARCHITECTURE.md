# Architecture: ML-Free Design

## Overview

This backend uses a **ML-free architecture** optimized for Render Free Tier (512MB RAM).

**Key Decision**: All intelligence is handled by Groq LLM API. No local ML models are used.

## Why This Architecture?

1. **Memory Efficiency**: No embeddings models (~200-300MB saved)
2. **Fast Cold Start**: <2 seconds (no model loading)
3. **Cost Effective**: Groq API is fast and affordable
4. **Simpler Deployment**: Fewer dependencies, smaller Docker images
5. **Production Safe**: Runs comfortably under 512MB RAM

## What Was Removed

❌ **HuggingFaceEmbeddings** - Local embedding models
❌ **sentence-transformers** - ML model library
❌ **FAISS** - Vector database
❌ **PyTorch** - Deep learning framework
❌ **langchain-huggingface** - LangChain HuggingFace integration
❌ **langchain-community** - Only needed for FAISS
❌ **langchain-text-splitters** - Replaced with simple text splitting

## What We Use Instead

✅ **Simple Text Chunking** - Character-based splitting (no ML)
✅ **Keyword Matching** - Lightweight text matching for chunk selection
✅ **Groq LLM** - Handles all intelligence and reasoning remotely

## Processing Flow

1. **PDF Upload** → Extract text (PyPDF2)
2. **Text Chunking** → Simple character-based splitting
3. **Chunk Selection** → Keyword matching (lightweight, no ML)
4. **Groq LLM** → Receives job description + selected chunks
5. **JSON Parsing** → Extract questions from LLM response

## Memory Usage

- **Python Runtime**: ~100-150MB
- **PDF Processing**: ~20-50MB (temporary)
- **Text Processing**: ~10-20MB
- **Total**: ~130-220MB (well under 512MB limit)

## Dependencies

Only essential libraries:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `python-multipart` - File uploads
- `langchain-groq` - Groq LLM integration
- `langchain-core` - Core LangChain (messages)
- `PyPDF2` - PDF parsing
- `pdfplumber` - Alternative PDF parser (backup)

No ML libraries = smaller footprint, faster startup.
