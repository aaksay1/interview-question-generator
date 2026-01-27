# Interview Question Generator - Frontend

A Next.js frontend application for generating interview questions from resumes and job descriptions.

## Getting Started

### Installation

```bash
cd frontend
npm install
```

### Development

Run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

### Build

Build the production version:

```bash
npm run build
npm start
```

## Features

- Upload PDF resumes
- Enter job descriptions
- Generate tailored interview questions
- View questions grouped by category
- Collapsible category sections
- Loading states and error handling

## API Integration

The frontend connects to the FastAPI backend running on `http://localhost:8000`.

Make sure the backend is running before using the frontend.
