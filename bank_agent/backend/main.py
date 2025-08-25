from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import asyncio
import re
from datetime import datetime
import logging
from dotenv import load_dotenv
import httpx

# Azure OpenAI imports
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential

# NeuroStack imports
from neurostack_integration import (
    execute_neurostack_text_to_sql,
    execute_neurostack_customer_search,
    execute_neurostack_data_analysis,
    execute_neurostack_customer_verification,
    get_neurostack_integration
)
from neurostack_cosmos_memory import get_cosmos_memory_manager

# Import user management
from user_management import user_manager, get_current_user, get_current_active_user, get_current_user_optional, require_role, User
from user_models import (
    UserRegistrationRequest, UserLoginRequest, UserLoginResponse, UserProfileResponse,
    UserUpdateRequest, UserListResponse, UserBehaviorResponse, UserSessionsResponse
)

# Import report models and service
from models import (
    CreateReportRequest, UpdateReportRequest, ReportResponse, 
    ReportsListResponse, ReportStatus, CreditInquiryType,
    InvestigationStrategy, CreateStrategyRequest, UpdateStrategyRequest, 
    StrategyResponse, StrategiesListResponse,
    ExecuteInvestigationRequest, InvestigationExecutionResponse, DataSourcesResponse, InvestigationResultsResponse,
    ChatMessageRequest, ChatResponse, ChatHistoryResponse, ScenarioAnalysisResponse
)
from report_service import report_service
from investigation_service import investigation_service
from chat_service import ChatService

# Load environment variables from root directory
load_dotenv(dotenv_path="/Users/kanavkahol/work/neurostack/.env")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Banking Agent Backend",
    description="FastAPI backend for banking agent with Azure OpenAI text-to-SQL capabilities",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class TableInfo(BaseModel):
    table_name: str
    fields: List[str]
    sample_data: Optional[List[Dict[str, Any]]] = None

class TextToSQLRequest(BaseModel):
    natural_language_query: str
    tables: Optional[List[TableInfo]] = None
    table_name: Optional[str] = None  # For backward compatibility
    fields: Optional[List[str]] = None  # For backward compatibility

class SQLQueryRequest(BaseModel):
    sql: str
    table_name: Optional[str] = None

class QueryResult(BaseModel):
    success: bool
    sql: Optional[str] = None
    data: Optional[List[Dict[str, Any]]] = None
    execution_time: Optional[float] = None
    error: Optional[str] = None
    neurostack_features: Optional[Dict[str, Any]] = None

class DataSource(BaseModel):
    id: str
    name: str
    description: str
    category: str
    is_enabled: bool
    table_name: str
    fields: List[str]
    sample_query: Optional[str] = None

class CustomerSearchRequest(BaseModel):
    query: str

class Customer(BaseModel):
    customer_id: int
    first_name: str
    last_name: str
    annual_income: Optional[int] = None
    state: Optional[str] = None
    date_of_birth: Optional[str] = None
    employment_status: Optional[str] = None
    customer_segment: Optional[str] = None

# Add new Pydantic models for customer data request
class CustomerDataRequest(BaseModel):
    customer_id: int
    include_summary: bool = True

class CustomerDataResponse(BaseModel):
    success: bool
    customer_id: int
    data: Dict[str, Any]
    summary: Optional[str] = None
    neurostack_features: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Azure OpenAI client initialization
def get_azure_openai_client():
    """Initialize Azure OpenAI client with environment variables"""
    try:
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_key = os.getenv("AZURE_OPENAI_KEY")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        
        if not endpoint or not api_key:
            raise ValueError("Azure OpenAI endpoint and key must be set in environment variables")
        
        # Check if this is an APIM endpoint
        if "azure-api.net" in endpoint:
            # For APIM endpoints, we need to use the subscription key header
            # The endpoint should be the base APIM URL
            base_endpoint = endpoint.replace("/ai/", "")
            client = AzureOpenAI(
                azure_endpoint=base_endpoint,
                api_key=api_key,
                api_version=api_version,
                default_headers={
                    "Ocp-Apim-Subscription-Key": api_key
                }
            )
        else:
            # Standard Azure OpenAI endpoint
            client = AzureOpenAI(
                azure_endpoint=endpoint,
                api_key=api_key,
                api_version=api_version
            )
        
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Azure OpenAI client: {e}")
        raise

