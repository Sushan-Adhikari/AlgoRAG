import React, { useState } from 'react';
import './App.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [question, setQuestion] = useState('');
  const [queryType, setQueryType] = useState('general');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [health, setHealth] = useState(null);

  // Fetch health status on mount
  React.useEffect(() => {
    fetch(`${API_URL}/api/health`)
      .then(res => res.json())
      .then(data => setHealth(data))
      .catch(err => console.error('Health check failed:', err));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/api/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question,
          query_type: queryType === 'auto' ? null : queryType,
          top_k: 5,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const renderLatex = (text) => {
    // Simple LaTeX rendering (inline $ and display $$)
    // For production, use react-katex or MathJax
    return text
      .split(/(\$\$[^$]+\$\$|\$[^$]+\$)/g)
      .map((part, i) => {
        if (part.startsWith('$$') && part.endsWith('$$')) {
          return <div key={i} className="latex-display">{part.slice(2, -2)}</div>;
        } else if (part.startsWith('$') && part.endsWith('$')) {
          return <span key={i} className="latex-inline">{part.slice(1, -1)}</span>;
        }
        return <span key={i}>{part}</span>;
      });
  };

  return (
    <div className="App">
      {/* Header */}
      <header className="header">
        <h1>AlgoRAG</h1>
        <p>Retrieval-Augmented Generation for Algorithm Analysis & Complexity Theory</p>
        {health && (
          <div className="health-status">
            <span className="status-indicator"></span>
            {health.embedding_backend} • {health.documents_indexed} docs indexed
          </div>
        )}
      </header>

      {/* Main Content */}
      <div className="container">
        {/* Query Input */}
        <div className="query-section">
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="question">Your Question:</label>
              <textarea
                id="question"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="E.g., Prove that QuickSort has O(n log n) average case complexity..."
                rows={4}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="queryType">Query Type:</label>
              <select
                id="queryType"
                value={queryType}
                onChange={(e) => setQueryType(e.target.value)}
              >
                <option value="auto">Auto-detect</option>
                <option value="proof">Proof</option>
                <option value="complexity_analysis">Complexity Analysis</option>
                <option value="algorithm">Algorithm Explanation</option>
                <option value="general">General Question</option>
              </select>
            </div>

            <button type="submit" disabled={loading || !question.trim()}>
              {loading ? 'Processing...' : 'Ask AlgoRAG'}
            </button>
          </form>
        </div>

        {/* Results */}
        {loading && (
          <div className="loading">
            <div className="spinner"></div>
            <p>Retrieving knowledge and generating answer...</p>
          </div>
        )}

        {error && (
          <div className="error">
            <h3>Error</h3>
            <p>{error}</p>
          </div>
        )}

        {result && (
          <div className="results">
            {/* Answer */}
            <div className="answer-section">
              <h2>Answer</h2>
              <div className="answer-content">
                {renderLatex(result.answer)}
              </div>
              <div className="answer-metadata">
                Query Type: <strong>{result.query_type}</strong> •
                Sources Used: <strong>{result.num_sources}</strong>
              </div>
            </div>

            {/* Evidence Sources */}
            <div className="sources-section">
              <h2>Evidence Sources</h2>
              {result.sources.map((source, idx) => (
                <div key={idx} className="source-card">
                  <div className="source-header">
                    <span className="source-number">Source {idx + 1}</span>
                    <div className="source-scores">
                      <span className="score similarity">
                        Similarity: {(source.similarity_score * 100).toFixed(1)}%
                      </span>
                      <span className="score pedagogical">
                        Pedagogical: {(source.pedagogical_score * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                  <div className="source-metadata">
                    {source.metadata.topic && (
                      <span className="tag">{source.metadata.topic.replace('_', ' ')}</span>
                    )}
                    {source.metadata.difficulty_level && (
                      <span className="tag level">
                        Level: {source.metadata.difficulty_level}
                      </span>
                    )}
                    {source.metadata.source_textbook && (
                      <span className="tag">{source.metadata.source_textbook}</span>
                    )}
                  </div>
                  <div className="source-content">
                    {source.content}
                  </div>
                </div>
              ))}
            </div>

            {/* Visualizations */}
            <div className="viz-section">
              <h2>📊 Analysis</h2>
              <div className="viz-grid">
                {/* Confidence Bar */}
                <div className="viz-card">
                  <h3>Confidence Score</h3>
                  <div className="confidence-bar">
                    <div
                      className="confidence-fill"
                      style={{
                        width: `${(result.sources[0]?.similarity_score || 0) * 100}%`
                      }}
                    ></div>
                  </div>
                  <p>{((result.sources[0]?.similarity_score || 0) * 100).toFixed(1)}%</p>
                </div>

                {/* Source Count */}
                <div className="viz-card">
                  <h3>Sources Retrieved</h3>
                  <div className="big-number">{result.num_sources}</div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="footer">
        <p>
          AlgoRAG - Educational RAG system for theoretical computer science
          <br />
          <a href="https://github.com/yourusername/algorag" target="_blank" rel="noopener noreferrer">
            GitHub
          </a>
        </p>
      </footer>
    </div>
  );
}

export default App;
