import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Box, Typography, Paper } from '@mui/material';
import { useTheme } from '../contexts/ThemeContext';

const MarkdownChatTest: React.FC = () => {
  const { theme } = useTheme();

  const sampleChatMessage = `The current credit limit for Michael Gonzales (Customer ID: 5) is **$32,000**.

**Key supporting details from the customer profile and investigation results:**
- **Current Balance:** $6,512.54 (Credit utilization: 20.4%)
- **FICO Scores:** 724 (FICO 8), 722 (FICO 9) – both indicating strong creditworthiness
- **Payment History:** Excellent, with 11 on-time payments in the past 12 months and zero late payments
- **Annual Income:** $111,398 (fully verified)
- **Debt-to-Income Ratio:** 31.7% (within acceptable range)
- **Fraud Risk Level:** Low (score: 7.95)
- **Employment Status:** Part-time, but with strong income and stability scores
- **Account Tenure:** 38 months (established relationship)

**Investigation results consistently highlight:**
- Strong FICO and perfect payment history support responsible credit management
- Moderate utilization suggests prudent use of available credit
- Low fraud risk and verified identity/income reduce overall risk profile

**Strategic Insights:**
- Multiple analysis streams recommend **approval of a credit limit increase** based on the strong overall profile.
- Some investigation items suggest reviewing the application with additional documentation.

**Actionable Next Steps for Analyst:**
- If considering a credit limit increase, a moderate raise (e.g., 10–20%) is supported by the data.
- Explore offering additional credit products, as the customer's profile aligns with premium segment upsell opportunities.`;

  return (
    <Box sx={{ p: 3, maxWidth: 800, mx: 'auto' }}>
      <Typography variant="h4" sx={{ mb: 3, color: theme.colors.text }}>
        Markdown Chat Rendering Test
      </Typography>
      
      <Paper
        sx={{
          p: 3,
          backgroundColor: 'rgba(255, 255, 255, 0.05)',
          border: `1px solid ${theme.colors.border}`,
          borderRadius: 2,
          mb: 3
        }}
      >
        <Typography variant="h6" sx={{ mb: 2, color: theme.colors.text }}>
          Sample Chat Message (Raw Markdown):
        </Typography>
        <Box
          sx={{
            p: 2,
            backgroundColor: 'rgba(0, 0, 0, 0.2)',
            borderRadius: 1,
            fontFamily: 'monospace',
            fontSize: '0.875em',
            color: theme.colors.textSecondary,
            whiteSpace: 'pre-wrap'
          }}
        >
          {sampleChatMessage}
        </Box>
      </Paper>

      <Paper
        sx={{
          p: 3,
          backgroundColor: 'rgba(255, 255, 255, 0.05)',
          border: `1px solid ${theme.colors.border}`,
          borderRadius: 2
        }}
      >
        <Typography variant="h6" sx={{ mb: 2, color: theme.colors.text }}>
          Rendered Markdown:
        </Typography>
        <Box
          sx={{
            color: theme.colors.text,
            '& > *:first-of-type': { mt: 0 },
            '& > *:last-of-type': { mb: 0 }
          }}
        >
          <ReactMarkdown
            components={{
              p: ({ children }) => (
                <Typography variant="body2" sx={{ mb: 1, '&:last-child': { mb: 0 } }}>
                  {children}
                </Typography>
              ),
              h1: ({ children }) => (
                <Typography variant="h6" sx={{ mb: 1, fontWeight: 'bold' }}>
                  {children}
                </Typography>
              ),
              h2: ({ children }) => (
                <Typography variant="subtitle1" sx={{ mb: 1, fontWeight: 'bold' }}>
                  {children}
                </Typography>
              ),
              h3: ({ children }) => (
                <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 'bold' }}>
                  {children}
                </Typography>
              ),
              strong: ({ children }) => (
                <Box component="span" sx={{ fontWeight: 'bold' }}>
                  {children}
                </Box>
              ),
              em: ({ children }) => (
                <Box component="span" sx={{ fontStyle: 'italic' }}>
                  {children}
                </Box>
              ),
              ul: ({ children }) => (
                <Box component="ul" sx={{ pl: 2, mb: 1 }}>
                  {children}
                </Box>
              ),
              ol: ({ children }) => (
                <Box component="ol" sx={{ pl: 2, mb: 1 }}>
                  {children}
                </Box>
              ),
              li: ({ children }) => (
                <Typography variant="body2" component="li" sx={{ mb: 0.5 }}>
                  {children}
                </Typography>
              ),
              code: ({ children }) => (
                <Box
                  component="code"
                  sx={{
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    padding: '2px 4px',
                    borderRadius: 1,
                    fontSize: '0.875em',
                    fontFamily: 'monospace'
                  }}
                >
                  {children}
                </Box>
              ),
              pre: ({ children }) => (
                <Box
                  component="pre"
                  sx={{
                    backgroundColor: 'rgba(255, 255, 255, 0.05)',
                    padding: 1,
                    borderRadius: 1,
                    overflow: 'auto',
                    mb: 1
                  }}
                >
                  {children}
                </Box>
              ),
              blockquote: ({ children }) => (
                <Box
                  component="blockquote"
                  sx={{
                    borderLeft: `3px solid ${theme.colors.primary}`,
                    pl: 2,
                    ml: 0,
                    mb: 1,
                    fontStyle: 'italic'
                  }}
                >
                  {children}
                </Box>
              )
            }}
          >
            {sampleChatMessage}
          </ReactMarkdown>
        </Box>
      </Paper>
    </Box>
  );
};

export default MarkdownChatTest;
