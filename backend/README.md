# Interview Question Generator - Backend

FastAPI backend service that generates tailored interview questions from resumes and job descriptions.

## Architecture: ML-Free Design

**No local ML models** - All intelligence handled by Groq LLM API:
- ✅ Lightweight keyword matching for chunk selection
- ✅ Groq LLM handles all reasoning and relevance
- ✅ Optimized for Render Free Tier (512MB RAM)
- ✅ Fast cold start (<2 seconds)
- ❌ No embeddings, no FAISS, no HuggingFace, no PyTorch

See [ARCHITECTURE.md](./ARCHITECTURE.md) for details.

## Features

- **PDF Resume Processing**: Extracts text from PDF resumes with robust error handling
- **Lightweight Chunk Selection**: Keyword-based matching (no ML models)
- **AI-Powered Question Generation**: Leverages Groq LLM to generate contextual interview questions
- **Input Validation**: Validates file size (2MB max), file type (PDF only), and text length limits
- **Error Handling**: Comprehensive error handling with clear error messages
- **Logging**: Detailed logging for debugging and monitoring
- **Memory Efficient**: Runs comfortably under 512MB RAM

## Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   
   Create a `.env` file in the `backend/` directory:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```
   
   You can get a Groq API key from [https://console.groq.com/](https://console.groq.com/)

5. **Run the server:**
   ```bash
   uvicorn main:app --reload
   ```
   
   The API will be available at `http://localhost:8000`
   
   API documentation (Swagger UI) will be available at `http://localhost:8000/docs`

## API Endpoints

### POST `/generate-questions`

Generates interview questions from a resume PDF and job description.

**Request:**
- `resume` (file): PDF file (max 2MB)
- `job_description` (form field): Text description of the job (10-10,000 characters)

**Response:**
```json
{
  "questions": [
    {
      "category": "Technical",
      "question": "Can you explain how you implemented..."
    },
    {
      "category": "Behavioral",
      "question": "Tell me about a time when..."
    }
  ]
}
```

**Error Responses:**
- `400`: Validation errors (invalid file type, file too large, empty job description)
- `413`: File size exceeds 5MB
- `500`: Server errors (PDF parsing failure, LLM errors, etc.)

## Project Structure

```
backend/
├── main.py                 # FastAPI application and endpoints
├── chains/
│   └── question_chain.py   # LLM chain for question generation
├── utils/
│   ├── validation.py       # Input validation utilities
│   ├── pdf_parser.py      # PDF text extraction
│   ├── chunker.py         # Text chunking logic
│   └── parsing.py         # JSON extraction from LLM responses
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables (not in git)
└── README.md             # This file
```

## Configuration

### File Size Limits
- Maximum resume file size: 2MB (optimized for memory efficiency)
- Maximum extracted text length: 15,000 characters

### Job Description Limits
- Minimum length: 10 characters
- Maximum length: 10,000 characters

### Chunking Strategy
Simple text-based chunking (no ML models):
- Short resumes (< 2000 chars): 500 char chunks
- Medium resumes (2000-10000 chars): 1000 char chunks
- Long resumes (> 10000 chars): 1200 char chunks
- Top 5 chunks selected using lightweight keyword matching

## Error Handling

The backend includes comprehensive error handling for:
- Invalid file types
- File size violations
- PDF parsing failures (blank pages, corrupted files)
- Empty or invalid job descriptions
- LLM API failures
- Vectorstore creation failures
- Network errors

All errors return appropriate HTTP status codes with descriptive error messages.

## Logging

The application logs:
- Request information (file names, job description length)
- Processing steps (PDF extraction, chunking, vectorstore creation)
- LLM responses (first 500 characters for debugging)
- Errors with full stack traces

Logs are output to stdout with timestamps and log levels.

## Development

### Running Tests

Test files are available in the backend directory:
- `test_pdf.py`: PDF parsing tests
- `test_chain.py`: LLM chain tests
- `test_embeddings.py`: Embedding tests
- `test_chunking.py`: Chunking tests

### Adding New Features

1. **New utilities**: Add to `utils/` directory
2. **New chains**: Add to `chains/` directory
3. **New endpoints**: Add to `main.py`

## Deployment

### Production Deployment (Render, Railway, etc.)

1. **Set Environment Variables:**
   - `GROQ_API_KEY`: Your Groq API key (required)

2. **Update CORS Settings:**
   
   In `main.py`, update the `allow_origins` list to include your frontend URL:
   ```python
   allow_origins=[
       "http://localhost:3000",  # Local development
       "https://your-frontend-domain.com",  # Your production frontend URL
   ],
   ```

3. **Start Command:**
   ```
   uvicorn backend.main:app --host 0.0.0.0 --port $PORT
   ```
   (Render sets `$PORT` automatically)

4. **Memory Usage:**
   - Total memory: ~130-220MB (well under 512MB limit)
   - No ML models loaded - fast cold start (<2 seconds)
   - Optimized for Render Free Tier

## Troubleshooting

### "GROQ_API_KEY environment variable is not set"
- Ensure you have a `.env` file in the `backend/` directory
- Verify the `.env` file contains `GROQ_API_KEY=your_key_here`
- Restart the server after creating/modifying `.env`

### "Failed to extract questions from LLM response"
- Check the logs for the raw LLM response
- The LLM may have returned a response in an unexpected format
- Try regenerating questions

### PDF parsing errors
- Ensure the PDF contains extractable text (not just images)
- Try a different PDF file
- Check logs for specific error messages

## License

This project is part of the Interview Question Generator application.
