"""
Data models for the code conversion agent system.

This module defines the data structures used throughout the conversion process,
including code files, analysis results, technical documents, and conversion requests.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ProgrammingLanguage(str, Enum):
    """Supported programming languages for conversion."""
    COBOL = "cobol"
    JAVA = "java"
    PYTHON = "python"
    C_SHARP = "csharp"
    CPP = "cpp"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    GO = "go"
    RUST = "rust"
    FORTRAN = "fortran"
    PASCAL = "pascal"
    BASIC = "basic"
    ASSEMBLY = "assembly"
    PHP = "php"
    RUBY = "ruby"
    SCALA = "scala"
    KOTLIN = "kotlin"
    SWIFT = "swift"
    R = "r"
    MATLAB = "matlab"


class CodeFileType(str, Enum):
    """Types of code files."""
    SOURCE = "source"
    HEADER = "header"
    CONFIG = "config"
    TEST = "test"
    DOCUMENTATION = "documentation"
    BUILD = "build"
    OTHER = "other"


class ConversionStatus(str, Enum):
    """Status of conversion process."""
    PENDING = "pending"
    ANALYZING = "analyzing"
    DOCUMENTING = "documenting"
    CONVERTING = "converting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class CodeFile:
    """Represents a single code file with metadata."""
    path: Path
    content: str
    language: ProgrammingLanguage
    file_type: CodeFileType = CodeFileType.SOURCE
    encoding: str = "utf-8"
    size_bytes: int = 0
    line_count: int = 0
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Calculate derived fields after initialization."""
        if self.size_bytes == 0:
            self.size_bytes = len(self.content.encode(self.encoding))
        if self.line_count == 0:
            self.line_count = len(self.content.splitlines())


class CodeAnalysis(BaseModel):
    """Result of code analysis."""
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # File information
    source_language: ProgrammingLanguage
    target_language: ProgrammingLanguage
    total_files: int
    total_lines: int
    
    # Analysis results
    main_functions: List[str] = Field(default_factory=list)
    classes: List[str] = Field(default_factory=list)
    variables: List[str] = Field(default_factory=list)
    imports: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    
    # Code structure
    file_structure: Dict[str, Any] = Field(default_factory=dict)
    control_flow: Dict[str, Any] = Field(default_factory=dict)
    data_flow: Dict[str, Any] = Field(default_factory=dict)
    
    # Complexity metrics
    cyclomatic_complexity: Dict[str, int] = Field(default_factory=dict)
    lines_of_code: Dict[str, int] = Field(default_factory=dict)
    comment_ratio: float = 0.0
    
    # Language-specific features
    language_features: Dict[str, Any] = Field(default_factory=dict)
    patterns: List[str] = Field(default_factory=list)
    
    # Issues and warnings
    issues: List[Dict[str, Any]] = Field(default_factory=list)
    warnings: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Metadata
    analysis_duration: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TechnicalDocument(BaseModel):
    """Technical requirements document for code conversion."""
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Document metadata
    title: str
    version: str = "1.0"
    author: str = "NeuroStack Conversion Agent"
    
    # Conversion context
    source_language: ProgrammingLanguage
    target_language: ProgrammingLanguage
    project_name: str
    project_description: str = ""
    
    # Requirements
    functional_requirements: List[str] = Field(default_factory=list)
    non_functional_requirements: List[str] = Field(default_factory=list)
    technical_constraints: List[str] = Field(default_factory=list)
    
    # Architecture
    system_architecture: Dict[str, Any] = Field(default_factory=dict)
    component_mapping: Dict[str, str] = Field(default_factory=dict)
    data_structures: Dict[str, Any] = Field(default_factory=dict)
    
    # Conversion rules
    language_mappings: Dict[str, str] = Field(default_factory=dict)
    pattern_conversions: List[Dict[str, Any]] = Field(default_factory=list)
    api_mappings: Dict[str, str] = Field(default_factory=dict)
    
    # Implementation details
    file_structure: Dict[str, Any] = Field(default_factory=dict)
    naming_conventions: Dict[str, str] = Field(default_factory=dict)
    coding_standards: List[str] = Field(default_factory=list)
    
    # Dependencies and libraries
    required_libraries: List[str] = Field(default_factory=list)
    external_dependencies: List[str] = Field(default_factory=list)
    build_configuration: Dict[str, Any] = Field(default_factory=dict)
    
    # Testing and validation
    test_requirements: List[str] = Field(default_factory=list)
    validation_criteria: List[str] = Field(default_factory=list)
    
    # Documentation
    api_documentation: Dict[str, Any] = Field(default_factory=dict)
    user_manual: str = ""
    deployment_guide: str = ""
    
    # Metadata
    generation_duration: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ConversionRequest(BaseModel):
    """Request for code conversion."""
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Request details
    source_language: ProgrammingLanguage
    target_language: ProgrammingLanguage
    project_name: str
    description: str = ""
    
    # Input files
    input_files: List[CodeFile] = Field(default_factory=list)
    input_zip_path: Optional[Path] = None
    
    # Configuration
    preserve_structure: bool = True
    include_tests: bool = True
    include_documentation: bool = True
    optimization_level: str = "balanced"  # minimal, balanced, aggressive
    
    # Output preferences
    output_format: str = "standard"  # standard, modern, legacy
    naming_convention: str = "camelCase"  # camelCase, snake_case, PascalCase
    code_style: str = "standard"  # standard, google, microsoft
    
    # Advanced options
    custom_mappings: Dict[str, str] = Field(default_factory=dict)
    exclude_patterns: List[str] = Field(default_factory=list)
    include_patterns: List[str] = Field(default_factory=list)
    
    # Metadata
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    priority: str = "normal"  # low, normal, high, urgent
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ConversionResult(BaseModel):
    """Result of code conversion process."""
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Request reference
    request_id: UUID
    status: ConversionStatus = ConversionStatus.PENDING
    
    # Analysis results
    code_analysis: Optional[CodeAnalysis] = None
    technical_document: Optional[TechnicalDocument] = None
    
    # Conversion results
    converted_files: List[CodeFile] = Field(default_factory=list)
    output_directory: Optional[Path] = None
    output_zip_path: Optional[Path] = None
    
    # Quality metrics
    conversion_accuracy: float = 0.0
    code_coverage: float = 0.0
    test_coverage: float = 0.0
    
    # Issues and warnings
    conversion_issues: List[Dict[str, Any]] = Field(default_factory=list)
    manual_review_required: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    
    # Performance metrics
    total_duration: float = 0.0
    analysis_duration: float = 0.0
    documentation_duration: float = 0.0
    conversion_duration: float = 0.0
    
    # Summary
    summary: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ConversionProgress(BaseModel):
    """Progress update during conversion process."""
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Progress tracking
    request_id: UUID
    current_step: str
    step_number: int
    total_steps: int
    progress_percentage: float
    
    # Current status
    status: ConversionStatus
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)
    
    # Error information (if any)
    error: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict) 