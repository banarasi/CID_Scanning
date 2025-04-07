import React, { useState } from 'react';
import './App.css';
import config from './config';

// Helper function to format redaction stats
const formatRedactionStats = (stats) => {
  if (!stats) return null;

  // Filter out zero counts
  const nonZeroStats = Object.entries(stats)
    .filter(([_, count]) => count > 0)
    .sort((a, b) => b[1] - a[1]); // Sort by count (descending)

  if (nonZeroStats.length === 0) return 'No sensitive information detected';

  return nonZeroStats.map(([type, count]) => {
    // Format the type name for display
    const formattedType = type
      .replace(/_/g, ' ')
      .replace(/\b\w/g, l => l.toUpperCase());

    return `${formattedType}: ${count}`;
  }).join(', ');
};

function App() {
  const [file, setFile] = useState(null);
  const [redactedText, setRedactedText] = useState(null);
  const [redactionStats, setRedactionStats] = useState(null);
  const [totalRedactions, setTotalRedactions] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
    setError(null);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!file) {
      setError('Please select a PDF file');
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${config.apiUrl}/api/redact-pdf`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (data.error) {
        setError(data.error);
      } else {
        setRedactedText(data.redacted_text);
        setRedactionStats(data.redaction_stats);
        setTotalRedactions(data.total_redactions);
      }
    } catch (err) {
      setError('Failed to process the PDF');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>PDF Redaction Tool</h1>
      </header>

      <main>
        <form onSubmit={handleSubmit}>
          <div className="file-input">
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
            />
          </div>
          <button type="submit" disabled={!file || loading}>
            {loading ? 'Processing...' : 'Redact PDF'}
          </button>
        </form>

        {error && <div className="error">{error}</div>}

        {redactedText && (
          <div className="results">
            {totalRedactions && (
              <div className="redaction-summary">
                <h2>Redaction Summary:</h2>
                <p className="redaction-stats">
                  {formatRedactionStats(totalRedactions) || 'No sensitive information detected'}
                </p>
                <p className="redaction-info">
                  The system has scanned for and redacted: personal names, email addresses, phone numbers,
                  social security numbers, credit card numbers, dates, addresses, company names, financial information,
                  IDs (passports, driver's licenses), and network information (IP addresses).
                </p>
              </div>
            )}

            <h2>Redacted Text:</h2>
            {redactedText.map((page, index) => (
              <div key={index} className="page">
                <h3>Page {index + 1}</h3>
                {redactionStats && redactionStats[index] && (
                  <div className="page-stats">
                    <p><strong>Page Redactions:</strong> {formatRedactionStats(redactionStats[index])}</p>
                  </div>
                )}
                <pre>{page}</pre>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;