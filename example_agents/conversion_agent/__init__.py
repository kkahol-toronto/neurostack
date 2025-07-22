"""
Code Conversion Agent Example

This module demonstrates how to use NeuroStack to build specialized agents for:
1. Analyzing code files from various programming languages
2. Generating technical documentation
3. Converting code between different programming languages

The system uses multiple agents working together:
- CodeAnalysisAgent: Analyzes code structure and functionality
- DocumentationAgent: Generates technical requirements documents
- CodeConversionAgent: Converts code to target language
- ConversionOrchestrator: Coordinates the entire conversion workflow
"""

from .agents import (
    CodeAnalysisAgent,
    DocumentationAgent,
    CodeConversionAgent,
    ConversionOrchestrator
)
from .models import (
    CodeFile,
    CodeAnalysis,
    TechnicalDocument,
    ConversionRequest,
    ConversionResult
)
from .utils import (
    CodeExtractor,
    LanguageDetector,
    CodeFormatter,
    DocumentationFormatter
)

__version__ = "0.1.0"
__all__ = [
    # Agents
    "CodeAnalysisAgent",
    "DocumentationAgent", 
    "CodeConversionAgent",
    "ConversionOrchestrator",
    
    # Models
    "CodeFile",
    "CodeAnalysis",
    "TechnicalDocument",
    "ConversionRequest",
    "ConversionResult",
    
    # Utilities
    "CodeExtractor",
    "LanguageDetector",
    "CodeFormatter",
    "DocumentationFormatter",
] 