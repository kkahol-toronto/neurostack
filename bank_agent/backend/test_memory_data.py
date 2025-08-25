#!/usr/bin/env python3
"""
Simple test to check memory data without importing main module.
"""

# Copy the MOCK_DATABASES data directly to avoid import issues
MOCK_DATABASES = {
    'customer_demographics': [
        {'customer_id': 5, 'first_name': 'Michael', 'last_name': 'Gonzales', 'date_of_birth': '1994-04-24', 'annual_income': 114394, 'state': 'CA', 'employment_status': 'Part-time', 'customer_segment': 'Premium', 'email': 'michael.gonzales@email.com', 'phone': '(672) 201-4656', 'ssn': '***-**-2707', 'address_line1': '2053 Mark Common Suite 157', 'address_line2': None, 'city': 'West Donaldton', 'zip_code': '44969', 'customer_since': '2023-04-15', 'employer_name': 'Mitchell Group', 'job_title': 'Teacher, English as a foreign language', 'household_size': 2}
    ],
    'internal_banking_data': [
        {'customer_id': 5, 'current_credit_limit': 32000, 'current_balance': 6512.54, 'utilization_rate': 20.35, 'on_time_payments_12m': 12, 'late_payments_12m': 0, 'tenure_months': 25}
    ],
    'credit_bureau_data': [
        {'customer_id': 5, 'fico_score_8': 724, 'fico_score_9': 720, 'total_accounts_bureau': 8, 'external_utilization_rate': 35.2, 'delinquencies_30_plus_12m': 0}
    ],
    'income_ability_to_pay': [
        {'customer_id': 5, 'verified_annual_income': 111398.05645685742, 'debt_to_income_ratio': 0.3167581065732502, 'total_monthly_debt_payments': 3019.6022369450325, 'income_stability_score': 82.42473592743112}
    ],
    'fraud_kyc_compliance': [
        {'customer_id': 5, 'overall_fraud_risk_score': 3.2, 'risk_level': 'Low', 'kyc_score': 9.5, 'identity_verification_status': 'Verified'}
    ]
}

