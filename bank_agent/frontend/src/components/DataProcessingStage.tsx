import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Button,
  Alert,
  CircularProgress,
  Divider,
  Chip
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Search as SearchIcon,
  Storage as StorageIcon,
  Assessment as AssessmentIcon,
  TrendingUp as TrendingUpIcon,
  Analytics as AnalyticsIcon,
  Timeline as TimelineIcon
} from '@mui/icons-material';
import { useTheme } from '../contexts/ThemeContext';
import apiService from '../services/api';

interface DataProcessingStageProps {
  customerId: number;
  customerName: string;
  customerData: any;
  reportId: string | null;
  reportData?: any;
  onClose: () => void;
}

interface InvestigationStep {
  id: string;
  title: string;
  description: string;
  category: 'data_collection' | 'analysis' | 'scenario' | 'visualization';
  priority: 'high' | 'medium' | 'low';
  estimatedTime: string;
}

const DataProcessingStage: React.FC<DataProcessingStageProps> = ({
  customerId,
  customerName,
  customerData,
  reportId,
  reportData,
  onClose
}) => {
  const { theme } = useTheme();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [investigationPlan, setInvestigationPlan] = useState<InvestigationStep[]>([]);

  // Steps taken so far
  const stepsTaken = [
    {
      label: 'Customer Search & Verification',
      description: `Searched for customer "${customerName}" (ID: ${customerId}) and verified their identity`,
      icon: <SearchIcon />,
      completed: true
    },
    {
      label: 'Initial Data Pull',
      description: 'Retrieved comprehensive customer data from multiple sources including banking, credit bureau, and demographic information',
      icon: <StorageIcon />,
      completed: true
    },
    {
      label: 'Report Created',
      description: reportData ? 
        `Created ${reportData.inquiry_type.replace(/_/g, ' ').toLowerCase()} report: "${reportData.inquiry_description}"` :
        'Report created with initial analysis',
      icon: <AssessmentIcon />,
      completed: true
    },
    {
      label: 'AI Recommendation Generated',
      description: reportData?.ai_recommendation ? 
        'Generated AI recommendation based on customer profile and credit request analysis' :
        'AI recommendation available for review',
      icon: <AssessmentIcon />,
      completed: true
    }
  ];

  // Generate investigation plan
  const generateInvestigationPlan = async () => {
    try {
      setLoading(true);
      setError('');
      
      const response = await apiService.generateInvestigationPlan({
        customerId,
        customerName,
        customerData,
        reportId
      });
      
      if (response.success) {
        setInvestigationPlan(response.data.steps || []);
      } else {
        setError(response.error || 'Failed to generate investigation plan');
      }
    } catch (err) {
      setError('Failed to generate investigation plan');
      console.error('Error generating investigation plan:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    generateInvestigationPlan();
  }, []);

  const getStepIcon = (category: string) => {
    switch (category) {
      case 'data_collection':
        return <StorageIcon />;
      case 'analysis':
        return <AnalyticsIcon />;
      case 'scenario':
        return <TimelineIcon />;
      case 'visualization':
        return <TrendingUpIcon />;
      default:
        return <AssessmentIcon />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'info';
      default:
        return 'default';
    }
  };

  return (
    <Box sx={{ mt: 1 }}>
      {/* Selected Report Info */}
      {reportData && (
        <Card sx={{ 
          mb: 3, 
          backgroundColor: 'rgba(255, 255, 255, 0.05)', 
          border: '1px solid rgba(255, 255, 255, 0.1)' 
        }}>
          <CardContent>
            <Typography variant="h6" sx={{ color: theme.colors.text, mb: 2 }}>
              Selected Report for Analysis
            </Typography>
            <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 2 }}>
              <Box>
                <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 0.5 }}>
                  Report Type
                </Typography>
                <Typography variant="body1" sx={{ color: theme.colors.text }}>
                  {reportData.inquiry_type.replace(/_/g, ' ').toUpperCase()}
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 0.5 }}>
                  Status
                </Typography>
                <Chip
                  label={reportData.status.replace(/_/g, ' ').toUpperCase()}
                  color={reportData.status === 'pending' ? 'warning' : 'success'}
                  size="small"
                />
              </Box>
              <Box>
                <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 0.5 }}>
                  Created
                </Typography>
                <Typography variant="body1" sx={{ color: theme.colors.text }}>
                  {new Date(reportData.created_at).toLocaleDateString()}
                </Typography>
              </Box>
            </Box>
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 0.5 }}>
                Description
              </Typography>
              <Typography variant="body1" sx={{ color: theme.colors.text }}>
                {reportData.inquiry_description}
              </Typography>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Steps Taken So Far */}
      <Typography variant="h6" sx={{ color: theme.colors.text, mb: 2 }}>
        Steps Completed
      </Typography>
      <Stepper orientation="vertical" sx={{ mb: 4 }}>
        {stepsTaken.map((step, index) => (
          <Step key={index} active={step.completed} completed={step.completed}>
            <StepLabel
              icon={step.completed ? <CheckCircleIcon color="success" /> : step.icon}
              sx={{ color: theme.colors.text }}
            >
              {step.label}
            </StepLabel>
            <StepContent>
              <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 2 }}>
                {step.description}
              </Typography>
            </StepContent>
          </Step>
        ))}
      </Stepper>

      <Divider sx={{ my: 3 }} />

      {/* Investigation Plan */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" sx={{ color: theme.colors.text }}>
          Investigation Plan for Further Analysis
        </Typography>
        <Button
          variant="outlined"
          onClick={generateInvestigationPlan}
          disabled={loading}
          startIcon={loading ? <CircularProgress size={20} /> : <AssessmentIcon />}
        >
          {loading ? 'Generating...' : 'Regenerate Plan'}
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2, backgroundColor: 'rgba(255, 255, 255, 0.05)' }}>
          {error}
        </Alert>
      )}

      {loading && !investigationPlan.length ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: 2 }}>
          {investigationPlan.map((step, index) => (
            <Card key={step.id} sx={{ 
              backgroundColor: 'rgba(255, 255, 255, 0.05)', 
              border: '1px solid rgba(255, 255, 255, 0.1)',
              height: '100%'
            }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1, mb: 2 }}>
                  {getStepIcon(step.category)}
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="h6" sx={{ color: theme.colors.text, mb: 1 }}>
                      {step.title}
                    </Typography>
                    <Chip
                      label={step.priority.toUpperCase()}
                      color={getPriorityColor(step.priority) as any}
                      size="small"
                      sx={{ mb: 1 }}
                    />
                    <Chip
                      label={step.estimatedTime}
                      variant="outlined"
                      size="small"
                      sx={{ ml: 1 }}
                    />
                  </Box>
                </Box>
                <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                  {step.description}
                </Typography>
              </CardContent>
            </Card>
          ))}
        </Box>
      )}

      {/* Action Buttons */}
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2, mt: 3 }}>
        <Button onClick={onClose} variant="outlined">
          Close
        </Button>
        <Button
          variant="contained"
          onClick={() => {
            // TODO: Navigate to next stage (scenario analysis, graphs, etc.)
            console.log('Proceeding to next stage...');
          }}
          startIcon={<TrendingUpIcon />}
          sx={{ 
            backgroundColor: theme.colors.primary,
            '&:hover': { backgroundColor: theme.colors.primaryDark }
          }}
        >
          Proceed to Scenario Analysis
        </Button>
      </Box>
    </Box>
  );
};

export default DataProcessingStage;
