#!/usr/bin/env python3
"""
Simple script to check customer data.
"""

# Copy the MOCK_DATABASES data directly
MOCK_DATABASES = {
    'customer_demographics': [
        {'customer_id': 5, 'first_name': 'Michael', 'last_name': 'Gonzales', 'date_of_birth': '1994-04-24', 'annual_income': 114394, 'state': 'CA', 'employment_status': 'Part-time', 'customer_segment': 'Premium', 'email': 'michael.gonzales@email.com', 'phone': '(672) 201-4656', 'ssn': '***-**-2707', 'address_line1': '2053 Mark Common Suite 157', 'address_line2': None, 'city': 'West Donaldton', 'zip_code': '44969', 'customer_since': '2023-04-15', 'employer_name': 'Mitchell Group', 'job_title': 'Teacher, English as a foreign language', 'household_size': 2}
    ],
    'income_ability_to_pay': [
        {'customer_id': 5, 'verified_annual_income': 111398.05645685742, 'debt_to_income_ratio': 0.3167581065732502, 'total_monthly_debt_payments': 3019.6022369450325, 'income_stability_score': 82.42473592743112}
    ]
}

print("Customer 5 demographics:", [c for c in MOCK_DATABASES['customer_demographics'] if c['customer_id'] == 5])
print("Customer 5 income data:", [c for c in MOCK_DATABASES['income_ability_to_pay'] if c['customer_id'] == 5])

# Test the extraction logic
customer_id = 5
demographics = next((c for c in MOCK_DATABASES["customer_demographics"] if c["customer_id"] == customer_id), None)
income_data = next((c for c in MOCK_DATABASES["income_ability_to_pay"] if c["customer_id"] == customer_id), None)

print("\nExtracted data:")
if demographics:
    print(f"Demographics annual_income: {demographics.get('annual_income')}")
if income_data:
    print(f"Income data verified_annual_income: {income_data.get('verified_annual_income')}")

# Test the profile building
customer_profile = {}
if demographics:
    customer_profile.update({
        "annual_income": demographics.get("annual_income"),  # Keep for reference
    })

if income_data:
    customer_profile.update({
        "verified_annual_income": income_data.get("verified_annual_income"),
        "income": income_data.get("verified_annual_income"),  # Use verified income as primary
    })

print(f"\nFinal customer profile income: {customer_profile.get('income')}")
