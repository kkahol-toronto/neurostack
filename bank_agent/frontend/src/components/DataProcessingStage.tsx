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
  Chip,
  Checkbox,
  FormControlLabel,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem
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
  const [selectedSteps, setSelectedSteps] = useState<Set<string>>(new Set());
  const [addStepDialogOpen, setAddStepDialogOpen] = useState(false);
  const [newStep, setNewStep] = useState({
    title: '',
    description: '',
    category: 'analysis' as 'data_collection' | 'analysis' | 'scenario' | 'visualization',
    priority: 'medium' as 'high' | 'medium' | 'low',
    estimatedTime: '15-20 min'
  });

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

  // Generate investigation strategy
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
        setError(response.error || 'Failed to generate investigation strategy');
      }
    } catch (err) {
      setError('Failed to generate investigation strategy');
      console.error('Error generating investigation strategy:', err);
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

  const handleStepSelection = (stepId: string, checked: boolean) => {
    const newSelectedSteps = new Set(selectedSteps);
    if (checked) {
      newSelectedSteps.add(stepId);
    } else {
      newSelectedSteps.delete(stepId);
    }
    setSelectedSteps(newSelectedSteps);
  };

  const handleSelectAll = () => {
    if (selectedSteps.size === investigationPlan.length) {
      setSelectedSteps(new Set());
    } else {
      setSelectedSteps(new Set(Array.from(investigationPlan.map(step => step.id))));
    }
  };

  const handleAddCustomStep = () => {
    if (newStep.title && newStep.description) {
      const customStep: InvestigationStep = {
        id: `custom_${Date.now()}`,
        ...newStep
      };
      setInvestigationPlan(prev => [...prev, customStep]);
      setSelectedSteps(prev => new Set([...Array.from(prev), customStep.id]));
      setAddStepDialogOpen(false);
      setNewStep({
        title: '',
        description: '',
        category: 'analysis',
        priority: 'medium',
        estimatedTime: '15-20 min'
      });
    }
  };

  const handleProceedToNextStage = () => {
    const selectedStepData = investigationPlan.filter(step => selectedSteps.has(step.id));
    console.log('Selected steps for next stage:', selectedStepData);
    // TODO: Navigate to next stage with selected steps
    onClose();
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

      {/* Investigation Strategy */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" sx={{ color: theme.colors.text }}>
          Investigation Strategy & Analysis Plan
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            onClick={generateInvestigationPlan}
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : <AssessmentIcon />}
          >
            {loading ? 'Generating...' : 'Regenerate Strategy'}
          </Button>
          <Button
            variant="outlined"
            onClick={() => setAddStepDialogOpen(true)}
            startIcon={<AssessmentIcon />}
          >
            Add Custom Step
          </Button>
        </Box>
      </Box>

      {/* Selection Controls */}
      {investigationPlan.length > 0 && (
        <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <FormControlLabel
            control={
              <Checkbox
                checked={selectedSteps.size === investigationPlan.length && investigationPlan.length > 0}
                indeterminate={selectedSteps.size > 0 && selectedSteps.size < investigationPlan.length}
                onChange={handleSelectAll}
              />
            }
            label={`Select All (${selectedSteps.size}/${investigationPlan.length} selected)`}
            sx={{ color: theme.colors.text }}
          />
          <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
            Select the steps you want to proceed with
          </Typography>
        </Box>
      )}

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
              backgroundColor: selectedSteps.has(step.id) ? 'rgba(255, 255, 255, 0.1)' : 'rgba(255, 255, 255, 0.05)', 
              border: selectedSteps.has(step.id) ? '2px solid rgba(255, 255, 255, 0.3)' : '1px solid rgba(255, 255, 255, 0.1)',
              height: '100%',
              transition: 'all 0.2s ease-in-out'
            }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1, mb: 2 }}>
                  <Checkbox
                    checked={selectedSteps.has(step.id)}
                    onChange={(e) => handleStepSelection(step.id, e.target.checked)}
                    sx={{ 
                      color: theme.colors.primary,
                      '&.Mui-checked': { color: theme.colors.primary }
                    }}
                  />
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
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 3 }}>
        <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
          {selectedSteps.size > 0 ? `${selectedSteps.size} step(s) selected` : 'No steps selected'}
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button onClick={onClose} variant="outlined">
            Close
          </Button>
          <Button
            variant="contained"
            onClick={handleProceedToNextStage}
            disabled={selectedSteps.size === 0}
            startIcon={<TrendingUpIcon />}
            sx={{ 
              backgroundColor: theme.colors.primary,
              '&:hover': { backgroundColor: theme.colors.primaryDark }
            }}
          >
            Proceed with Selected Steps ({selectedSteps.size})
          </Button>
        </Box>
      </Box>

      {/* Add Custom Step Dialog */}
      <Dialog
        open={addStepDialogOpen}
        onClose={() => setAddStepDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle sx={{ color: theme.colors.text }}>
          Add Custom Investigation Step
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 2, mt: 1 }}>
            <TextField
              fullWidth
              label="Step Title"
              value={newStep.title}
              onChange={(e) => setNewStep(prev => ({ ...prev, title: e.target.value }))}
              placeholder="e.g., Industry Trend Analysis"
              sx={{ gridColumn: '1 / -1' }}
            />
            
            <TextField
              fullWidth
              label="Step Description"
              value={newStep.description}
              onChange={(e) => setNewStep(prev => ({ ...prev, description: e.target.value }))}
              multiline
              rows={3}
              placeholder="Describe what this step involves..."
              sx={{ gridColumn: '1 / -1' }}
            />
            
            <FormControl fullWidth>
              <InputLabel>Category</InputLabel>
              <Select
                value={newStep.category}
                onChange={(e) => setNewStep(prev => ({ ...prev, category: e.target.value as any }))}
                label="Category"
              >
                <MenuItem value="data_collection">Data Collection</MenuItem>
                <MenuItem value="analysis">Analysis</MenuItem>
                <MenuItem value="scenario">Scenario Modeling</MenuItem>
                <MenuItem value="visualization">Visualization</MenuItem>
              </Select>
            </FormControl>
            
            <FormControl fullWidth>
              <InputLabel>Priority</InputLabel>
              <Select
                value={newStep.priority}
                onChange={(e) => setNewStep(prev => ({ ...prev, priority: e.target.value as any }))}
                label="Priority"
              >
                <MenuItem value="high">High</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="low">Low</MenuItem>
              </Select>
            </FormControl>
            
            <TextField
              fullWidth
              label="Estimated Time"
              value={newStep.estimatedTime}
              onChange={(e) => setNewStep(prev => ({ ...prev, estimatedTime: e.target.value }))}
              placeholder="e.g., 15-20 min"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddStepDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleAddCustomStep}
            variant="contained"
            disabled={!newStep.title || !newStep.description}
          >
            Add Step
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DataProcessingStage;
