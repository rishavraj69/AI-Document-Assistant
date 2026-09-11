import { useState } from 'react'
import './App.css'

function App() {
  const [file, setFile] = useState(null)
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [sources, setSources] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

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
      <h1>AI Document Assistant</h1>

      <form onSubmit={handleSubmit} className="query-form">
        <label className="field-label">
          PDF File
          <input
            type="file"
            accept="application/pdf"
            onChange={(event) => setFile(event.target.files[0])}
          />
        </label>

        <label className="field-label">
          Question
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            rows="4"
            placeholder="Ask a question about the PDF"
          />
        </label>

        <button type="submit" disabled={loading}>
          {loading ? 'Loading...' : 'Ask Question'}
        </button>
      </form>

      {error && <div className="error-box">{error}</div>}

      {answer && (
        <div className="result-box">
          <h2>Answer</h2>
          <p>{answer}</p>
        </div>
      )}

      {sources.length > 0 && (
        <div className="result-box">
          <h2>Sources</h2>
          <ul>
            {sources.map((source, index) => (
              <li key={`${source.source_filename}-${source.page_number}-${index}`}>
                <strong>{source.source_filename}</strong> — Page {source.page_number}
                <div>Score: {source.score}</div>
                <div>{source.preview}</div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default App
