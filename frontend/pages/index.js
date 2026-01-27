/**
 * Interview Question Generator - Main Page
 * 
 * This page provides a form to:
 * 1. Upload a PDF resume (max 5MB)
 * 2. Enter a job description (min 10 characters)
 * 3. Submit to backend API to generate questions
 * 4. Display questions grouped by category
 * 5. Export questions as JSON or CSV
 * 
 * Run locally: npm run dev (from frontend/ directory)
 */
import { useState } from 'react'
import Head from 'next/head'

// Constants
const MAX_FILE_SIZE = 5 * 1024 * 1024 // 5MB in bytes
const MIN_JOB_DESCRIPTION_LENGTH = 10

// API URL: Use environment variable if set, otherwise default to production backend
// For local development, set NEXT_PUBLIC_API_URL=http://localhost:8000 in .env.local
// The env var should be the base URL (without /generate-questions)
const getApiUrl = () => {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'https://interview-question-generator-lqa9.onrender.com';
  // If the URL already ends with /generate-questions, use it as-is
  // Otherwise, append /generate-questions
  if (baseUrl.endsWith('/generate-questions')) {
    return baseUrl;
  }
  // Remove trailing slash if present, then add /generate-questions
  return baseUrl.replace(/\/$/, '') + '/generate-questions';
};

const API_URL = getApiUrl();

