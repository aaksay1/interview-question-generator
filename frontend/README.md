# Interview Question Generator - Frontend

A modern Next.js frontend application for generating interview questions from resumes and job descriptions.

## Features

- **PDF Resume Upload**: Drag-and-drop or click to upload PDF resumes (max 5MB)
- **Job Description Input**: Text area for entering job descriptions
- **AI-Powered Questions**: Generates tailored interview questions using AI
- **Category Grouping**: Questions organized by category (Technical, Behavioral, Role-Specific)
- **Collapsible Categories**: Expand/collapse categories for better organization
- **Copy to Clipboard**: Copy individual questions with one click
- **Export Options**: Download questions as JSON or CSV
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Error Handling**: Clear error messages for validation and API errors
- **Loading States**: Visual feedback during question generation

## Getting Started

### Prerequisites

- Node.js 16.x or higher
- npm or yarn package manager
- Backend API running on `http://localhost:8000` (see backend README)

### Installation

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Run the development server:**
   ```bash
   npm run dev
   ```

4. **Open your browser:**
   Navigate to [http://localhost:3000](http://localhost:3000)

### Build for Production

```bash
npm run build
npm start
```

## Usage

1. **Upload Resume**: Click "Choose File" and select a PDF resume (max 5MB)
2. **Enter Job Description**: Paste or type the job description (minimum 10 characters)
3. **Generate Questions**: Click "Generate Questions" button
4. **View Results**: Questions will be displayed grouped by category
5. **Interact**: 
   - Click category headers to expand/collapse
   - Hover over questions to see copy button
   - Use download buttons to export questions

## File Validation

- **File Type**: Only PDF files are accepted
- **File Size**: Maximum 5MB
- **Job Description**: Minimum 10 characters, maximum 10,000 characters

## Project Structure

```
frontend/
├── pages/
│   ├── _app.js          # Next.js app wrapper with global styles
│   └── index.js         # Main page component
├── styles/
│   └── globals.css      # Global Tailwind CSS styles
├── public/              # Static assets
├── package.json         # Dependencies and scripts
├── tailwind.config.js   # Tailwind CSS configuration
├── postcss.config.js    # PostCSS configuration
├── next.config.js       # Next.js configuration
└── README.md           # This file
```

## Features in Detail

### Category Colors
- **Technical**: Blue theme
- **Behavioral**: Green theme
- **Role-Specific**: Purple theme
- **Uncategorized**: Gray theme

### Export Formats

**JSON Export:**
```json
{
  "questions": [
    {
      "category": "Technical",
      "question": "..."
    }
  ]
}
```

**CSV Export:**
```csv
Category,Question
Technical,"..."
```

### Error Handling

The frontend handles various error scenarios:
- File size validation (before upload)
- File type validation
- Network errors (connection issues)
- API errors (server-side errors)
- Invalid responses

### Responsive Design

- **Mobile**: Single column layout, optimized touch targets
- **Tablet**: Two-column layout where appropriate
- **Desktop**: Full-width layout with optimal spacing

## API Integration

The frontend communicates with the FastAPI backend at `http://localhost:8000/generate-questions`.

**Request Format:**
- Method: POST
- Content-Type: multipart/form-data
- Fields:
  - `resume`: PDF file
  - `job_description`: Text string

**Response Format:**
```json
{
  "questions": [
    {
      "category": "Technical",
      "question": "..."
    }
  ]
}
```

## Customization

### Changing API Endpoint

Edit `pages/index.js` and update the fetch URL:
```javascript
const response = await fetch('http://localhost:8000/generate-questions', {
  // ...
})
```

### Styling

The app uses Tailwind CSS. Modify `tailwind.config.js` to customize the theme, or edit component classes directly in `pages/index.js`.

### Category Colors

Update the `categoryColors` object in `pages/index.js` to change category color schemes.

## Troubleshooting

### "Unable to connect to the server"
- Ensure the backend is running on `http://localhost:8000`
- Check that CORS is properly configured in the backend
- Verify the backend API is accessible

### File upload errors
- Ensure the file is a PDF
- Check file size is under 5MB
- Try a different PDF file

### Questions not displaying
- Check browser console for errors
- Verify the API response format matches expected structure
- Check network tab for API response

## Development

### Adding New Features

1. **New Components**: Create in `components/` directory
2. **New Pages**: Add to `pages/` directory
3. **Styling**: Use Tailwind CSS classes or extend `globals.css`

### Code Style

- Use functional components with hooks
- Follow React best practices
- Use Tailwind CSS for styling
- Keep components focused and modular

## License

This project is part of the Interview Question Generator application.
