#!/usr/bin/env python3
"""
Script to generate complete customer data and update MOCK_DATABASES
"""

import random
from datetime import datetime, date, timedelta
from faker import Faker

# Initialize Faker for realistic data
fake = Faker('en_US')

def generate_complete_customer_data():
    """Generate complete customer data with all fields"""
    
    # US States
    states = {
        'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
        'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
        'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
        'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
        'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri',
        'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey',
        'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio',
        'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
        'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont',
        'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'
    }
    
    customers = []
    
    # Generate data for existing customers (John Doe, Jane Smith, Bob Johnson)
    existing_customers = [
        {'customer_id': 1, 'first_name': 'John', 'last_name': 'Doe', 'annual_income': 75000, 'state': 'CA'},
        {'customer_id': 2, 'first_name': 'Jane', 'last_name': 'Smith', 'annual_income': 95000, 'state': 'NY'},
        {'customer_id': 3, 'first_name': 'Bob', 'last_name': 'Johnson', 'annual_income': 65000, 'state': 'TX'},
    ]
    
    for base_customer in existing_customers:
        # Generate age and date of birth
        age = random.randint(25, 65)
        birth_year = datetime.now().year - age
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)
        date_of_birth = f"{birth_year}-{birth_month:02d}-{birth_day:02d}"
        
        # Generate employment status based on age and income
        if age < 30:
            employment_status = random.choices(['Full-time', 'Part-time', 'Student'], weights=[70, 20, 10])[0]
        elif age > 60:
            employment_status = random.choices(['Full-time', 'Part-time', 'Retired'], weights=[60, 25, 15])[0]
        else:
            employment_status = random.choices(['Full-time', 'Part-time', 'Self-employed'], weights=[75, 15, 10])[0]
        
        # Generate customer segment based on income
        if base_customer['annual_income'] > 100000:
            customer_segment = 'Premium'
        elif base_customer['annual_income'] > 70000:
            customer_segment = random.choices(['Premium', 'Standard'], weights=[30, 70])[0]
        else:
            customer_segment = random.choices(['Standard', 'Basic'], weights=[60, 40])[0]
        
        # Generate complete address
        city = fake.city()
        zip_code = fake.zipcode()
        address_line1 = fake.street_address()
        address_line2 = fake.secondary_address() if random.random() < 0.3 else None
        
        # Generate phone and email
        phone = f"({random.randint(200, 999)}) {random.randint(100, 999)}-{random.randint(1000, 9999)}"
        email = f"{base_customer['first_name'].lower()}.{base_customer['last_name'].lower()}@email.com"
        
        # Generate SSN
        ssn = f"***-**-{random.randint(1000, 9999)}"
        
        # Create complete customer record
        customer = {
            'customer_id': base_customer['customer_id'],
            'first_name': base_customer['first_name'],
            'last_name': base_customer['last_name'],
            'date_of_birth': date_of_birth,
            'annual_income': base_customer['annual_income'],
            'state': base_customer['state'],
            'employment_status': employment_status,
            'customer_segment': customer_segment,
            'email': email,
            'phone': phone,
            'ssn': ssn,
            'address_line1': address_line1,
            'address_line2': address_line2,
            'city': city,
            'zip_code': zip_code,
            'customer_since': f"{birth_year + age - random.randint(1, 10)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
            'employer_name': fake.company(),
            'job_title': fake.job(),
            'household_size': random.randint(1, 5)
        }
        
        customers.append(customer)
    
    return customers

