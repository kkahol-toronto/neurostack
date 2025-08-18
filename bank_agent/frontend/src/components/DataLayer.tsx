import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const DataLayer: React.FC = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Data Layer
      </Typography>
      <Typography variant="body1" color="text.secondary" gutterBottom>
        Select data sources for credit limit decisions
      </Typography>
      
      <Paper sx={{ p: 3, mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          Data Sources
        </Typography>
        <Typography variant="body2" color="text.secondary">
          • Customer Demographics
        </Typography>
        <Typography variant="body2" color="text.secondary">
          • Internal Banking Data
        </Typography>
        <Typography variant="body2" color="text.secondary">
          • Credit Bureau Data
        </Typography>
        <Typography variant="body2" color="text.secondary">
          • Income & Ability-to-Pay
        </Typography>
        <Typography variant="body2" color="text.secondary">
          • Open Banking Data
        </Typography>
        <Typography variant="body2" color="text.secondary">
          • Fraud/KYC/Compliance
        </Typography>
        <Typography variant="body2" color="text.secondary">
          • Economic Indicators
        </Typography>
      </Paper>
    </Box>
  );
};

export default DataLayer;