# Mock database for demo purposes
MOCK_DATABASES = {'customer_demographics': [{'customer_id': 1, 'first_name': 'John', 'last_name': 'Doe', 'date_of_birth': '1987-08-16', 'annual_income': 75000, 'state': 'CA', 'employment_status': 'Self-employed', 'customer_segment': 'Standard', 'email': 'john.doe@email.com', 'phone': '(524) 436-2415', 'ssn': '***-**-7119', 'address_line1': '131 Chad Well Suite 339', 'address_line2': None, 'city': 'Port Autumn', 'zip_code': '46708', 'customer_since': '2022-12-02', 'employer_name': 'Lam-Roman', 'job_title': 'Restaurant manager', 'household_size': 2}, {'customer_id': 2, 'first_name': 'Jane', 'last_name': 'Smith', 'date_of_birth': '1971-01-17', 'annual_income': 95000, 'state': 'NY', 'employment_status': 'Full-time', 'customer_segment': 'Standard', 'email': 'jane.smith@email.com', 'phone': '(203) 948-4006', 'ssn': '***-**-7069', 'address_line1': '772 Garner Port', 'address_line2': None, 'city': 'Austinfort', 'zip_code': '47055', 'customer_since': '2017-03-16', 'employer_name': 'Wade, Garcia and Bush', 'job_title': 'Sales professional, IT', 'household_size': 2}, {'customer_id': 3, 'first_name': 'Bob', 'last_name': 'Johnson', 'date_of_birth': '1968-07-20', 'annual_income': 65000, 'state': 'TX', 'employment_status': 'Full-time', 'customer_segment': 'Basic', 'email': 'bob.johnson@email.com', 'phone': '(511) 106-5782', 'ssn': '***-**-3003', 'address_line1': '752 Steven Roads', 'address_line2': None, 'city': 'North Benjaminberg', 'zip_code': '64689', 'customer_since': '2016-07-26', 'employer_name': 'Hahn Ltd', 'job_title': 'Producer, radio', 'household_size': 4}, {'customer_id': 4, 'first_name': 'Tom', 'last_name': 'Young', 'date_of_birth': '1982-09-08', 'annual_income': 64485, 'state': 'CA', 'employment_status': 'Full-time', 'customer_segment': 'Standard', 'email': 'tom.young@email.com', 'phone': '(743) 141-2569', 'ssn': '***-**-8190', 'address_line1': '51426 Cunningham Garden', 'address_line2': None, 'city': 'East Annborough', 'zip_code': '93429', 'customer_since': '2019-11-23', 'employer_name': 'Ray Inc', 'job_title': 'Accounting technician', 'household_size': 3}, {'customer_id': 5, 'first_name': 'Michael', 'last_name': 'Gonzales', 'date_of_birth': '1994-04-24', 'annual_income': 114394, 'state': 'CA', 'employment_status': 'Part-time', 'customer_segment': 'Premium', 'email': 'michael.gonzales@email.com', 'phone': '(672) 201-4656', 'ssn': '***-**-2707', 'address_line1': '2053 Mark Common Suite 157', 'address_line2': None, 'city': 'West Donaldton', 'zip_code': '44969', 'customer_since': '2023-04-15', 'employer_name': 'Mitchell Group', 'job_title': 'Teacher, English as a foreign language', 'household_size': 2}, {'customer_id': 6, 'first_name': 'Kyle', 'last_name': 'Johnson', 'date_of_birth': '2002-07-13', 'annual_income': 62859, 'state': 'OH', 'employment_status': 'Full-time', 'customer_segment': 'Standard', 'email': 'kyle.johnson@email.com', 'phone': '(910) 313-2876', 'ssn': '***-**-4213', 'address_line1': '7713 Carrillo Estates', 'address_line2': None, 'city': 'Goodmanmouth', 'zip_code': '03051', 'customer_since': '2021-03-05', 'employer_name': 'Kennedy-Taylor', 'job_title': 'Horticultural consultant', 'household_size': 2}, {'customer_id': 7, 'first_name': 'Thomas', 'last_name': 'Pratt', 'date_of_birth': '1994-12-20', 'annual_income': 109841, 'state': 'IL', 'employment_status': 'Full-time', 'customer_segment': 'Premium', 'email': 'thomas.pratt@email.com', 'phone': '(551) 311-5902', 'ssn': '***-**-6961', 'address_line1': '186 James Unions Apt. 037', 'address_line2': None, 'city': 'Georgeburgh', 'zip_code': '93674', 'customer_since': '2018-02-17', 'employer_name': 'Smith Ltd', 'job_title': 'Civil Service administrator', 'household_size': 5}, {'customer_id': 8, 'first_name': 'Brandon', 'last_name': 'Johnson', 'date_of_birth': '2000-06-19', 'annual_income': 64046, 'state': 'TX', 'employment_status': 'Full-time', 'customer_segment': 'Standard', 'email': 'brandon.johnson@email.com', 'phone': '(899) 326-6238', 'ssn': '***-**-9117', 'address_line1': '59945 Williams Harbor Apt. 076', 'address_line2': None, 'city': 'Nathanview', 'zip_code': '37621', 'customer_since': '2018-09-22', 'employer_name': 'Simmons-Howell', 'job_title': 'Analytical chemist', 'household_size': 2}, {'customer_id': 9, 'first_name': 'Jacqueline', 'last_name': 'Gray', 'date_of_birth': '1961-08-19', 'annual_income': 79181, 'state': 'OH', 'employment_status': 'Full-time', 'customer_segment': 'Standard', 'email': 'jacqueline.gray@email.com', 'phone': '(825) 589-6570', 'ssn': '***-**-5939', 'address_line1': '711 Scott Ridges', 'address_line2': None, 'city': 'Jennifermouth', 'zip_code': '25025', 'customer_since': '2021-12-26', 'employer_name': 'Lutz-Rodriguez', 'job_title': 'Engineer, electrical', 'household_size': 5}, {'customer_id': 10, 'first_name': 'John', 'last_name': 'Hoover', 'date_of_birth': '1968-11-21', 'annual_income': 82719, 'state': 'PA', 'employment_status': 'Full-time', 'customer_segment': 'Standard', 'email': 'john.hoover@email.com', 'phone': '(777) 593-1986', 'ssn': '***-**-7473', 'address_line1': '66865 Rachel Green', 'address_line2': None, 'city': 'Nelsonmouth', 'zip_code': '01513', 'customer_since': '2024-05-28', 'employer_name': 'Cooke and Sons', 'job_title': 'Surveyor, minerals', 'household_size': 3}], 'internal_banking_data': [{'customer_id': 1, 'current_credit_limit': 22000, 'current_balance': 10502.92131344284, 'utilization_rate': 47.740551424740175, 'on_time_payments_12m': 12, 'late_payments_12m': 1, 'tenure_months': 111}, {'customer_id': 2, 'current_credit_limit': 18000, 'current_balance': 10063.825291754425, 'utilization_rate': 55.91014050974681, 'on_time_payments_12m': 12, 'late_payments_12m': 0, 'tenure_months': 119}, {'customer_id': 3, 'current_credit_limit': 21000, 'current_balance': 12375.461518433758, 'utilization_rate': 58.93076913539884, 'on_time_payments_12m': 10, 'late_payments_12m': 2, 'tenure_months': 39}, {'customer_id': 4, 'current_credit_limit': 13000, 'current_balance': 6417.40839835151, 'utilization_rate': 49.364679987319306, 'on_time_payments_12m': 11, 'late_payments_12m': 2, 'tenure_months': 66}, {'customer_id': 5, 'current_credit_limit': 32000, 'current_balance': 6512.544260638192, 'utilization_rate': 20.35170081449435, 'on_time_payments_12m': 11, 'late_payments_12m': 0, 'tenure_months': 38}, {'customer_id': 6, 'current_credit_limit': 18000, 'current_balance': 9062.95104271733, 'utilization_rate': 50.349728015096275, 'on_time_payments_12m': 10, 'late_payments_12m': 0, 'tenure_months': 111}, {'customer_id': 7, 'current_credit_limit': 37000, 'current_balance': 18548.321611445284, 'utilization_rate': 50.13059894985212, 'on_time_payments_12m': 12, 'late_payments_12m': 2, 'tenure_months': 14}, {'customer_id': 8, 'current_credit_limit': 10000, 'current_balance': 5902.834361642002, 'utilization_rate': 59.028343616420024, 'on_time_payments_12m': 10, 'late_payments_12m': 1, 'tenure_months': 50}, {'customer_id': 9, 'current_credit_limit': 27000, 'current_balance': 17005.00818458548, 'utilization_rate': 62.98151179476104, 'on_time_payments_12m': 10, 'late_payments_12m': 2, 'tenure_months': 49}, {'customer_id': 10, 'current_credit_limit': 25000, 'current_balance': 13317.115518155157, 'utilization_rate': 53.26846207262063, 'on_time_payments_12m': 10, 'late_payments_12m': 0, 'tenure_months': 47}], 'credit_bureau_data': [{'customer_id': 1, 'fico_score_8': 687, 'fico_score_9': 680, 'total_accounts_bureau': 11, 'delinquencies_30_plus_12m': 2}, {'customer_id': 2, 'fico_score_8': 677, 'fico_score_9': 664, 'total_accounts_bureau': 4, 'delinquencies_30_plus_12m': 0}, {'customer_id': 3, 'fico_score_8': 636, 'fico_score_9': 646, 'total_accounts_bureau': 7, 'delinquencies_30_plus_12m': 2}, {'customer_id': 4, 'fico_score_8': 699, 'fico_score_9': 684, 'total_accounts_bureau': 14, 'delinquencies_30_plus_12m': 2}, {'customer_id': 5, 'fico_score_8': 724, 'fico_score_9': 722, 'total_accounts_bureau': 9, 'delinquencies_30_plus_12m': 0}, {'customer_id': 6, 'fico_score_8': 613, 'fico_score_9': 600, 'total_accounts_bureau': 13, 'delinquencies_30_plus_12m': 2}, {'customer_id': 7, 'fico_score_8': 744, 'fico_score_9': 755, 'total_accounts_bureau': 12, 'delinquencies_30_plus_12m': 2}, {'customer_id': 8, 'fico_score_8': 688, 'fico_score_9': 701, 'total_accounts_bureau': 8, 'delinquencies_30_plus_12m': 0}, {'customer_id': 9, 'fico_score_8': 661, 'fico_score_9': 666, 'total_accounts_bureau': 9, 'delinquencies_30_plus_12m': 1}, {'customer_id': 10, 'fico_score_8': 749, 'fico_score_9': 767, 'total_accounts_bureau': 12, 'delinquencies_30_plus_12m': 2}], 'fraud_kyc_compliance': [{'customer_id': 1, 'overall_fraud_risk_score': 3.833180872339027, 'risk_level': 'low', 'kyc_score': 87.55148872036064, 'identity_verification_status': 'verified'}, {'customer_id': 2, 'overall_fraud_risk_score': 3.3845604013486987, 'risk_level': 'low', 'kyc_score': 91.42505867290342, 'identity_verification_status': 'verified'}, {'customer_id': 3, 'overall_fraud_risk_score': 4.70160620619146, 'risk_level': 'low', 'kyc_score': 99.11862035234205, 'identity_verification_status': 'verified'}, {'customer_id': 4, 'overall_fraud_risk_score': 2.6444442346574197, 'risk_level': 'medium', 'kyc_score': 76.0861918767091, 'identity_verification_status': 'verified'}, {'customer_id': 5, 'overall_fraud_risk_score': 7.946254314885415, 'risk_level': 'low', 'kyc_score': 74.42342165879084, 'identity_verification_status': 'verified'}, {'customer_id': 6, 'overall_fraud_risk_score': 3.135137151902513, 'risk_level': 'medium', 'kyc_score': 89.34050138356436, 'identity_verification_status': 'verified'}, {'customer_id': 7, 'overall_fraud_risk_score': 4.1446330109242115, 'risk_level': 'low', 'kyc_score': 88.28153373249489, 'identity_verification_status': 'verified'}, {'customer_id': 8, 'overall_fraud_risk_score': 4.720554199915192, 'risk_level': 'low', 'kyc_score': 87.98770583587809, 'identity_verification_status': 'verified'}, {'customer_id': 9, 'overall_fraud_risk_score': 5.560533399506257, 'risk_level': 'low', 'kyc_score': 70.90835169988362, 'identity_verification_status': 'verified'}, {'customer_id': 10, 'overall_fraud_risk_score': 2.789346822584694, 'risk_level': 'low', 'kyc_score': 79.61913016692344, 'identity_verification_status': 'verified'}], 'income_ability_to_pay': [{'customer_id': 1, 'verified_annual_income': 75932.56333069566, 'debt_to_income_ratio': 0.20230207729985694, 'total_monthly_debt_payments': 1264.3879831241059, 'income_stability_score': 89.08880163249897}, {'customer_id': 2, 'verified_annual_income': 97386.78993845794, 'debt_to_income_ratio': 0.4213010074545644, 'total_monthly_debt_payments': 3335.2996423486347, 'income_stability_score': 93.801861293268}, {'customer_id': 3, 'verified_annual_income': 66396.22057920022, 'debt_to_income_ratio': 0.5477854542496878, 'total_monthly_debt_payments': 2967.1712105191423, 'income_stability_score': 81.8691405034217}, {'customer_id': 4, 'verified_annual_income': 63804.13202259315, 'debt_to_income_ratio': 0.4662816558696768, 'total_monthly_debt_payments': 2505.6810482296755, 'income_stability_score': 75.44613175710835}, {'customer_id': 5, 'verified_annual_income': 111398.05645685742, 'debt_to_income_ratio': 0.3167581065732502, 'total_monthly_debt_payments': 3019.6022369450325, 'income_stability_score': 82.42473592743112}, {'customer_id': 6, 'verified_annual_income': 65155.46865714394, 'debt_to_income_ratio': 0.25239909521171017, 'total_monthly_debt_payments': 1322.1295604927407, 'income_stability_score': 73.5447653541292}, {'customer_id': 7, 'verified_annual_income': 111697.1891462478, 'debt_to_income_ratio': 0.3368739029552933, 'total_monthly_debt_payments': 3083.5471978760306, 'income_stability_score': 79.2838867204519}, {'customer_id': 8, 'verified_annual_income': 66522.13648915158, 'debt_to_income_ratio': 0.41086361841433316, 'total_monthly_debt_payments': 2192.8476087470317, 'income_stability_score': 88.45103596272648}, {'customer_id': 9, 'verified_annual_income': 75748.62016811015, 'debt_to_income_ratio': 0.31703443762208305, 'total_monthly_debt_payments': 2091.9253171128466, 'income_stability_score': 78.45711209920695}, {'customer_id': 10, 'verified_annual_income': 82424.02550378154, 'debt_to_income_ratio': 0.4830624946710481, 'total_monthly_debt_payments': 3329.8705413912026, 'income_stability_score': 88.48918042444988}], 'open_banking_data': [{'customer_id': 1, 'open_banking_consent': False, 'avg_monthly_income': 5930.300230349518, 'cash_flow_stability_score': 84.13479297943562, 'expense_obligations_rent': 2431}, {'customer_id': 2, 'open_banking_consent': False, 'avg_monthly_income': 8330.344708991664, 'cash_flow_stability_score': 89.23520139097971, 'expense_obligations_rent': 889}, {'customer_id': 3, 'open_banking_consent': True, 'avg_monthly_income': 5926.328214958623, 'cash_flow_stability_score': 97.02388532194855, 'expense_obligations_rent': 2022}, {'customer_id': 4, 'open_banking_consent': False, 'avg_monthly_income': 5096.1385706394585, 'cash_flow_stability_score': 61.754200700274964, 'expense_obligations_rent': 1723}, {'customer_id': 5, 'open_banking_consent': False, 'avg_monthly_income': 9147.212899353815, 'cash_flow_stability_score': 81.51379994452373, 'expense_obligations_rent': 2175}, {'customer_id': 6, 'open_banking_consent': False, 'avg_monthly_income': 5265.243243051161, 'cash_flow_stability_score': 63.59282972077131, 'expense_obligations_rent': 1537}, {'customer_id': 7, 'open_banking_consent': False, 'avg_monthly_income': 8342.621538727915, 'cash_flow_stability_score': 98.12114056750016, 'expense_obligations_rent': 1037}, {'customer_id': 8, 'open_banking_consent': True, 'avg_monthly_income': 4972.256346271397, 'cash_flow_stability_score': 67.20952662029416, 'expense_obligations_rent': 2473}, {'customer_id': 9, 'open_banking_consent': True, 'avg_monthly_income': 6573.6436446930875, 'cash_flow_stability_score': 66.12059234566405, 'expense_obligations_rent': 1251}, {'customer_id': 10, 'open_banking_consent': False, 'avg_monthly_income': 7380.342520940033, 'cash_flow_stability_score': 75.20835535970673, 'expense_obligations_rent': 955}], 'state_economic_indicators': [{'state_code': 'CA', 'unemployment_rate': 5.646809813422138, 'macro_risk_score': 37.170520782533295, 'risk_level': 'medium', 'gdp_growth_rate': 4.325897349226025}, {'state_code': 'NY', 'unemployment_rate': 4.993932548730503, 'macro_risk_score': 43.05161731180951, 'risk_level': 'medium', 'gdp_growth_rate': 3.8865462834147944}, {'state_code': 'TX', 'unemployment_rate': 5.906421076732912, 'macro_risk_score': 51.731969114504565, 'risk_level': 'low', 'gdp_growth_rate': 4.136441195494254}, {'state_code': 'FL', 'unemployment_rate': 4.2720902882199105, 'macro_risk_score': 33.50540561047708, 'risk_level': 'low', 'gdp_growth_rate': 2.6448379861610167}, {'state_code': 'IL', 'unemployment_rate': 3.1867414823171405, 'macro_risk_score': 32.92949380226529, 'risk_level': 'low', 'gdp_growth_rate': 3.344595524152923}, {'state_code': 'PA', 'unemployment_rate': 3.3200820838729284, 'macro_risk_score': 48.9751659747833, 'risk_level': 'low', 'gdp_growth_rate': 2.8398773755665276}, {'state_code': 'OH', 'unemployment_rate': 4.015212606150735, 'macro_risk_score': 38.289954061761094, 'risk_level': 'low', 'gdp_growth_rate': 3.6235877736773356}, {'state_code': 'GA', 'unemployment_rate': 5.043991943986768, 'macro_risk_score': 46.281285717468876, 'risk_level': 'low', 'gdp_growth_rate': 2.854995438260856}, {'state_code': 'NC', 'unemployment_rate': 4.844191822483808, 'macro_risk_score': 53.16150796969741, 'risk_level': 'medium', 'gdp_growth_rate': 4.301356400508233}, {'state_code': 'MI', 'unemployment_rate': 5.318043359619665, 'macro_risk_score': 55.88017097670608, 'risk_level': 'low', 'gdp_growth_rate': 3.0333892730395653}]}