def generate_mock_databases():
    """Generate complete MOCK_DATABASES with all fields"""
    
    # Generate complete customer demographics
    customer_demographics = generate_complete_customer_data()
    
    # Generate additional customers for more variety
    for i in range(4, 11):  # Add customers 4-10
        age = random.randint(22, 70)
        birth_year = datetime.now().year - age
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)
        date_of_birth = f"{birth_year}-{birth_month:02d}-{birth_day:02d}"
        
        # Generate income based on age
        if age < 30:
            annual_income = random.randint(30000, 70000)
        elif age < 45:
            annual_income = random.randint(45000, 120000)
        else:
            annual_income = random.randint(50000, 180000)
        
        # Generate employment status
        if age < 25:
            employment_status = random.choices(['Full-time', 'Part-time', 'Student'], weights=[60, 25, 15])[0]
        elif age > 65:
            employment_status = random.choices(['Full-time', 'Part-time', 'Retired'], weights=[50, 30, 20])[0]
        else:
            employment_status = random.choices(['Full-time', 'Part-time', 'Self-employed'], weights=[75, 15, 10])[0]
        
        # Generate customer segment
        if annual_income > 100000:
            customer_segment = 'Premium'
        elif annual_income > 70000:
            customer_segment = random.choices(['Premium', 'Standard'], weights=[25, 75])[0]
        else:
            customer_segment = random.choices(['Standard', 'Basic'], weights=[65, 35])[0]
        
        # Generate state
        state = random.choice(['CA', 'NY', 'TX', 'FL', 'IL', 'PA', 'OH', 'GA', 'NC', 'MI'])
        
        # Generate complete address
        city = fake.city()
        zip_code = fake.zipcode()
        address_line1 = fake.street_address()
        address_line2 = fake.secondary_address() if random.random() < 0.2 else None
        
        # Generate name
        first_name = fake.first_name()
        last_name = fake.last_name()
        
        # Generate phone and email
        phone = f"({random.randint(200, 999)}) {random.randint(100, 999)}-{random.randint(1000, 9999)}"
        email = f"{first_name.lower()}.{last_name.lower()}@email.com"
        
        # Generate SSN
        ssn = f"***-**-{random.randint(1000, 9999)}"
        
        customer = {
            'customer_id': i,
            'first_name': first_name,
            'last_name': last_name,
            'date_of_birth': date_of_birth,
            'annual_income': annual_income,
            'state': state,
            'employment_status': employment_status,
            'customer_segment': customer_segment,
            'email': email,
            'phone': phone,
            'ssn': ssn,
            'address_line1': address_line1,
            'address_line2': address_line2,
            'city': city,
            'zip_code': zip_code,
            'customer_since': f"{birth_year + age - random.randint(1, 8)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
            'employer_name': fake.company(),
            'job_title': fake.job(),
            'household_size': random.randint(1, 5)
        }
        
        customer_demographics.append(customer)
    
    # Generate other tables with matching customer IDs
    internal_banking_data = []
    credit_bureau_data = []
    fraud_kyc_compliance = []
    income_ability_to_pay = []
    open_banking_data = []
    state_economic_indicators = []
    
    for customer in customer_demographics:
        customer_id = customer['customer_id']
        
        # Internal banking data
        current_credit_limit = round(customer['annual_income'] * random.uniform(0.15, 0.35) / 1000) * 1000
        utilization_rate = random.uniform(20, 80)
        current_balance = current_credit_limit * utilization_rate / 100
        
        internal_banking_data.append({
            'customer_id': customer_id,
            'current_credit_limit': current_credit_limit,
            'current_balance': current_balance,
            'utilization_rate': utilization_rate,
            'on_time_payments_12m': random.randint(10, 12),
            'late_payments_12m': random.randint(0, 2),
            'tenure_months': random.randint(12, 120)
        })
        
        # Credit bureau data
        fico_base = 650
        if customer['annual_income'] > 80000:
            fico_base += 50
        elif customer['annual_income'] < 50000:
            fico_base -= 30
        
        fico_score_8 = max(300, min(850, fico_base + random.randint(-50, 50)))
        fico_score_9 = max(300, min(850, fico_score_8 + random.randint(-20, 20)))
        
        credit_bureau_data.append({
            'customer_id': customer_id,
            'fico_score_8': fico_score_8,
            'fico_score_9': fico_score_9,
            'total_accounts_bureau': random.randint(3, 15),
            'delinquencies_30_plus_12m': random.randint(0, 2)
        })
        
        # Fraud/KYC data
        fraud_kyc_compliance.append({
            'customer_id': customer_id,
            'overall_fraud_risk_score': random.uniform(1, 8),
            'risk_level': random.choices(['low', 'medium', 'high'], weights=[70, 25, 5])[0],
            'kyc_score': random.uniform(70, 100),
            'identity_verification_status': 'verified'
        })
        
        # Income data
        debt_to_income_ratio = random.uniform(0.2, 0.6)
        total_monthly_debt_payments = customer['annual_income'] * debt_to_income_ratio / 12
        
        income_ability_to_pay.append({
            'customer_id': customer_id,
            'verified_annual_income': customer['annual_income'] * random.uniform(0.95, 1.05),
            'debt_to_income_ratio': debt_to_income_ratio,
            'total_monthly_debt_payments': total_monthly_debt_payments,
            'income_stability_score': random.uniform(70, 100)
        })
        
        # Open banking data
        open_banking_data.append({
            'customer_id': customer_id,
            'open_banking_consent': random.random() < 0.4,
            'avg_monthly_income': customer['annual_income'] / 12 * random.uniform(0.9, 1.1),
            'cash_flow_stability_score': random.uniform(60, 100),
            'expense_obligations_rent': random.randint(800, 2500)
        })
    
    # State economic indicators
    for state in ['CA', 'NY', 'TX', 'FL', 'IL', 'PA', 'OH', 'GA', 'NC', 'MI']:
        state_economic_indicators.append({
            'state_code': state,
            'unemployment_rate': random.uniform(3.0, 6.0),
            'macro_risk_score': random.uniform(30, 80),
            'risk_level': random.choices(['low', 'medium', 'high'], weights=[60, 30, 10])[0],
            'gdp_growth_rate': random.uniform(1.5, 4.5)
        })
    
    return {
        "customer_demographics": customer_demographics,
        "internal_banking_data": internal_banking_data,
        "credit_bureau_data": credit_bureau_data,
        "fraud_kyc_compliance": fraud_kyc_compliance,
        "income_ability_to_pay": income_ability_to_pay,
        "open_banking_data": open_banking_data,
        "state_economic_indicators": state_economic_indicators
    }

