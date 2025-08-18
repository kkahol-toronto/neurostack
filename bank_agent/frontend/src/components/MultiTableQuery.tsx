import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Alert,
  CircularProgress,
  Chip,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Paper,
  Divider,
  Checkbox,
  FormControlLabel,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  Close as CloseIcon,
  CheckCircle as SelectedIcon,
  RadioButtonUnchecked as UnselectedIcon,
  QueryStats as QueryIcon,
  ExpandMore as ExpandMoreIcon
} from '@mui/icons-material';
import { DataSource, QueryResult, TableInfo } from '../types';
import { useTheme } from '../contexts/ThemeContext';
import apiService from '../services/api';

interface MultiTableQueryProps {
  open: boolean;
  onClose: () => void;
  dataSources: DataSource[];
}

const MultiTableQuery: React.FC<MultiTableQueryProps> = ({ open, onClose, dataSources }) => {
  const [query, setQuery] = useState('');
  const [queryResult, setQueryResult] = useState<QueryResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [generatedSQL, setGeneratedSQL] = useState<string>('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [selectedTables, setSelectedTables] = useState<string[]>([]);
  const [showTableSelection, setShowTableSelection] = useState(false);
  const { theme } = useTheme();

  // Convert all data sources to table info for the backend
  const allTables: TableInfo[] = dataSources.map(dataSource => ({
    tableName: dataSource.table_name,
    fields: dataSource.fields
  }));

  const handleTableToggle = (tableName: string) => {
    setSelectedTables(prev => 
      prev.includes(tableName) 
        ? prev.filter(t => t !== tableName)
        : [...prev, tableName]
    );
  };

  const handleGenerateQuery = async () => {
    if (!query.trim()) return;

    setIsGenerating(true);
    setGeneratedSQL('');
    setQueryResult(null);

    try {
      // Use selected tables if any, otherwise use all tables
      const tablesToUse = selectedTables.length > 0 
        ? allTables.filter(table => selectedTables.includes(table.tableName))
        : allTables;
      
      // Convert natural language to SQL with selected tables
      const sqlResult = await apiService.convertTextToSQLMultiTable(query, tablesToUse);
      
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
      const executeResult = await apiService.executeSQL(generatedSQL);
      
      // Set the results
      setQueryResult({
        success: executeResult.success,
        sql: generatedSQL,
        data: executeResult.data,
        executionTime: executeResult.executionTime,
        error: executeResult.error
      });
    } catch (error) {
      setQueryResult({
        success: false,
        error: 'Failed to execute query'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    setQuery('');
    setQueryResult(null);
    setGeneratedSQL('');
    setSelectedTables([]);
    setShowTableSelection(false);
    onClose();
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
    <Dialog 
      open={open} 
      onClose={handleClose}
      maxWidth="lg"
      fullWidth
      PaperProps={{
        sx: {
          background: theme.colors.surface,
          fontFamily: theme.fonts.primary,
          minHeight: '80vh',
          backdropFilter: 'blur(10px)',
          backgroundColor: `${theme.colors.surface} !important`,
          opacity: 1
        }
      }}
      BackdropProps={{
        sx: {
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          backdropFilter: 'blur(5px)'
        }
      }}
    >
      <DialogTitle sx={{ 
        color: theme.colors.text,
        borderBottom: `1px solid ${theme.colors.border}`,
        display: 'flex',
        alignItems: 'center',
        gap: 2,
        p: 3
      }}>
        <QueryIcon sx={{ color: theme.colors.primary, fontSize: 28 }} />
        <Typography variant="h5" sx={{ color: theme.colors.text, fontWeight: 600 }}>
          Intelligent Query
        </Typography>
        <IconButton
          onClick={handleClose}
          sx={{ marginLeft: 'auto', color: theme.colors.textSecondary }}
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <DialogContent sx={{ 
        p: 4,
        backgroundColor: `${theme.colors.surface} !important`,
        opacity: 1
      }}>
        {/* Optional Table Selection */}
        <Box mb={3}>
          <Button
            variant="text"
            onClick={() => setShowTableSelection(!showTableSelection)}
            sx={{ 
              color: theme.colors.primary,
              textTransform: 'none',
              fontSize: '0.9rem'
            }}
          >
            {showTableSelection ? 'Hide' : 'Show'} table selection ({selectedTables.length} selected)
          </Button>
          
          {showTableSelection && (
            <Paper sx={{ 
              mt: 2, 
              p: 2, 
              border: `1px solid ${theme.colors.border}`,
              backgroundColor: `${theme.colors.background} !important`,
              opacity: 1
            }}>
              <Typography variant="subtitle2" sx={{ color: theme.colors.text, mb: 2, fontWeight: 600 }}>
                Select specific tables (optional - AI will choose automatically if none selected)
              </Typography>
              <Box display="flex" flexWrap="wrap" gap={2}>
                {dataSources.map((dataSource) => (
                  <FormControlLabel
                    key={dataSource.id}
                    control={
                      <Checkbox
                        checked={selectedTables.includes(dataSource.table_name)}
                        onChange={() => handleTableToggle(dataSource.table_name)}
                        sx={{
                          color: theme.colors.primary,
                          '&.Mui-checked': {
                            color: theme.colors.primary
                          }
                        }}
                      />
                    }
                    label={
                      <Box display="flex" alignItems="center" gap={1}>
                        <Typography variant="body2">
                          {getCategoryIcon(dataSource.category)}
                        </Typography>
                        <Typography variant="body2" sx={{ color: theme.colors.text }}>
                          {dataSource.name}
                        </Typography>
                        <Chip 
                          label={`${dataSource.fields.length}`}
                          size="small"
                          sx={{
                            backgroundColor: theme.colors.primary,
                            color: 'white',
                            fontSize: '0.7rem',
                            height: 16
                          }}
                        />
                      </Box>
                    }
                    sx={{ 
                      margin: 0,
                      '& .MuiFormControlLabel-label': {
                        fontSize: '0.85rem'
                      }
                    }}
                  />
                ))}
              </Box>
            </Paper>
          )}
        </Box>

        {/* Query Input */}
        <Box mb={4}>
          <Typography variant="h6" sx={{ color: theme.colors.text, mb: 2, fontWeight: 600 }}>
            Natural Language Query
          </Typography>
          <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 3 }}>
            Describe what you want to find. The AI will automatically determine which data sources to use.
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={5}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g., Show me customers with high income and low credit utilization, or find customers with good credit scores and low fraud risk..."
            variant="outlined"
            sx={{
              '& .MuiOutlinedInput-root': {
                color: theme.colors.text,
                backgroundColor: `${theme.colors.background} !important`,
                fontSize: '1rem',
                opacity: 1,
                '& fieldset': {
                  borderColor: theme.colors.border
                },
                '&:hover fieldset': {
                  borderColor: theme.colors.primary
                },
                '&.Mui-focused fieldset': {
                  borderColor: theme.colors.primary
                }
              }
            }}
          />
        </Box>

        {/* Generated SQL */}
        {generatedSQL && (
          <Box mb={4}>
            <Typography variant="h6" sx={{ color: theme.colors.text, mb: 2, fontWeight: 600 }}>
              Generated SQL Query
            </Typography>
            <Paper
              sx={{
                p: 3,
                backgroundColor: `${theme.colors.background} !important`,
                border: `1px solid ${theme.colors.border}`,
                fontFamily: 'monospace',
                fontSize: '0.9rem',
                whiteSpace: 'pre-wrap',
                overflow: 'auto',
                maxHeight: 200,
                borderRadius: 2,
                opacity: 1
              }}
            >
              {generatedSQL}
            </Paper>
          </Box>
        )}

        {/* Query Results */}
        {queryResult && (
          <Box mb={4}>
            <Typography variant="h6" sx={{ color: theme.colors.text, mb: 2, fontWeight: 600 }}>
              Query Results
            </Typography>
            {queryResult.success ? (
              <Box>
                <Alert severity="success" sx={{ mb: 3, borderRadius: 2 }}>
                  Query executed successfully in {queryResult.executionTime?.toFixed(2)}ms
                </Alert>
                {queryResult.data && queryResult.data.length > 0 ? (
                  <Paper
                    sx={{
                      p: 3,
                      backgroundColor: `${theme.colors.background} !important`,
                      border: `1px solid ${theme.colors.border}`,
                      maxHeight: 400,
                      overflow: 'auto',
                      borderRadius: 2,
                      opacity: 1
                    }}
                  >
                    <Typography variant="subtitle1" sx={{ color: theme.colors.text, mb: 2, fontWeight: 600 }}>
                      Results ({queryResult.data.length} rows):
                    </Typography>
                    <pre style={{ 
                      margin: 0, 
                      fontSize: '0.85rem',
                      color: theme.colors.text,
                      fontFamily: 'monospace',
                      lineHeight: 1.4
                    }}>
                      {JSON.stringify(queryResult.data, null, 2)}
                    </pre>
                  </Paper>
                ) : (
                  <Alert severity="info" sx={{ borderRadius: 2 }}>No data returned</Alert>
                )}
              </Box>
            ) : (
              <Alert severity="error" sx={{ borderRadius: 2 }}>
                {queryResult.error || 'An error occurred'}
              </Alert>
            )}
          </Box>
        )}
      </DialogContent>

      <DialogActions sx={{ 
        p: 4, 
        borderTop: `1px solid ${theme.colors.border}`, 
        gap: 2,
        backgroundColor: `${theme.colors.surface} !important`,
        opacity: 1
      }}>
        <Button 
          onClick={handleClose} 
          variant="outlined"
          size="large"
          sx={{ 
            color: theme.colors.textSecondary,
            borderColor: theme.colors.border,
            px: 4,
            py: 1.5
          }}
        >
          Close
        </Button>
        
        <Button
          variant="contained"
          onClick={handleGenerateQuery}
          disabled={!query.trim() || isGenerating}
          startIcon={isGenerating ? <CircularProgress size={20} /> : <QueryIcon />}
          size="large"
          sx={{
            backgroundColor: theme.colors.primary,
            px: 4,
            py: 1.5,
            fontSize: '1rem',
            fontWeight: 600,
            '&:hover': {
              backgroundColor: theme.colors.primaryDark
            }
          }}
        >
          {isGenerating ? 'Generating...' : 'Generate Query'}
        </Button>
        
        {generatedSQL && (
          <Button
            variant="contained"
            onClick={handleExecuteQuery}
            disabled={isLoading}
            startIcon={isLoading ? <CircularProgress size={20} /> : <QueryIcon />}
            size="large"
            sx={{
              backgroundColor: theme.colors.primary,
              px: 4,
              py: 1.5,
              fontSize: '1rem',
              fontWeight: 600,
              '&:hover': {
                backgroundColor: theme.colors.primaryDark
              }
            }}
          >
            {isLoading ? 'Executing...' : 'Execute Query'}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default MultiTableQuery;
