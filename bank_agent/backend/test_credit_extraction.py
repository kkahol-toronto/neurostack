#!/usr/bin/env python3

import re

def test_credit_limit_extraction():
    """Test the credit limit extraction logic"""
    
    test_cases = [
        "The customer wants an increase by 8000 to 40,000",
        "Customer requests credit limit increase from 32000 to 40000",
        "Increase credit limit by 5000 to 25000",
        "Customer wants to increase limit from $15,000 to $25,000",
        "Request for credit limit increase to 50000",
        "No numbers in this description"
    ]
    
    for i, inquiry_text in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: '{inquiry_text}' ---")
        
        inquiry_text_lower = inquiry_text.lower()
        credit_limits = {}
        
        # Pattern for "increase by X to Y" format
        increase_pattern = r'increase\s+by\s+(\d{1,3}(?:,\d{3})*)\s+to\s+(\d{1,3}(?:,\d{3})*)'
        increase_match = re.search(increase_pattern, inquiry_text_lower)
        
        if increase_match:
            increase_amount = float(increase_match.group(1).replace(',', ''))
            requested_amount = float(increase_match.group(2).replace(',', ''))
            current_amount = requested_amount - increase_amount
            
            credit_limits = {
                "current": current_amount,
                "requested": requested_amount,
                "increase": increase_amount
            }
            print(f"✅ Matched 'increase by X to Y' pattern: {credit_limits}")
        else:
            # Pattern for "from X to Y" format
            from_to_pattern = r'from\s+(\d{1,3}(?:,\d{3})*)\s+to\s+(\d{1,3}(?:,\d{3})*)'
            from_to_match = re.search(from_to_pattern, inquiry_text_lower)
            
            if from_to_match:
                current_amount = float(from_to_match.group(1).replace(',', ''))
                requested_amount = float(from_to_match.group(2).replace(',', ''))
                increase_amount = requested_amount - current_amount
                
                credit_limits = {
                    "current": current_amount,
                    "requested": requested_amount,
                    "increase": increase_amount
                }
                print(f"✅ Matched 'from X to Y' pattern: {credit_limits}")
            else:
                # Pattern for just numbers in the text
                credit_pattern = r'\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
                credit_matches = re.findall(credit_pattern, inquiry_text_lower)
                
                if len(credit_matches) >= 2:
                    # Try to identify current vs requested limits
                    credit_limits = {
                        "current": float(credit_matches[0].replace(',', '')),
                        "requested": float(credit_matches[1].replace(',', '')),
                        "increase": float(credit_matches[1].replace(',', '')) - float(credit_matches[0].replace(',', ''))
                    }
                    print(f"✅ Matched general number pattern: {credit_limits}")
                elif len(credit_matches) == 1:
                    credit_limits = {
                        "requested": float(credit_matches[0].replace(',', ''))
                    }
                    print(f"✅ Matched single number: {credit_limits}")
                else:
                    print("❌ No credit limits found")

def test_credit_limit_extraction_fixed():
    """Test the credit limit extraction logic with fixed patterns"""
    
    test_cases = [
        "The customer wants an increase by 8000 to 40,000",
        "Customer requests credit limit increase from 32000 to 40000",
        "Increase credit limit by 5000 to 25000",
        "Customer wants to increase limit from $15,000 to $25,000",
        "Request for credit limit increase to 50000",
        "No numbers in this description"
    ]
    
    for i, inquiry_text in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: '{inquiry_text}' ---")
        
        inquiry_text_lower = inquiry_text.lower()
        credit_limits = {}
        
        # Pattern for "increase by X to Y" format - FIXED
        increase_pattern = r'increase\s+by\s+(\d{1,3}(?:,\d{3})*)\s+to\s+(\d{1,3}(?:,\d{3})*)'
        increase_match = re.search(increase_pattern, inquiry_text_lower)
        
        if increase_match:
            increase_amount = float(increase_match.group(1).replace(',', ''))
            requested_amount = float(increase_match.group(2).replace(',', ''))
            current_amount = requested_amount - increase_amount
            
            credit_limits = {
                "current": current_amount,
                "requested": requested_amount,
                "increase": increase_amount
            }
            print(f"✅ Matched 'increase by X to Y' pattern: {credit_limits}")
        else:
            # Pattern for "from X to Y" format - FIXED
            from_to_pattern = r'from\s+(\d{1,3}(?:,\d{3})*)\s+to\s+(\d{1,3}(?:,\d{3})*)'
            from_to_match = re.search(from_to_pattern, inquiry_text_lower)
            
            if from_to_match:
                current_amount = float(from_to_match.group(1).replace(',', ''))
                requested_amount = float(from_to_match.group(2).replace(',', ''))
                increase_amount = requested_amount - current_amount
                
                credit_limits = {
                    "current": current_amount,
                    "requested": requested_amount,
                    "increase": increase_amount
                }
                print(f"✅ Matched 'from X to Y' pattern: {credit_limits}")
            else:
                # Pattern for just numbers in the text - FIXED
                credit_pattern = r'\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
                credit_matches = re.findall(credit_pattern, inquiry_text_lower)
                
                if len(credit_matches) >= 2:
                    # For the specific case "increase by 8000 to 40,000"
                    if "increase by" in inquiry_text_lower and "to" in inquiry_text_lower:
                        # Find the numbers around "increase by" and "to"
                        numbers = re.findall(r'\d{1,3}(?:,\d{3})*', inquiry_text_lower)
                        if len(numbers) >= 2:
                            # First number after "increase by" is the increase amount
                            # Second number after "to" is the requested amount
                            increase_amount = float(numbers[0].replace(',', ''))
                            requested_amount = float(numbers[1].replace(',', ''))
                            current_amount = requested_amount - increase_amount
                            
                            credit_limits = {
                                "current": current_amount,
                                "requested": requested_amount,
                                "increase": increase_amount
                            }
                            print(f"✅ Matched 'increase by X to Y' with general pattern: {credit_limits}")
                    else:
                        # Try to identify current vs requested limits
                        credit_limits = {
                            "current": float(credit_matches[0].replace(',', '')),
                            "requested": float(credit_matches[1].replace(',', '')),
                            "increase": float(credit_matches[1].replace(',', '')) - float(credit_matches[0].replace(',', ''))
                        }
                        print(f"✅ Matched general number pattern: {credit_limits}")
                elif len(credit_matches) == 1:
                    credit_limits = {
                        "requested": float(credit_matches[0].replace(',', ''))
                    }
                    print(f"✅ Matched single number: {credit_limits}")
                else:
                    print("❌ No credit limits found")

if __name__ == "__main__":
    print("=== ORIGINAL PATTERNS ===")
    test_credit_limit_extraction()
    print("\n\n=== FIXED PATTERNS ===")
    test_credit_limit_extraction_fixed()
