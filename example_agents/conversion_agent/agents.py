"""
Specialized agents for code conversion using NeuroStack.

This module implements three main agents:
1. CodeAnalysisAgent - Analyzes code structure and functionality
2. DocumentationAgent - Generates technical requirements documents
3. CodeConversionAgent - Converts code to target language
4. ConversionOrchestrator - Coordinates the entire conversion workflow
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import structlog

# Import NeuroStack components
from neurostack import Agent, AgentConfig, AgentContext, AgentOrchestrator
from neurostack.core.agents.base import AgentMessage

from .models import (
    CodeAnalysis, CodeFile, ConversionProgress, ConversionRequest,
    ConversionResult, ConversionStatus, ProgrammingLanguage, TechnicalDocument
)
from .utils import CodeExtractor, CodeFormatter, DocumentationFormatter, LanguageDetector

logger = structlog.get_logger(__name__)


class CodeAnalysisAgent(Agent):
    """
    Agent responsible for analyzing code files and extracting structural information.
    
    This agent:
    - Extracts code from zip files or directories
    - Detects programming languages
    - Analyzes code structure, functions, classes, and dependencies
    - Calculates complexity metrics
    - Identifies patterns and language-specific features
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.extractor = CodeExtractor()
        self.language_detector = LanguageDetector()
        self.formatter = CodeFormatter()
        
    async def execute(self, task: Any, context: Optional[AgentContext] = None) -> CodeAnalysis:
        """
        Execute code analysis task.
        
        Args:
            task: Can be a ConversionRequest, zip file path, or directory path
            context: Optional execution context
            
        Returns:
            CodeAnalysis object with analysis results
        """
        start_time = time.time()
        self.logger.info("Starting code analysis", task_type=type(task).__name__)
        
        try:
            # Handle different input types
            if isinstance(task, ConversionRequest):
                code_files = await self._extract_files_from_request(task)
            elif isinstance(task, (str, Path)):
                path = Path(task)
                if path.suffix.lower() == '.zip':
                    code_files = self.extractor.extract_from_zip(path)
                else:
                    code_files = self.extractor.extract_from_directory(path)
            else:
                raise ValueError(f"Unsupported task type: {type(task)}")
            
            # Perform analysis
            analysis = await self._analyze_code_files(code_files, task)
            
            # Calculate duration
            analysis.analysis_duration = time.time() - start_time
            
            self.logger.info("Code analysis completed", 
                           file_count=len(code_files),
                           duration=analysis.analysis_duration)
            
            return analysis
            
        except Exception as e:
            self.logger.error("Code analysis failed", error=str(e))
            raise
    
    async def _extract_files_from_request(self, request: ConversionRequest) -> List[CodeFile]:
        """Extract code files from a conversion request."""
        if request.input_zip_path:
            return self.extractor.extract_from_zip(request.input_zip_path)
        else:
            return request.input_files
    
    async def _analyze_code_files(self, code_files: List[CodeFile], 
                                request: Any) -> CodeAnalysis:
        """Analyze a list of code files."""
        if not code_files:
            raise ValueError("No code files to analyze")
        
        # Determine source and target languages
        source_language = self._detect_source_language(code_files)
        target_language = self._get_target_language(request)
        
        # Initialize analysis
        analysis = CodeAnalysis(
            source_language=source_language,
            target_language=target_language,
            total_files=len(code_files),
            total_lines=sum(f.line_count for f in code_files)
        )
        
        # Analyze each file
        for code_file in code_files:
            await self._analyze_single_file(code_file, analysis)
        
        # Calculate overall metrics
        self._calculate_overall_metrics(analysis)
        
        return analysis
    
    def _detect_source_language(self, code_files: List[CodeFile]) -> ProgrammingLanguage:
        """Detect the primary source language from code files."""
        language_counts = {}
        for file in code_files:
            lang = file.language
            language_counts[lang] = language_counts.get(lang, 0) + 1
        
        if language_counts:
            return max(language_counts.items(), key=lambda x: x[1])[0]
        
        return ProgrammingLanguage.PYTHON  # Default fallback
    
    def _get_target_language(self, request: Any) -> ProgrammingLanguage:
        """Get target language from request."""
        if hasattr(request, 'target_language'):
            return request.target_language
        return ProgrammingLanguage.JAVA  # Default target
    
    async def _analyze_single_file(self, code_file: CodeFile, analysis: CodeAnalysis):
        """Analyze a single code file and update the analysis."""
        try:
            # Extract functions, classes, variables based on language
            if code_file.language == ProgrammingLanguage.COBOL:
                self._analyze_cobol_file(code_file, analysis)
            elif code_file.language == ProgrammingLanguage.JAVA:
                self._analyze_java_file(code_file, analysis)
            elif code_file.language == ProgrammingLanguage.PYTHON:
                self._analyze_python_file(code_file, analysis)
            else:
                self._analyze_generic_file(code_file, analysis)
            
            # Calculate file-specific metrics
            self._calculate_file_metrics(code_file, analysis)
            
        except Exception as e:
            self.logger.warning("Failed to analyze file", 
                              file_path=str(code_file.path), 
                              error=str(e))
            analysis.warnings.append({
                "file": str(code_file.path),
                "message": f"Analysis failed: {str(e)}"
            })
    
    def _analyze_cobol_file(self, code_file: CodeFile, analysis: CodeAnalysis):
        """Analyze COBOL file structure."""
        content = code_file.content
        lines = content.split('\n')
        
        # Extract divisions and sections
        divisions = []
        sections = []
        
        for line in lines:
            line_upper = line.upper().strip()
            if 'DIVISION' in line_upper:
                divisions.append(line_upper)
            elif 'SECTION' in line_upper:
                sections.append(line_upper)
        
        analysis.language_features.setdefault('cobol', {})
        analysis.language_features['cobol']['divisions'] = divisions
        analysis.language_features['cobol']['sections'] = sections
        
        # Extract paragraph names (PROCEDURE DIVISION)
        paragraphs = []
        in_procedure = False
        for line in lines:
            line_upper = line.upper().strip()
            if 'PROCEDURE DIVISION' in line_upper:
                in_procedure = True
                continue
            elif in_procedure and line_upper and not line_upper.startswith('*'):
                # Simple paragraph detection
                if not line_upper.startswith(('IF', 'ELSE', 'END-IF', 'PERFORM', 'END-PERFORM')):
                    paragraphs.append(line_upper)
        
        analysis.main_functions.extend(paragraphs)
    
    def _analyze_java_file(self, code_file: CodeFile, analysis: CodeAnalysis):
        """Analyze Java file structure."""
        content = code_file.content
        
        # Extract class names
        import re
        class_pattern = r'public\s+class\s+(\w+)'
        classes = re.findall(class_pattern, content)
        analysis.classes.extend(classes)
        
        # Extract method names
        method_pattern = r'public\s+(?:static\s+)?(?:void|String|int|boolean|double|float|long|short|byte|char)\s+(\w+)\s*\('
        methods = re.findall(method_pattern, content)
        analysis.main_functions.extend(methods)
        
        # Extract imports
        import_pattern = r'import\s+([^;]+);'
        imports = re.findall(import_pattern, content)
        analysis.imports.extend(imports)
    
    def _analyze_python_file(self, code_file: CodeFile, analysis: CodeAnalysis):
        """Analyze Python file structure."""
        content = code_file.content
        
        # Extract function names
        import re
        function_pattern = r'def\s+(\w+)\s*\('
        functions = re.findall(function_pattern, content)
        analysis.main_functions.extend(functions)
        
        # Extract class names
        class_pattern = r'class\s+(\w+)'
        classes = re.findall(class_pattern, content)
        analysis.classes.extend(classes)
        
        # Extract imports
        import_pattern = r'import\s+(\w+)'
        imports = re.findall(import_pattern, content)
        analysis.imports.extend(imports)
    
    def _analyze_generic_file(self, code_file: CodeFile, analysis: CodeAnalysis):
        """Analyze generic file structure."""
        # Basic analysis for unsupported languages
        content = code_file.content
        lines = content.split('\n')
        
        # Count comments
        comment_lines = sum(1 for line in lines if line.strip().startswith(('//', '/*', '*', '#')))
        analysis.comment_ratio = comment_lines / len(lines) if lines else 0.0
    
    def _calculate_file_metrics(self, code_file: CodeFile, analysis: CodeAnalysis):
        """Calculate metrics for a single file."""
        file_path = str(code_file.path)
        
        # Lines of code
        analysis.lines_of_code[file_path] = code_file.line_count
        
        # Cyclomatic complexity (simplified)
        content = code_file.content
        complexity = 1  # Base complexity
        
        # Count decision points
        decision_keywords = ['if', 'else', 'while', 'for', 'case', 'catch', '&&', '||']
        for keyword in decision_keywords:
            complexity += content.lower().count(keyword)
        
        analysis.cyclomatic_complexity[file_path] = complexity
    
    def _calculate_overall_metrics(self, analysis: CodeAnalysis):
        """Calculate overall project metrics."""
        if analysis.lines_of_code:
            total_loc = sum(analysis.lines_of_code.values())
            analysis.metadata['total_lines_of_code'] = total_loc
            analysis.metadata['average_complexity'] = sum(analysis.cyclomatic_complexity.values()) / len(analysis.cyclomatic_complexity)


