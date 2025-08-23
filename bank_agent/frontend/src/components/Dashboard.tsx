import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  IconButton,
  Drawer,
  Collapse,
  Fade,
  Slide,
  Avatar,
  Chip,
  Button
} from '@mui/material';
import {
  Storage as DataSourcesIcon,
  Settings as DataProcessingIcon,
  Analytics as DataSimulationIcon,
  Description as DocumentationIcon,
  Search as SearchIcon,
  ArrowForward as ArrowIcon,
  Menu as MenuIcon,
  Close as CloseIcon,
  Logout as LogoutIcon,
  Person as PersonIcon
} from '@mui/icons-material';
import { useTheme } from '../contexts/ThemeContext';
import ThemeSwitcher from './ThemeSwitcher';
import DataLayer from './DataLayer';
import CustomerSearch from './CustomerSearch';

interface DashboardTile {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  color: string;
  isExpanded: boolean;
}

interface WorkflowConnection {
  from: string;
  to: string;
  isActive: boolean;
}

interface DashboardProps {
  onLogout: () => void;
  user: any;
}

const Dashboard: React.FC<DashboardProps> = ({ onLogout, user }) => {
  const [selectedTile, setSelectedTile] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [workflowConnections, setWorkflowConnections] = useState<WorkflowConnection[]>([
    { from: 'data-sources', to: 'data-processing', isActive: true },
    { from: 'data-processing', to: 'data-simulation', isActive: true },
    { from: 'data-simulation', to: 'documentation', isActive: true }
  ]);
  const [verifiedCustomer, setVerifiedCustomer] = useState<any>(null);
  const { theme } = useTheme();

  const tiles: DashboardTile[] = [
    {
      id: 'customer-search',
      title: 'Customer Search',
      description: 'Search and verify customer identity',
      icon: <SearchIcon sx={{ fontSize: 40 }} />,
      color: '#f59e0b',
      isExpanded: selectedTile === 'customer-search'
    },
    {
      id: 'data-sources',
      title: 'Data Sources',
      description: 'Select and configure data sources for analysis',
      icon: <DataSourcesIcon sx={{ fontSize: 40 }} />,
      color: '#6366f1',
      isExpanded: selectedTile === 'data-sources'
    },
    {
      id: 'data-processing',
      title: 'Data Processing',
      description: 'Transform and prepare data for analysis',
      icon: <DataProcessingIcon sx={{ fontSize: 40 }} />,
      color: '#8b5cf6',
      isExpanded: selectedTile === 'data-processing'
    },
    {
      id: 'data-simulation',
      title: 'Data Simulation & Visualization Studio',
      description: 'Run simulations and create visualizations',
      icon: <DataSimulationIcon sx={{ fontSize: 40 }} />,
      color: '#06b6d4',
      isExpanded: selectedTile === 'data-simulation'
    },
    {
      id: 'documentation',
      title: 'Decision Documentation',
      description: 'Document and communicate decisions',
      icon: <DocumentationIcon sx={{ fontSize: 40 }} />,
      color: '#10b981',
      isExpanded: selectedTile === 'documentation'
    }
  ];

  const handleTileClick = (tileId: string) => {
    setSelectedTile(selectedTile === tileId ? null : tileId);
    setSidebarOpen(false);
  };

  const handleSidebarItemClick = (tileId: string) => {
    if (tileId === 'home') {
      setSelectedTile(null);
    } else {
      setSelectedTile(tileId);
    }
    setSidebarOpen(false);
  };

  const handleWorkflowConnectionToggle = (from: string, to: string) => {
    setWorkflowConnections(prev => 
      prev.map(conn => 
        conn.from === from && conn.to === to 
          ? { ...conn, isActive: !conn.isActive }
          : conn
      )
    );
  };

  const handleCustomerVerified = (customer: any) => {
    setVerifiedCustomer(customer);
  };

  const renderTile = (tile: DashboardTile, index: number) => (
    <Box key={tile.id} sx={{ position: 'relative' }}>
      <Paper
        onClick={() => handleTileClick(tile.id)}
        sx={{
          p: 3,
          cursor: 'pointer',
          transition: 'all 0.3s ease',
          backgroundColor: verifiedCustomer && tile.id === 'customer-search' 
            ? 'rgba(76, 175, 80, 0.1)' 
            : 'rgba(255, 255, 255, 0.1)',
          backdropFilter: 'blur(10px)',
          border: `1px solid ${verifiedCustomer && tile.id === 'customer-search' 
            ? 'rgba(76, 175, 80, 0.3)' 
            : 'rgba(255, 255, 255, 0.2)'}`,
          borderRadius: 3,
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: '0 12px 40px rgba(0, 0, 0, 0.15)',
            backgroundColor: verifiedCustomer && tile.id === 'customer-search'
              ? 'rgba(76, 175, 80, 0.15)'
              : 'rgba(255, 255, 255, 0.15)'
          },
          position: 'relative',
          overflow: 'hidden',
          height: verifiedCustomer && tile.id === 'customer-search' ? 250 : 200, // Increased height for customer info
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          width: 400 // Fixed width for consistent layout
        }}
      >
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: 4,
            backgroundColor: tile.color,
            opacity: 0.8
          }}
        />
        
        <Box>
          <Box display="flex" alignItems="center" gap={2} mb={2}>
            <Box
              sx={{
                color: tile.color,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              {tile.icon}
            </Box>
            <Box>
              <Typography variant="h5" sx={{ 
                color: theme.colors.text,
                fontWeight: 700,
                mb: 0.5
              }}>
                {tile.title}
              </Typography>
              <Typography variant="body2" sx={{ 
                color: theme.colors.textSecondary,
                maxWidth: 300
              }}>
                {tile.description}
              </Typography>
            </Box>
          </Box>
        </Box>
        
        <Box display="flex" alignItems="center" justifyContent="space-between">
          {verifiedCustomer && tile.id === 'customer-search' ? (
            <Box sx={{ width: '100%' }}>
              <Box sx={{ 
                backgroundColor: 'rgba(255, 255, 255, 0.1)', 
                p: 2, 
                borderRadius: 2,
                mb: 1
              }}>
                <Typography variant="body2" sx={{ 
                  color: theme.colors.textSecondary,
                  fontSize: '0.7rem',
                  mb: 0.5
                }}>
                  Verified Customer
                </Typography>
                <Typography variant="body1" sx={{ 
                  color: theme.colors.text,
                  fontWeight: 600,
                  fontSize: '0.9rem'
                }}>
                  {verifiedCustomer.first_name} {verifiedCustomer.last_name}
                </Typography>
                <Typography variant="body2" sx={{ 
                  color: theme.colors.textSecondary,
                  fontSize: '0.8rem',
                  fontFamily: 'monospace'
                }}>
                  Account: {verifiedCustomer.customer_id}
                </Typography>
              </Box>
              <Typography variant="body2" sx={{ 
                color: theme.colors.textSecondary,
                fontSize: '0.7rem'
              }}>
                Click to view details
              </Typography>
            </Box>
          ) : (
            <Typography variant="body2" sx={{ 
              color: theme.colors.textSecondary,
              fontSize: '0.8rem'
            }}>
              Click to expand
            </Typography>
          )}
        </Box>
      </Paper>
      
      {/* L-shaped workflow arrows between tiles */}
      {index < tiles.length - 1 && (() => {
        const connection = workflowConnections.find(
          conn => conn.from === tile.id && conn.to === tiles[index + 1].id
        );
        const isNextTileRight = index % 2 === 0; // Even indices go right, odd go left
        
        return (
          <Box
            onClick={() => handleWorkflowConnectionToggle(tile.id, tiles[index + 1].id)}
            sx={{
              position: 'absolute',
              top: '50%',
              left: isNextTileRight ? '100%' : 'auto',
              right: isNextTileRight ? 'auto' : '100%',
              transform: 'translateY(-50%)',
              zIndex: 10,
              display: { xs: 'none', md: 'flex' },
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              '&:hover': {
                transform: 'translateY(-50%) scale(1.05)'
              }
            }}
          >
            {/* L-shaped arrow */}
            <Box sx={{ position: 'relative' }}>
              {/* Horizontal line */}
              <Box
                sx={{
                  width: isNextTileRight ? 120 : 120,
                  height: 3,
                  backgroundColor: connection?.isActive 
                    ? 'rgba(255, 255, 255, 0.6)' 
                    : 'rgba(255, 255, 255, 0.2)',
                  borderRadius: 2,
                  transition: 'all 0.3s ease'
                }}
              />
              
              {/* Vertical line with integrated arrowhead */}
              <Box
                sx={{
                  position: 'absolute',
                  top: 0,
                  left: isNextTileRight ? '100%' : 'auto',
                  right: isNextTileRight ? 'auto' : '100%',
                  width: 3,
                  height: 92, // Extended to include arrowhead
                  backgroundColor: connection?.isActive 
                    ? 'rgba(255, 255, 255, 0.6)' 
                    : 'rgba(255, 255, 255, 0.2)',
                  borderRadius: 2,
                  transition: 'all 0.3s ease',
                  '&::after': {
                    content: '""',
                    position: 'absolute',
                    bottom: -12,
                    left: -6.5, // Center the arrowhead on the 3px line
                    width: 0,
                    height: 0,
                    borderLeft: '8px solid transparent',
                    borderRight: '8px solid transparent',
                    borderTop: '12px solid',
                    borderTopColor: connection?.isActive 
                      ? 'rgba(255, 255, 255, 0.6)' 
                      : 'rgba(255, 255, 255, 0.2)',
                    transition: 'all 0.3s ease'
                  }
                }}
              />
            </Box>
            
            {/* Connection status indicator */}
            <Box
              sx={{
                position: 'absolute',
                top: -8,
                left: isNextTileRight ? 60 : 'auto',
                right: isNextTileRight ? 'auto' : 60,
                width: 16,
                height: 16,
                borderRadius: '50%',
                backgroundColor: connection?.isActive 
                  ? 'rgba(76, 175, 80, 0.8)' 
                  : 'rgba(244, 67, 54, 0.8)',
                border: '2px solid rgba(255, 255, 255, 0.3)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              <Typography
                variant="caption"
                sx={{
                  color: 'white',
                  fontSize: '0.6rem',
                  fontWeight: 'bold'
                }}
              >
                {connection?.isActive ? '✓' : '✗'}
              </Typography>
            </Box>
          </Box>
        );
      })()}
    </Box>
  );

  const renderExpandedContent = () => {
    switch (selectedTile) {
      case 'customer-search':
        return <CustomerSearch onCustomerVerified={handleCustomerVerified} />;
      case 'data-sources':
        return <DataLayer />;
      case 'data-processing':
        return (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h4" sx={{ color: theme.colors.text, mb: 2 }}>
              Data Processing
            </Typography>
            <Typography variant="body1" sx={{ color: theme.colors.textSecondary }}>
              Data processing functionality coming soon...
            </Typography>
          </Box>
        );
      case 'data-simulation':
        return (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h4" sx={{ color: theme.colors.text, mb: 2 }}>
              Data Simulation & Visualization Studio
            </Typography>
            <Typography variant="body1" sx={{ color: theme.colors.textSecondary }}>
              Simulation and visualization functionality coming soon...
            </Typography>
          </Box>
        );
      case 'documentation':
        return (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h4" sx={{ color: theme.colors.text, mb: 2 }}>
              Decision Documentation
            </Typography>
            <Typography variant="body1" sx={{ color: theme.colors.textSecondary }}>
              Documentation functionality coming soon...
            </Typography>
          </Box>
        );
      default:
        return null;
    }
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* Sidebar */}
      <Drawer
        variant="temporary"
        anchor="left"
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        PaperProps={{
          sx: {
            width: 280,
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
            backdropFilter: 'blur(10px)',
            border: 'none'
          }
        }}
      >
        <Box sx={{ p: 2 }}>
          <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
            <Typography variant="h6" sx={{ color: theme.colors.text, fontWeight: 600 }}>
              Navigation
            </Typography>
            <IconButton onClick={() => setSidebarOpen(false)}>
              <CloseIcon sx={{ color: theme.colors.text }} />
            </IconButton>
          </Box>
          
          <Box>
            {/* Home/Dashboard Option */}
            <Box
              onClick={() => handleSidebarItemClick('home')}
              sx={{
                display: 'flex',
                alignItems: 'center',
                p: 2,
                borderRadius: 2,
                mb: 1,
                backgroundColor: selectedTile === null ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 0.05)'
                }
              }}
            >
              <Box sx={{ color: '#6366f1', mr: 2, fontSize: 24 }}>
                🏠
              </Box>
              <Typography
                sx={{ 
                  color: theme.colors.text,
                  fontWeight: selectedTile === null ? 600 : 400
                }}
              >
                Home
              </Typography>
            </Box>
            
            {/* Divider */}
            <Box sx={{ 
              height: 1, 
              backgroundColor: 'rgba(255, 255, 255, 0.1)', 
              my: 2 
            }} />
            
            {tiles.map((tile) => (
              <Box
                key={tile.id}
                onClick={() => handleSidebarItemClick(tile.id)}
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  p: 2,
                  borderRadius: 2,
                  mb: 1,
                  backgroundColor: selectedTile === tile.id ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.05)'
                  }
                }}
              >
                <Box sx={{ color: tile.color, mr: 2 }}>
                  {tile.icon}
                </Box>
                <Typography
                  sx={{ 
                    color: theme.colors.text,
                    fontWeight: selectedTile === tile.id ? 600 : 400
                  }}
                >
                  {tile.title}
                </Typography>
              </Box>
            ))}
          </Box>
        </Box>
      </Drawer>

      {/* Fixed Top Bar */}
      <Box sx={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 9999,
        backgroundColor: 'rgba(255, 255, 255, 0.1)',
        backdropFilter: 'blur(10px)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.2)',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
      }}>
        <Box sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          p: 2,
          px: 3
        }}>
          <Box display="flex" alignItems="center" gap={2}>
            <IconButton
              onClick={() => setSidebarOpen(true)}
              sx={{ 
                color: theme.colors.text,
                '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 0.1)'
                }
              }}
            >
              <MenuIcon />
            </IconButton>
            <Typography variant="h5" sx={{ 
              color: theme.colors.text,
              fontWeight: 700
            }}>
              Banking Agent
            </Typography>
          </Box>
          
          <Box display="flex" alignItems="center" gap={2}>
            {/* User Info */}
            <Box display="flex" alignItems="center" gap={1}>
              <Avatar sx={{ width: 32, height: 32, bgcolor: '#6366f1' }}>
                <PersonIcon />
              </Avatar>
              <Box>
                <Typography variant="body2" sx={{ 
                  color: theme.colors.text,
                  fontWeight: 600,
                  fontSize: '0.8rem'
                }}>
                  {user?.first_name} {user?.last_name}
                </Typography>
                <Chip 
                  label={user?.role || 'User'} 
                  size="small" 
                  sx={{ 
                    height: 20, 
                    fontSize: '0.7rem',
                    backgroundColor: user?.role === 'admin' ? '#ef4444' : 
                                   user?.role === 'manager' ? '#f59e0b' : '#10b981'
                  }} 
                />
              </Box>
            </Box>
            
            <ThemeSwitcher />
            
            <Button
              onClick={onLogout}
              startIcon={<LogoutIcon />}
              variant="outlined"
              size="small"
              sx={{
                color: theme.colors.text,
                borderColor: 'rgba(255, 255, 255, 0.3)',
                '&:hover': {
                  borderColor: 'rgba(255, 255, 255, 0.5)',
                  backgroundColor: 'rgba(255, 255, 255, 0.05)'
                }
              }}
            >
              Logout
            </Button>
          </Box>
        </Box>
      </Box>

      {/* Main Content */}
      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', pt: 8 }}>
        {/* Content Area */}
        <Box sx={{ flex: 1, p: 3 }}>
          {selectedTile ? (
            // Expanded view
            <Slide direction="up" in={true} mountOnEnter unmountOnExit>
              <Box>
                <IconButton
                  onClick={() => setSelectedTile(null)}
                  sx={{ 
                    mb: 2,
                    color: theme.colors.textSecondary,
                    '&:hover': { color: theme.colors.text }
                  }}
                >
                  <ArrowIcon sx={{ transform: 'rotate(180deg)' }} />
                  Back to Dashboard
                </IconButton>
                {renderExpandedContent()}
              </Box>
            </Slide>
          ) : (
            // Dashboard tiles view
            <Fade in={true}>
              <Box>
                <Typography variant="h3" sx={{ 
                  color: theme.colors.text,
                  fontWeight: 700,
                  mb: 1,
                  textAlign: 'center'
                }}>
                  Welcome to Banking Agent
                </Typography>
                <Typography variant="h6" sx={{ 
                  color: theme.colors.textSecondary,
                  mb: 4,
                  textAlign: 'center'
                }}>
                  Select a module to get started
                </Typography>
                
                <Box sx={{ 
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 6,
                  alignItems: 'center'
                }}>
                  {tiles.map((tile, index) => (
                    <Box key={tile.id} sx={{ 
                      position: 'relative',
                      transform: index % 2 === 1 ? 'translateX(200px)' : 'translateX(0)',
                      transition: 'transform 0.3s ease'
                    }}>
                      {renderTile(tile, index)}
                    </Box>
                  ))}
                </Box>
              </Box>
            </Fade>
          )}
        </Box>
      </Box>
    </Box>
  );
};

export default Dashboard;
