# Interview Question Generator

A full-stack application that generates tailored interview questions from resumes and job descriptions using AI.

## Overview

This application uses semantic search and AI to generate contextual interview questions:
1. **Resume PDF** → Extract text → Chunk text
2. **Chunks** → FAISS vectorstore (semantic search)
3. **Job description + Relevant chunks** → LLM (Groq)
4. **LLM response** → Parse JSON → Return questions

## Quick Start

### Prerequisites

- **Python 3.8+** (for backend)
- **Node.js 16+** (for frontend)
- **Groq API Key** ([Get one here](https://console.groq.com/))

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your Groq API key
echo "GROQ_API_KEY=your_api_key_here" > .env

# Run the server
uvicorn backend.main:app --reload
```

Backend will run on `http://localhost:8000`
API docs available at `http://localhost:8000/docs`

### Frontend Setup

```bash
# Navigate to frontend directory (in a new terminal)
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

Frontend will run on `http://localhost:3000`

## Project Structure

```
interview-question-generator/
├── backend/                    # FastAPI backend
│   ├── chains/                 # LLM chains
│   │   └── question_chain.py  # Groq LLM integration
│   ├── utils/                 # Utility functions
│   │   ├── validation.py      # Input validation
│   │   ├── pdf_parser.py      # PDF text extraction
│   │   ├── chunker.py         # Text chunking
│   │   └── parsing.py         # JSON extraction
│   ├── main.py                # FastAPI app (main entry point)
│   ├── requirements.txt        # Python dependencies
│   └── README.md              # Backend documentation
├── frontend/                   # Next.js frontend
│   ├── pages/
│   │   └── index.js           # Main page component
│   ├── styles/
│   │   └── globals.css        # Tailwind CSS
│   ├── package.json           # Node.js dependencies
│   └── README.md              # Frontend documentation
└── README.md                  # This file
```

## 🔧 How It Works

### Processing Flow

1. **Resume Upload**: User uploads PDF resume (max 5MB)
2. **Text Extraction**: PDF text is extracted with error handling for blank/corrupted pages
3. **Intelligent Chunking**: Resume is chunked based on length:
   - Short resumes (< 2000 chars): 500 char chunks
   - Medium resumes (2000-10000 chars): 1000 char chunks
   - Long resumes (> 10000 chars): 1500 char chunks
4. **Vectorstore Creation**: FAISS vectorstore built in-memory from chunks
5. **Semantic Search**: Top 3 relevant chunks retrieved using job description
6. **LLM Generation**: Groq LLM generates questions from job description + resume chunks
7. **JSON Parsing**: Questions extracted from LLM response (handles markdown code blocks)
8. **Display**: Questions grouped by category and displayed in frontend

### Key Features

**Backend:**
- File size validation (5MB max)
- PDF type validation
- Robust PDF parsing (handles blank pages, corrupted files)
- Job description validation (10-10,000 characters)
- Intelligent text chunking (adapts to resume length)
- In-memory FAISS vectorstore (no persistent storage)
- Comprehensive error handling
- Detailed logging

**Frontend:**
- File size validation before upload
- Real-time character count
- Category-based question grouping
- Collapsible category sections
- Copy to clipboard (per question)
- Download as JSON or CSV
- Responsive mobile design
- Loading states and error handling

## 📖 Usage

1. **Start Backend**: `uvicorn backend.main:app --reload` (from project root)
2. **Start Frontend**: `npm run dev` (from `frontend/` directory)
3. **Open Browser**: Navigate to `http://localhost:3000`
4. **Upload Resume**: Select a PDF file (max 5MB)
5. **Enter Job Description**: Paste job description (min 10 characters)
6. **Generate Questions**: Click "Generate Questions"
7. **View Results**: Questions displayed grouped by category
8. **Export**: Download as JSON or CSV

## Configuration

### Backend

- **File Size Limit**: 5MB (configurable in `backend/utils/validation.py`)
- **Job Description**: 10-10,000 characters
- **Chunking**: Automatically adjusts based on resume length
- **Vectorstore**: In-memory FAISS (no persistent storage)

### Frontend

- **API Endpoint**: `http://localhost:8000/generate-questions` (configurable in `frontend/pages/index.js`)
- **File Size Limit**: 5MB (client-side validation)
- **Job Description Min**: 10 characters

## Troubleshooting

### Backend Issues

**"GROQ_API_KEY environment variable is not set"**
- Ensure `.env` file exists in `backend/` directory
- Verify the key is correctly formatted: `GROQ_API_KEY=your_key_here`
- Restart the server after modifying `.env`

**PDF parsing errors**
- Ensure PDF contains extractable text (not just images)
- Try a different PDF file
- Check logs for specific error messages

**Import errors**
- Ensure you're running from project root: `uvicorn backend.main:app --reload`
- Verify all dependencies are installed: `pip install -r requirements.txt`

### Frontend Issues

**"Unable to connect to the server"**
- Ensure backend is running on `http://localhost:8000`
- Check CORS configuration in backend
- Verify network connectivity

**File upload errors**
- Check file is a PDF
- Verify file size is under 5MB
- Try a different PDF file

## Documentation

- **Backend Documentation**: See `backend/README.md`
- **Frontend Documentation**: See `frontend/README.md`
- **API Documentation**: Available at `http://localhost:8000/docs` when backend is running

## Testing

Test files are available in the `backend/` directory:
- `test_pdf.py`: PDF parsing tests
- `test_chain.py`: LLM chain tests
- `test_embeddings.py`: Embedding tests
- `test_chunking.py`: Chunking tests

Run tests:
```bash
cd backend
python test_pdf.py
python test_chain.py
```

## License

This project is open source and available for educational and commercial use.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

**Built with:**
- FastAPI (Backend)
- Next.js (Frontend)
- TailwindCSS (Styling)
- Groq LLM (AI)
- FAISS (Vector Search)
- LangChain (LLM Framework)
