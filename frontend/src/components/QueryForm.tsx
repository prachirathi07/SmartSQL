import React, { useState, useEffect } from 'react';
import {
  TextField,
  Button,
  Paper,
  Box,
  CircularProgress,
  Fade,
  IconButton,
  Tooltip,
  Typography,
} from '@mui/material';
import { Send as SendIcon, Delete as DeleteIcon, Download as DownloadIcon, History as HistoryIcon } from '@mui/icons-material';
import { QueryResponse } from '../types';

interface QueryFormProps {
  onSubmit: (query: string) => Promise<void>;
  loading: boolean;
  response?: QueryResponse;
  initialQuery?: string;
  setQuery?: (q: string) => void;
  error?: string | null;
}

// Helper to check if value is a 2D array (list of lists/tuples)
function is2DArray(val: any): val is any[][] {
  return (
    Array.isArray(val) &&
    val.length > 0 &&
    Array.isArray(val[0]) &&
    (Array.isArray(val[0]) || typeof val[0] === 'object' || typeof val[0] === 'string' || typeof val[0] === 'number')
  );
}

function parseResult(result: any) {
  // Try to parse stringified Python/JSON tuples/lists
  if (typeof result === 'string') {
    // Try JSON first
    try {
      return JSON.parse(result);
    } catch {
      // Try to parse Python-style list of tuples: [(1, 'a'), (2, 'b')]
      const tupleRegex = /\(([^)]+)\)/g;
      const matches = Array.from(result.matchAll(tupleRegex));
      if (matches.length > 0) {
        return matches.map(m =>
          m[1].split(',').map((s: string) => s.trim().replace(/^'|'$/g, ''))
        );
      }
    }
  }
  return result;
}

function ResultTable({ data }: { data: any[][] }) {
  // Try to infer headers from the first row if possible
  const headers = Array.isArray(data[0])
    ? data[0].map((_, i) => `Col ${i + 1}`)
    : [];
  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: 8, background: '#fff' }}>
        <thead>
          <tr>
            {headers.map((h, i) => (
              <th key={i} style={{ border: '1px solid #e0e0e0', padding: 8, background: '#f5f6fa', color: '#1976d2', fontWeight: 600 }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr key={i}>
              {row.map((cell: any, j: number) => (
                <td
                  key={j}
                  style={{
                    border: '1px solid #e0e0e0',
                    padding: 8,
                    fontFamily: 'monospace',
                    background: i % 2 === 0 ? '#fafbfc' : '#f5f6fa',
                    color: '#222',
                  }}
                >
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function downloadCSV(data: any[][], filename = 'results.csv') {
  const csv = data.map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(',')).join('\n');
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export const QueryForm: React.FC<QueryFormProps> = ({
  onSubmit,
  loading,
  response,
  initialQuery = '',
  setQuery,
  error,
}) => {
  const [query, setLocalQuery] = useState(initialQuery);
  const [history, setHistory] = useState<{ query: string; response: QueryResponse | undefined }[]>([]);

  useEffect(() => {
    setLocalQuery(initialQuery);
  }, [initialQuery]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setLocalQuery(e.target.value);
    setQuery && setQuery(e.target.value);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    await onSubmit(query);
    setHistory([{ query, response }, ...history]);
  };

  const handleClear = () => {
    setLocalQuery('');
    setQuery && setQuery('');
    setHistory([]);
  };

  return (
    <Fade in timeout={700}>
      <Paper elevation={1} sx={{ p: 3, mb: 3, bgcolor: '#fff', borderRadius: 4, boxShadow: '0 1px 4px rgba(0,0,0,0.04)' }}>
        <form onSubmit={handleSubmit} style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
          <TextField
            fullWidth
            multiline
            rows={2}
            value={query}
            onChange={handleChange}
            placeholder="Ask a question about your data in natural language..."
            variant="outlined"
            disabled={loading}
            inputProps={{ 'aria-label': 'Query input' }}
          />
          <Tooltip title="Submit">
            <span>
              <Button
                type="submit"
                variant="contained"
                color="primary"
                disabled={loading || !query.trim()}
                sx={{ minWidth: 56, minHeight: 56, borderRadius: 2, fontWeight: 600, fontSize: 18 }}
                aria-label="Submit query"
              >
                {loading ? <CircularProgress size={24} /> : <SendIcon />}
              </Button>
            </span>
          </Tooltip>
          <Tooltip title="Clear">
            <span>
              <IconButton onClick={handleClear} aria-label="Clear history" disabled={loading}>
                <DeleteIcon />
              </IconButton>
            </span>
          </Tooltip>
        </form>

        {error && (
          <Typography color="error" sx={{ mb: 2 }}>
            {error}
          </Typography>
        )}

        {response && (
          <div style={{ marginTop: 24 }}>
            <div style={{ fontWeight: 600, color: '#1976d2', marginBottom: 8 }}>Generated SQL:</div>
            <pre style={{
              background: '#f5f6fa',
              padding: 12,
              borderRadius: 6,
              fontFamily: 'monospace',
              color: '#222',
              border: '1px solid #e0e0e0'
            }}>
              {response.sql}
            </pre>
            <div style={{ fontWeight: 600, color: '#d32f2f', margin: '16px 0 8px' }}>Results:</div>
            {(() => {
              const parsed = parseResult(response.result);
              if (is2DArray(parsed)) {
                return (
                  <>
                    <ResultTable data={parsed} />
                    <Button
                      startIcon={<DownloadIcon />}
                      sx={{ mt: 2 }}
                      onClick={() => downloadCSV(parsed)}
                      variant="outlined"
                      color="primary"
                    >
                      Download CSV
                    </Button>
                  </>
                );
              }
              return (
                <pre style={{
                  background: '#f5f6fa',
                  padding: 12,
                  borderRadius: 6,
                  fontFamily: 'monospace',
                  color: '#222',
                  border: '1px solid #e0e0e0'
                }}>
                  {typeof parsed === 'object' ? JSON.stringify(parsed, null, 2) : String(parsed)}
                </pre>
              );
            })()}
          </div>
        )}

        {history.length > 0 && (
          <Box sx={{ mt: 4 }}>
            <Typography variant="subtitle2" sx={{ color: '#888', mb: 1 }}>
              <HistoryIcon fontSize="small" sx={{ mr: 1, verticalAlign: 'middle' }} />
              Query History
            </Typography>
            <ul style={{ paddingLeft: 16 }}>
              {history.map((h, i) => (
                <li key={i} style={{ marginBottom: 8 }}>
                  <Button
                    variant="text"
                    onClick={() => setLocalQuery(h.query)}
                    sx={{ textTransform: 'none', color: '#1976d2', fontWeight: 500 }}
                  >
                    {h.query}
                  </Button>
                </li>
              ))}
            </ul>
          </Box>
        )}
      </Paper>
    </Fade>
  );
}; 