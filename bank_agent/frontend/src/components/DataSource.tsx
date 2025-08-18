import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Chip,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Alert,
  CircularProgress
} from '@mui/material';
import {
  QueryStats as QueryIcon,
  CheckCircle as EnabledIcon,
  Cancel as DisabledIcon
} from '@mui/icons-material';
import { DataSource as DataSourceType, QueryResult } from '../types';
import { useTheme } from '../contexts/ThemeContext';
import apiService from '../services/api';

interface DataSourceProps {
  dataSource: DataSourceType;
  onToggle: (id: string) => void;
}

const DataSource: React.FC<DataSourceProps> = ({ dataSource, onToggle }) => {
  const [isHovered, setIsHovered] = useState(false);
  const [showQueryDialog, setShowQueryDialog] = useState(false);
  const [query, setQuery] = useState('');
  const [queryResult, setQueryResult] = useState<QueryResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [generatedSQL, setGeneratedSQL] = useState<string>('');
  const [isGenerating, setIsGenerating] = useState(false);
  const { theme } = useTheme();

  const handleClick = () => {
    onToggle(dataSource.id);
  };

  const handleDoubleClick = () => {
    // Set a default query that will return results
    const defaultQuery = dataSource.sample_query || 'Show me customers with income above $70,000';
    setQuery(defaultQuery);
    setShowQueryDialog(true);
    setGeneratedSQL('');
    setQueryResult(null);
  };

  const handleGenerateQuery = async () => {
    if (!query.trim()) return;

    setIsGenerating(true);
    setGeneratedSQL('');
    setQueryResult(null);

    try {
      // Convert natural language to SQL
      const sqlResult = await apiService.convertTextToSQL(
        query,
        dataSource.table_name,
        dataSource.fields
      );
      
      if (sqlResult.success && sqlResult.sql) {
        setGeneratedSQL(sqlResult.sql);
      } else {
        setQueryResult({
          success: false,
          error: sqlResult.error || 'Failed to generate SQL query'
        });
      }
    } catch (error) {
      setQueryResult({
        success: false,
        error: 'Failed to generate SQL query'
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const handleExecuteQuery = async () => {
    if (!generatedSQL.trim()) return;

    setIsLoading(true);
    setQueryResult(null);

    try {
      // Execute the generated SQL against the database
      const executeResult = await apiService.executeSQL(generatedSQL, dataSource.table_name);
      
      console.log('Execute result:', executeResult); // Debug log
      
      // Set the results
      const result = {
        success: executeResult.success,
        sql: generatedSQL,
        data: executeResult.data,
        executionTime: executeResult.executionTime,
        error: executeResult.error
      };
      
      console.log('Setting queryResult:', result); // Debug log
      setQueryResult(result);
    } catch (error) {
      console.error('Execute error:', error); // Debug log
      setQueryResult({
        success: false,
        error: 'Failed to execute query'
      });
    } finally {
      setIsLoading(false);
    }
  };



  const getCategoryIcon = (category: string) => {
    const icons: { [key: string]: string } = {
      demographics: '👥',
      banking: '🏦',
      credit_bureau: '📊',
      income: '💰',
      open_banking: '🔗',
      fraud: '⚠️',
      economic: '📈'
    };
    return icons[category] || '📋';
  };

  return (
    <>
      <Card
        sx={{
          width: '100%',
          height: 300,
          cursor: 'pointer',
          transition: 'all 0.3s ease',
          transform: isHovered ? 'scale(1.02)' : 'scale(1)',
          boxShadow: isHovered ? theme.effects.hoverGlow : theme.effects.shadow,
          border: dataSource.is_enabled ? `2px solid ${theme.colors.primary}` : `2px solid ${theme.colors.border}`,
          position: 'relative',
          overflow: 'hidden',
          background: theme.colors.surface,
          fontFamily: theme.fonts.primary
        }}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        onClick={handleClick}
        onDoubleClick={handleDoubleClick}
      >
        <CardContent sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
          {/* Header Section */}
          <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
            <Box display="flex" alignItems="center" gap={1} sx={{ flex: 1, minWidth: 0 }}>
              <Typography variant="h6" component="div" fontSize="1.2rem" sx={{ flexShrink: 0 }}>
                {getCategoryIcon(dataSource.category)}
              </Typography>
              <Typography 
                variant="h6" 
                component="div" 
                fontSize="1rem"
                sx={{ 
                  color: '#000000', 
                  fontFamily: theme.fonts.primary, 
                  fontWeight: 700,
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                  textShadow: '0 1px 2px rgba(255, 255, 255, 0.8)',
                  flex: 1,
                  minWidth: 0
                }}
              >
                {dataSource.name}
              </Typography>
            </Box>
            {dataSource.is_enabled ? (
              <EnabledIcon sx={{ color: theme.colors.success, flexShrink: 0 }} />
            ) : (
              <DisabledIcon sx={{ color: theme.colors.textSecondary, flexShrink: 0 }} />
            )}
          </Box>

          {/* Chip Section */}
          <Box sx={{ mb: 1 }}>
            <Chip
              label={dataSource.category.replace('_', ' ')}
              size="medium"
              sx={{
                backgroundColor: 'rgba(255, 255, 255, 0.9)',
                color: '#000000',
                border: `2px solid ${theme.colors.primary}`,
                fontFamily: theme.fonts.primary,
                fontSize: '0.9rem',
                fontWeight: 700,
                height: '28px',
                textShadow: '0 1px 2px rgba(255, 255, 255, 0.8)'
              }}
            />
          </Box>

          {/* Description Section - Compact */}
          <Box sx={{ flex: 1, minHeight: 0, mb: 0 }}>
            <Typography 
              variant="body1" 
              sx={{ 
                color: '#000000', 
                fontFamily: theme.fonts.primary,
                fontSize: '1.1rem',
                lineHeight: 1.4,
                fontWeight: 600,
                textShadow: '0 1px 2px rgba(255, 255, 255, 0.8)',
                display: '-webkit-box',
                WebkitLineClamp: 5,
                WebkitBoxOrient: 'vertical',
                overflow: 'hidden'
              }}
            >
              {dataSource.description}
            </Typography>
          </Box>

          {/* Footer Section - Guaranteed Space */}
          <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ 
            height: '48px',
            mt: 1,
            pt: 1,
            pb: 0.5,
            borderTop: `1px solid ${theme.colors.border}`,
            backgroundColor: 'rgba(255, 255, 255, 0.1)'
          }}>
            <Typography 
              variant="body1" 
              sx={{ 
                color: '#000000', 
                fontFamily: theme.fonts.primary,
                fontWeight: 700,
                fontSize: '1.2rem',
                textShadow: '0 1px 2px rgba(255, 255, 255, 0.8)',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
                flex: 1,
                minWidth: 0
              }}
            >
              {dataSource.fields.length} fields
            </Typography>
            <Tooltip title="Double-click to query">
              <IconButton size="medium" sx={{ color: '#000000', flexShrink: 0, ml: 1 }}>
                <QueryIcon fontSize="medium" />
              </IconButton>
            </Tooltip>
          </Box>

          {isHovered && (
            <Box
              sx={{
                position: 'absolute',
                top: -10,
                left: '50%',
                transform: 'translateX(-50%)',
                backgroundColor: theme.colors.surface,
                color: theme.colors.text,
                padding: 1,
                borderRadius: 1,
                fontSize: '0.75rem',
                zIndex: 1000,
                maxWidth: 250,
                textAlign: 'center',
                border: `1px solid ${theme.colors.border}`,
                boxShadow: theme.effects.shadow,
                fontFamily: theme.fonts.primary
              }}
            >
              Click to toggle • Double-click to query
            </Box>
          )}
        </CardContent>
      </Card>

      <Dialog
        open={showQueryDialog}
        onClose={() => setShowQueryDialog(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            background: 'rgba(255, 255, 255, 0.95)',
            border: `2px solid ${theme.colors.primary}`,
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
            backdropFilter: 'blur(10px)',
            fontFamily: theme.fonts.primary,
            maxHeight: '90vh'
          }
        }}
      >
        <DialogTitle sx={{ color: '#1a1a1a', fontFamily: theme.fonts.primary, fontWeight: 700, fontSize: '1.3rem' }}>
          <Box display="flex" alignItems="center" gap={1}>
            <QueryIcon sx={{ color: theme.colors.primary, fontSize: 28 }} />
            <Typography sx={{ color: '#1a1a1a', fontFamily: theme.fonts.primary, fontWeight: 700, fontSize: '1.3rem' }}>Query {dataSource.name}</Typography>
          </Box>
        </DialogTitle>
        <DialogContent sx={{ color: '#1a1a1a', fontFamily: theme.fonts.primary }}>
          <Box mb={2}>
            <Typography variant="body1" sx={{ color: theme.colors.textSecondary, mb: 1, fontFamily: theme.fonts.primary, fontSize: '1rem' }}>
              Available fields: {dataSource.fields.join(', ')}
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={3}
              label="Natural Language Query"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g., Show me customers with income above $70,000"
              variant="outlined"
              sx={{
                '& .MuiOutlinedInput-root': {
                  color: '#1a1a1a',
                  backgroundColor: 'rgba(255, 255, 255, 0.8)',
                  fontSize: '1.1rem',
                  '& fieldset': {
                    borderColor: theme.colors.border,
                    borderWidth: '2px',
                  },
                  '&:hover fieldset': {
                    borderColor: theme.colors.primary,
                    borderWidth: '2px',
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: theme.colors.primary,
                    borderWidth: '2px',
                  },
                },
                '& .MuiInputLabel-root': {
                  color: '#4a4a4a',
                  fontSize: '1.1rem',
                  fontWeight: 600,
                  '&.Mui-focused': {
                    color: theme.colors.primary,
                  },
                },
                '& .MuiInputBase-input': {
                  color: '#1a1a1a',
                  fontFamily: theme.fonts.primary,
                  fontSize: '1.1rem',
                  fontWeight: 500,
                },
                '& .MuiInputBase-input::placeholder': {
                  color: '#666666',
                  opacity: 0.8,
                  fontSize: '1rem',
                },
              }}
            />
          </Box>

          {(isGenerating || isLoading) && (
            <Box display="flex" justifyContent="center" my={2}>
              <CircularProgress />
            </Box>
          )}

          {generatedSQL && (
            <Box mb={2}>
                                <Typography variant="h6" gutterBottom sx={{ color: theme.colors.text, fontFamily: theme.fonts.primary, fontWeight: 600 }}>
                    Generated SQL:
                  </Typography>
                              <Box
                  sx={{
                    backgroundColor: theme.colors.background,
                    padding: 1.5,
                    borderRadius: 1,
                    fontFamily: theme.fonts.monospace,
                    fontSize: '1rem',
                    border: `1px solid ${theme.colors.primary}`,
                    color: theme.colors.primary
                  }}
                >
                {generatedSQL}
              </Box>
            </Box>
          )}

          {queryResult && (
            <Box>
              {queryResult.success ? (
                <>
                  <Alert severity="success" sx={{ mb: 2 }}>
                    Query executed successfully in {queryResult.executionTime}ms
                  </Alert>
                  
                  {/* Debug info */}
                  <Box sx={{ mb: 2, p: 1, backgroundColor: '#f0f0f0', borderRadius: 1, fontSize: '0.8rem' }}>
                    Debug: data exists: {queryResult.data ? 'Yes' : 'No'}, 
                    data length: {queryResult.data ? queryResult.data.length : 'N/A'},
                    data type: {typeof queryResult.data}
                  </Box>
                  
                  {queryResult.data && Array.isArray(queryResult.data) && queryResult.data.length > 0 ? (
                    <>
                      <Typography variant="h6" gutterBottom sx={{ color: theme.colors.text, fontFamily: theme.fonts.primary, fontWeight: 600 }}>
                        Results ({queryResult.data.length} rows):
                      </Typography>
                      <Box
                        sx={{
                          maxHeight: 300,
                          overflow: 'auto',
                          border: `1px solid ${theme.colors.primary}`,
                          borderRadius: 1,
                          backgroundColor: theme.colors.background
                        }}
                      >
                        <pre style={{ 
                          margin: 0, 
                          padding: 12, 
                          fontSize: '0.9rem',
                          color: theme.colors.primary,
                          fontFamily: theme.fonts.monospace
                        }}>
                          {JSON.stringify(queryResult.data.slice(0, 5), null, 2)}
                          {queryResult.data.length > 5 && `\n... and ${queryResult.data.length - 5} more rows`}
                        </pre>
                      </Box>
                    </>
                  ) : (
                    <Alert severity="info" sx={{ mt: 2 }}>
                      {queryResult.data && Array.isArray(queryResult.data) && queryResult.data.length === 0 
                        ? 'Query returned no data (0 rows)' 
                        : 'No data available to display'}
                    </Alert>
                  )}
                </>
              ) : (
                <Alert severity="error">
                  {queryResult.error}
                </Alert>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions sx={{ backgroundColor: 'rgba(255, 255, 255, 0.9)', borderTop: `1px solid ${theme.colors.border}`, padding: '16px 24px' }}>
          <Button 
            onClick={() => setShowQueryDialog(false)}
            sx={{ 
              color: '#000000', 
              border: `2px solid #000000`,
              fontFamily: theme.fonts.primary,
              fontSize: '1.1rem',
              fontWeight: 700,
              padding: '10px 24px',
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
              textShadow: '0 1px 2px rgba(255, 255, 255, 0.8)',
              '&:hover': {
                backgroundColor: '#000000',
                border: `2px solid #000000`,
                color: '#ffffff',
                transform: 'translateY(-1px)',
                boxShadow: '0 4px 8px rgba(0, 0, 0, 0.2)'
              }
            }}
          >
            CLOSE
          </Button>
          <Button
            onClick={handleGenerateQuery}
            variant="contained"
            disabled={!query.trim() || isGenerating || isLoading}
            sx={{ 
              backgroundColor: '#000000',
              color: '#ffffff',
              border: `2px solid #000000`,
              fontFamily: theme.fonts.primary,
              fontSize: '1.1rem',
              fontWeight: 700,
              padding: '10px 24px',
              textShadow: '0 1px 2px rgba(0, 0, 0, 0.3)',
              '&:hover': {
                backgroundColor: theme.colors.primary,
                color: '#ffffff',
                transform: 'translateY(-1px)',
                boxShadow: '0 4px 8px rgba(0, 0, 0, 0.3)'
              },
              '&:disabled': {
                backgroundColor: '#cccccc',
                color: '#666666',
                border: '2px solid #cccccc'
              }
            }}
          >
            GENERATE QUERY
          </Button>
          <Button
            onClick={handleExecuteQuery}
            variant="contained"
            disabled={!generatedSQL.trim() || isLoading}
            sx={{ 
              backgroundColor: '#000000',
              color: '#ffffff',
              border: `2px solid #000000`,
              fontFamily: theme.fonts.primary,
              fontSize: '1.1rem',
              fontWeight: 700,
              padding: '10px 24px',
              textShadow: '0 1px 2px rgba(0, 0, 0, 0.3)',
              '&:hover': {
                backgroundColor: theme.colors.primary,
                color: '#ffffff',
                transform: 'translateY(-1px)',
                boxShadow: '0 4px 8px rgba(0, 0, 0, 0.3)'
              },
              '&:disabled': {
                backgroundColor: '#cccccc',
                color: '#666666',
                border: '2px solid #cccccc'
              }
            }}
          >
            EXECUTE QUERY
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default DataSource;
