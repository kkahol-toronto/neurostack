# Bank Agent Data System

A comprehensive simulated banking data system for credit limit decision making using NeuroStack agents.

## 🏦 **Overview**

This system provides realistic simulated data for 100 banking customers across all major data sources used in credit limit decision making:

- **Internal Banking Data** - Account history, utilization, spending patterns
- **Credit Bureau Data** - FICO scores, tradelines, derogatories
- **Income & Ability-to-Pay** - Verified income, DTI ratios, debt obligations
- **Open Banking & Alternative Data** - Transaction data, cash flow analysis
- **Fraud/KYC/Compliance** - Identity verification, risk scores, AML checks
- **Economic Indicators** - State-level macro data for portfolio analysis

## 📊 **Database Schema**

### **Main Database: `bank_agent_db`**

1. **`customer_demographics`** - Core customer information
2. **`internal_banking_data`** - Account & payment history, utilization, spending
3. **`credit_bureau_data`** - Tri-merge credit data (Experian, Equifax, TransUnion)
4. **`income_ability_to_pay`** - Income verification, DTI calculations
5. **`open_banking_data`** - Alternative data (40% of customers)
6. **`fraud_kyc_compliance`** - Risk assessment, identity verification
7. **`credit_limit_decisions`** - Decision history tracking

### **Economic Database: `economic_indicators_db`**

1. **`state_economic_indicators`** - Macro data for all 50 US states

## 🚀 **Quick Start**

### **1. Setup Database**

```bash
# Create and populate the database
mysql -u root -p < data/schema.sql
```

### **2. Install Dependencies**

```bash
pip install -r requirements.txt
```

### **3. Generate Data**

```bash
cd data
python generate_data.py
```

### **4. Verify Data**

```sql
-- Check customer count
SELECT COUNT(*) FROM customer_demographics;

-- View sample customer
SELECT 
    cd.first_name,
    cd.last_name,
    cd.customer_segment,
    ibd.current_credit_limit,
    cbd.fico_score_8,
    iatp.debt_to_income_ratio
FROM customer_demographics cd
JOIN internal_banking_data ibd ON cd.customer_id = ibd.customer_id
JOIN credit_bureau_data cbd ON cd.customer_id = cbd.customer_id
JOIN income_ability_to_pay iatp ON cd.customer_id = iatp.customer_id
LIMIT 5;
```

## 📋 **Data Coverage**

### **Customer Demographics (100 customers)**
- ✅ Age distribution (18-75 years)
- ✅ Geographic distribution (all 50 US states)
- ✅ Income levels ($0-$200k+)
- ✅ Employment types and industries
- ✅ Customer segments (Premium, Standard, Basic, Student)

### **Internal Banking Data (100 customers)**
- ✅ Payment history (on-time/late payments)
- ✅ Credit utilization and exposure
- ✅ Spending patterns and merchant categories
- ✅ Account relationships and tenure
- ✅ Operational signals (disputes, chargebacks)

### **Credit Bureau Data (100 customers)**
- ✅ FICO scores (8, 9, 10, Bankcard)
- ✅ VantageScore (3, 4)
- ✅ Tradeline details and utilization
- ✅ Derogatory information
- ✅ Credit seeking behavior

### **Income & Ability-to-Pay (100 customers)**
- ✅ Stated and verified income
- ✅ Multiple income sources
- ✅ Debt-to-income ratios
- ✅ Monthly debt obligations
- ✅ Income stability metrics

### **Open Banking Data (40 customers)**
- ✅ Transaction aggregation
- ✅ Cash flow analysis
- ✅ Alternative tradelines
- ✅ Gig economy detection
- ✅ Multi-stream income

### **Fraud/KYC/Compliance (100 customers)**
- ✅ Identity verification status
- ✅ Risk scores and factors
- ✅ Device and behavioral risk
- ✅ Consortium fraud data
- ✅ AML and compliance checks

### **Economic Indicators (50 states)**
- ✅ Unemployment rates and trends
- ✅ GDP and income growth
- ✅ Housing market indicators
- ✅ Default rates by product
- ✅ Regional risk assessments

## 🎯 **Data Quality Features**

### **Realistic Correlations**
- Income affects credit limits and FICO scores
- Payment history influences bureau scores
- Age and employment impact income levels
- Geographic location affects economic indicators

### **Risk Distribution**
- 80% Low risk customers
- 15% Medium risk customers
- 4% High risk customers
- 1% Critical risk customers

### **Data Completeness**
- 100% coverage for core banking data
- 100% coverage for credit bureau data
- 40% coverage for open banking data
- Realistic missing data patterns