# Sample data sources
SAMPLE_DATA_SOURCES = [
    {
        "id": "customer_demographics",
        "name": "Customer Demographics",
        "description": "Basic customer information including age, income, employment status, and location.",
        "category": "demographics",
        "is_enabled": True,
        "table_name": "customer_demographics",
        "fields": ["customer_id", "first_name", "last_name", "date_of_birth", "annual_income", "employment_status", "customer_segment", "state"],
        "sample_query": "Show me customers with income above $70,000"
    },
    {
        "id": "internal_banking_data",
        "name": "Internal Banking Data",
        "description": "Banking relationship data including payment history, credit utilization, account relationships, and tenure.",
        "category": "banking",
        "is_enabled": True,
        "table_name": "internal_banking_data",
        "fields": ["customer_id", "current_credit_limit", "current_balance", "utilization_rate", "on_time_payments_12m", "late_payments_12m", "tenure_months"],
        "sample_query": "Find customers with utilization rate above 80%"
    },
    {
        "id": "credit_bureau_data",
        "name": "Credit Bureau Data",
        "description": "External credit information including FICO scores, external accounts, delinquencies, and credit history.",
        "category": "credit_bureau",
        "is_enabled": True,
        "table_name": "credit_bureau_data",
        "fields": ["customer_id", "fico_score_8", "fico_score_9", "total_accounts_bureau", "external_utilization_rate", "delinquencies_30_plus_12m"],
        "sample_query": "List customers with FICO score below 650"
    },
    {
        "id": "fraud_kyc_compliance",
        "name": "Fraud/KYC/Compliance",
        "description": "Fraud detection, KYC verification, and compliance monitoring data.",
        "category": "fraud",
        "is_enabled": True,
        "table_name": "fraud_kyc_compliance",
        "fields": ["customer_id", "overall_fraud_risk_score", "risk_level", "kyc_score", "identity_verification_status"],
        "sample_query": "Identify high-risk customers with fraud score above 7"
    },
    {
        "id": "income_ability_to_pay",
        "name": "Income & Ability-to-Pay",
        "description": "Verified income data, debt-to-income ratios, and payment capacity metrics. Determines customer ability to handle additional credit.",
        "category": "income",
        "is_enabled": True,
        "table_name": "income_ability_to_pay",
        "fields": ["customer_id", "verified_annual_income", "debt_to_income_ratio", "total_monthly_debt_payments", "income_stability_score"],
        "sample_query": "Show customers with debt-to-income ratio above 40%"
    },
    {
        "id": "open_banking_data",
        "name": "Open Banking Data",
        "description": "Transaction data and alternative financial information from external sources. Provides insights into spending patterns and cash flow.",
        "category": "open_banking",
        "is_enabled": False,
        "table_name": "open_banking_data",
        "fields": ["customer_id", "open_banking_consent", "avg_monthly_income", "cash_flow_stability_score", "expense_obligations_rent"],
        "sample_query": "Find customers with open banking consent and stable cash flow"
    },
    {
        "id": "economic_indicators",
        "name": "Economic Indicators",
        "description": "Regional economic data including unemployment rates, GDP growth, and market conditions. Provides macro-economic context for decisions.",
        "category": "economic",
        "is_enabled": True,
        "table_name": "state_economic_indicators",
        "fields": ["state_code", "unemployment_rate", "macro_risk_score", "risk_level", "gdp_growth_rate"],
        "sample_query": "Show states with high unemployment rates"
    }
]

