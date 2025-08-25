from pydantic import BaseModel
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
