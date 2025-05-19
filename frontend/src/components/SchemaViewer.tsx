import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Stack,
  Tooltip,
  Divider,
} from '@mui/material';
import { TableChart, Visibility, Key } from '@mui/icons-material';
import { DatabaseSchema } from '../types';

interface SchemaViewerProps {
  schema: DatabaseSchema;
}

export const SchemaViewer: React.FC<SchemaViewerProps> = ({ schema }) => {
  return (
    <Box>
      <Typography variant="h6" gutterBottom sx={{ fontWeight: 700, color: 'primary.main', mb: 2 }}>
        Database Schema
      </Typography>
      <Box
        sx={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: 2,
          justifyContent: { xs: 'center', md: 'flex-start' },
        }}
      >
        {Object.entries(schema).map(([tableName, info]) => (
          <Box
            key={tableName}
            sx={{
              flex: '1 1 320px',
              minWidth: 280,
              maxWidth: 400,
              mb: 2,
            }}
          >
            <Card
              elevation={4}
              sx={{
                bgcolor: 'rgba(30,34,44,0.95)',
                borderRadius: 3,
                borderLeft: `4px solid ${info.is_view ? '#ff4081' : '#00bcd4'}`,
                height: '100%',
                transition: 'transform 0.2s',
                '&:hover': { transform: 'scale(1.03)' },
              }}
            >
              <CardContent>
                <Box display="flex" alignItems="center" mb={1}>
                  {info.is_view ? (
                    <Visibility sx={{ color: 'secondary.main', mr: 1 }} />
                  ) : (
                    <TableChart sx={{ color: 'primary.main', mr: 1 }} />
                  )}
                  <Typography variant="subtitle1" fontWeight={600}>
                    {tableName}
                  </Typography>
                  {info.is_view && (
                    <Chip
                      label="View"
                      size="small"
                      color="secondary"
                      sx={{ ml: 2, fontWeight: 600 }}
                    />
                  )}
                </Box>
                <Divider sx={{ mb: 1, opacity: 0.2 }} />
                <Stack direction="row" spacing={1} flexWrap="wrap" mb={1}>
                  {info.columns.map((col) => (
                    <Tooltip
                      key={col}
                      title={`Type: ${info.types[col]}`}
                      arrow
                      placement="top"
                    >
                      <Chip
                        label={col}
                        size="small"
                        sx={{
                          bgcolor: 'rgba(0,188,212,0.13)',
                          color: 'primary.main',
                          fontWeight: 500,
                          mb: 0.5,
                        }}
                      />
                    </Tooltip>
                  ))}
                </Stack>
                {info.foreign_keys && info.foreign_keys.length > 0 && (
                  <Box mt={1}>
                    <Typography variant="caption" color="secondary" fontWeight={700}>
                      <Key sx={{ fontSize: 16, verticalAlign: 'middle', mr: 0.5 }} />
                      Foreign Keys:
                    </Typography>
                    <Stack direction="row" spacing={1} flexWrap="wrap" mt={0.5}>
                      {info.foreign_keys.map((fk, idx) => (
                        <Chip
                          key={idx}
                          label={`${fk.constrained_columns.join(', ')} → ${fk.referred_table}(${fk.referred_columns.join(', ')})`}
                          size="small"
                          color="secondary"
                          variant="outlined"
                          sx={{ fontWeight: 500, mb: 0.5 }}
                        />
                      ))}
                    </Stack>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Box>
        ))}
      </Box>
    </Box>
  );
};