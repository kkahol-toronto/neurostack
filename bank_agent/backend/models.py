from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class ReportStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    UNDER_REVIEW = "under_review"

class CreditInquiryType(str, Enum):
    CREDIT_LIMIT_INCREASE = "credit_limit_increase"
    NEW_CREDIT_PRODUCT = "new_credit_product"
    LOAN_APPLICATION = "loan_application"
    REFINANCING = "refinancing"
    GENERAL_INQUIRY = "general_inquiry"

class InvestigationExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class DataSourceType(str, Enum):
    INTERNAL_BANKING = "banking"
    CREDIT_BUREAU = "credit_bureau"
    INCOME_VERIFICATION = "income"
    CUSTOMER_DEMOGRAPHICS = "demographics"
    ECONOMIC_INDICATORS = "economic"
    OPEN_BANKING = "open_banking"
    FRAUD_KYC_COMPLIANCE = "fraud"

class CustomerReport(BaseModel):
    report_id: Optional[str] = None
    customer_id: int
    customer_name: str
    report_date: datetime
    inquiry_type: CreditInquiryType
    inquiry_description: str
    ai_summary: str
    ai_recommendation: Optional[str] = None
    suggested_decision: Optional[str] = None
    current_credit_limit: Optional[float] = None
    requested_credit_limit: Optional[float] = None
    credit_limit_increase: Optional[float] = None
    agent_notes: Optional[str] = None
    status: ReportStatus = ReportStatus.PENDING
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    customer_data: Dict[str, Any]
    credit_recommendation: Optional[str] = None
    final_decision: Optional[str] = None
    decision_date: Optional[datetime] = None
    decision_by: Optional[str] = None

class CreateReportRequest(BaseModel):
    customer_id: int
    customer_name: str
    inquiry_type: CreditInquiryType
    inquiry_description: str
    ai_summary: str
    ai_recommendation: Optional[str] = None
    suggested_decision: Optional[str] = None
    current_credit_limit: Optional[float] = None
    requested_credit_limit: Optional[float] = None
    credit_limit_increase: Optional[float] = None
    agent_notes: Optional[str] = None
    status: Optional[ReportStatus] = ReportStatus.PENDING
    customer_data: Dict[str, Any]

class UpdateReportRequest(BaseModel):
    agent_notes: Optional[str] = None
    status: Optional[ReportStatus] = None
    credit_recommendation: Optional[str] = None
    final_decision: Optional[str] = None
    current_credit_limit: Optional[float] = None
    requested_credit_limit: Optional[float] = None
    credit_limit_increase: Optional[float] = None

class ReportResponse(BaseModel):
    success: bool
    report: Optional[CustomerReport] = None
    error: Optional[str] = None

class ReportsListResponse(BaseModel):
    success: bool
    reports: List[CustomerReport] = []
    total_count: int = 0
    error: Optional[str] = None

class InvestigationStrategy(BaseModel):
    strategy_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    strategy_focus: str
    risk_profile: str
    steps: List[Dict[str, Any]]
    created_by: str

class ChatMessage(BaseModel):
    message_id: Optional[str] = None
    session_id: str
    customer_id: int
    customer_name: str
    message_type: str = "user"  # "user" or "assistant"
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None  # For storing scenario data, graphs, etc.

class ChatSession(BaseModel):
    session_id: Optional[str] = None
    customer_id: int
    customer_name: str
    execution_id: Optional[str] = None
    investigation_results: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    message_count: int = 0

class ScenarioAnalysis(BaseModel):
    scenario_id: Optional[str] = None
    session_id: str
    customer_id: int
    base_increase: float
    scenarios: List[Dict[str, Any]]  # 40%, 60%, 80%, 100%, 120% variations
    utilization_projections: List[Dict[str, Any]]
    risk_assessments: List[Dict[str, Any]]
    spending_trends: Dict[str, Any]
    created_at: datetime

class ChatMessageRequest(BaseModel):
    session_id: str
    customer_id: int
    customer_name: str
    content: str
    execution_id: Optional[str] = None
    investigation_results: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    success: bool
    message: Optional[ChatMessage] = None
    session: Optional[ChatSession] = None
    error: Optional[str] = None

class ChatHistoryResponse(BaseModel):
    success: bool
    messages: List[ChatMessage] = []
    session: Optional[ChatSession] = None
    error: Optional[str] = None

class ScenarioAnalysisResponse(BaseModel):
    success: bool
    scenario: Optional[ScenarioAnalysis] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_template: bool = False
    tags: List[str] = []

class CreateStrategyRequest(BaseModel):
    name: str
    description: Optional[str] = None
    strategy_focus: str
    risk_profile: str
    steps: List[Dict[str, Any]]
    is_template: bool = False
    tags: List[str] = []

class UpdateStrategyRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    is_template: Optional[bool] = None

class StrategyResponse(BaseModel):
    success: bool
    strategy: Optional[InvestigationStrategy] = None
    error: Optional[str] = None

class StrategiesListResponse(BaseModel):
    success: bool
    strategies: List[InvestigationStrategy] = []
    total_count: int = 0
    error: Optional[str] = None

# New models for Data Simulation and Visualization Studio
class DataSource(BaseModel):
    id: str
    name: str
    category: str
    description: str
    table_name: str
    fields: List[Dict[str, Any]]
    sample_data: Optional[List[Dict[str, Any]]] = None
    is_enabled: bool = True

class InvestigationExecution(BaseModel):
    execution_id: str = Field(alias="executionId")
    customer_id: int = Field(alias="customerId")
    customer_name: str = Field(alias="customerName")
    report_id: Optional[str] = Field(None, alias="reportId")
    selectedSteps: List[Dict[str, Any]]
    status: InvestigationExecutionStatus
    started_at: datetime = Field(alias="startedAt")
    completed_at: Optional[datetime] = Field(None, alias="completedAt")
    results: Dict[str, Any] = {}
    errors: List[str] = []
    progress: float = 0.0
    current_step: Optional[str] = Field(None, alias="currentStep")
    step_status: Dict[str, str] = Field(default_factory=dict, alias="stepStatus")  # Track individual step status

class InvestigationResult(BaseModel):
    step_id: str
    step_title: str
    execution_time: float
    status: InvestigationExecutionStatus
    data: Dict[str, Any]
    visualizations: List[Dict[str, Any]]
    insights: List[str]
    recommendations: List[str]
    metadata: Dict[str, Any]

class ExecuteInvestigationRequest(BaseModel):
    customer_id: int = Field(alias="customerId")
    customer_name: str = Field(alias="customerName")
    report_id: Optional[str] = Field(None, alias="reportId")
    selectedSteps: List[Dict[str, Any]]
    execution_mode: str = Field("batch", alias="executionMode")

class InvestigationExecutionResponse(BaseModel):
    success: bool
    execution: Optional[InvestigationExecution] = None
    error: Optional[str] = None

class DataSourcesResponse(BaseModel):
    success: bool
    data_sources: List[DataSource] = []
    error: Optional[str] = None

class InvestigationResultsResponse(BaseModel):
    success: bool
    results: List[InvestigationResult] = []
    summary: Dict[str, Any] = {}
    error: Optional[str] = None

class InvestigationExecutionsResponse(BaseModel):
    success: bool
    executions: List[InvestigationExecution] = []
    summary: Dict[str, Any] = {}
    error: Optional[str] = None