export default function Home() {
  // State management
  const [resume, setResume] = useState(null)
  const [jobDescription, setJobDescription] = useState('')
  const [questions, setQuestions] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [groupedQuestions, setGroupedQuestions] = useState({})
  const [expandedCategories, setExpandedCategories] = useState({})
  const [fileError, setFileError] = useState(null)

  // Category color mapping for visual distinction
  const categoryColors = {
    'Technical': 'bg-blue-50 border-blue-200 text-blue-900',
    'Behavioral': 'bg-green-50 border-green-200 text-green-900',
    'Role-Specific': 'bg-purple-50 border-purple-200 text-purple-900',
    'Uncategorized': 'bg-gray-50 border-gray-200 text-gray-900',
  }

  const getCategoryColor = (category) => {
    return categoryColors[category] || categoryColors['Uncategorized']
  }

  /**
   * Handle file selection and validation
   */
  const handleFileChange = (e) => {
    const file = e.target.files[0]
    setFileError(null)
    setError(null)

    if (!file) {
      setResume(null)
      return
    }

    // Validate file type
    if (file.type !== 'application/pdf') {
      setFileError('Please upload a PDF file')
      setResume(null)
      return
    }

    // Validate file size
    if (file.size > MAX_FILE_SIZE) {
      const fileSizeMB = (file.size / (1024 * 1024)).toFixed(2)
      setFileError(`File size (${fileSizeMB}MB) exceeds the maximum allowed size of 5MB`)
      setResume(null)
      return
    }

    setResume(file)
  }

  /**
   * Group questions by category for display
   */
  const groupQuestionsByCategory = (questionsList) => {
    const grouped = {}
    questionsList.forEach((q) => {
      const category = q.category || 'Uncategorized'
      if (!grouped[category]) {
        grouped[category] = []
      }
      grouped[category].push(q)
    })
    return grouped
  }

  /**
   * Toggle category expansion/collapse
   */
  const toggleCategory = (category) => {
    setExpandedCategories((prev) => ({
      ...prev,
      [category]: !prev[category],
    }))
  }

  /**
   * Copy question text to clipboard
   */
  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text)
      // Could add toast notification here
    } catch (err) {
      console.error('Failed to copy text:', err)
    }
  }

  /**
   * Download questions as JSON or CSV
   */
  const downloadQuestions = (format) => {
    if (!questions || questions.length === 0) return

    let content, mimeType, filename

    if (format === 'json') {
      content = JSON.stringify({ questions }, null, 2)
      mimeType = 'application/json'
      filename = 'interview-questions.json'
    } else if (format === 'csv') {
      // Convert to CSV format
      const headers = ['Category', 'Question']
      const rows = questions.map(q => [
        `"${q.category || 'Uncategorized'}"`,
        `"${q.question.replace(/"/g, '""')}"` // Escape quotes in CSV
      ])
      content = [headers.join(','), ...rows.map(row => row.join(','))].join('\n')
      mimeType = 'text/csv'
      filename = 'interview-questions.csv'
    }

    // Create download link
    const blob = new Blob([content], { type: mimeType })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  /**
   * Wake up Render service if it's sleeping (free tier)
   * Makes a quick GET request to the health endpoint
   */
  const wakeUpBackend = async () => {
    try {
      const baseUrl = API_URL.replace('/generate-questions', '')
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 10000) // 10 second timeout
      
      await fetch(baseUrl, { 
        method: 'GET',
        signal: controller.signal
      })
      
      clearTimeout(timeoutId)
    } catch (err) {
      // Ignore wake-up errors, just proceed with main request
      console.log('Wake-up request completed (backend may be waking up)')
    }
  }

  /**
   * Handle form submission
   * Sends resume and job description to backend API
   */
  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setQuestions([])
    setGroupedQuestions({})

    // Validate resume
    if (!resume) {
      setError('Please upload a resume PDF')
      return
    }

    // Validate job description
    if (!jobDescription.trim()) {
      setError('Please enter a job description')
      return
    }

    if (jobDescription.trim().length < MIN_JOB_DESCRIPTION_LENGTH) {
      setError(`Job description must be at least ${MIN_JOB_DESCRIPTION_LENGTH} characters long`)
      return
    }

    setLoading(true)

    try {
      // Wake up Render service if it's sleeping (free tier)
      // This helps reduce timeout errors on first request
      await wakeUpBackend()
      
      // Prepare form data
      const formData = new FormData()
      formData.append('resume', resume)
      formData.append('job_description', jobDescription)

      // Send request to backend with timeout
      // Note: Render free tier services may sleep - first request might take longer
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 60000) // 60 second timeout
      
      const response = await fetch(API_URL, {
        method: 'POST',
        body: formData,
        signal: controller.signal,
      })
      
      clearTimeout(timeoutId)

      // Handle errors
      if (!response.ok) {
        let errorMessage = `Server error: ${response.status}`
        try {
          const errorData = await response.json()
          errorMessage = errorData.detail || errorMessage
        } catch {
          // If response is not JSON, use status text
          errorMessage = response.statusText || errorMessage
        }
        throw new Error(errorMessage)
      }

      // Parse response
      const data = await response.json()
      
      if (data.questions && Array.isArray(data.questions)) {
        setQuestions(data.questions)
        const grouped = groupQuestionsByCategory(data.questions)
        setGroupedQuestions(grouped)
        // Expand all categories by default
        const expanded = {}
        Object.keys(grouped).forEach((cat) => {
          expanded[cat] = true
        })
        setExpandedCategories(expanded)
      } else {
        throw new Error('Invalid response format from server')
      }
    } catch (err) {
      // Handle different types of errors
      if (err.name === 'AbortError') {
        setError('Request timed out. The backend might be waking up (Render free tier). Please try again in a moment.')
      } else if (err.name === 'TypeError' && (err.message.includes('fetch') || err.message.includes('Failed to fetch'))) {
        setError(`Unable to connect to the server. The backend might be sleeping (Render free tier takes ~30s to wake up). Please wait a moment and try again.`)
      } else if (err.message) {
        setError(err.message)
      } else {
        setError('Failed to generate questions. Please try again.')
      }
      console.error('Error:', err)
      console.error('Error name:', err.name)
      console.error('Error message:', err.message)
      console.error('API URL used:', API_URL)
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <Head>
        <title>Interview Question Generator</title>
        <meta name="description" content="Generate interview questions from resume and job description" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 py-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-2">
              Interview Question Generator
            </h1>
            <p className="text-base sm:text-lg text-gray-600">
              Upload a resume and job description to generate tailored interview questions
            </p>
          </div>

          {/* Form Card */}
          <div className="bg-white rounded-lg shadow-xl p-4 sm:p-6 mb-6">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Resume Upload */}
              <div>
                <label htmlFor="resume" className="block text-sm font-medium text-gray-700 mb-2">
                  Resume (PDF) <span className="text-gray-500 text-xs">(Max 5MB)</span>
                </label>
                <input
                  type="file"
                  id="resume"
                  accept=".pdf,application/pdf"
                  onChange={handleFileChange}
                  className="block w-full text-sm text-gray-500
                    file:mr-4 file:py-2 file:px-4
                    file:rounded-md file:border-0
                    file:text-sm file:font-semibold
                    file:bg-indigo-50 file:text-indigo-700
                    hover:file:bg-indigo-100
                    cursor-pointer
                    disabled:opacity-50 disabled:cursor-not-allowed"
                  disabled={loading}
                />
                {resume && !fileError && (
                  <p className="mt-2 text-sm text-green-600 flex items-center">
                    <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    {resume.name} ({(resume.size / (1024 * 1024)).toFixed(2)}MB)
                  </p>
                )}
                {fileError && (
                  <p className="mt-2 text-sm text-red-600">{fileError}</p>
                )}
              </div>

              {/* Job Description */}
              <div>
                <label htmlFor="job_description" className="block text-sm font-medium text-gray-700 mb-2">
                  Job Description <span className="text-gray-500 text-xs">(Min {MIN_JOB_DESCRIPTION_LENGTH} characters)</span>
                </label>
                <textarea
                  id="job_description"
                  rows={8}
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  placeholder="Paste the job description here..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-md shadow-sm 
                    focus:ring-indigo-500 focus:border-indigo-500 
                    resize-none text-sm
                    disabled:opacity-50 disabled:cursor-not-allowed"
                  disabled={loading}
                />
                <p className="mt-1 text-xs text-gray-500">
                  {jobDescription.length} characters
                </p>
              </div>

              {/* Error Message */}
              {error && (
                <div className="bg-red-50 border-l-4 border-red-400 text-red-700 px-4 py-3 rounded-md text-sm">
                  <div className="flex items-center">
                    <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                    {error}
                  </div>
                </div>
              )}

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading || !resume || !jobDescription.trim() || jobDescription.trim().length < MIN_JOB_DESCRIPTION_LENGTH}
                className="w-full bg-indigo-600 text-white py-3 px-4 rounded-md 
                  font-medium hover:bg-indigo-700 focus:outline-none 
                  focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500
                  disabled:bg-gray-400 disabled:cursor-not-allowed
                  transition-colors duration-200
                  flex items-center justify-center"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Generating Questions...
                  </>
                ) : (
                  'Generate Questions'
                )}
              </button>
            </form>
          </div>

          {/* Questions Display */}
          {questions.length > 0 && (
            <div className="bg-white rounded-lg shadow-xl p-4 sm:p-6">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-2 sm:mb-0">
                  Generated Questions ({questions.length})
                </h2>
                <div className="flex flex-wrap gap-2">
                  <button
                    onClick={() => downloadQuestions('json')}
                    className="px-3 py-1.5 text-sm bg-indigo-100 text-indigo-700 rounded-md hover:bg-indigo-200 transition-colors"
                  >
                    Download JSON
                  </button>
                  <button
                    onClick={() => downloadQuestions('csv')}
                    className="px-3 py-1.5 text-sm bg-indigo-100 text-indigo-700 rounded-md hover:bg-indigo-200 transition-colors"
                  >
                    Download CSV
                  </button>
                </div>
              </div>

              <div className="space-y-4">
                {Object.entries(groupedQuestions).map(([category, categoryQuestions]) => (
                  <div key={category} className="border rounded-lg overflow-hidden shadow-sm">
                    {/* Category Header */}
                    <button
                      onClick={() => toggleCategory(category)}
                      className={`w-full px-4 py-3 ${getCategoryColor(category)} 
                        flex items-center justify-between text-left transition-colors
                        hover:opacity-90`}
                    >
                      <span className="font-semibold flex items-center">
                        <span className="inline-block w-2 h-2 rounded-full bg-current mr-2"></span>
                        {category} <span className="ml-2 text-xs opacity-75">({categoryQuestions.length})</span>
                      </span>
                      <svg
                        className={`w-5 h-5 transform transition-transform ${
                          expandedCategories[category] ? 'rotate-180' : ''
                        }`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>

                    {/* Questions List */}
                    {expandedCategories[category] && (
                      <div className="divide-y divide-gray-200">
                        {categoryQuestions.map((q, index) => (
                          <div key={index} className="px-4 py-4 hover:bg-gray-50 transition-colors group">
                            <div className="flex items-start justify-between">
                              <p className="text-gray-800 leading-relaxed flex-1 pr-4">
                                {q.question}
                              </p>
                              <button
                                onClick={() => copyToClipboard(q.question)}
                                className="opacity-0 group-hover:opacity-100 transition-opacity p-1.5 text-gray-400 hover:text-indigo-600"
                                title="Copy to clipboard"
                              >
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                                </svg>
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Empty State */}
          {!loading && questions.length === 0 && !error && (
            <div className="bg-white rounded-lg shadow-xl p-8 sm:p-12 text-center">
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                />
              </svg>
              <h3 className="mt-4 text-lg font-medium text-gray-900">
                No questions yet
              </h3>
              <p className="mt-2 text-sm text-gray-500">
                Upload a resume and job description, then click "Generate Questions" to get started.
              </p>
            </div>
          )}
        </div>
      </main>
    </>
  )
}
