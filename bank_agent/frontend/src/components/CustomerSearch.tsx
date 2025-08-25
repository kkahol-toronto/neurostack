import React, { useState } from 'react';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Chip,
  Alert,
  CircularProgress,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio
} from '@mui/material';
import {
  Search as SearchIcon,
  Person as PersonIcon,
  Security as SecurityIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon
} from '@mui/icons-material';
import { useTheme } from '../contexts/ThemeContext';
import apiService from '../services/api';

interface Customer {
  customer_id: number;
  first_name: string;
  last_name: string;
  annual_income?: number;
  state?: string;
  date_of_birth?: string;
  employment_status?: string;
  customer_segment?: string;
  // Additional fields for display and verification
  address?: string;
  phone?: string;
  email?: string;
  ssn?: string;
  accountNumber?: string;
  securityQuestions?: SecurityQuestion[];
}

interface SecurityQuestion {
  id: string;
  question: string;
  answer: string;
  type: 'personal' | 'financial' | 'address';
}

interface CustomerSearchProps {
  onCustomerVerified?: (customer: Customer) => void;
  onNavigateToDataSources?: () => void;
}

const CustomerSearch: React.FC<CustomerSearchProps> = ({ onCustomerVerified, onNavigateToDataSources }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Customer[]>([]);
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [verificationDialogOpen, setVerificationDialogOpen] = useState(false);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<string[]>([]);
  const [verificationStep, setVerificationStep] = useState<'questions' | 'success' | 'failed'>('questions');
  const [isSearching, setIsSearching] = useState(false);
  const [selectedQuestions, setSelectedQuestions] = useState<SecurityQuestion[]>([]);
  const { theme } = useTheme();



  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }

    setIsSearching(true);
    console.log('Searching for:', searchQuery);

    try {
      // Call the backend API
      const result = await apiService.searchCustomers(searchQuery);
      
      if (result.success) {
        console.log('Search results from API:', result.customers);
        setSearchResults(result.customers);
      } else {
        console.error('Search failed:', result.error);
        setSearchResults([]);
      }
    } catch (error) {
      console.error('Search error:', error);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const handleCustomerSelect = (customer: Customer) => {
    // Generate default security questions for backend customers
    const defaultQuestions: SecurityQuestion[] = [
      {
        id: '1',
        question: 'What is the last 4 digits of your customer ID?',
        answer: customer.customer_id.toString().slice(-4),
        type: 'financial'
      },
      {
        id: '2',
        question: 'What state do you live in?',
        answer: customer.state || 'Unknown',
        type: 'personal'
      },
      {
        id: '3',
        question: 'What is your annual income range?',
        answer: customer.annual_income ? `${Math.floor(customer.annual_income / 10000) * 10000}-${Math.floor(customer.annual_income / 10000) * 10000 + 9999}` : 'Unknown',
        type: 'financial'
      }
    ];
    
    // Generate questions once and store them
    const shuffled = [...defaultQuestions].sort(() => 0.5 - Math.random());
    const questions = shuffled.slice(0, 2);
    
    console.log('Selected questions for verification:', questions);
    
    setSelectedCustomer(customer);
    setSelectedQuestions(questions);
    setCurrentQuestionIndex(0);
    
    // Pre-select the correct answers for the agent
    const correctAnswers = questions.map(q => q.answer);
    setSelectedAnswers(correctAnswers);
    
    setVerificationStep('questions');
    setVerificationDialogOpen(true);
  };

  const handleAnswerSelect = (answer: string) => {
    console.log('Answer selected:', answer, 'for question:', currentQuestionIndex);
    const newAnswers = [...selectedAnswers];
    newAnswers[currentQuestionIndex] = answer;
    setSelectedAnswers(newAnswers);
    console.log('Updated answers:', newAnswers);
  };

  const handleNextQuestion = () => {
    console.log('Current question index:', currentQuestionIndex);
    console.log('Selected answers:', selectedAnswers);
    console.log('Selected questions:', selectedQuestions);
    
    if (currentQuestionIndex < 1) { // Only 2 questions (index 0 and 1)
      console.log('Moving to next question');
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    } else {
      console.log('Verifying answers...');
      // Verify answers
      const isCorrect = selectedAnswers.every((answer, index) => {
        const question = selectedQuestions[index];
        const isAnswerCorrect = question && answer === question.answer;
        console.log(`Question ${index}: Expected "${question?.answer}", Got "${answer}", Correct: ${isAnswerCorrect}`);
        return isAnswerCorrect;
      });
      
      console.log('Verification result:', isCorrect);
      setVerificationStep(isCorrect ? 'success' : 'failed');
      
      // If verification is successful, notify parent component
      if (isCorrect && selectedCustomer && onCustomerVerified) {
        onCustomerVerified(selectedCustomer);
      }
    }
  };

  const handleCloseDialog = () => {
    setVerificationDialogOpen(false);
    setSelectedQuestions([]);
    setCurrentQuestionIndex(0);
    setSelectedAnswers([]);
    setVerificationStep('questions');
    
    // If verification was successful, navigate to Data Sources
    if (verificationStep === 'success' && selectedCustomer && onNavigateToDataSources) {
      onNavigateToDataSources();
    } else {
      // Reset customer selection only if verification failed or was cancelled
      setSelectedCustomer(null);
    }
  };

  const getRandomQuestions = (customer: Customer) => {
    // This function is no longer used since we generate questions dynamically
    // in handleCustomerSelect, but keeping it for potential future use
    return [];
  };

  const generateAnswerOptions = (correctAnswer: string, questionType: string) => {
    const options = [correctAnswer];
    
    // Generate wrong answers based on question type
    if (questionType === 'personal') {
      const personalOptions = ['Red', 'Green', 'Yellow', 'Black', 'White', 'Purple', 'Orange', 'Pink'];
      const wrongOptions = personalOptions.filter(option => option !== correctAnswer);
      options.push(...wrongOptions.sort(() => 0.5 - Math.random()).slice(0, 3));
    } else if (questionType === 'financial') {
      const financialOptions = ['1234', '5678', '9999', '0000', '1111', '2222', '3333', '4444'];
      const wrongOptions = financialOptions.filter(option => option !== correctAnswer);
      options.push(...wrongOptions.sort(() => 0.5 - Math.random()).slice(0, 3));
    } else {
      // Generic wrong answers
      const genericOptions = ['Option A', 'Option B', 'Option C', 'Option D'];
      options.push(...genericOptions.slice(0, 3));
    }
    
    return options.sort(() => 0.5 - Math.random()); // Shuffle all options
  };

  const currentAnswerOptions = selectedQuestions[currentQuestionIndex] 
    ? generateAnswerOptions(
        selectedQuestions[currentQuestionIndex].answer, 
        selectedQuestions[currentQuestionIndex].type
      ) 
    : [];

  return (
    <Box sx={{ p: 3 }}>
      <Paper sx={{ 
        p: 4, 
        backgroundColor: 'rgba(255, 255, 255, 0.1)',
        backdropFilter: 'blur(10px)',
        border: `1px solid rgba(255, 255, 255, 0.2)`,
        borderRadius: 3,
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)'
      }}>
        {/* Header */}
        <Box display="flex" alignItems="center" gap={2} mb={3}>
          <SearchIcon sx={{ fontSize: 32, color: theme.colors.primary }} />
          <Box>
            <Typography variant="h4" sx={{ 
              color: theme.colors.text,
              fontWeight: 700
            }}>
              Customer Search
            </Typography>
            <Typography variant="body1" sx={{ 
              color: theme.colors.textSecondary
            }}>
              Search for customers by name, address, phone, or email
            </Typography>
          </Box>
        </Box>

        {/* Search Bar */}
        <Box display="flex" gap={2} mb={3}>
          <TextField
            fullWidth
            placeholder="Enter customer name, address, phone, or email..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            sx={{
              '& .MuiOutlinedInput-root': {
                backgroundColor: 'rgba(255, 255, 255, 0.05)',
                '& fieldset': {
                  borderColor: 'rgba(255, 255, 255, 0.2)',
                },
                '&:hover fieldset': {
                  borderColor: 'rgba(255, 255, 255, 0.3)',
                },
                '&.Mui-focused fieldset': {
                  borderColor: theme.colors.primary,
                },
                '& input': {
                  color: theme.colors.text,
                },
                '& input::placeholder': {
                  color: theme.colors.textSecondary,
                  opacity: 0.7,
                },
              },
            }}
          />
          <Button
            variant="contained"
            onClick={handleSearch}
            disabled={isSearching || !searchQuery.trim()}
            sx={{
              backgroundColor: theme.colors.primary,
              '&:hover': {
                backgroundColor: theme.colors.primaryDark,
              },
              minWidth: 120,
            }}
          >
            {isSearching ? <CircularProgress size={20} /> : 'Search'}
          </Button>
        </Box>
        
        {/* Demo Search Buttons */}
        <Box display="flex" gap={1} mb={3} flexWrap="wrap">
          <Typography variant="body2" sx={{ 
            color: theme.colors.textSecondary,
            mr: 1,
            alignSelf: 'center'
          }}>
            Try searching for:
          </Typography>
          <Button
            size="small"
            variant="outlined"
            onClick={async () => {
              setSearchQuery('John');
              await new Promise(resolve => setTimeout(resolve, 100));
              handleSearch();
            }}
            sx={{
              borderColor: 'rgba(255, 255, 255, 0.3)',
              color: theme.colors.text,
              '&:hover': {
                borderColor: theme.colors.primary,
                backgroundColor: 'rgba(255, 255, 255, 0.05)'
              }
            }}
          >
            John
          </Button>
          <Button
            size="small"
            variant="outlined"
            onClick={async () => {
              setSearchQuery('Sarah');
              await new Promise(resolve => setTimeout(resolve, 100));
              handleSearch();
            }}
            sx={{
              borderColor: 'rgba(255, 255, 255, 0.3)',
              color: theme.colors.text,
              '&:hover': {
                borderColor: theme.colors.primary,
                backgroundColor: 'rgba(255, 255, 255, 0.05)'
              }
            }}
          >
            Sarah
          </Button>
          <Button
            size="small"
            variant="outlined"
            onClick={async () => {
              setSearchQuery('Michael');
              await new Promise(resolve => setTimeout(resolve, 100));
              handleSearch();
            }}
            sx={{
              borderColor: 'rgba(255, 255, 255, 0.3)',
              color: theme.colors.text,
              '&:hover': {
                borderColor: theme.colors.primary,
                backgroundColor: 'rgba(255, 255, 255, 0.05)'
              }
            }}
          >
            Michael
          </Button>
          <Button
            size="small"
            variant="outlined"
            onClick={async () => {
              setSearchQuery('New York');
              await new Promise(resolve => setTimeout(resolve, 100));
              handleSearch();
            }}
            sx={{
              borderColor: 'rgba(255, 255, 255, 0.3)',
              color: theme.colors.text,
              '&:hover': {
                borderColor: theme.colors.primary,
                backgroundColor: 'rgba(255, 255, 255, 0.05)'
              }
            }}
          >
            New York
          </Button>
        </Box>

        {/* Search Results */}
        {searchResults.length > 0 && (
          <Box>
            <Typography variant="h6" sx={{ 
              color: theme.colors.text,
              mb: 2
            }}>
              Search Results ({searchResults.length})
            </Typography>
            <List>
              {searchResults.map((customer) => (
                <ListItem
                  key={customer.customer_id}
                  sx={{
                    backgroundColor: 'rgba(255, 255, 255, 0.05)',
                    borderRadius: 2,
                    mb: 1,
                    cursor: 'pointer',
                    '&:hover': {
                      backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    },
                  }}
                  onClick={() => handleCustomerSelect(customer)}
                >
                  <ListItemAvatar>
                    <Avatar sx={{ backgroundColor: theme.colors.primary }}>
                      <PersonIcon />
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText
                    primary={`${customer.first_name} ${customer.last_name}`}
                    secondary={
                      <Box>
                        <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                          {customer.address}
                        </Typography>
                        <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                          {customer.phone} • {customer.email}
                        </Typography>
                      </Box>
                    }
                  />
                  <Chip
                    label="Select"
                    color="primary"
                    size="small"
                    sx={{ backgroundColor: theme.colors.primary }}
                  />
                </ListItem>
              ))}
            </List>
          </Box>
        )}

        {/* No Results */}
        {searchResults.length === 0 && searchQuery && !isSearching && (
          <Alert severity="info" sx={{ 
            backgroundColor: 'rgba(255, 255, 255, 0.05)',
            color: theme.colors.textSecondary
          }}>
            No customers found matching your search criteria.
          </Alert>
        )}
      </Paper>

      {/* Identity Verification Dialog */}
      <Dialog
        open={verificationDialogOpen}
        onClose={handleCloseDialog}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(10px)',
            borderRadius: 3,
          }
        }}
      >
        <DialogTitle sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: 2,
          color: theme.colors.text
        }}>
          <SecurityIcon sx={{ color: theme.colors.primary }} />
          Identity Verification
        </DialogTitle>
        
        <DialogContent>
          {verificationStep === 'questions' && selectedCustomer && (
            <Box>
                             <Typography variant="body1" sx={{ 
                 color: theme.colors.text,
                 mb: 3
               }}>
                 Verify customer identity for <strong>{selectedCustomer.first_name} {selectedCustomer.last_name}</strong> by confirming their responses to 2 security questions.
               </Typography>
               
               <Box sx={{ 
                 backgroundColor: 'rgba(255, 255, 255, 0.05)', 
                 p: 2, 
                 borderRadius: 2, 
                 mb: 3 
               }}>
                 <Typography variant="body2" sx={{ 
                   color: theme.colors.textSecondary,
                   textAlign: 'center'
                 }}>
                   Question {currentQuestionIndex + 1} of 2 • {selectedAnswers.filter(a => a).length} confirmed
                 </Typography>
               </Box>
              
                             <Box mb={3}>
                 <Typography variant="h6" sx={{ 
                   color: theme.colors.text,
                   mb: 2
                 }}>
                   Question {currentQuestionIndex + 1} of 2:
                 </Typography>
                 <Typography variant="body1" sx={{ 
                   color: theme.colors.text,
                   mb: 2,
                   fontStyle: 'italic'
                 }}>
                   {selectedQuestions[currentQuestionIndex]?.question}
                 </Typography>
                 
                 {selectedAnswers[currentQuestionIndex] && (
                   <Typography variant="body2" sx={{ 
                     color: 'success.main',
                     mb: 2,
                     fontWeight: 500,
                     backgroundColor: 'rgba(76, 175, 80, 0.1)',
                     p: 1,
                     borderRadius: 1,
                     border: '1px solid rgba(76, 175, 80, 0.3)'
                   }}>
                     ✅ Customer Response: {selectedAnswers[currentQuestionIndex]} (Correct Answer)
                   </Typography>
                 )}
                
                <FormControl component="fieldset" fullWidth>
                  <RadioGroup
                    value={selectedAnswers[currentQuestionIndex] || ''}
                    onChange={(e) => handleAnswerSelect(e.target.value)}
                    sx={{ width: '100%' }}
                  >
                    {currentAnswerOptions.map((option, index) => {
                      const isCorrectAnswer = option === selectedQuestions[currentQuestionIndex]?.answer;
                      return (
                        <FormControlLabel
                          key={index}
                          value={option}
                          control={
                            <Radio 
                              disabled={true}
                              sx={{
                                color: isCorrectAnswer ? 'success.main' : theme.colors.textSecondary,
                                '&.Mui-checked': {
                                  color: isCorrectAnswer ? 'success.main' : theme.colors.primary,
                                },
                                '&.Mui-disabled': {
                                  color: isCorrectAnswer ? 'success.main' : theme.colors.textSecondary,
                                }
                              }}
                            />
                          }
                          label={option}
                          sx={{ 
                            color: isCorrectAnswer ? 'success.main' : theme.colors.text,
                            mb: 2,
                            p: 1,
                            borderRadius: 1,
                            border: isCorrectAnswer ? '1px solid rgba(76, 175, 80, 0.5)' : '1px solid transparent',
                            cursor: 'default',
                            width: '100%',
                            backgroundColor: isCorrectAnswer ? 'rgba(76, 175, 80, 0.1)' : 'transparent',
                            '&:hover': {
                              backgroundColor: isCorrectAnswer ? 'rgba(76, 175, 80, 0.15)' : 'rgba(255, 255, 255, 0.05)',
                            },
                            '&.Mui-checked': {
                              backgroundColor: isCorrectAnswer ? 'rgba(76, 175, 80, 0.2)' : 'rgba(255, 255, 255, 0.1)',
                            }
                          }}
                        />
                      );
                    })}
                  </RadioGroup>
                </FormControl>
              </Box>
            </Box>
          )}
          
          {verificationStep === 'success' && selectedCustomer && (
            <Box>
              <Box textAlign="center" py={2} mb={3}>
                <CheckCircleIcon sx={{ 
                  fontSize: 64, 
                  color: 'success.main',
                  mb: 2
                }} />
                <Typography variant="h6" sx={{ 
                  color: 'success.main',
                  mb: 1
                }}>
                  Identity Verified Successfully!
                </Typography>
                <Typography variant="body1" sx={{ 
                  color: theme.colors.textSecondary
                }}>
                  Customer identity has been confirmed. You can now proceed with banking operations.
                </Typography>
              </Box>
              
              {/* Customer Profile Information */}
              <Paper sx={{ 
                p: 3, 
                backgroundColor: 'rgba(255, 255, 255, 0.05)',
                borderRadius: 2,
                border: '1px solid rgba(255, 255, 255, 0.1)'
              }}>
                <Typography variant="h6" sx={{ 
                  color: theme.colors.text,
                  mb: 2,
                  fontWeight: 600
                }}>
                  Customer Profile
                </Typography>
                
                <Box display="grid" gridTemplateColumns="repeat(auto-fit, minmax(250px, 1fr))" gap={2}>
                  <Box>
                    <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 0.5 }}>
                      Full Name
                    </Typography>
                    <Typography variant="body1" sx={{ color: theme.colors.text, fontWeight: 500 }}>
                      {selectedCustomer.first_name} {selectedCustomer.last_name}
                    </Typography>
                  </Box>
                  
                  <Box>
                    <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 0.5 }}>
                      Customer ID
                    </Typography>
                    <Typography variant="body1" sx={{ color: theme.colors.text, fontWeight: 500, fontFamily: 'monospace' }}>
                      {selectedCustomer.customer_id}
                    </Typography>
                  </Box>
                  
                  <Box>
                    <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 0.5 }}>
                      Annual Income
                    </Typography>
                    <Typography variant="body1" sx={{ color: theme.colors.text, fontWeight: 500 }}>
                      ${selectedCustomer.annual_income?.toLocaleString() || 'N/A'}
                    </Typography>
                  </Box>
                  
                  <Box>
                    <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 0.5 }}>
                      State
                    </Typography>
                    <Typography variant="body1" sx={{ color: theme.colors.text, fontWeight: 500 }}>
                      {selectedCustomer.state || 'N/A'}
                    </Typography>
                  </Box>
                  
                  <Box>
                    <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 0.5 }}>
                      Date of Birth
                    </Typography>
                    <Typography variant="body1" sx={{ color: theme.colors.text, fontWeight: 500 }}>
                      {selectedCustomer.date_of_birth ? new Date(selectedCustomer.date_of_birth).toLocaleDateString() : 'N/A'}
                    </Typography>
                  </Box>
                  
                  <Box>
                    <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 0.5 }}>
                      Employment Status
                    </Typography>
                    <Typography variant="body1" sx={{ color: theme.colors.text, fontWeight: 500 }}>
                      {selectedCustomer.employment_status || 'N/A'}
                    </Typography>
                  </Box>
                  
                  <Box>
                    <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 0.5 }}>
                      Customer Segment
                    </Typography>
                    <Typography variant="body1" sx={{ color: theme.colors.text, fontWeight: 500 }}>
                      {selectedCustomer.customer_segment || 'N/A'}
                    </Typography>
                  </Box>
                </Box>
              </Paper>
            </Box>
          )}
          
          {verificationStep === 'failed' && (
            <Box textAlign="center" py={2}>
              <CancelIcon sx={{ 
                fontSize: 64, 
                color: 'error.main',
                mb: 2
              }} />
              <Typography variant="h6" sx={{ 
                color: 'error.main',
                mb: 1
              }}>
                Identity Verification Failed
              </Typography>
              <Typography variant="body1" sx={{ 
                color: theme.colors.textSecondary
              }}>
                The provided answers do not match our records. Please try again or contact support.
              </Typography>
            </Box>
          )}
        </DialogContent>
        
        <DialogActions sx={{ p: 3 }}>
          {verificationStep === 'questions' && (
            <>
              <Button onClick={handleCloseDialog} sx={{ color: theme.colors.textSecondary }}>
                Cancel
              </Button>
              <Button
                onClick={handleNextQuestion}
                disabled={!selectedAnswers[currentQuestionIndex]}
                variant="contained"
                sx={{
                  backgroundColor: theme.colors.primary,
                  '&:hover': {
                    backgroundColor: theme.colors.primaryDark,
                  },
                }}
              >
                {currentQuestionIndex < 1 ? 'Confirm & Continue' : 'Complete Verification'}
              </Button>
            </>
          )}
          
          {verificationStep === 'success' && (
            <Button
              onClick={handleCloseDialog}
              variant="contained"
              sx={{
                backgroundColor: 'success.main',
                '&:hover': {
                  backgroundColor: 'success.dark',
                },
              }}
            >
              Continue
            </Button>
          )}
          
          {verificationStep === 'failed' && (
            <Button
              onClick={handleCloseDialog}
              variant="contained"
              sx={{
                backgroundColor: 'error.main',
                '&:hover': {
                  backgroundColor: 'error.dark',
                },
              }}
            >
              Close
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CustomerSearch;
