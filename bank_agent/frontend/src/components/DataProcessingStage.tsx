import React, { useState, useEffect } from 'react';
import DataSimulationStudio from './DataSimulationStudio';
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
  Timeline as TimelineIcon,
  Save as SaveIcon,
  Folder as FolderIcon,
  Delete as DeleteIcon
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
  strategy_focus?: string;
  risk_profile?: string;
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

  // Strategy management state
  const [strategies, setStrategies] = useState<any[]>([]);
  const [selectedStrategy, setSelectedStrategy] = useState<string>('');
  const [saveStrategyDialogOpen, setSaveStrategyDialogOpen] = useState(false);
  const [strategyToSave, setStrategyToSave] = useState({
    name: '',
    description: '',
    tags: [] as string[]
  });
  const [showDataSimulationStudio, setShowDataSimulationStudio] = useState(false);

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

  const personalizeStrategy = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Pass current steps for personalization
      const response = await apiService.generateInvestigationPlan({
        customerId,
        customerName,
        customerData,
        reportId,
        currentSteps: investigationPlan // Pass current steps for LLM personalization
      });
      
      if (response.success) {
        setInvestigationPlan(response.data.steps || []);
        setSelectedSteps(new Set()); // Clear selections
      } else {
        setError(response.error || 'Failed to personalize strategy');
      }
    } catch (err) {
      setError('Failed to personalize strategy');
      console.error('Error personalizing strategy:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    generateInvestigationPlan();
    loadStrategies();
  }, []);

  const loadStrategies = async () => {
    try {
      const response = await apiService.getStrategies();
      if (response.success) {
        setStrategies(response.strategies || []);
      }
    } catch (error) {
      console.error('Error loading strategies:', error);
    }
  };

  const handleSaveStrategy = async () => {
    if (!strategyToSave.name.trim()) {
      setError('Strategy name is required');
      return;
    }

    try {
      const strategyData = {
        name: strategyToSave.name,
        description: strategyToSave.description,
        strategy_focus: investigationPlan[0]?.strategy_focus || 'standard_analysis',
        risk_profile: investigationPlan[0]?.risk_profile || 'medium_risk',
        steps: investigationPlan,
        tags: strategyToSave.tags
      };

      const response = await apiService.createStrategy(strategyData);
      if (response.success) {
        setSaveStrategyDialogOpen(false);
        setStrategyToSave({ name: '', description: '', tags: [] });
        await loadStrategies(); // Reload strategies
        setError('');
      } else {
        setError(response.error || 'Failed to save strategy');
      }
    } catch (error) {
      setError('Error saving strategy');
    }
  };

  const handleLoadStrategy = async (strategyId: string) => {
    try {
      const response = await apiService.getStrategy(strategyId);
      if (response.success && response.strategy) {
        setInvestigationPlan(response.strategy.steps);
        setSelectedSteps(new Set()); // Clear selections
        setSelectedStrategy(strategyId);
        setError('');
      } else {
        setError('Failed to load strategy');
      }
    } catch (error) {
      setError('Error loading strategy');
    }
  };

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
    if (selectedSteps.size === 0) {
      setError('Please select at least one step to proceed');
      return;
    }
    
    const selectedStepData = investigationPlan.filter(step => selectedSteps.has(step.id));
    setShowDataSimulationStudio(true);
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
        <Box>
          <Typography variant="h6" sx={{ color: theme.colors.text }}>
            Investigation Strategy & Analysis Plan
          </Typography>
          {investigationPlan.length > 0 && (
            <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
              <Chip
                label={`${investigationPlan[0]?.strategy_focus?.replace('_', ' ').toUpperCase() || 'STANDARD'} STRATEGY`}
                color="primary"
                size="small"
                variant="outlined"
              />
              <Chip
                label={`${investigationPlan[0]?.risk_profile?.replace('_', ' ').toUpperCase() || 'MEDIUM'} RISK`}
                color={investigationPlan[0]?.risk_profile === 'high_risk' ? 'error' : investigationPlan[0]?.risk_profile === 'low_risk' ? 'success' : 'warning'}
                size="small"
                variant="outlined"
              />
            </Box>
          )}
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            onClick={personalizeStrategy}
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : <AssessmentIcon />}
          >
            {loading ? 'Personalizing...' : 'Personalize Strategy'}
          </Button>
          <Button
            variant="outlined"
            onClick={() => setAddStepDialogOpen(true)}
            startIcon={<AssessmentIcon />}
          >
            Add Custom Step
          </Button>
          <Button
            variant="outlined"
            onClick={() => setSaveStrategyDialogOpen(true)}
            startIcon={<SaveIcon />}
            disabled={investigationPlan.length === 0}
          >
            Save Strategy
          </Button>
        </Box>
      </Box>

      {/* Strategy Selection */}
      {strategies.length > 0 && (
        <Box sx={{ mb: 3, p: 2, backgroundColor: 'rgba(255, 255, 255, 0.05)', borderRadius: 1 }}>
          <Typography variant="subtitle1" sx={{ color: theme.colors.text, mb: 1 }}>
            Load Saved Strategy
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
            <FormControl sx={{ minWidth: 300 }}>
              <InputLabel sx={{ color: theme.colors.textSecondary }}>Select Strategy</InputLabel>
              <Select
                value={selectedStrategy}
                onChange={(e) => handleLoadStrategy(e.target.value)}
                sx={{ 
                  color: theme.colors.text,
                  '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255, 255, 255, 0.2)' },
                  '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255, 255, 255, 0.3)' }
                }}
              >
                <MenuItem value="">
                  <em>Choose a saved strategy...</em>
                </MenuItem>
                {strategies.map((strategy) => (
                  <MenuItem key={strategy.strategy_id} value={strategy.strategy_id}>
                    <Box>
                      <Typography variant="body2" sx={{ color: theme.colors.text }}>
                        {strategy.name}
                      </Typography>
                      <Typography variant="caption" sx={{ color: theme.colors.textSecondary }}>
                        {strategy.strategy_focus?.replace('_', ' ')} • {strategy.risk_profile?.replace('_', ' ')} • {strategy.steps?.length || 0} steps
                      </Typography>
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            {selectedStrategy && (
              <Button
                variant="outlined"
                size="small"
                onClick={() => setSelectedStrategy('')}
                startIcon={<DeleteIcon />}
              >
                Clear
              </Button>
            )}
          </Box>
        </Box>
      )}

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

      {/* Save Strategy Dialog */}
      <Dialog 
        open={saveStrategyDialogOpen} 
        onClose={() => setSaveStrategyDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle sx={{ backgroundColor: theme.colors.background, color: theme.colors.text }}>
          Save Investigation Strategy
        </DialogTitle>
        <DialogContent sx={{ backgroundColor: theme.colors.background }}>
          <Box sx={{ pt: 2 }}>
            <TextField
              fullWidth
              label="Strategy Name"
              value={strategyToSave.name}
              onChange={(e) => setStrategyToSave({ ...strategyToSave, name: e.target.value })}
              sx={{ mb: 2 }}
              required
            />
            <TextField
              fullWidth
              label="Description (Optional)"
              value={strategyToSave.description}
              onChange={(e) => setStrategyToSave({ ...strategyToSave, description: e.target.value })}
              multiline
              rows={3}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Tags (comma-separated)"
              value={strategyToSave.tags.join(', ')}
              onChange={(e) => setStrategyToSave({ 
                ...strategyToSave, 
                tags: e.target.value.split(',').map(tag => tag.trim()).filter(tag => tag)
              })}
              placeholder="e.g., high-risk, credit-limit, self-employed"
              sx={{ mb: 2 }}
            />
            <Box sx={{ p: 2, backgroundColor: 'rgba(255, 255, 255, 0.05)', borderRadius: 1 }}>
              <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 1 }}>
                Strategy Details:
              </Typography>
              <Typography variant="body2" sx={{ color: theme.colors.text }}>
                • Focus: {investigationPlan[0]?.strategy_focus?.replace('_', ' ').toUpperCase() || 'STANDARD'}
              </Typography>
              <Typography variant="body2" sx={{ color: theme.colors.text }}>
                • Risk Profile: {investigationPlan[0]?.risk_profile?.replace('_', ' ').toUpperCase() || 'MEDIUM'}
              </Typography>
              <Typography variant="body2" sx={{ color: theme.colors.text }}>
                • Steps: {investigationPlan.length}
              </Typography>
            </Box>
          </Box>
        </DialogContent>
        <DialogActions sx={{ backgroundColor: theme.colors.background }}>
          <Button onClick={() => setSaveStrategyDialogOpen(false)} sx={{ color: theme.colors.textSecondary }}>
            Cancel
          </Button>
          <Button 
            onClick={handleSaveStrategy}
            variant="contained"
            disabled={!strategyToSave.name.trim()}
          >
            Save Strategy
          </Button>
        </DialogActions>
      </Dialog>

      {/* Data Simulation Studio */}
      {showDataSimulationStudio && (
        <DataSimulationStudio
          customerId={customerId}
          customerName={customerName}
          reportId={reportId || undefined}
          selectedSteps={investigationPlan.filter(step => selectedSteps.has(step.id))}
          onClose={() => setShowDataSimulationStudio(false)}
        />
      )}
    </Box>
  );
};

export default DataProcessingStage;
