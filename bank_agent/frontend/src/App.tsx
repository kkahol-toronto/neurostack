import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  AppBar,
  Toolbar,
  Paper,
  Chip,
  Alert
} from '@mui/material';
import DataLayer from './components/DataLayer';
import ThemeSwitcher from './components/ThemeSwitcher';
import { useTheme } from './contexts/ThemeContext';
import './App.css';

function App() {
  const { theme } = useTheme();

  return (
    <div className="App">
      <AppBar 
        position="static" 
        sx={{
          backgroundColor: theme.colors.surface,
          boxShadow: theme.effects.shadow,
          borderBottom: `1px solid ${theme.colors.border}`
        }}
      >
        <Toolbar>
          <Typography 
            variant="h4" 
            component="div" 
            sx={{ 
              flexGrow: 1, 
              fontFamily: theme.fonts.primary,
              color: theme.colors.text,
              fontWeight: 700
            }}
          >
            🏦 Banking Agent - Data Source Management
          </Typography>
          <ThemeSwitcher />
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <DataLayer />
        
        <Box 
          sx={{
            mt: 4,
            pt: 3,
            borderTop: `1px solid ${theme.colors.border}`,
            textAlign: 'center'
          }}
        >
          <Typography 
            variant="h6" 
            sx={{ 
              fontFamily: theme.fonts.primary,
              color: theme.colors.textSecondary,
              fontWeight: 600
            }}
          >
            Powered by NeuroStack - AI-Powered Banking Intelligence
          </Typography>
        </Box>
      </Container>
    </div>
  );
}

export default App;
