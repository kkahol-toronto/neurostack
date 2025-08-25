import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';
import { useTheme } from '../contexts/ThemeContext';
import ReactMarkdown from 'react-markdown';

const MarkdownTest: React.FC = () => {
  const { theme } = useTheme();

  const sampleMarkdown = `## **Customer Profile**

- **Customer Name:** Michael Gonzales
- **Customer ID:** 5
- **Date of Birth:** 1994-04-24 (Age: 30)
- **State of Residence:** CA (West Donaldton, Zip: 44969)
- **Employment Status:** Part-time
- **Employer:** Mitchell Group
- **Job Title:** Teacher, English as a foreign language
- **Annual Income (Verified):** $111,398
- **Customer Segment:** Premium
- **Household Size:** 2
- **Customer Since:** 2023-04-15

---

## **Financial Health Overview**

- **Income Analysis:**
- **Verified Annual Income:** $111,398
- **Income Stability Score:** 82.4 (High; indicates stable income)
- **Employment:** Part-time, but income is above average for the segment

- **Account Activity:**
- **Current Credit Limit:** $32,000
- **Current Balance:** $6,512.54
- **Utilization Rate:** 20.4% (Well within healthy range; below risk thresholds)
- **Tenure with Bank:** 38 months

- **Financial Metrics:**
- **Debt-to-Income Ratio:** 0.32 (Acceptable; below typical risk thresholds)
- **Total Monthly Debt Payments:** $3,019.60

---

## **Credit Risk Assessment**

- **Credit Score Analysis:**
- **FICO Score 8:** 724
- **FICO Score 9:** 722
- **Score Range:** Good (Prime segment; strong approval candidate)

- **Payment History:**
- **On-time Payments (Last 12 Months):** 11
- **Late Payments (Last 12 Months):** 0
- **Delinquencies (30+ Days, Last 12 Months):** 0
- **Total Accounts (Credit Bureau):** 9

- **Fraud, KYC, and Compliance:**
- **Overall Fraud Risk Score:** 7.95 (Low risk)
- **Risk Level:** Low
- **KYC Score:** 74.4 (Satisfactory)
- **Identity Verification:** Verified

- **Macroeconomic Factors (CA):**
- **Unemployment Rate:** 5.65% (Moderate)
- **Macro Risk Score:** 37.2 (Medium; local economic conditions should be monitored)
- **GDP Growth Rate:** 4.33% (Positive outlook)

---

## **Summary & Recommendations**

- **Overall Assessment:**
- Michael Gonzales is a low-risk, prime credit customer with strong financial metrics, a stable income, and an exemplary payment history. He maintains a healthy credit utilization rate and has no late payments or recent delinquencies.
- Verified identity and compliance scores reinforce trustworthiness and suitability for further credit products.
- While employment is part-time, income and stability scores offset concerns.

- **Recommendations:**
- **Credit Line:** Consider eligibility for a modest credit line increase, ensuring continued utilization rates below 30%.
- **Product Suitability:** Eligible for premium credit products, personal loans, or refinancing options.
- **Monitoring:** Routine account monitoring; no immediate red flags. Monitor for changes in employment status or economic shifts in California.
- **Cross-Sell Opportunities:** Explore offers for savings, investment, or insurance products given the customer's premium segment and income levels.

**Conclusion:**
Michael Gonzales presents as a strong candidate for further credit products with low risk. Maintain engagement and proactively offer tailored financial solutions aligned with his profile.`;

  return (
    <Card sx={{ 
      backgroundColor: 'rgba(255, 255, 255, 0.05)',
      backdropFilter: 'blur(10px)',
      border: `1px solid rgba(255, 255, 255, 0.1)`,
      maxWidth: 800,
      margin: '20px auto'
    }}>
      <CardContent>
        <Typography variant="h5" sx={{ color: theme.colors.text, mb: 3, textAlign: 'center' }}>
          AI Summary - Markdown Rendering Test
        </Typography>
        
        <Box sx={{ 
          color: theme.colors.textSecondary,
          lineHeight: 1.6,
          '& h2': {
            color: theme.colors.text,
            fontSize: '1.5rem',
            fontWeight: 600,
            marginTop: 2,
            marginBottom: 1,
            borderBottom: `1px solid ${theme.colors.primary}`,
            paddingBottom: 0.5
          },
          '& h3': {
            color: theme.colors.text,
            fontSize: '1.2rem',
            fontWeight: 500,
            marginTop: 1.5,
            marginBottom: 0.5
          },
          '& strong': {
            color: theme.colors.text,
            fontWeight: 600
          },
          '& ul': {
            marginLeft: 2,
            marginTop: 0.5,
            marginBottom: 0.5
          },
          '& li': {
            marginBottom: 0.25
          },
          '& hr': {
            borderColor: theme.colors.primary,
            marginTop: 1,
            marginBottom: 1
          }
        }}>
          <ReactMarkdown>{sampleMarkdown}</ReactMarkdown>
        </Box>
      </CardContent>
    </Card>
  );
};

export default MarkdownTest;
