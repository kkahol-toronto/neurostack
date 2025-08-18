import React from 'react';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  Container,
  CssBaseline,
  ThemeProvider,
  createTheme
} from '@mui/material';
import {
  Psychology as NeuroStackIcon
} from '@mui/icons-material';
import DataLayer from './components/DataLayer';
import Logo from './components/Logo';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    h4: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 500,
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static" elevation={0} sx={{ backgroundColor: '#fff', color: '#333' }}>
          <Toolbar>
            <Box display="flex" alignItems="center" gap={2}>
              <Logo variant="header" />
            </Box>
            <Box sx={{ flexGrow: 1 }} />
            <Box 
              display="flex" 
              alignItems="center" 
              gap={1}
              sx={{
                backgroundColor: '#f5f5f5',
                borderRadius: 2,
                px: 2,
                py: 1
              }}
            >
              <NeuroStackIcon sx={{ color: '#1976d2', fontSize: 20 }} />
              <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>
                Powered by NeuroStack
              </Typography>
            </Box>
          </Toolbar>
        </AppBar>
        
        <Container maxWidth="xl" sx={{ mt: 3 }}>
          <DataLayer />
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;
