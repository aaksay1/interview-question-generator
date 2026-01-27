import { useState } from 'react'
import Head from 'next/head'

export default function Home() {
  const [resume, setResume] = useState(null)
  const [jobDescription, setJobDescription] = useState('')
  const [questions, setQuestions] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [groupedQuestions, setGroupedQuestions] = useState({})
  const [expandedCategories, setExpandedCategories] = useState({})

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (file && file.type === 'application/pdf') {
      setResume(file)
      setError(null)
    } else {
      setError('Please upload a PDF file')
      setResume(null)
    }
  }

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

  const toggleCategory = (category) => {
    setExpandedCategories((prev) => ({
      ...prev,
      [category]: !prev[category],
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setQuestions([])
    setGroupedQuestions({})

    if (!resume) {
      setError('Please upload a resume PDF')
      return
    }

    if (!jobDescription.trim()) {
      setError('Please enter a job description')
      return
    }

    setLoading(true)

    try {
      const formData = new FormData()
      formData.append('resume', resume)
      formData.append('job_description', jobDescription)

      const response = await fetch('http://localhost:8000/generate-questions', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `Server error: ${response.status}`)
      }

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
      setError(err.message || 'Failed to generate questions. Please try again.')
      console.error('Error:', err)
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

      <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              Interview Question Generator
            </h1>
            <p className="text-lg text-gray-600">
              Upload a resume and job description to generate tailored interview questions
            </p>
          </div>

          {/* Form Card */}
          <div className="bg-white rounded-lg shadow-xl p-6 mb-8">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Resume Upload */}
              <div>
                <label htmlFor="resume" className="block text-sm font-medium text-gray-700 mb-2">
                  Resume (PDF)
                </label>
                <input
                  type="file"
                  id="resume"
                  accept=".pdf"
                  onChange={handleFileChange}
                  className="block w-full text-sm text-gray-500
                    file:mr-4 file:py-2 file:px-4
                    file:rounded-md file:border-0
                    file:text-sm file:font-semibold
                    file:bg-indigo-50 file:text-indigo-700
                    hover:file:bg-indigo-100
                    cursor-pointer"
                  disabled={loading}
                />
                {resume && (
                  <p className="mt-2 text-sm text-green-600">
                    ✓ {resume.name}
                  </p>
                )}
              </div>

              {/* Job Description */}
              <div>
                <label htmlFor="job_description" className="block text-sm font-medium text-gray-700 mb-2">
                  Job Description
                </label>
                <textarea
                  id="job_description"
                  rows={8}
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  placeholder="Paste the job description here..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-md shadow-sm 
                    focus:ring-indigo-500 focus:border-indigo-500 
                    resize-none text-sm"
                  disabled={loading}
                />
              </div>

              {/* Error Message */}
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md text-sm">
                  {error}
                </div>
              )}

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading || !resume || !jobDescription.trim()}
                className="w-full bg-indigo-600 text-white py-3 px-4 rounded-md 
                  font-medium hover:bg-indigo-700 focus:outline-none 
                  focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500
                  disabled:bg-gray-400 disabled:cursor-not-allowed
                  transition-colors duration-200"
              >
                {loading ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Generating Questions...
                  </span>
                ) : (
                  'Generate Questions'
                )}
              </button>
            </form>
          </div>

          {/* Questions Display */}
          {questions.length > 0 && (
            <div className="bg-white rounded-lg shadow-xl p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">
                Generated Questions ({questions.length})
              </h2>

              <div className="space-y-4">
                {Object.entries(groupedQuestions).map(([category, categoryQuestions]) => (
                  <div key={category} className="border border-gray-200 rounded-lg overflow-hidden">
                    {/* Category Header */}
                    <button
                      onClick={() => toggleCategory(category)}
                      className="w-full px-4 py-3 bg-indigo-50 hover:bg-indigo-100 
                        flex items-center justify-between text-left transition-colors"
                    >
                      <span className="font-semibold text-indigo-900">
                        {category} ({categoryQuestions.length})
                      </span>
                      <svg
                        className={`w-5 h-5 text-indigo-600 transform transition-transform ${
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
                          <div key={index} className="px-4 py-4 hover:bg-gray-50 transition-colors">
                            <p className="text-gray-800 leading-relaxed">
                              {q.question}
                            </p>
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
            <div className="bg-white rounded-lg shadow-xl p-12 text-center">
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
