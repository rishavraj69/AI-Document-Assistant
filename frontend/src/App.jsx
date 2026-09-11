import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import './App.css'

function App() {
  const [file, setFile] = useState(null)
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [sources, setSources] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0]
    setFile(selectedFile || null)

    if (selectedFile) {
      setError('')
    }
  }

  const handleSubmit = async (event) => {
    event.preventDefault()

    if (!file) {
      setError('Please select a PDF file.')
      return
    }

    if (!question.trim()) {
      setError('Please enter a question.')
      return
    }

    setLoading(true)
    setError('')
    setAnswer('')
    setSources([])

    const formData = new FormData()
    formData.append('file', file)
    formData.append('question', question)

    try {
      const response = await fetch('http://127.0.0.1:8000/api/query', {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to get a response from the backend.')
      }

      setAnswer(data.answer || '')
      setSources(data.sources || [])
    } catch (err) {
      setError(err.message || 'Something went wrong while contacting the backend.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-shell">
      <div className="app-card">
        <header className="page-header">
          <div>
            <p className="eyebrow">AI-powered document search</p>
            <h1>AI Document Assistant</h1>
          </div>
        </header>

        <form onSubmit={handleSubmit} className="query-form">
          <label className="field-label">
            <span className="label-text">PDF File</span>
            <div className="upload-box">
              <input
                type="file"
                accept="application/pdf"
                onChange={handleFileChange}
              />
            </div>
          </label>

          {file && (
            <div className="selected-file">
              <span className="selected-file-label">Selected PDF</span>
              <strong>{file.name}</strong>
            </div>
          )}

          <label className="field-label">
            <span className="label-text">Question</span>
            <textarea
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              rows="4"
              placeholder="Ask a question about the PDF"
            />
          </label>

          <button type="submit" disabled={loading} className="primary-button">
            {loading ? (
              <span className="button-content">
                <span className="spinner" aria-hidden="true" />
                Loading...
              </span>
            ) : (
              'Ask Question'
            )}
          </button>
        </form>

        {!loading && !answer && !error && sources.length === 0 && (
          <div className="empty-state">
            Upload a PDF and ask a question to get started.
          </div>
        )}

        {loading && (
          <div className="loading-state">
            Searching your document and generating an answer...
          </div>
        )}

        {error && <div className="error-box">{error}</div>}

        {answer && (
          <div className="result-box answer-box">
            <h2>Answer</h2>
            <div className="markdown-content">
              <ReactMarkdown>{answer}</ReactMarkdown>
            </div>
          </div>
        )}

        {sources.length > 0 && (
          <div className="result-box">
            <h2>Sources</h2>
            <ul className="sources-list">
              {sources.map((source, index) => (
                <li key={`${source.source_filename}-${source.page_number}-${index}`} className="source-item">
                  <div className="source-header">
                    <strong>{source.source_filename}</strong>
                    <span>Page {source.page_number}</span>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