## 🔧 **Customization**

### **Modify Data Generation**

Edit `data/generate_data.py` to adjust:

```python
# Change customer count
generator.generate_all_data(num_customers=500)

# Modify risk distribution
risk_level = random.choices(['Low', 'Medium', 'High', 'Critical'], 
                          weights=[70, 20, 8, 2])[0]

# Adjust income ranges
if age < 25:
    annual_income = random.randint(30000, 70000)  # Customize
```

### **Add New Data Sources**

1. Create new table in `schema.sql`
2. Add generation method in `BankDataGenerator`
3. Update `insert_customer_data()` method

## 📈 **Sample Queries**

### **Credit Risk Analysis**
```sql
SELECT 
    customer_segment,
    AVG(fico_score_8) as avg_fico,
    AVG(utilization_rate) as avg_utilization,
    AVG(debt_to_income_ratio) as avg_dti
FROM customer_demographics cd
JOIN internal_banking_data ibd ON cd.customer_id = ibd.customer_id
JOIN credit_bureau_data cbd ON cd.customer_id = cbd.customer_id
JOIN income_ability_to_pay iatp ON cd.customer_id = iatp.customer_id
GROUP BY customer_segment;
```

### **Geographic Risk Assessment**
```sql
SELECT 
    cd.state,
    sei.unemployment_rate,
    sei.macro_risk_score,
    AVG(cbd.fico_score_8) as avg_fico,
    COUNT(*) as customer_count
FROM customer_demographics cd
JOIN credit_bureau_data cbd ON cd.customer_id = cbd.customer_id
JOIN economic_indicators_db.state_economic_indicators sei ON cd.state = sei.state_code
GROUP BY cd.state, sei.unemployment_rate, sei.macro_risk_score
ORDER BY sei.macro_risk_score DESC;
```

### **Open Banking Insights**
```sql
SELECT 
    cd.customer_segment,
    COUNT(obd.customer_id) as open_banking_customers,
    AVG(obd.cash_flow_stability_score) as avg_cash_flow_score,
    AVG(obd.income_regularity_score) as avg_income_regularity
FROM customer_demographics cd
LEFT JOIN open_banking_data obd ON cd.customer_id = obd.customer_id 
    AND obd.open_banking_consent = TRUE
GROUP BY cd.customer_segment;
```

## 🤖 **Integration with NeuroStack**

This data system is designed to work with NeuroStack agents for:

1. **Credit Limit Decision Making**
2. **Risk Assessment**
3. **Customer Segmentation**
4. **Portfolio Analysis**
5. **Regulatory Compliance**

### **Example Agent Usage**
```python
from neurostack import Agent, AgentConfig, AgentContext
from bank_agent.data import BankDataConnector

# Create bank data connector
connector = BankDataConnector()

# Get customer data for analysis
customer_data = connector.get_customer_profile(customer_id=1)

# Create credit decision agent
credit_agent = CreditDecisionAgent(AgentConfig(
    name="credit_decision_agent",
    model="gpt-4",
    memory_enabled=True
))

# Make credit limit decision
decision = await credit_agent.execute(customer_data)
```

## 🔒 **Data Privacy & Security**

- All SSNs are masked (***-**-1234 format)
- Names are generated using Faker library
- Addresses are fictional
- No real financial data included
- Suitable for development and testing only

## 📊 **Data Statistics**

| Metric | Value |
|--------|-------|
| Total Customers | 100 |
| States Covered | 50 |
| Data Tables | 8 |
| Open Banking Coverage | 40% |
| Average FICO Score | 650-750 |
| Income Range | $0-$200k+ |
| Credit Limit Range | $1k-$50k |

## 🛠 **Troubleshooting**

### **Database Connection Issues**
```bash
# Check MySQL service
sudo systemctl status mysql

# Test connection
mysql -u root -p -e "SHOW DATABASES;"
```

### **Data Generation Errors**
```bash
# Check dependencies
pip list | grep -E "(mysql|faker|names)"

# Verify schema
mysql -u root -p bank_agent_db -e "SHOW TABLES;"
```

### **Performance Issues**
```bash
# Add indexes for large datasets
ALTER TABLE customer_demographics ADD INDEX idx_state (state);
ALTER TABLE credit_bureau_data ADD INDEX idx_fico (fico_score_8);
```

## 📚 **Additional Resources**

- [NeuroStack Documentation](../docs/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [Faker Library](https://faker.readthedocs.io/)
- [Banking Data Standards](https://www.ffiec.gov/)

---

**Need Help?** Check the troubleshooting section or create an issue in the repository.