async def convert_text_to_sql(natural_language_query: str, tables: List[TableInfo]) -> str:
    """Convert natural language query to SQL using Azure OpenAI for multiple tables"""
    try:
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_key = os.getenv("AZURE_OPENAI_KEY")
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        
        if not deployment_name:
            raise ValueError("Azure OpenAI deployment name must be set in environment variables")
        
        # Build the prompt for multiple tables with intelligent selection guidance
        tables_info = []
        for table in tables:
            tables_info.append(f"Table: {table.table_name}\nAvailable fields: {', '.join(table.fields)}")
        
        tables_text = "\n\n".join(tables_info)
        
        prompt = f"""
You are a SQL expert. Convert the following natural language query to a MySQL SELECT statement.

Available Tables and Fields:
{tables_text}

Natural language query: "{natural_language_query}"

Instructions:
1. Analyze the query and determine which tables are relevant
2. Use JOINs to combine data from multiple tables when needed
3. Only include tables that are actually needed for the query
4. Use appropriate WHERE clauses, ORDER BY, and LIMIT as needed
5. For customer-related queries, typically join on customer_id
6. Only return the SQL query, no explanations or markdown formatting

SQL Query:
"""
        
        # Check if this is an APIM endpoint
        if "azure-api.net" in endpoint:
            # Use direct HTTP request for APIM
            
            # For APIM, we need to use the correct path format
            # Remove any trailing slashes and ensure proper format
            base_endpoint = endpoint.rstrip('/')
            url = f"{base_endpoint}/openai/deployments/{deployment_name}/chat/completions?api-version={api_version}"
            
            headers = {
                "Content-Type": "application/json",
                "Ocp-Apim-Subscription-Key": api_key,
                "User-Agent": "BankingAgent/1.0"
            }
            
            data = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a SQL expert. Convert natural language queries to MySQL SQL statements. Only return the SQL query, no explanations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.1
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                logger.info(f"Making request to APIM: {url}")
                logger.info(f"Deployment: {deployment_name}")
                logger.info(f"API Version: {api_version}")
                
                try:
                    response = await client.post(url, json=data, headers=headers)
                    logger.info(f"Response status: {response.status_code}")
                    
                    if response.status_code != 200:
                        logger.error(f"APIM Error: {response.text}")
                        # Try to get more details from the error response
                        try:
                            error_data = response.json()
                            error_msg = error_data.get('message', response.text)
                        except:
                            error_msg = response.text
                        raise Exception(f"APIM returned status {response.status_code}: {error_msg}")
                    
                    result = response.json()
                    sql_query = result["choices"][0]["message"]["content"].strip()
                    
                except httpx.TimeoutException:
                    logger.error("APIM request timed out")
                    raise Exception("APIM request timed out after 30 seconds")
                except httpx.RequestError as e:
                    logger.error(f"APIM request error: {e}")
                    raise Exception(f"APIM request failed: {str(e)}")
        else:
            # Use Azure OpenAI SDK for standard endpoints
            client = get_azure_openai_client()
            response = client.chat.completions.create(
                model=deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a SQL expert. Convert natural language queries to MySQL SQL statements. Only return the SQL query, no explanations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.1
            )
            sql_query = response.choices[0].message.content.strip()
        
        logger.info(f"Generated SQL: {sql_query}")
        return sql_query
        
    except Exception as e:
        logger.error(f"Error converting text to SQL: {e}")
        
        # Fallback to mock SQL generation for demo purposes
        logger.warning("Falling back to mock SQL generation")
        try:
            sql_query = generate_mock_sql(natural_language_query, tables)
            logger.info(f"Generated mock SQL: {sql_query}")
            return sql_query
        except Exception as fallback_error:
            logger.error(f"Mock SQL generation also failed: {fallback_error}")
            raise HTTPException(status_code=500, detail=f"Failed to convert text to SQL: {str(e)}")

def generate_mock_sql(natural_language_query: str, tables: List[TableInfo]) -> str:
    """Generate mock SQL for demo purposes with intelligent table selection"""
    query_lower = natural_language_query.lower()
    
    # Get all table names for reference
    table_names = [table.table_name for table in tables]
    
    # Intelligent table selection based on query content
    selected_tables = []
    
    # Check for customer demographics related queries
    if any(word in query_lower for word in ["customer", "income", "demographic", "name", "location", "john"]):
        if "customer_demographics" in table_names:
            selected_tables.append("customer_demographics")
    
    # Check for banking related queries
    if any(word in query_lower for word in ["banking", "credit", "utilization", "balance", "payment"]):
        if "internal_banking_data" in table_names:
            selected_tables.append("internal_banking_data")
    
    # Check for credit bureau related queries
    if any(word in query_lower for word in ["fico", "credit score", "bureau", "external", "credit risk", "delinquencies"]):
        if "credit_bureau_data" in table_names:
            selected_tables.append("credit_bureau_data")
    
    # Check for fraud related queries
    if any(word in query_lower for word in ["fraud", "risk", "kyc", "compliance"]):
        if "fraud_kyc_compliance" in table_names:
            selected_tables.append("fraud_kyc_compliance")
    
    # Check for income/ability to pay queries
    if any(word in query_lower for word in ["debt", "ratio", "ability", "payment capacity"]):
        if "income_ability_to_pay" in table_names:
            selected_tables.append("income_ability_to_pay")
    
    # Check for open banking queries
    if any(word in query_lower for word in ["open banking", "transaction", "cash flow", "spending"]):
        if "open_banking_data" in table_names:
            selected_tables.append("open_banking_data")
    
    # Check for economic queries
    if any(word in query_lower for word in ["economic", "unemployment", "gdp", "macro"]):
        if "state_economic_indicators" in table_names:
            selected_tables.append("state_economic_indicators")
    
    # If no specific tables identified, use customer_demographics as default
    if not selected_tables and "customer_demographics" in table_names:
        selected_tables = ["customer_demographics"]
    
    # Generate SQL based on selected tables
    if len(selected_tables) == 1:
        table_name = selected_tables[0]
        # Find the table info
        table_info = next((t for t in tables if t.table_name == table_name), None)
        if table_info:
            fields = table_info.fields
            
            if "john" in query_lower:
                return f"SELECT {', '.join(fields[:4])} FROM {table_name} WHERE first_name = 'John'"
            
            elif "income" in query_lower and ("above" in query_lower or ">" in query_lower):
                numbers = re.findall(r'\d+', natural_language_query)
                threshold = int(numbers[0]) if numbers else 50000
                return f"SELECT {', '.join(fields[:4])} FROM {table_name} WHERE annual_income > {threshold} ORDER BY annual_income DESC"
            
            elif "fico" in query_lower and ("below" in query_lower or "<" in query_lower):
                numbers = re.findall(r'\d+', natural_language_query)
                threshold = int(numbers[0]) if numbers else 650
                return f"SELECT {', '.join(fields[:4])} FROM {table_name} WHERE fico_score_8 < {threshold} ORDER BY fico_score_8 ASC"
            
            else:
                return f"SELECT {', '.join(fields[:4])} FROM {table_name} LIMIT 10"
    
    elif len(selected_tables) >= 2:
        # Multi-table JOIN query
        if "customer_demographics" in selected_tables and "internal_banking_data" in selected_tables:
            return f"""
SELECT cd.customer_id, cd.first_name, cd.last_name, cd.annual_income, 
       ibd.current_credit_limit, ibd.utilization_rate
FROM customer_demographics cd
JOIN internal_banking_data ibd ON cd.customer_id = ibd.customer_id
WHERE cd.annual_income > 50000
ORDER BY cd.annual_income DESC
LIMIT 10
"""
        elif "customer_demographics" in selected_tables and "credit_bureau_data" in selected_tables:
            # Check if this is a credit risk query
            if "credit risk" in query_lower or "risk" in query_lower or "john" in query_lower:
                return f"""
SELECT cd.customer_id, cd.first_name, cd.last_name, cbd.fico_score_8, cbd.fico_score_9, cbd.delinquencies_30_plus_12m
FROM customer_demographics cd
JOIN credit_bureau_data cbd ON cd.customer_id = cbd.customer_id
WHERE cd.first_name = 'John'
"""
            else:
                return f"""
SELECT cd.customer_id, cd.first_name, cd.last_name, cd.annual_income,
       cbd.fico_score_8, cbd.total_accounts_bureau
FROM customer_demographics cd
JOIN credit_bureau_data cbd ON cd.customer_id = cbd.customer_id
WHERE cbd.fico_score_8 > 700
ORDER BY cbd.fico_score_8 DESC
LIMIT 10
"""
        elif "customer_demographics" in selected_tables and "fraud_kyc_compliance" in selected_tables:
            return f"""
SELECT cd.customer_id, cd.first_name, cd.last_name, cd.annual_income,
       fk.overall_fraud_risk_score, fk.risk_level
FROM customer_demographics cd
JOIN fraud_kyc_compliance fk ON cd.customer_id = fk.customer_id
WHERE fk.risk_level = 'high'
ORDER BY fk.overall_fraud_risk_score DESC
LIMIT 10
"""
        else:
            # Generic multi-table query
            return f"""
SELECT * FROM {selected_tables[0]} t1
JOIN {selected_tables[1]} t2 ON t1.customer_id = t2.customer_id
LIMIT 10
"""
    
    # Fallback
    return f"SELECT * FROM {table_names[0]} LIMIT 5"