class DocumentationAgent(Agent):
    """
    Agent responsible for generating technical documentation from code analysis.
    
    This agent:
    - Takes code analysis results as input
    - Generates comprehensive technical requirements documents
    - Creates language-specific conversion rules
    - Documents system architecture and component mappings
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.doc_formatter = DocumentationFormatter()
        
    async def execute(self, task: Any, context: Optional[AgentContext] = None) -> TechnicalDocument:
        """
        Execute documentation generation task.
        
        Args:
            task: CodeAnalysis object or tuple of (analysis, request)
            context: Optional execution context
            
        Returns:
            TechnicalDocument object
        """
        start_time = time.time()
        self.logger.info("Starting documentation generation")
        
        try:
            # Extract analysis and request
            if isinstance(task, tuple) and len(task) == 2:
                analysis, request = task
            elif isinstance(task, CodeAnalysis):
                analysis = task
                request = None
            else:
                raise ValueError(f"Unsupported task type: {type(task)}")
            
            # Generate documentation
            document = await self._generate_technical_document(analysis, request)
            
            # Calculate duration
            document.generation_duration = time.time() - start_time
            
            self.logger.info("Documentation generation completed", 
                           duration=document.generation_duration)
            
            return document
            
        except Exception as e:
            self.logger.error("Documentation generation failed", error=str(e))
            raise
    
    async def _generate_technical_document(self, analysis: CodeAnalysis, 
                                         request: Optional[ConversionRequest]) -> TechnicalDocument:
        """Generate technical document from code analysis."""
        # Create base document
        document = TechnicalDocument(
            title=f"Technical Requirements: {analysis.source_language.value} to {analysis.target_language.value} Conversion",
            source_language=analysis.source_language,
            target_language=analysis.target_language,
            project_name=request.project_name if request else "Code Conversion Project",
            project_description=request.description if request else "Automated code conversion project"
        )
        
        # Generate requirements
        await self._generate_requirements(analysis, document)
        
        # Generate architecture
        await self._generate_architecture(analysis, document)
        
        # Generate conversion rules
        await self._generate_conversion_rules(analysis, document)
        
        # Generate implementation details
        await self._generate_implementation_details(analysis, document)
        
        # Generate testing requirements
        await self._generate_testing_requirements(analysis, document)
        
        return document
    
    async def _generate_requirements(self, analysis: CodeAnalysis, document: TechnicalDocument):
        """Generate functional and non-functional requirements."""
        # Functional requirements based on analysis
        document.functional_requirements = [
            f"Convert {analysis.source_language.value} code to {analysis.target_language.value}",
            f"Preserve {len(analysis.main_functions)} main functions/procedures",
            f"Maintain {len(analysis.classes)} class structures",
            f"Handle {len(analysis.imports)} external dependencies",
            f"Support {analysis.total_files} source files",
        ]
        
        # Non-functional requirements
        document.non_functional_requirements = [
            "Maintain code readability and structure",
            "Preserve business logic and functionality",
            "Ensure type safety and error handling",
            "Optimize for performance and memory usage",
            "Follow target language coding standards",
        ]
        
        # Technical constraints
        document.technical_constraints = [
            f"Source language: {analysis.source_language.value}",
            f"Target language: {analysis.target_language.value}",
            f"Total lines of code: {analysis.total_lines}",
            f"Average complexity: {analysis.metadata.get('average_complexity', 0):.2f}",
        ]
    
    async def _generate_architecture(self, analysis: CodeAnalysis, document: TechnicalDocument):
        """Generate system architecture and component mappings."""
        # System architecture
        document.system_architecture = {
            "source_system": {
                "language": analysis.source_language.value,
                "files": analysis.total_files,
                "components": {
                    "functions": len(analysis.main_functions),
                    "classes": len(analysis.classes),
                    "dependencies": len(analysis.imports)
                }
            },
            "target_system": {
                "language": analysis.target_language.value,
                "architecture_pattern": self._get_architecture_pattern(analysis.target_language),
                "framework": self._get_default_framework(analysis.target_language)
            },
            "conversion_layers": [
                "Lexical Analysis",
                "Syntax Parsing", 
                "Semantic Analysis",
                "Code Generation",
                "Optimization"
            ]
        }
        
        # Component mappings
        document.component_mapping = self._generate_component_mappings(analysis)
        
        # Data structures
        document.data_structures = self._generate_data_structures(analysis)
    
    def _get_architecture_pattern(self, language: ProgrammingLanguage) -> str:
        """Get default architecture pattern for target language."""
        patterns = {
            ProgrammingLanguage.JAVA: "Object-Oriented",
            ProgrammingLanguage.PYTHON: "Object-Oriented",
            ProgrammingLanguage.C_SHARP: "Object-Oriented",
            ProgrammingLanguage.CPP: "Object-Oriented",
            ProgrammingLanguage.JAVASCRIPT: "Functional/Object-Oriented",
            ProgrammingLanguage.GO: "Procedural/Object-Oriented",
            ProgrammingLanguage.RUST: "Systems Programming",
            ProgrammingLanguage.COBOL: "Procedural",
        }
        return patterns.get(language, "Object-Oriented")
    
    def _get_default_framework(self, language: ProgrammingLanguage) -> str:
        """Get default framework for target language."""
        frameworks = {
            ProgrammingLanguage.JAVA: "Spring Boot",
            ProgrammingLanguage.PYTHON: "FastAPI/Django",
            ProgrammingLanguage.C_SHARP: ".NET Core",
            ProgrammingLanguage.JAVASCRIPT: "Node.js/Express",
            ProgrammingLanguage.GO: "Gin/Echo",
            ProgrammingLanguage.RUST: "Actix-web",
        }
        return frameworks.get(language, "Standard Library")
    
    def _generate_component_mappings(self, analysis: CodeAnalysis) -> Dict[str, str]:
        """Generate component mappings from source to target."""
        mappings = {}
        
        # Map functions to target language equivalents
        for func in analysis.main_functions:
            if analysis.source_language == ProgrammingLanguage.COBOL:
                if analysis.target_language == ProgrammingLanguage.JAVA:
                    mappings[func] = f"public static void {func}()"
                elif analysis.target_language == ProgrammingLanguage.PYTHON:
                    mappings[func] = f"def {func}():"
        
        # Map classes
        for cls in analysis.classes:
            if analysis.target_language == ProgrammingLanguage.JAVA:
                mappings[cls] = f"public class {cls}"
            elif analysis.target_language == ProgrammingLanguage.PYTHON:
                mappings[cls] = f"class {cls}:"
        
        return mappings
    
    def _generate_data_structures(self, analysis: CodeAnalysis) -> Dict[str, Any]:
        """Generate data structure mappings."""
        structures = {
            "primitive_types": {
                ProgrammingLanguage.COBOL: ["PIC X", "PIC 9", "PIC S9"],
                ProgrammingLanguage.JAVA: ["String", "int", "double", "boolean"],
                ProgrammingLanguage.PYTHON: ["str", "int", "float", "bool"],
            },
            "complex_types": {
                ProgrammingLanguage.COBOL: ["OCCURS", "REDEFINES"],
                ProgrammingLanguage.JAVA: ["List", "Map", "Set", "Array"],
                ProgrammingLanguage.PYTHON: ["list", "dict", "set", "tuple"],
            }
        }
        
        return {
            "source_types": structures.get(analysis.source_language, {}),
            "target_types": structures.get(analysis.target_language, {}),
            "mappings": self._generate_type_mappings(analysis.source_language, analysis.target_language)
        }
    
    def _generate_type_mappings(self, source: ProgrammingLanguage, target: ProgrammingLanguage) -> Dict[str, str]:
        """Generate type mappings between languages."""
        mappings = {}
        
        if source == ProgrammingLanguage.COBOL and target == ProgrammingLanguage.JAVA:
            mappings = {
                "PIC X": "String",
                "PIC 9": "int", 
                "PIC S9": "int",
                "PIC 9V99": "double",
                "PIC S9V99": "double",
            }
        elif source == ProgrammingLanguage.COBOL and target == ProgrammingLanguage.PYTHON:
            mappings = {
                "PIC X": "str",
                "PIC 9": "int",
                "PIC S9": "int", 
                "PIC 9V99": "float",
                "PIC S9V99": "float",
            }
        
        return mappings
    
    async def _generate_conversion_rules(self, analysis: CodeAnalysis, document: TechnicalDocument):
        """Generate language-specific conversion rules."""
        # Language mappings
        document.language_mappings = self._generate_language_mappings(analysis)
        
        # Pattern conversions
        document.pattern_conversions = self._generate_pattern_conversions(analysis)
        
        # API mappings
        document.api_mappings = self._generate_api_mappings(analysis)
    
    def _generate_language_mappings(self, analysis: CodeAnalysis) -> Dict[str, str]:
        """Generate language-specific syntax mappings."""
        mappings = {}
        
        if analysis.source_language == ProgrammingLanguage.COBOL:
            if analysis.target_language == ProgrammingLanguage.JAVA:
                mappings = {
                    "PERFORM": "for/while loop",
                    "IF-ELSE": "if-else statement",
                    "MOVE": "assignment",
                    "DISPLAY": "System.out.println",
                    "ACCEPT": "Scanner input",
                }
            elif analysis.target_language == ProgrammingLanguage.PYTHON:
                mappings = {
                    "PERFORM": "for/while loop",
                    "IF-ELSE": "if-else statement", 
                    "MOVE": "assignment",
                    "DISPLAY": "print",
                    "ACCEPT": "input",
                }
        
        return mappings
    
    def _generate_pattern_conversions(self, analysis: CodeAnalysis) -> List[Dict[str, Any]]:
        """Generate pattern conversion rules."""
        patterns = []
        
        if analysis.source_language == ProgrammingLanguage.COBOL:
            if analysis.target_language == ProgrammingLanguage.JAVA:
                patterns = [
                    {
                        "source_pattern": "PERFORM UNTIL condition",
                        "target_pattern": "while (!condition) { ... }",
                        "description": "Convert COBOL PERFORM UNTIL to Java while loop"
                    },
                    {
                        "source_pattern": "IF condition THEN ... ELSE ... END-IF",
                        "target_pattern": "if (condition) { ... } else { ... }",
                        "description": "Convert COBOL IF-ELSE to Java if-else"
                    }
                ]
        
        return patterns
    
    def _generate_api_mappings(self, analysis: CodeAnalysis) -> Dict[str, str]:
        """Generate API and library mappings."""
        mappings = {}
        
        if analysis.source_language == ProgrammingLanguage.COBOL:
            if analysis.target_language == ProgrammingLanguage.JAVA:
                mappings = {
                    "COBOL File I/O": "Java File API",
                    "COBOL Database": "JDBC",
                    "COBOL Math": "Java Math class",
                }
            elif analysis.target_language == ProgrammingLanguage.PYTHON:
                mappings = {
                    "COBOL File I/O": "Python file operations",
                    "COBOL Database": "SQLAlchemy/psycopg2",
                    "COBOL Math": "Python math module",
                }
        
        return mappings
    
    async def _generate_implementation_details(self, analysis: CodeAnalysis, document: TechnicalDocument):
        """Generate implementation details."""
        # File structure
        document.file_structure = {
            "source_files": analysis.total_files,
            "target_structure": self._get_target_file_structure(analysis.target_language),
            "naming_convention": self._get_naming_convention(analysis.target_language),
        }
        
        # Naming conventions
        document.naming_conventions = {
            "classes": "PascalCase" if analysis.target_language in [ProgrammingLanguage.JAVA, ProgrammingLanguage.C_SHARP] else "snake_case",
            "functions": "camelCase" if analysis.target_language in [ProgrammingLanguage.JAVA, ProgrammingLanguage.JAVASCRIPT] else "snake_case",
            "variables": "camelCase" if analysis.target_language in [ProgrammingLanguage.JAVA, ProgrammingLanguage.JAVASCRIPT] else "snake_case",
        }
        
        # Coding standards
        document.coding_standards = self._get_coding_standards(analysis.target_language)
        
        # Dependencies
        document.required_libraries = self._get_required_libraries(analysis.target_language)
        document.build_configuration = self._get_build_configuration(analysis.target_language)
    
    def _get_target_file_structure(self, language: ProgrammingLanguage) -> Dict[str, Any]:
        """Get target file structure for language."""
        structures = {
            ProgrammingLanguage.JAVA: {
                "src/main/java": "Source files",
                "src/test/java": "Test files",
                "src/main/resources": "Resources",
                "pom.xml": "Build configuration"
            },
            ProgrammingLanguage.PYTHON: {
                "src": "Source files",
                "tests": "Test files",
                "requirements.txt": "Dependencies",
                "setup.py": "Build configuration"
            }
        }
        return structures.get(language, {"src": "Source files"})
    
    def _get_naming_convention(self, language: ProgrammingLanguage) -> str:
        """Get naming convention for language."""
        conventions = {
            ProgrammingLanguage.JAVA: "camelCase",
            ProgrammingLanguage.PYTHON: "snake_case",
            ProgrammingLanguage.JAVASCRIPT: "camelCase",
            ProgrammingLanguage.C_SHARP: "PascalCase",
        }
        return conventions.get(language, "snake_case")
    
    def _get_coding_standards(self, language: ProgrammingLanguage) -> List[str]:
        """Get coding standards for language."""
        standards = {
            ProgrammingLanguage.JAVA: [
                "Follow Java naming conventions",
                "Use meaningful variable names",
                "Add proper documentation",
                "Handle exceptions appropriately"
            ],
            ProgrammingLanguage.PYTHON: [
                "Follow PEP 8 style guide",
                "Use type hints where appropriate",
                "Write docstrings for functions",
                "Handle exceptions with try-except"
            ]
        }
        return standards.get(language, ["Follow language best practices"])
    
    def _get_required_libraries(self, language: ProgrammingLanguage) -> List[str]:
        """Get required libraries for language."""
        libraries = {
            ProgrammingLanguage.JAVA: ["junit-jupiter", "slf4j-api"],
            ProgrammingLanguage.PYTHON: ["pytest", "requests"],
            ProgrammingLanguage.JAVASCRIPT: ["jest", "axios"],
        }
        return libraries.get(language, [])
    
    def _get_build_configuration(self, language: ProgrammingLanguage) -> Dict[str, Any]:
        """Get build configuration for language."""
        configs = {
            ProgrammingLanguage.JAVA: {
                "build_tool": "Maven",
                "java_version": "11",
                "encoding": "UTF-8"
            },
            ProgrammingLanguage.PYTHON: {
                "python_version": "3.9+",
                "package_manager": "pip",
                "virtual_env": "venv"
            }
        }
        return configs.get(language, {})
    
    async def _generate_testing_requirements(self, analysis: CodeAnalysis, document: TechnicalDocument):
        """Generate testing requirements."""
        document.test_requirements = [
            "Unit tests for all converted functions",
            "Integration tests for data flow",
            "Performance tests for critical paths",
            "Regression tests to ensure functionality preservation"
        ]
        
        document.validation_criteria = [
            "All source functionality is preserved",
            "Code compiles without errors",
            "Tests pass with expected results",
            "Performance meets requirements",
            "Code follows target language standards"
        ]


class CodeConversionAgent(Agent):
    """
    Agent responsible for converting code from source to target language.
    
    This agent:
    - Takes technical document and code files as input
    - Applies conversion rules and patterns
    - Generates target language code
    - Ensures code quality and standards compliance
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.formatter = CodeFormatter()
        
    async def execute(self, task: Any, context: Optional[AgentContext] = None) -> List[CodeFile]:
        """
        Execute code conversion task.
        
        Args:
            task: Tuple of (code_files, technical_document, request)
            context: Optional execution context
            
        Returns:
            List of converted CodeFile objects
        """
        start_time = time.time()
        self.logger.info("Starting code conversion")
        
        try:
            # Extract inputs
            if isinstance(task, tuple) and len(task) == 3:
                code_files, technical_doc, request = task
            else:
                raise ValueError(f"Unsupported task type: {type(task)}")
            
            # Convert code files
            converted_files = await self._convert_code_files(code_files, technical_doc, request)
            
            # Format converted code
            formatted_files = await self._format_converted_files(converted_files, request)
            
            self.logger.info("Code conversion completed", 
                           input_files=len(code_files),
                           output_files=len(formatted_files),
                           duration=time.time() - start_time)
            
            return formatted_files
            
        except Exception as e:
            self.logger.error("Code conversion failed", error=str(e))
            raise
    
    async def _convert_code_files(self, code_files: List[CodeFile], 
                                technical_doc: TechnicalDocument,
                                request: ConversionRequest) -> List[CodeFile]:
        """Convert code files using technical document rules."""
        converted_files = []
        
        for code_file in code_files:
            try:
                converted_file = await self._convert_single_file(code_file, technical_doc, request)
                if converted_file:
                    converted_files.append(converted_file)
            except Exception as e:
                self.logger.warning("Failed to convert file", 
                                  file_path=str(code_file.path), 
                                  error=str(e))
        
        return converted_files
    
    async def _convert_single_file(self, code_file: CodeFile, 
                                 technical_doc: TechnicalDocument,
                                 request: ConversionRequest) -> Optional[CodeFile]:
        """Convert a single code file."""
        # Determine target file path
        target_path = self._get_target_file_path(code_file, request)
        
        # Convert content based on language pair
        converted_content = await self._convert_content(code_file, technical_doc, request)
        
        if converted_content:
            return CodeFile(
                path=target_path,
                content=converted_content,
                language=request.target_language,
                file_type=code_file.file_type
            )
        
        return None
    
    def _get_target_file_path(self, code_file: CodeFile, request: ConversionRequest) -> Path:
        """Get target file path with appropriate extension."""
        source_path = code_file.path
        target_ext = self._get_target_extension(request.target_language)
        
        # Replace source extension with target extension
        target_name = source_path.stem + target_ext
        return Path(target_name)
    
    def _get_target_extension(self, language: ProgrammingLanguage) -> str:
        """Get file extension for target language."""
        extensions = {
            ProgrammingLanguage.JAVA: ".java",
            ProgrammingLanguage.PYTHON: ".py",
            ProgrammingLanguage.C_SHARP: ".cs",
            ProgrammingLanguage.CPP: ".cpp",
            ProgrammingLanguage.JAVASCRIPT: ".js",
            ProgrammingLanguage.TYPESCRIPT: ".ts",
            ProgrammingLanguage.GO: ".go",
            ProgrammingLanguage.RUST: ".rs",
        }
        return extensions.get(language, ".txt")
    
    async def _convert_content(self, code_file: CodeFile, 
                             technical_doc: TechnicalDocument,
                             request: ConversionRequest) -> str:
        """Convert code content using technical document rules."""
        content = code_file.content
        
        # Apply language-specific conversions
        if code_file.language == ProgrammingLanguage.COBOL:
            if request.target_language == ProgrammingLanguage.JAVA:
                return self._convert_cobol_to_java(content, technical_doc)
            elif request.target_language == ProgrammingLanguage.PYTHON:
                return self._convert_cobol_to_python(content, technical_doc)
        
        # For other languages, return original content with basic formatting
        return self.formatter.format_code(content, request.target_language, request.code_style)
    
    def _convert_cobol_to_java(self, content: str, technical_doc: TechnicalDocument) -> str:
        """Convert COBOL code to Java."""
        java_code = []
        
        # Add Java class structure
        java_code.append("import java.util.*;")
        java_code.append("import java.io.*;")
        java_code.append("")
        java_code.append("public class ConvertedCobolProgram {")
        java_code.append("    public static void main(String[] args) {")
        java_code.append("        // Converted from COBOL")
        java_code.append("        try {")
        
        # Convert COBOL lines
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith('*'):
                continue
            
            # Apply conversion rules from technical document
            converted_line = self._apply_conversion_rules(line, technical_doc.language_mappings)
            if converted_line:
                java_code.append(f"            {converted_line}")
        
        # Close Java structure
        java_code.append("        } catch (Exception e) {")
        java_code.append("            System.err.println(\"Error: \" + e.getMessage());")
        java_code.append("        }")
        java_code.append("    }")
        java_code.append("}")
        
        return '\n'.join(java_code)
    
    def _convert_cobol_to_python(self, content: str, technical_doc: TechnicalDocument) -> str:
        """Convert COBOL code to Python."""
        python_code = []
        
        # Add Python imports
        python_code.append("#!/usr/bin/env python3")
        python_code.append("# Converted from COBOL")
        python_code.append("")
        python_code.append("def main():")
        python_code.append("    try:")
        
        # Convert COBOL lines
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith('*'):
                continue
            
            # Apply conversion rules from technical document
            converted_line = self._apply_conversion_rules(line, technical_doc.language_mappings)
            if converted_line:
                python_code.append(f"        {converted_line}")
        
        # Close Python structure
        python_code.append("    except Exception as e:")
        python_code.append("        print(f\"Error: {e}\")")
        python_code.append("")
        python_code.append("if __name__ == \"__main__\":")
        python_code.append("    main()")
        
        return '\n'.join(python_code)
    
    def _apply_conversion_rules(self, line: str, mappings: Dict[str, str]) -> str:
        """Apply conversion rules to a line of code."""
        converted_line = line
        
        # Apply basic COBOL to target language mappings
        cobol_mappings = {
            'DISPLAY': 'System.out.println' if 'java' in str(mappings) else 'print',
            'ACCEPT': 'Scanner input' if 'java' in str(mappings) else 'input',
            'MOVE': '=',
            'TO': '=',
            'PERFORM': 'for' if 'loop' in str(mappings) else 'call',
            'UNTIL': 'while',
            'END-PERFORM': '}',
            'IF': 'if',
            'THEN': ':',
            'ELSE': 'else:',
            'END-IF': '}',
        }
        
        for cobol_keyword, target_keyword in cobol_mappings.items():
            if cobol_keyword in converted_line.upper():
                converted_line = converted_line.upper().replace(cobol_keyword, target_keyword)
        
        return converted_line
    
    async def _format_converted_files(self, converted_files: List[CodeFile], 
                                    request: ConversionRequest) -> List[CodeFile]:
        """Format converted files according to target language standards."""
        formatted_files = []
        
        for code_file in converted_files:
            try:
                formatted_content = self.formatter.format_code(
                    code_file.content, 
                    code_file.language, 
                    request.code_style
                )
                
                formatted_file = CodeFile(
                    path=code_file.path,
                    content=formatted_content,
                    language=code_file.language,
                    file_type=code_file.file_type
                )
                
                formatted_files.append(formatted_file)
                
            except Exception as e:
                self.logger.warning("Failed to format file", 
                                  file_path=str(code_file.path), 
                                  error=str(e))
                formatted_files.append(code_file)  # Keep unformatted version
        
        return formatted_files


