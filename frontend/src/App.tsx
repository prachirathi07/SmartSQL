import React, { useState } from 'react';
import {
  Container,
  CssBaseline,
  ThemeProvider,
  createTheme,
  Box,
  Typography,
  Alert,
  CircularProgress,
  Chip,
  AppBar,
  Toolbar,
  Tooltip,
  Fade,
  Slide,
  Paper,
} from '@mui/material';
import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query';
import { QueryForm } from './components/QueryForm';
import { SchemaViewer } from './components/SchemaViewer';
import { apiService } from './services/api';
import { QueryResponse, DatabaseSchema } from './types';
import { AutoAwesome, DataObject } from '@mui/icons-material';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#00bcd4',
    },
    secondary: {
      main: '#ff4081',
    },
    background: {
      default: '#181c24',
      paper: 'rgba(30,34,44,0.95)',
    },
  },
  shape: {
    borderRadius: 16,
  },
  typography: {
    fontFamily: 'Inter, Roboto, Arial, sans-serif',
  },
});

const queryClient = new QueryClient();

const EXAMPLE_QUERIES = [
  'List all students in section B',
  'Show average marks for the CS class',
  'Which teachers teach Algorithms?',
  'Show names and marks for Algorithms course',
  'List teachers in Computer Science department',
];

function AnimatedHero() {
  return (
    <Box
      sx={{
        position: 'relative',
        py: { xs: 6, md: 10 },
        mb: 4,
        textAlign: 'center',
        overflow: 'hidden',
      }}
    >
      {/* Animated Gradient Background */}
      <Box
        sx={{
          position: 'absolute',
          inset: 0,
          zIndex: 0,
          background: 'linear-gradient(120deg, #00bcd4 0%, #181c24 60%, #ff4081 100%)',
          opacity: 0.18,
          filter: 'blur(40px)',
          animation: 'gradientMove 8s ease-in-out infinite alternate',
          '@keyframes gradientMove': {
            '0%': { backgroundPosition: '0% 50%' },
            '100%': { backgroundPosition: '100% 50%' },
          },
        }}
      />
      <Box sx={{ position: 'relative', zIndex: 1 }}>
        <AutoAwesome sx={{ fontSize: 60, color: 'primary.main', mb: 1, filter: 'drop-shadow(0 0 8px #00bcd4)' }} />
        <Typography variant="h2" fontWeight={700} gutterBottom>
          SmartSQL
        </Typography>
        <Typography variant="h5" color="text.secondary" fontWeight={400}>
          Natural Language to SQL Interface
        </Typography>
      </Box>
    </Box>
  );
}

function AppContent() {
  const [queryResponse, setQueryResponse] = useState<QueryResponse | undefined>();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { data: schema, isLoading: schemaLoading } = useQuery<DatabaseSchema>({
    queryKey: ['schema'],
    queryFn: apiService.getSchema,
  });
  const [query, setQuery] = useState('');

  const handleQuery = async (q: string) => {
    try {
      setError(null);
      setLoading(true);
      const response = await apiService.processQuery(q);
      setQueryResponse(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <AppBar position="sticky" elevation={0} sx={{ bgcolor: 'rgba(24,28,36,0.85)', backdropFilter: 'blur(8px)' }}>
        <Toolbar>
          <DataObject sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="h6" sx={{ flexGrow: 1, fontWeight: 700 }}>
            SmartSQL
          </Typography>
          <Typography variant="body2" color="text.secondary">
            AI-powered SQL for everyone
          </Typography>
        </Toolbar>
      </AppBar>
      <AnimatedHero />
      <Container maxWidth="lg" sx={{ pb: 6 }}>
        <Fade in timeout={800}>
          <Box>
            <Box sx={{ mb: 3, display: 'flex', flexWrap: 'wrap', gap: 1, justifyContent: 'center' }}>
              {EXAMPLE_QUERIES.map((ex, i) => (
                <Chip
                  key={i}
                  label={ex}
                  color="primary"
                  variant="outlined"
                  clickable
                  onClick={() => setQuery(ex)}
                  sx={{ fontWeight: 500, fontSize: 15, letterSpacing: 0.2 }}
                />
              ))}
            </Box>
            {error && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {error}
              </Alert>
            )}
            <Slide in direction="up" timeout={600}>
              <Box>
                <QueryForm
                  onSubmit={handleQuery}
                  loading={loading}
                  response={queryResponse}
                  initialQuery={query}
                  setQuery={setQuery}
                />
              </Box>
            </Slide>
            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 350px' }, gap: 4, mt: 4 }}>
              <Box>
                {/* Results are already shown in QueryForm */}
              </Box>
              <Box>
                <Fade in timeout={1000}>
                  <Paper elevation={4} sx={{ p: 2, bgcolor: 'background.paper', borderRadius: 4 }}>
                    {schemaLoading ? (
                      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                        <CircularProgress color="primary" size={36} thickness={4} />
                      </Box>
                    ) : schema ? (
                      <SchemaViewer schema={schema} />
                    ) : (
                      <Alert severity="error">Failed to load schema</Alert>
                    )}
                  </Paper>
                </Fade>
              </Box>
            </Box>
          </Box>
        </Fade>
      </Container>
      <Box component="footer" sx={{ textAlign: 'center', py: 3, color: 'text.secondary', bgcolor: 'rgba(24,28,36,0.7)', mt: 6, fontSize: 15, letterSpacing: 0.2 }}>
        &copy; {new Date().getFullYear()} SmartSQL &mdash; Powered by AI &amp; FAISS
      </Box>
    </>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <AppContent />
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