def execute_mock_sql(sql_query: str, table_name: str) -> List[Dict[str, Any]]:
    """Execute SQL query against mock database"""
    try:
        sql_lower = sql_query.lower()
        
        # Check if this is a JOIN query
        if "join" in sql_lower:
            return execute_mock_join_sql(sql_query)
        
        # Single table query
        if table_name not in MOCK_DATABASES:
            return []
        
        data = MOCK_DATABASES[table_name].copy()
        
        # Simple SQL parsing for demo purposes
        # Filter by WHERE conditions
        if "where" in sql_lower:
            # Handle name filtering
            if "first_name = 'john'" in sql_lower:
                data = [row for row in data if row.get('first_name', '').lower() == 'john']
            
            # Handle fraud risk score filtering
            if "overall_fraud_risk_score >" in sql_lower:
                import re
                numbers = re.findall(r'overall_fraud_risk_score > (\d+(?:\.\d+)?)', sql_lower)
                if numbers:
                    threshold = float(numbers[0])
                    data = [row for row in data if row.get('overall_fraud_risk_score', 0) > threshold]
            
            # Handle risk level filtering
            if "risk_level = 'high'" in sql_lower:
                data = [row for row in data if row.get('risk_level') == 'high']
            
            # Handle income filtering
            if "annual_income >" in sql_lower:
                import re
                numbers = re.findall(r'annual_income > (\d+)', sql_lower)
                if numbers:
                    threshold = int(numbers[0])
                    data = [row for row in data if row.get('annual_income', 0) > threshold]
            
            # Handle FICO score filtering
            if "fico_score_8 <" in sql_lower:
                import re
                numbers = re.findall(r'fico_score_8 < (\d+)', sql_lower)
                if numbers:
                    threshold = int(numbers[0])
                    data = [row for row in data if row.get('fico_score_8', 0) < threshold]
            
            # Handle utilization rate filtering
            if "utilization_rate >" in sql_lower:
                import re
                numbers = re.findall(r'utilization_rate > ([\d.]+)', sql_lower)
                if numbers:
                    threshold = float(numbers[0])
                    data = [row for row in data if row.get('utilization_rate', 0) > threshold]
        
        # Handle ORDER BY
        if "order by" in sql_lower:
            if "overall_fraud_risk_score desc" in sql_lower:
                data.sort(key=lambda x: x.get('overall_fraud_risk_score', 0), reverse=True)
            elif "annual_income desc" in sql_lower:
                data.sort(key=lambda x: x.get('annual_income', 0), reverse=True)
            elif "fico_score_8 asc" in sql_lower:
                data.sort(key=lambda x: x.get('fico_score_8', 0))
            elif "utilization_rate desc" in sql_lower:
                data.sort(key=lambda x: x.get('utilization_rate', 0), reverse=True)
        
        # Handle LIMIT
        if "limit" in sql_lower:
            import re
            numbers = re.findall(r'limit (\d+)', sql_lower)
            if numbers:
                limit = int(numbers[0])
                data = data[:limit]
        
        return data
        
    except Exception as e:
        logger.error(f"Error executing mock SQL: {e}")
        return []

def execute_mock_join_sql(sql_query: str) -> List[Dict[str, Any]]:
    """Execute JOIN SQL query against mock database"""
    try:
        sql_lower = sql_query.lower()
        logger.info(f"Executing JOIN SQL: {sql_query}")
        
        # Extract tables from JOIN
        tables = []
        if "customer_demographics" in sql_lower:
            tables.append("customer_demographics")
        if "internal_banking_data" in sql_lower:
            tables.append("internal_banking_data")
        if "credit_bureau_data" in sql_lower:
            tables.append("credit_bureau_data")
        if "fraud_kyc_compliance" in sql_lower:
            tables.append("fraud_kyc_compliance")
        if "income_ability_to_pay" in sql_lower:
            tables.append("income_ability_to_pay")
        if "open_banking_data" in sql_lower:
            tables.append("open_banking_data")
        if "state_economic_indicators" in sql_lower:
            tables.append("state_economic_indicators")
        
        logger.info(f"Detected tables: {tables}")
        
        # Get data from all tables
        all_data = {}
        for table in tables:
            if table in MOCK_DATABASES:
                all_data[table] = MOCK_DATABASES[table]
        
        logger.info(f"Available data: {list(all_data.keys())}")
        
        # Perform JOIN on customer_id
        joined_data = []
        
        # Get all unique customer IDs
        customer_ids = set()
        for table_data in all_data.values():
            for row in table_data:
                if 'customer_id' in row:
                    customer_ids.add(row['customer_id'])
        
        logger.info(f"Customer IDs found: {customer_ids}")
        
        # Join data for each customer
        for customer_id in customer_ids:
            joined_row = {}
            
            # Merge data from all tables for this customer
            for table_name, table_data in all_data.items():
                for row in table_data:
                    if row.get('customer_id') == customer_id:
                        # Add table prefix to avoid column name conflicts
                        for key, value in row.items():
                            if key == 'customer_id':
                                joined_row[key] = value
                            elif table_name == 'customer_demographics':
                                # Don't prefix customer_demographics columns
                                joined_row[key] = value
                            else:
                                # Add prefix for other tables
                                prefix = table_name.split('_')[0]
                                joined_row[f"{prefix}_{key}"] = value
            
            logger.info(f"Joined row for customer {customer_id}: {joined_row}")
            
            # Apply WHERE conditions
            if "where" in sql_lower:
                # Handle name filtering
                if "first_name = 'john'" in sql_lower:
                    logger.info(f"Checking first_name filter: {joined_row.get('first_name', '')}")
                    if joined_row.get('first_name', '').lower() != 'john':
                        logger.info(f"Filtered out customer {customer_id} - name doesn't match")
                        continue
                    else:
                        logger.info(f"Customer {customer_id} matches John filter")
                
                # Add more WHERE conditions as needed
                pass
            
            if joined_row:  # Only add if row has data
                joined_data.append(joined_row)
                logger.info(f"Added joined row: {joined_row}")
        
        logger.info(f"Final joined data: {joined_data}")
        
        # Handle ORDER BY
        if "order by" in sql_lower:
            if "annual_income desc" in sql_lower:
                joined_data.sort(key=lambda x: x.get('annual_income', 0), reverse=True)
            elif "fico_score_8 desc" in sql_lower:
                joined_data.sort(key=lambda x: x.get('cbd_fico_score_8', 0), reverse=True)
        
        # Handle LIMIT
        if "limit" in sql_lower:
            import re
            numbers = re.findall(r'limit (\d+)', sql_lower)
            if numbers:
                limit = int(numbers[0])
                joined_data = joined_data[:limit]
        
        return joined_data
        
    except Exception as e:
        logger.error(f"Error executing mock JOIN SQL: {e}")
        return []

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Banking Agent Backend API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "azure_openai_configured": bool(os.getenv("AZURE_OPENAI_ENDPOINT") and os.getenv("AZURE_OPENAI_KEY"))
    }