def generate_enhanced_customer(customer_id):
    """Generate enhanced customer data with actual database values."""
    # Get actual data from all database sources
    demographics = next((c for c in MOCK_DATABASES["customer_demographics"] if c["customer_id"] == customer_id), None)
    banking_data = next((c for c in MOCK_DATABASES["internal_banking_data"] if c["customer_id"] == customer_id), None)
    credit_bureau = next((c for c in MOCK_DATABASES["credit_bureau_data"] if c["customer_id"] == customer_id), None)
    income_data = next((c for c in MOCK_DATABASES["income_ability_to_pay"] if c["customer_id"] == customer_id), None)
    fraud_data = next((c for c in MOCK_DATABASES["fraud_kyc_compliance"] if c["customer_id"] == customer_id), None)
    
    # Build comprehensive customer profile from actual database data
    customer = {
        "customer_id": customer_id,
        # Demographics data
        "first_name": demographics.get("first_name") if demographics else f"Customer{customer_id}",
        "last_name": demographics.get("last_name") if demographics else "Unknown",
        "date_of_birth": demographics.get("date_of_birth") if demographics else "1990-01-01",
        "annual_income": demographics.get("annual_income") if demographics else 50000,
        "state": demographics.get("state") if demographics else "CA",
        "employment_status": demographics.get("employment_status") if demographics else "Full-time",
        "customer_segment": demographics.get("customer_segment") if demographics else "Standard",
        "address": demographics.get("address_line1") if demographics else "Unknown Address",
        "phone": demographics.get("phone") if demographics else "Unknown",
        "email": demographics.get("email") if demographics else f"customer{customer_id}@example.com",
        "ssn": demographics.get("ssn") if demographics else "***-**-0000",
        "city": demographics.get("city") if demographics else "Unknown City",
        "zip_code": demographics.get("zip_code") if demographics else "00000",
        "customer_since": demographics.get("customer_since") if demographics else "2020-01-01",
        "employer_name": demographics.get("employer_name") if demographics else "Unknown",
        "job_title": demographics.get("job_title") if demographics else "Unknown",
        "household_size": demographics.get("household_size") if demographics else 1,
        
        # Banking data
        "credit_limit": banking_data.get("current_credit_limit") if banking_data else 25000,
        "current_balance": banking_data.get("current_balance") if banking_data else 10000,
        "credit_utilization": banking_data.get("utilization_rate") if banking_data else 40.0,
        "on_time_payments_12m": banking_data.get("on_time_payments_12m") if banking_data else 12,
        "late_payments_12m": banking_data.get("late_payments_12m") if banking_data else 0,
        "tenure_months": banking_data.get("tenure_months") if banking_data else 24,
        
        # Credit bureau data
        "fico_score": credit_bureau.get("fico_score_8") if credit_bureau else 700,
        "fico_score_9": credit_bureau.get("fico_score_9") if credit_bureau else 700,
        "total_accounts_bureau": credit_bureau.get("total_accounts_bureau") if credit_bureau else 5,
        "delinquencies_30_plus_12m": credit_bureau.get("delinquencies_30_plus_12m") if credit_bureau else 0,
        
        # Income and ability to pay data
        "verified_annual_income": income_data.get("verified_annual_income") if income_data else 50000,
        "debt_to_income_ratio": income_data.get("debt_to_income_ratio") if income_data else 0.3,
        "total_monthly_debt_payments": income_data.get("total_monthly_debt_payments") if income_data else 1500,
        "income_stability_score": income_data.get("income_stability_score") if income_data else 75.0,
        
        # Fraud/KYC data
        "fraud_risk_score": fraud_data.get("overall_fraud_risk_score") if fraud_data else 5.0,
        "fraud_risk_level": fraud_data.get("risk_level") if fraud_data else "Medium",
        "kyc_score": fraud_data.get("kyc_score") if fraud_data else 8.0,
        "identity_verification_status": fraud_data.get("identity_verification_status") if fraud_data else "Verified",
        
        # Derived fields
        "payment_history": "Excellent" if (banking_data and banking_data.get("late_payments_12m", 0) == 0) else "Good" if (banking_data and banking_data.get("late_payments_12m", 0) <= 1) else "Fair",
        "income": income_data.get("verified_annual_income") if income_data else demographics.get("annual_income") if demographics else 50000,
        "dti_ratio": (income_data.get("debt_to_income_ratio", 0) * 100) if income_data else 30.0,
    }
    
    return customer

def main():
    """Test the memory data generation."""
    print("🚀 Testing Memory Data Generation")
    print("=" * 50)
    
    # Test customer ID 5
    customer_id = 5
    print(f"🔍 Testing Customer ID: {customer_id}")
    
    # Generate customer data
    customer_data = generate_enhanced_customer(customer_id)
    
    if customer_data:
        print("✅ Customer data generated:")
        print(f"  Customer ID: {customer_data.get('customer_id')}")
        print(f"  Name: {customer_data.get('first_name')} {customer_data.get('last_name')}")
        print(f"  Credit Limit: ${customer_data.get('credit_limit'):,.0f}")
        print(f"  FICO Score: {customer_data.get('fico_score')}")
        print(f"  Credit Utilization: {customer_data.get('credit_utilization'):.1f}%")
        print(f"  Annual Income: ${customer_data.get('annual_income'):,.0f}")
        print(f"  Verified Annual Income: ${customer_data.get('verified_annual_income'):,.0f}")
        print(f"  Income (primary): ${customer_data.get('income'):,.0f}")
        print(f"  DTI Ratio: {customer_data.get('dti_ratio'):.1f}%")
        print(f"  Payment History: {customer_data.get('payment_history')}")
        print(f"  Employment Status: {customer_data.get('employment_status')}")
        print(f"  Customer Segment: {customer_data.get('customer_segment')}")
        print(f"  State: {customer_data.get('state')}")
        print(f"  City: {customer_data.get('city')}")
        
        # Check if income is correct
        expected_income = 111398.06
        actual_income = customer_data.get('income')
        if abs(actual_income - expected_income) < 1:
            print(f"✅ Income is correct: ${actual_income:,.0f}")
        else:
            print(f"❌ Income is incorrect: ${actual_income:,.0f} (expected: ${expected_income:,.0f})")
    else:
        print("❌ No customer data generated")

if __name__ == "__main__":
    main()
