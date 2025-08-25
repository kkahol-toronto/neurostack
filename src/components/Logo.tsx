import React from 'react';
import { Box, Typography } from '@mui/material';
import {
  AccountBalance as BankIcon,
  TrendingUp as TrendingIcon,
  Psychology as NeuroStackIcon
} from '@mui/icons-material';

interface LogoProps {
  variant?: 'header' | 'sidebar' | 'footer';
  showText?: boolean;
}

const Logo: React.FC<LogoProps> = ({ variant = 'header', showText = true }) => {
  const getSize = () => {
    switch (variant) {
      case 'header':
        return { iconSize: 28, textSize: 'h5' };
      case 'sidebar':
        return { iconSize: 24, textSize: 'h6' };
      case 'footer':
        return { iconSize: 20, textSize: 'body2' };
      default:
        return { iconSize: 28, textSize: 'h5' };
    }
  };

  const { iconSize, textSize } = getSize();

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: 1,
        backgroundColor: variant === 'header' ? '#1976d2' : 'transparent',
        borderRadius: 2,
        px: variant === 'header' ? 2 : 0,
        py: variant === 'header' ? 1 : 0,
        color: variant === 'header' ? 'white' : 'inherit'
      }}
    >
      <Box sx={{ position: 'relative' }}>
        <BankIcon sx={{ fontSize: iconSize }} />
        <TrendingIcon 
          sx={{ 
            fontSize: iconSize * 0.6, 
            position: 'absolute',
            top: -2,
            right: -2,
            color: '#4CAF50'
          }} 
        />
      </Box>
      {showText && (
        <Box>
          <Typography 
            variant={textSize as any} 
            component="div" 
            sx={{ 
              fontWeight: 600,
              lineHeight: 1.2
            }}
          >
            Credit Limit Agent
          </Typography>
          {variant === 'header' && (
            <Typography 
              variant="caption" 
              sx={{ 
                opacity: 0.8,
                fontSize: '0.7rem'
              }}
            >
              AI-Powered Banking
            </Typography>
          )}
        </Box>
      )}
    </Box>
  );
};

export default Logo;