def update_main_py():
    """Update the MOCK_DATABASES in main.py"""
    
    # Generate new mock data
    mock_databases = generate_mock_databases()
    
    # Read the current main.py file
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Find the MOCK_DATABASES section and replace it
    start_marker = "# Mock database for demo purposes\nMOCK_DATABASES = {"
    
    # Find the start of MOCK_DATABASES
    start_idx = content.find(start_marker)
    if start_idx == -1:
        print("❌ Could not find MOCK_DATABASES in main.py")
        return False
    
    # Find the end of MOCK_DATABASES (look for the closing brace)
    brace_count = 0
    end_idx = start_idx
    for i, char in enumerate(content[start_idx:], start_idx):
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                end_idx = i + 1
                break
    
    # Create the new MOCK_DATABASES content
    new_mock_databases = "# Mock database for demo purposes\nMOCK_DATABASES = " + repr(mock_databases)
    
    # Replace the old MOCK_DATABASES with the new one
    new_content = content[:start_idx] + new_mock_databases + content[end_idx:]
    
    # Write the updated content back to main.py
    with open('main.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Successfully updated MOCK_DATABASES in main.py")
    print(f"📊 Generated data for {len(mock_databases['customer_demographics'])} customers")
    
    # Show sample of the first customer
    first_customer = mock_databases['customer_demographics'][0]
    print(f"\n👤 Sample customer data:")
    print(f"   Name: {first_customer['first_name']} {first_customer['last_name']}")
    print(f"   Email: {first_customer['email']}")
    print(f"   Phone: {first_customer['phone']}")
    print(f"   Address: {first_customer['address_line1']}, {first_customer['city']}, {first_customer['state']} {first_customer['zip_code']}")
    print(f"   Date of Birth: {first_customer['date_of_birth']}")
    print(f"   Employment: {first_customer['employment_status']}")
    print(f"   Segment: {first_customer['customer_segment']}")
    
    return True

if __name__ == "__main__":
    print("🔄 Updating MOCK_DATABASES with complete customer data...")
    success = update_main_py()
    if success:
        print("\n🎉 MOCK_DATABASES updated successfully!")
        print("🚀 Restart your backend server to see the changes.")
    else:
        print("\n❌ Failed to update MOCK_DATABASES")
