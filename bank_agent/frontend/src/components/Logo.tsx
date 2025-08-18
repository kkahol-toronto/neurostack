import React from 'react';
import { Box, Typography } from '@mui/material';
import { AccountBalance as BankIcon } from '@mui/icons-material';

const Logo: React.FC = () => {
  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: 1,
        backgroundColor: '#1976d2',
        borderRadius: 2,
        px: 2,
        py: 1,
        color: 'white'
      }}
    >
      <BankIcon sx={{ fontSize: 28 }} />
      <Box>
        <Typography variant="h5" component="div" sx={{ fontWeight: 600 }}>
          Credit Limit Agent
        </Typography>
        <Typography variant="caption" sx={{ opacity: 0.8, fontSize: '0.7rem' }}>
          AI-Powered Banking
        </Typography>
      </Box>
    </Box>
  );
};

export default Logo;