class ConversionOrchestrator:
    """
    Orchestrates the entire code conversion workflow.
    
    This class coordinates the three main agents:
    1. CodeAnalysisAgent - Analyzes source code
    2. DocumentationAgent - Generates technical documentation
    3. CodeConversionAgent - Converts code to target language
    """
    
    def __init__(self):
        self.orchestrator = AgentOrchestrator()
        self.logger = logger.bind(orchestrator="conversion")
        
        # Initialize agents
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize the conversion agents."""
        # Code Analysis Agent
        analysis_config = AgentConfig(
            name="code_analysis_agent",
            description="Analyzes code structure and functionality",
            model="gpt-4",
            memory_enabled=True,
            reasoning_enabled=True
        )
        self.analysis_agent = CodeAnalysisAgent(analysis_config)
        
        # Documentation Agent
        doc_config = AgentConfig(
            name="documentation_agent", 
            description="Generates technical requirements documents",
            model="gpt-4",
            memory_enabled=True,
            reasoning_enabled=True
        )
        self.doc_agent = DocumentationAgent(doc_config)
        
        # Code Conversion Agent
        conversion_config = AgentConfig(
            name="code_conversion_agent",
            description="Converts code to target language",
            model="gpt-4", 
            memory_enabled=True,
            reasoning_enabled=True
        )
        self.conversion_agent = CodeConversionAgent(conversion_config)
        
        # Register agents with orchestrator
        self.orchestrator.register_agent("code_analysis", self.analysis_agent)
        self.orchestrator.register_agent("documentation", self.doc_agent)
        self.orchestrator.register_agent("conversion", self.conversion_agent)
        
        self.logger.info("Conversion agents initialized")
    
    async def convert_code(self, request: ConversionRequest) -> ConversionResult:
        """
        Execute the complete code conversion workflow.
        
        Args:
            request: ConversionRequest with source files and target configuration
            
        Returns:
            ConversionResult with analysis, documentation, and converted code
        """
        start_time = time.time()
        result = ConversionResult(request_id=request.id)
        
        try:
            self.logger.info("Starting code conversion workflow", 
                           request_id=str(request.id),
                           source_language=request.source_language.value,
                           target_language=request.target_language.value)
            
            # Step 1: Code Analysis
            result.status = ConversionStatus.ANALYZING
            analysis_start = time.time()
            
            analysis = await self.analysis_agent.execute(request)
            result.code_analysis = analysis
            result.analysis_duration = time.time() - analysis_start
            
            self.logger.info("Code analysis completed", 
                           duration=result.analysis_duration,
                           files_analyzed=analysis.total_files)
            
            # Step 2: Documentation Generation
            result.status = ConversionStatus.DOCUMENTING
            doc_start = time.time()
            
            technical_doc = await self.doc_agent.execute((analysis, request))
            result.technical_document = technical_doc
            result.documentation_duration = time.time() - doc_start
            
            self.logger.info("Documentation generation completed", 
                           duration=result.documentation_duration)
            
            # Step 3: Code Conversion
            result.status = ConversionStatus.CONVERTING
            conversion_start = time.time()
            
            # Extract code files from request
            if request.input_zip_path:
                from .utils import CodeExtractor
                extractor = CodeExtractor()
                code_files = extractor.extract_from_zip(request.input_zip_path)
            else:
                code_files = request.input_files
            
            converted_files = await self.conversion_agent.execute((code_files, technical_doc, request))
            result.converted_files = converted_files
            result.conversion_duration = time.time() - conversion_start
            
            self.logger.info("Code conversion completed", 
                           duration=result.conversion_duration,
                           files_converted=len(converted_files))
            
            # Step 4: Generate output
            await self._generate_output(result, request)
            
            # Step 5: Calculate metrics and finalize
            result.status = ConversionStatus.COMPLETED
            result.total_duration = time.time() - start_time
            
            # Calculate quality metrics
            result.conversion_accuracy = self._calculate_accuracy(result)
            result.code_coverage = self._calculate_coverage(result)
            
            # Generate summary
            result.summary = self._generate_summary(result)
            result.recommendations = self._generate_recommendations(result)
            
            self.logger.info("Code conversion workflow completed", 
                           total_duration=result.total_duration,
                           accuracy=result.conversion_accuracy)
            
        except Exception as e:
            result.status = ConversionStatus.FAILED
            result.conversion_issues.append({
                "type": "workflow_error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
            self.logger.error("Code conversion workflow failed", 
                            error=str(e))
            raise
        
        return result
    
    async def _generate_output(self, result: ConversionResult, request: ConversionRequest):
        """Generate output files and directories."""
        # Create output directory
        output_dir = Path(f"converted_code_{request.id}")
        output_dir.mkdir(exist_ok=True)
        result.output_directory = output_dir
        
        # Write converted files
        for code_file in result.converted_files:
            file_path = output_dir / code_file.path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(code_file.content, encoding='utf-8')
        
        # Write technical document
        if result.technical_document:
            doc_path = output_dir / "technical_documentation.md"
            doc_content = self._format_documentation(result.technical_document)
            doc_path.write_text(doc_content, encoding='utf-8')
        
        # Write conversion report
        report_path = output_dir / "conversion_report.json"
        report_content = result.json(indent=2)
        report_path.write_text(report_content, encoding='utf-8')
        
        self.logger.info("Output generated", output_directory=str(output_dir))
    
    def _format_documentation(self, doc: TechnicalDocument) -> str:
        """Format technical document as markdown."""
        formatter = DocumentationFormatter()
        return formatter.format_documentation(doc.dict(), "markdown")
    
    def _calculate_accuracy(self, result: ConversionResult) -> float:
        """Calculate conversion accuracy."""
        if not result.code_analysis or not result.converted_files:
            return 0.0
        
        # Simple accuracy calculation based on file count
        source_files = result.code_analysis.total_files
        converted_files = len(result.converted_files)
        
        if source_files == 0:
            return 0.0
        
        return min(1.0, converted_files / source_files)
    
    def _calculate_coverage(self, result: ConversionResult) -> float:
        """Calculate code coverage."""
        if not result.code_analysis:
            return 0.0
        
        # Simple coverage calculation
        total_lines = result.code_analysis.total_lines
        if total_lines == 0:
            return 0.0
        
        # Estimate converted lines (this would be more sophisticated in practice)
        converted_lines = sum(f.line_count for f in result.converted_files)
        return min(1.0, converted_lines / total_lines)
    
    def _generate_summary(self, result: ConversionResult) -> Dict[str, Any]:
        """Generate conversion summary."""
        return {
            "total_files": result.code_analysis.total_files if result.code_analysis else 0,
            "converted_files": len(result.converted_files),
            "source_language": result.code_analysis.source_language.value if result.code_analysis else "unknown",
            "target_language": result.code_analysis.target_language.value if result.code_analysis else "unknown",
            "total_lines": result.code_analysis.total_lines if result.code_analysis else 0,
            "conversion_accuracy": result.conversion_accuracy,
            "code_coverage": result.code_coverage,
            "total_duration": result.total_duration,
        }
    
    def _generate_recommendations(self, result: ConversionResult) -> List[str]:
        """Generate recommendations for the converted code."""
        recommendations = []
        
        if result.conversion_accuracy < 0.8:
            recommendations.append("Review converted code for missing functionality")
        
        if result.code_coverage < 0.9:
            recommendations.append("Add comprehensive tests for converted code")
        
        if result.conversion_issues:
            recommendations.append("Address conversion issues before deployment")
        
        if not result.converted_files:
            recommendations.append("No files were successfully converted")
        
        recommendations.extend([
            "Review and test all converted functions",
            "Update any hardcoded paths or configurations",
            "Verify external dependencies are properly mapped",
            "Run performance tests on converted code"
        ])
        
        return recommendations 