@app.post("/api/text-to-sql", response_model=QueryResult)
async def text_to_sql(
    request: TextToSQLRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Convert natural language to SQL using NeuroStack integration"""
    start_time = datetime.now()
    
    try:
        # Use NeuroStack integration for enhanced text-to-SQL
        if request.tables:
            # Multi-table query with NeuroStack
            result = await execute_neurostack_text_to_sql(
                natural_query=request.natural_language_query,
                tables=request.tables,
                user_id=current_user.user_id
            )
            
            if result["success"]:
                    # Execute the generated SQL
                    sql_result = execute_mock_sql(result["sql"], request.tables[0].table_name if request.tables else None)
                    
                    execution_time = (datetime.now() - start_time).total_seconds() * 1000
                    
                    # Store query results for learning with enhanced memory
                    try:
                        cosmos_memory = await get_cosmos_memory_manager()
                        await cosmos_memory.store_query_result({
                            "query": request.natural_language_query,
                            "sql": result["sql"],
                            "data": sql_result,  # sql_result is already a list
                            "result_count": len(sql_result),
                            "tables": [t.table_name for t in request.tables],
                            "query_type": "text_to_sql",
                            "success": True,
                            "execution_time": execution_time,
                            "user_id": current_user.user_id
                        })
                        
                        # Get optimization suggestions for the response
                        optimization_suggestions = await cosmos_memory.get_optimization_suggestions(
                            request.natural_language_query, 
                            current_user.user_id
                        )
                        
                        # Add optimization suggestions to neurostack features
                        result["neurostack_features"]["optimization_suggestions"] = optimization_suggestions
                        result["neurostack_features"]["persistent_memory"] = True
                        result["neurostack_features"]["historical_learning"] = True
                        
                    except Exception as e:
                        logger.error(f"Failed to store query result: {str(e)}")
                    
                    return QueryResult(
                        success=True,
                        sql=result["sql"],
                        data=sql_result,  # sql_result is already a list
                        execution_time=execution_time,
                        neurostack_features=result.get("neurostack_features", {})
                    )
            else:
                return QueryResult(
                    success=False,
                    error=result["error"]
                )
        else:
            # Fallback to original logic for backward compatibility
            if not request.table_name or not request.fields:
                raise ValueError("Either 'tables' or both 'table_name' and 'fields' must be provided")
            
            # Create a single table info for backward compatibility
            table_info = TableInfo(
                table_name=request.table_name,
                fields=request.fields
            )
            sql_query = await convert_text_to_sql(
                request.natural_language_query,
                [table_info]
            )
            primary_table = request.table_name
            
            # Execute the SQL query (mock execution for demo)
            data = execute_mock_sql(sql_query, primary_table)
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return QueryResult(
                success=True,
                sql=sql_query,
                data=data,
                execution_time=execution_time
            )
        
    except Exception as e:
        logger.error(f"Error in text-to-sql endpoint: {e}")
        return QueryResult(
            success=False,
            error=str(e)
        )

@app.post("/api/query", response_model=QueryResult)
async def execute_sql(request: SQLQueryRequest):
    """Execute a SQL query directly"""
    start_time = datetime.now()
    
    try:
        # For demo purposes, we'll use a default table if not specified
        table_name = request.table_name or "customer_demographics"
        
        # Execute the SQL query (mock execution for demo)
        data = execute_mock_sql(request.sql, table_name)
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return QueryResult(
            success=True,
            sql=request.sql,
            data=data,
            execution_time=execution_time
        )
        
    except Exception as e:
        logger.error(f"Error executing SQL: {e}")
        return QueryResult(
            success=False,
            error=str(e)
        )

@app.get("/api/datasources", response_model=List[DataSource])
async def get_data_sources():
    """Get available data sources"""
    return SAMPLE_DATA_SOURCES

@app.get("/api/sample/{table_name}")
async def get_sample_data(table_name: str, limit: int = 5):
    """Get sample data from a specific table"""
    try:
        if table_name in MOCK_DATABASES:
            data = MOCK_DATABASES[table_name][:limit]
            return {"data": data, "count": len(data)}
        else:
            return {"data": [], "count": 0, "error": f"Table {table_name} not found"}
    except Exception as e:
        logger.error(f"Error getting sample data: {e}")
        return {"data": [], "count": 0, "error": str(e)}

@app.post("/api/search-customers")
async def search_customers(request: CustomerSearchRequest):
    """Search customers using NeuroStack integration"""
    try:
        # Use NeuroStack integration for enhanced customer search
        result = await execute_neurostack_customer_search(
            query=request.query,
            search_type="semantic",
            user_id="demo_user"
        )
        
        if result["success"]:
            return {
                "success": True,
                "customers": result["customers"],
                "total_count": result["count"],
                "neurostack_features": result.get("neurostack_features", {})
            }
        else:
            # Fallback to direct search if NeuroStack fails
            integration = await get_neurostack_integration()
            customers = integration.search_customers_direct(request.query)
            
            return {
                "success": True,
                "customers": customers,
                "total_count": len(customers),
                "neurostack_features": {"fallback_used": True}
            }
            
    except Exception as e:
        logger.error(f"Error searching customers: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "customers": [],
            "total_count": 0
        }

# NeuroStack-specific endpoints
@app.get("/api/neurostack/tools")
async def get_neurostack_tools():
    """Get available NeuroStack tools"""
    try:
        integration = await get_neurostack_integration()
        return {
            "success": True,
            "tools": integration.get_available_tools(),
            "schemas": integration.get_tool_schemas()
        }
    except Exception as e:
        logger.error(f"Error getting NeuroStack tools: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/neurostack/data-analysis")
async def neurostack_data_analysis(analysis_type: str, data_source: str = "customer_demographics"):
    """Execute data analysis using NeuroStack"""
    try:
        result = await execute_neurostack_data_analysis(
            analysis_type=analysis_type,
            data_source=data_source,
            user_id="demo_user"
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in NeuroStack data analysis: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/neurostack/recent-activity")
async def get_neurostack_recent_activity(hours: int = 24):
    """Get recent activity from NeuroStack memory"""
    try:
        integration = await get_neurostack_integration()
        activity = await integration.get_recent_activity(hours)
        
        return {
            "success": True,
            "activity": activity
        }
        
    except Exception as e:
        logger.error(f"Error getting recent activity: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/neurostack/similar-queries")
async def get_similar_queries(query: str, limit: int = 5):
    """Get similar queries from NeuroStack memory"""
    try:
        cosmos_memory = await get_cosmos_memory_manager()
        similar_queries = await cosmos_memory.get_similar_queries(query, limit)
        
        return {
            "success": True,
            "similar_queries": similar_queries
        }
        
    except Exception as e:
        logger.error(f"Error getting similar queries: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/neurostack/query-analytics")
async def get_query_analytics(hours: int = 24):
    """Get comprehensive query analytics"""
    try:
        cosmos_memory = await get_cosmos_memory_manager()
        analytics = await cosmos_memory.get_query_analytics(hours)
        
        return {
            "success": True,
            "analytics": analytics
        }
        
    except Exception as e:
        logger.error(f"Error getting query analytics: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/neurostack/optimization-suggestions")
async def get_optimization_suggestions(query: str, user_id: Optional[str] = None):
    """Get optimization suggestions based on historical patterns"""
    try:
        cosmos_memory = await get_cosmos_memory_manager()
        suggestions = await cosmos_memory.get_optimization_suggestions(query, user_id)
        
        return {
            "success": True,
            "suggestions": suggestions
        }
        
    except Exception as e:
        logger.error(f"Error getting optimization suggestions: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/neurostack/user-behavior/{user_id}")
async def get_user_behavior(user_id: str):
    """Get user behavior patterns"""
    try:
        cosmos_memory = await get_cosmos_memory_manager()
        behavior = await cosmos_memory.get_user_behavior(user_id)
        
        return {
            "success": True,
            "behavior": behavior
        }
        
    except Exception as e:
        logger.error(f"Error getting user behavior: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/neurostack/query-patterns")
async def get_query_patterns(query_type: Optional[str] = None):
    """Get query patterns for learning and optimization"""
    try:
        cosmos_memory = await get_cosmos_memory_manager()
        patterns = await cosmos_memory.get_query_patterns(query_type)
        
        return {
            "success": True,
            "patterns": patterns
        }
        
    except Exception as e:
        logger.error(f"Error getting query patterns: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

# ============================================================================
# USER MANAGEMENT ENDPOINTS
# ============================================================================

@app.post("/api/auth/register", response_model=UserProfileResponse)
async def register_user(request: UserRegistrationRequest):
    """Register a new user."""
    try:
        user_data = user_manager.register_user(
            username=request.username,
            email=request.email,
            first_name=request.first_name,
            last_name=request.last_name,
            password=request.password,
            role=request.role,
            department=request.department
        )
        
        return UserProfileResponse(
            user_id=user_data["user_id"],
            username=user_data["username"],
            email=user_data["email"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            role=user_data["role"],
            department=user_data["department"],
            is_active=True,
            created_at=datetime.fromisoformat(user_data["created_at"]),
            last_login=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/auth/login", response_model=UserLoginResponse)
async def login_user(request: UserLoginRequest, client_request: Request):
    """Login user and return JWT token."""
    try:
        # Authenticate user
        user = user_manager.authenticate_user(request.username, request.password)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password"
            )
        
        # Create session
        session = user_manager.create_session(
            user=user,
            ip_address=client_request.client.host if client_request.client else "unknown",
            user_agent=client_request.headers.get("user-agent", "unknown")
        )
        
        return UserLoginResponse(
            access_token=session.token,
            token_type="bearer",
            user_id=user.user_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
            department=user.department,
            expires_at=session.expires_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging in user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/auth/profile", response_model=UserProfileResponse)
async def get_user_profile(current_user: User = Depends(get_current_active_user)):
    """Get current user's profile."""
    return UserProfileResponse(
        user_id=current_user.user_id,
        username=current_user.username,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        role=current_user.role,
        department=current_user.department,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )

@app.put("/api/auth/profile", response_model=UserProfileResponse)
async def update_user_profile(
    request: UserUpdateRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Update current user's profile."""
    try:
        # Only allow users to update their own profile (except admins)
        if current_user.role != "admin":
            # Remove role and is_active from update if not admin
            update_data = request.dict(exclude_unset=True)
            update_data.pop("role", None)
            update_data.pop("is_active", None)
        else:
            update_data = request.dict(exclude_unset=True)
        
        updated_user = user_manager.update_user(current_user.user_id, **update_data)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserProfileResponse(
            user_id=updated_user.user_id,
            username=updated_user.username,
            email=updated_user.email,
            first_name=updated_user.first_name,
            last_name=updated_user.last_name,
            role=updated_user.role,
            department=updated_user.department,
            is_active=updated_user.is_active,
            created_at=updated_user.created_at,
            last_login=updated_user.last_login
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/users", response_model=UserListResponse)
async def list_users(
    role: Optional[str] = None,
    current_user: User = Depends(require_role("admin"))
):
    """List all users (admin only)."""
    try:
        users_data = user_manager.list_users(role=role)
        users = [
            UserProfileResponse(
                user_id=user["user_id"],
                username=user["username"],
                email=user["email"],
                first_name=user["first_name"],
                last_name=user["last_name"],
                role=user["role"],
                department=user["department"],
                is_active=user["is_active"],
                created_at=datetime.fromisoformat(user["created_at"]),
                last_login=datetime.fromisoformat(user["last_login"]) if user["last_login"] else None
            )
            for user in users_data
        ]
        
        return UserListResponse(users=users, total_count=len(users))
        
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/users/{user_id}/behavior", response_model=UserBehaviorResponse)
async def get_user_behavior_enhanced(
    user_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get enhanced user behavior with profile information."""
    try:
        # Check if user can access this data (own data or admin)
        if current_user.user_id != user_id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get user profile
        user = user_manager.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get behavior data
        cosmos_memory = await get_cosmos_memory_manager()
        behavior = await cosmos_memory.get_user_behavior(user_id)
        
        if not behavior:
            # Return empty behavior for new users
            return UserBehaviorResponse(
                user_id=user.user_id,
                username=user.username,
                total_queries=0,
                preferred_query_types=[],
                common_tables=[],
                avg_query_complexity=0.0,
                last_activity=user.last_login or user.created_at,
                department=user.department,
                role=user.role
            )
        
        return UserBehaviorResponse(
            user_id=user.user_id,
            username=user.username,
            total_queries=behavior.get("total_queries", 0),
            preferred_query_types=behavior.get("preferred_query_types", []),
            common_tables=behavior.get("common_tables", []),
            avg_query_complexity=behavior.get("avg_query_complexity", 0.0),
            last_activity=datetime.fromisoformat(behavior["last_activity"]) if isinstance(behavior["last_activity"], str) else behavior["last_activity"],
            department=user.department,
            role=user.role
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user behavior: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/auth/logout")
async def logout_user(current_user: User = Depends(get_current_active_user)):
    """Logout user (invalidate session)."""
    try:
        # In a real implementation, you would invalidate the JWT token
        # For now, we'll just return success
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        logger.error(f"Error logging out user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/customer-data", response_model=CustomerDataResponse)
async def get_customer_data(request: CustomerDataRequest, current_user: User = Depends(get_current_user)):
    """Get comprehensive customer data from all enabled data sources with LLM summary"""
    try:
        customer_id = request.customer_id
        include_summary = request.include_summary
        
        # Get enabled data sources
        enabled_sources = [source for source in SAMPLE_DATA_SOURCES if source["is_enabled"]]
        
        # Collect data from all enabled sources
        customer_data = {}
        neurostack_features = {}
        
        for source in enabled_sources:
            table_name = source["table_name"]
            if table_name in MOCK_DATABASES:
                # Find customer data in this table
                table_data = MOCK_DATABASES[table_name]
                customer_record = None
                
                # Handle different table structures
                if table_name == "state_economic_indicators":
                    # For economic indicators, we need to join with customer demographics
                    customer_demo = next((c for c in MOCK_DATABASES["customer_demographics"] if c["customer_id"] == customer_id), None)
                    if customer_demo:
                        state_code = customer_demo["state"]
                        customer_record = next((e for e in table_data if e["state_code"] == state_code), None)
                else:
                    # For customer-specific tables
                    customer_record = next((c for c in table_data if c["customer_id"] == customer_id), None)
                
                if customer_record:
                    customer_data[source["id"]] = {
                        "source_name": source["name"],
                        "source_description": source["description"],
                        "category": source["category"],
                        "data": customer_record
                    }
        
        # Generate LLM summary using NeuroStack if requested
        summary = None
        if include_summary and customer_data:
            try:
                # Prepare data for LLM analysis
                summary_data = {
                    "customer_id": customer_id,
                    "sources": customer_data
                }
                
                # Use NeuroStack integration for LLM summary
                integration = await get_neurostack_integration()
                
                # Create a simple prompt for the LLM
                prompt = f"Analyze this customer data for credit decisions: Customer ID {customer_id}. "
                
                for source_id, source_info in customer_data.items():
                    prompt += f"{source_info['source_name']}: "
                    for key, value in source_info['data'].items():
                        prompt += f"{key}={value}, "
                
                prompt += "Provide a brief banking summary with customer profile, financial health, credit risk, and recommendations."
                
                # Use NeuroStack reasoning engine for summary generation
                summary_result = await integration.generate_customer_summary(
                    customer_id=customer_id,
                    customer_data=customer_data,
                    prompt=prompt
                )
                
                if summary_result.get("success"):
                    summary = summary_result.get("summary")
                    neurostack_features["summary_generation"] = summary_result.get("neurostack_features", {})
                else:
                    # Fallback to basic summary
                    summary = f"Customer {customer_id} data retrieved from {len(customer_data)} sources. Manual review recommended."
                    
            except Exception as e:
                logger.error(f"Error generating LLM summary: {str(e)}")
                summary = f"Customer {customer_id} data retrieved from {len(customer_data)} sources. Summary generation failed: {str(e)}"
        
        return CustomerDataResponse(
            success=True,
            customer_id=customer_id,
            data=customer_data,
            summary=summary,
            neurostack_features=neurostack_features
        )
        
    except Exception as e:
        logger.error(f"Error getting customer data: {str(e)}")
        return CustomerDataResponse(
            success=False,
            customer_id=request.customer_id,
            data={},
            error=str(e)
        )

# ============================================================================
# REPORT MANAGEMENT ENDPOINTS
# ============================================================================

@app.post("/api/reports", response_model=ReportResponse)
async def create_customer_report(
    request: CreateReportRequest,
    current_user: User = Depends(get_current_user_optional)
):
    """Create a new customer report with AI summary and inquiry details."""
    try:
        username = current_user.username if current_user else "test_user"
        report = report_service.create_report(request, username)
        return ReportResponse(success=True, report=report)
    except Exception as e:
        logger.error(f"Error creating report: {str(e)}")
        return ReportResponse(success=False, error=str(e))

@app.get("/api/reports", response_model=ReportsListResponse)
async def get_reports(
    customer_id: Optional[int] = None,
    status: Optional[ReportStatus] = None,
    limit: Optional[int] = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user_optional)
):
    """Get customer reports with optional filtering."""
    try:
        if customer_id:
            reports = report_service.get_reports_by_customer(customer_id)
        elif status:
            reports = report_service.get_reports_by_status(status)
        else:
            reports = report_service.get_all_reports(limit=limit, offset=offset)
        
        return ReportsListResponse(
            success=True,
            reports=reports,
            total_count=len(reports)
        )
    except Exception as e:
        logger.error(f"Error getting reports: {str(e)}")
        return ReportsListResponse(success=False, error=str(e))

@app.get("/api/reports/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: str,
    current_user: User = Depends(get_current_user_optional)
):
    """Get a specific customer report by ID."""
    try:
        report = report_service.get_report(report_id)
        if not report:
            return ReportResponse(success=False, error="Report not found")
        
        return ReportResponse(success=True, report=report)
    except Exception as e:
        logger.error(f"Error getting report: {str(e)}")
        return ReportResponse(success=False, error=str(e))

@app.put("/api/reports/{report_id}", response_model=ReportResponse)
async def update_report(
    report_id: str,
    request: UpdateReportRequest,
    current_user: User = Depends(get_current_user_optional)
):
    """Update a customer report (agent notes, status, decisions)."""
    try:
        username = current_user.username if current_user else "test_user"
        report = report_service.update_report(report_id, request, username)
        if not report:
            return ReportResponse(success=False, error="Report not found")
        
        return ReportResponse(success=True, report=report)
    except Exception as e:
        logger.error(f"Error updating report: {str(e)}")
        return ReportResponse(success=False, error=str(e))

@app.delete("/api/reports/{report_id}")
async def delete_report(
    report_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a customer report."""
    try:
        success = report_service.delete_report(report_id)
        if not success:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return {"success": True, "message": "Report deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/reports/extract-credit-limit")
async def extract_credit_limit_info(
    request: dict
):
    """Extract credit limit information from inquiry description using LLM."""
    try:
        extraction_result = report_service.extract_credit_limit_info(
            inquiry_description=request.get("inquiryDescription"),
            current_credit_limit=request.get("currentCreditLimit")
        )
        
        return {
            "success": True,
            "data": extraction_result
        }
    except Exception as e:
        logger.error(f"Error extracting credit limit info: {str(e)}")
        return {"success": False, "error": str(e)}

@app.post("/api/reports/generate-recommendation")
async def generate_report_recommendation(
    request: dict
):
    """Generate AI recommendation for a customer report using Neurostack Agent."""
    try:
        recommendation = report_service.generate_ai_recommendation(
            customer_id=request.get("customerId"),
            customer_data=request.get("customerData"),
            ai_summary=request.get("aiSummary"),
            inquiry_type=request.get("inquiryType"),
            inquiry_description=request.get("inquiryDescription"),
            extracted_credit_data=request.get("extractedCreditData")
        )
        
        return {
            "success": True,
            "data": {
                "recommendation": recommendation.get("recommendation", ""),
                "suggested_decision": recommendation.get("suggested_decision", ""),
                "credit_limits": recommendation.get("credit_limits", {})
            }
        }
    except Exception as e:
        logger.error(f"Error generating report recommendation: {str(e)}")
        return {"success": False, "error": str(e)}

@app.post("/api/reports/generate-investigation-plan")
async def generate_investigation_plan(
    request: dict
):
    """Generate investigation strategy for analysis stage."""
    try:
        plan = await report_service.generate_investigation_plan(
            customer_id=request.get("customerId"),
            customer_name=request.get("customerName"),
            customer_data=request.get("customerData"),
            report_id=request.get("reportId"),
            current_steps=request.get("currentSteps")  # New parameter for personalization
        )
        
        return {
            "success": True,
            "data": plan
        }
    except Exception as e:
        logger.error(f"Error generating investigation plan: {str(e)}")
        return {"success": False, "error": str(e)}

@app.get("/api/reports/enums/status")
async def get_report_statuses():
    """Get available report statuses."""
    return {"statuses": [status.value for status in ReportStatus]}

@app.get("/api/reports/enums/inquiry-types")
async def get_inquiry_types():
    """Get available inquiry types."""
    return {"inquiry_types": [inquiry_type.value for inquiry_type in CreditInquiryType]}

# Strategy Management Endpoints
@app.post("/api/strategies", response_model=StrategyResponse)
async def create_strategy(
    request: CreateStrategyRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a new investigation strategy."""
    try:
        strategy = report_service.create_strategy(request, current_user.user_id)
        return StrategyResponse(success=True, strategy=strategy)
    except Exception as e:
        logger.error(f"Error creating strategy: {str(e)}")
        return StrategyResponse(success=False, error=str(e))

@app.get("/api/strategies", response_model=StrategiesListResponse)
async def get_strategies(
    focus: Optional[str] = None,
    risk_profile: Optional[str] = None,
    search: Optional[str] = None,
    templates_only: bool = False,
    current_user: User = Depends(get_current_user)
):
    """Get all strategies with optional filtering."""
    try:
        if search:
            strategies = report_service.search_strategies(search)
        elif templates_only:
            strategies = report_service.get_template_strategies()
        elif focus:
            strategies = report_service.get_strategies_by_focus(focus)
        elif risk_profile:
            strategies = report_service.get_strategies_by_risk_profile(risk_profile)
        else:
            strategies = report_service.get_all_strategies()
        
        return StrategiesListResponse(
            success=True,
            strategies=strategies,
            total_count=len(strategies)
        )
    except Exception as e:
        logger.error(f"Error getting strategies: {str(e)}")
        return StrategiesListResponse(success=False, error=str(e))

@app.get("/api/strategies/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(
    strategy_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific strategy by ID."""
    try:
        strategy = report_service.get_strategy(strategy_id)
        if not strategy:
            return StrategyResponse(success=False, error="Strategy not found")
        return StrategyResponse(success=True, strategy=strategy)
    except Exception as e:
        logger.error(f"Error getting strategy: {str(e)}")
        return StrategyResponse(success=False, error=str(e))

@app.put("/api/strategies/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(
    strategy_id: str,
    request: UpdateStrategyRequest,
    current_user: User = Depends(get_current_user)
):
    """Update a strategy."""
    try:
        strategy = report_service.update_strategy(strategy_id, request)
        if not strategy:
            return StrategyResponse(success=False, error="Strategy not found")
        return StrategyResponse(success=True, strategy=strategy)
    except Exception as e:
        logger.error(f"Error updating strategy: {str(e)}")
        return StrategyResponse(success=False, error=str(e))

@app.delete("/api/strategies/{strategy_id}")
async def delete_strategy(
    strategy_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a strategy."""
    try:
        success = report_service.delete_strategy(strategy_id)
        if not success:
            return {"success": False, "error": "Strategy not found"}
        return {"success": True, "message": "Strategy deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting strategy: {str(e)}")
        return {"success": False, "error": str(e)}

# Initialize chat service
chat_service = ChatService()

# Investigation Execution Endpoints
@app.post("/api/investigations/execute", response_model=InvestigationExecutionResponse)
async def execute_investigation(
    request: ExecuteInvestigationRequest,
    current_user: User = Depends(get_current_user)
):
    """Execute investigation steps using LLM-based planning and execution."""
    try:
        logger.info(f"🔍 Received investigation execution request: {request}")
        logger.info(f"🔍 Request type: {type(request)}")
        logger.info(f"🔍 selectedSteps type: {type(request.selectedSteps)}")
        logger.info(f"🔍 selectedSteps content: {request.selectedSteps}")
        execution = await investigation_service.execute_investigation(request)
        logger.info(f"🔍 Created execution: {execution}")
        logger.info(f"🔍 Execution ID: {execution.execution_id}")
        return InvestigationExecutionResponse(success=True, execution=execution)
    except Exception as e:
        logger.error(f"Error executing investigation: {str(e)}")
        return InvestigationExecutionResponse(success=False, error=str(e))



@app.get("/api/investigations/executions/{execution_id}", response_model=InvestigationExecutionResponse)
async def get_investigation_execution(
    execution_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get investigation execution by ID."""
    try:
        execution = investigation_service.get_execution(execution_id)
        if not execution:
            return InvestigationExecutionResponse(success=False, error="Execution not found")
        return InvestigationExecutionResponse(success=True, execution=execution)
    except Exception as e:
        logger.error(f"Error getting execution: {str(e)}")
        return InvestigationExecutionResponse(success=False, error=str(e))

@app.get("/api/investigations/executions", response_model=InvestigationResultsResponse)
async def get_all_investigation_executions(
    current_user: User = Depends(get_current_user)
):
    """Get all investigation executions."""
    try:
        executions = investigation_service.get_all_executions()
        return InvestigationResultsResponse(
            success=True,
            results=[execution.dict() for execution in executions],
            summary={"total_executions": len(executions)}
        )
    except Exception as e:
        logger.error(f"Error getting executions: {str(e)}")
        return InvestigationResultsResponse(success=False, error=str(e))

@app.get("/api/investigations/data-sources", response_model=DataSourcesResponse)
async def get_data_sources(
    current_user: User = Depends(get_current_user)
):
    """Get all available data sources for investigation execution."""
    try:
        data_sources = investigation_service.get_data_sources()
        return DataSourcesResponse(success=True, data_sources=data_sources)
    except Exception as e:
        logger.error(f"Error getting data sources: {str(e)}")
        return DataSourcesResponse(success=False, error=str(e))

# Chat with Investigations Endpoints
@app.post("/api/chat/send", response_model=ChatResponse)
async def send_chat_message(
    request: ChatMessageRequest,
    current_user: User = Depends(get_current_user)
):
    """Send a chat message and get AI response with investigation context."""
    try:
        logger.info(f"💬 Received chat message: {request.content[:100]}...")
        response = await chat_service.process_message(request)
        return ChatResponse(**response)
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        return ChatResponse(success=False, error=str(e))

@app.get("/api/chat/history/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get chat history for a session."""
    try:
        messages = chat_service.get_chat_history(session_id)
        session = chat_service.get_session(session_id)
        return ChatHistoryResponse(
            success=True,
            messages=messages,
            session=session
        )
    except Exception as e:
        logger.error(f"Error getting chat history: {str(e)}")
        return ChatHistoryResponse(success=False, error=str(e))

@app.get("/api/chat/sessions", response_model=ChatHistoryResponse)
async def get_all_chat_sessions(
    current_user: User = Depends(get_current_user)
):
    """Get all chat sessions for the current user."""
    try:
        # For now, return empty list - in production, filter by user
        return ChatHistoryResponse(
            success=True,
            messages=[],
            session=None
        )
    except Exception as e:
        logger.error(f"Error getting chat sessions: {str(e)}")
        return ChatHistoryResponse(success=False, error=str(e))

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    logger.info(f"Starting Banking Agent Backend on {host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=debug)
