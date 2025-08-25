import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Paper,
  Container,
  Alert,
  Tabs,
  Tab,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import { useTheme } from '@mui/material/styles';

interface LoginProps {
  onLogin: (token: string, user: any) => void;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`auth-tabpanel-${index}`}
      aria-labelledby={`auth-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

export default function Login({ onLogin }: LoginProps) {
  const theme = useTheme();
  const [tabValue, setTabValue] = useState(0);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Login form state
  const [loginData, setLoginData] = useState({
    username: '',
    password: ''
  });

  // Registration form state
  const [registerData, setRegisterData] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    password: '',
    role: 'analyst',
    department: 'Data Analytics'
  });

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
    setError('');
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(loginData),
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify({
          user_id: data.user_id,
          username: data.username,
          first_name: data.first_name,
          last_name: data.last_name,
          role: data.role,
          department: data.department
        }));
        onLogin(data.access_token, data);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Login failed');
      }
    } catch (err) {
      setError('Network error. Please check if the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(registerData),
      });

      if (response.ok) {
        const data = await response.json();
        setError('');
        // Switch to login tab after successful registration
        setTabValue(0);
        setLoginData({
          username: registerData.username,
          password: registerData.password
        });
        alert('Registration successful! Please login with your credentials.');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Registration failed');
      }
    } catch (err) {
      setError('Network error. Please check if the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper
          elevation={3}
          sx={{
            padding: 4,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            width: '100%',
            backgroundColor: theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(255, 255, 255, 0.9)',
            backdropFilter: 'blur(10px)',
          }}
        >
          <Typography component="h1" variant="h4" gutterBottom>
            Banking Agent
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Sign in to access the enhanced NeuroStack features
          </Typography>

          <Box sx={{ borderBottom: 1, borderColor: 'divider', width: '100%', mb: 2 }}>
            <Tabs value={tabValue} onChange={handleTabChange} aria-label="auth tabs">
              <Tab label="Login" />
              <Tab label="Register" />
            </Tabs>
          </Box>

          {error && (
            <Alert severity="error" sx={{ width: '100%', mb: 2 }}>
              {error}
            </Alert>
          )}

          <TabPanel value={tabValue} index={0}>
            <Box component="form" onSubmit={handleLogin} sx={{ width: '100%' }}>
              <TextField
                margin="normal"
                required
                fullWidth
                id="username"
                label="Username"
                name="username"
                autoComplete="username"
                autoFocus
                value={loginData.username}
                onChange={(e) => setLoginData({ ...loginData, username: e.target.value })}
              />
              <TextField
                margin="normal"
                required
                fullWidth
                name="password"
                label="Password"
                type="password"
                id="password"
                autoComplete="current-password"
                value={loginData.password}
                onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}
              />
              <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{ mt: 3, mb: 2 }}
                disabled={loading}
              >
                {loading ? 'Signing In...' : 'Sign In'}
              </Button>
            </Box>
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            <Box component="form" onSubmit={handleRegister} sx={{ width: '100%' }}>
              <TextField
                margin="normal"
                required
                fullWidth
                id="reg-username"
                label="Username"
                name="username"
                autoComplete="username"
                value={registerData.username}
                onChange={(e) => setRegisterData({ ...registerData, username: e.target.value })}
              />
              <TextField
                margin="normal"
                required
                fullWidth
                id="reg-email"
                label="Email Address"
                name="email"
                autoComplete="email"
                type="email"
                value={registerData.email}
                onChange={(e) => setRegisterData({ ...registerData, email: e.target.value })}
              />
              <TextField
                margin="normal"
                required
                fullWidth
                id="reg-first-name"
                label="First Name"
                name="first_name"
                value={registerData.first_name}
                onChange={(e) => setRegisterData({ ...registerData, first_name: e.target.value })}
              />
              <TextField
                margin="normal"
                required
                fullWidth
                id="reg-last-name"
                label="Last Name"
                name="last_name"
                value={registerData.last_name}
                onChange={(e) => setRegisterData({ ...registerData, last_name: e.target.value })}
              />
              <FormControl fullWidth margin="normal">
                <InputLabel id="role-label">Role</InputLabel>
                <Select
                  labelId="role-label"
                  id="role"
                  value={registerData.role}
                  label="Role"
                  onChange={(e) => setRegisterData({ ...registerData, role: e.target.value })}
                >
                  <MenuItem value="analyst">Analyst</MenuItem>
                  <MenuItem value="manager">Manager</MenuItem>
                  <MenuItem value="admin">Admin</MenuItem>
                </Select>
              </FormControl>
              <TextField
                margin="normal"
                required
                fullWidth
                id="reg-department"
                label="Department"
                name="department"
                value={registerData.department}
                onChange={(e) => setRegisterData({ ...registerData, department: e.target.value })}
              />
              <TextField
                margin="normal"
                required
                fullWidth
                name="password"
                label="Password"
                type="password"
                id="reg-password"
                autoComplete="new-password"
                value={registerData.password}
                onChange={(e) => setRegisterData({ ...registerData, password: e.target.value })}
              />
              <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{ mt: 3, mb: 2 }}
                disabled={loading}
              >
                {loading ? 'Creating Account...' : 'Create Account'}
              </Button>
            </Box>
          </TabPanel>

          <Box sx={{ mt: 2, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              Demo Users:
            </Typography>
            <Typography variant="caption" display="block">
              admin / admin123 (Admin)
            </Typography>
            <Typography variant="caption" display="block">
              analyst / analyst123 (Analyst)
            </Typography>
            <Typography variant="caption" display="block">
              manager / manager123 (Manager)
            </Typography>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
}
