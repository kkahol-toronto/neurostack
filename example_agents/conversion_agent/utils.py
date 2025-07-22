"""
Utility classes and functions for the code conversion agent system.

This module provides helper classes for:
- Extracting code from zip files
- Detecting programming languages
- Formatting code and documentation
- File processing and validation
"""

import ast
import json
import re
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import structlog

from .models import CodeFile, CodeFileType, ProgrammingLanguage

logger = structlog.get_logger(__name__)


class CodeExtractor:
    """Extracts code files from various input formats."""
    
    def __init__(self):
        self.supported_extensions = {
            # Source files
            '.cobol': ProgrammingLanguage.COBOL,
            '.cbl': ProgrammingLanguage.COBOL,
            '.cob': ProgrammingLanguage.COBOL,
            '.java': ProgrammingLanguage.JAVA,
            '.py': ProgrammingLanguage.PYTHON,
            '.cs': ProgrammingLanguage.C_SHARP,
            '.cpp': ProgrammingLanguage.CPP,
            '.cc': ProgrammingLanguage.CPP,
            '.cxx': ProgrammingLanguage.CPP,
            '.c': ProgrammingLanguage.CPP,
            '.js': ProgrammingLanguage.JAVASCRIPT,
            '.ts': ProgrammingLanguage.TYPESCRIPT,
            '.go': ProgrammingLanguage.GO,
            '.rs': ProgrammingLanguage.RUST,
            '.f90': ProgrammingLanguage.FORTRAN,
            '.f95': ProgrammingLanguage.FORTRAN,
            '.pas': ProgrammingLanguage.PASCAL,
            '.bas': ProgrammingLanguage.BASIC,
            '.asm': ProgrammingLanguage.ASSEMBLY,
            '.s': ProgrammingLanguage.ASSEMBLY,
            '.php': ProgrammingLanguage.PHP,
            '.rb': ProgrammingLanguage.RUBY,
            '.scala': ProgrammingLanguage.SCALA,
            '.kt': ProgrammingLanguage.KOTLIN,
            '.swift': ProgrammingLanguage.SWIFT,
            '.r': ProgrammingLanguage.R,
            '.m': ProgrammingLanguage.MATLAB,
            
            # Header files
            '.h': ProgrammingLanguage.CPP,
            '.hpp': ProgrammingLanguage.CPP,
            '.hxx': ProgrammingLanguage.CPP,
            
            # Configuration files
            '.json': ProgrammingLanguage.JAVASCRIPT,
            '.xml': ProgrammingLanguage.JAVA,
            '.yaml': ProgrammingLanguage.PYTHON,
            '.yml': ProgrammingLanguage.PYTHON,
            '.toml': ProgrammingLanguage.RUST,
            '.ini': ProgrammingLanguage.PYTHON,
            '.cfg': ProgrammingLanguage.PYTHON,
            
            # Build files
            '.gradle': ProgrammingLanguage.JAVA,
            '.pom.xml': ProgrammingLanguage.JAVA,
            '.build.gradle': ProgrammingLanguage.JAVA,
            '.sbt': ProgrammingLanguage.SCALA,
            '.cargo.toml': ProgrammingLanguage.RUST,
            '.go.mod': ProgrammingLanguage.GO,
            '.requirements.txt': ProgrammingLanguage.PYTHON,
            '.setup.py': ProgrammingLanguage.PYTHON,
            '.pyproject.toml': ProgrammingLanguage.PYTHON,
        }
        
        self.ignore_patterns = [
            r'\.git/',
            r'\.svn/',
            r'\.hg/',
            r'__pycache__/',
            r'\.pyc$',
            r'\.class$',
            r'\.o$',
            r'\.exe$',
            r'\.dll$',
            r'\.so$',
            r'\.dylib$',
            r'\.log$',
            r'\.tmp$',
            r'\.temp$',
            r'\.DS_Store$',
            r'Thumbs\.db$',
        ]
    
    def extract_from_zip(self, zip_path: Path, extract_to: Optional[Path] = None) -> List[CodeFile]:
        """
        Extract code files from a zip archive.
        
        Args:
            zip_path: Path to the zip file
            extract_to: Directory to extract files to (optional)
            
        Returns:
            List of CodeFile objects
        """
        if not zip_path.exists():
            raise FileNotFoundError(f"Zip file not found: {zip_path}")
        
        code_files = []
        extract_dir = extract_to or Path(f"/tmp/neurostack_extract_{zip_path.stem}")
        extract_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Extract all files
                zip_ref.extractall(extract_dir)
                
                # Process extracted files
                for file_path in extract_dir.rglob('*'):
                    if file_path.is_file() and not self._should_ignore(file_path):
                        code_file = self._process_file(file_path)
                        if code_file:
                            code_files.append(code_file)
            
            logger.info("Extracted code files from zip", 
                       zip_path=str(zip_path), 
                       file_count=len(code_files))
            
        except Exception as e:
            logger.error("Failed to extract zip file", 
                        zip_path=str(zip_path), 
                        error=str(e))
            raise
        
        return code_files
    
    def extract_from_directory(self, directory: Path) -> List[CodeFile]:
        """
        Extract code files from a directory.
        
        Args:
            directory: Path to the directory
            
        Returns:
            List of CodeFile objects
        """
        if not directory.exists() or not directory.is_dir():
            raise ValueError(f"Invalid directory: {directory}")
        
        code_files = []
        
        for file_path in directory.rglob('*'):
            if file_path.is_file() and not self._should_ignore(file_path):
                code_file = self._process_file(file_path)
                if code_file:
                    code_files.append(code_file)
        
        logger.info("Extracted code files from directory", 
                   directory=str(directory), 
                   file_count=len(code_files))
        
        return code_files
    
    def _process_file(self, file_path: Path) -> Optional[CodeFile]:
        """Process a single file and create a CodeFile object."""
        try:
            # Detect language
            language = self._detect_language(file_path)
            if not language:
                return None
            
            # Determine file type
            file_type = self._determine_file_type(file_path)
            
            # Read file content
            content = self._read_file_content(file_path)
            
            # Create CodeFile object
            code_file = CodeFile(
                path=file_path,
                content=content,
                language=language,
                file_type=file_type
            )
            
            return code_file
            
        except Exception as e:
            logger.warning("Failed to process file", 
                          file_path=str(file_path), 
                          error=str(e))
            return None
    
    def _detect_language(self, file_path: Path) -> Optional[ProgrammingLanguage]:
        """Detect programming language from file extension and content."""
        # Check file extension
        extension = file_path.suffix.lower()
        if extension in self.supported_extensions:
            return self.supported_extensions[extension]
        
        # Check filename patterns
        filename = file_path.name.lower()
        if filename in self.supported_extensions:
            return self.supported_extensions[filename]
        
        # Try content-based detection
        return self._detect_language_by_content(file_path)
    
    def _detect_language_by_content(self, file_path: Path) -> Optional[ProgrammingLanguage]:
        """Detect language by analyzing file content."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')[:1000]
            
            # Language-specific patterns
            patterns = {
                ProgrammingLanguage.COBOL: [
                    r'IDENTIFICATION DIVISION',
                    r'PROCEDURE DIVISION',
                    r'DATA DIVISION',
                    r'WORKING-STORAGE SECTION',
                    r'PERFORM UNTIL',
                    r'END-PERFORM',
                ],
                ProgrammingLanguage.JAVA: [
                    r'public class',
                    r'import java\.',
                    r'@Override',
                    r'public static void main',
                ],
                ProgrammingLanguage.PYTHON: [
                    r'def ',
                    r'import ',
                    r'from ',
                    r'class ',
                    r'if __name__ == "__main__"',
                ],
                ProgrammingLanguage.C_SHARP: [
                    r'using System',
                    r'namespace ',
                    r'public class',
                    r'static void Main',
                ],
                ProgrammingLanguage.CPP: [
                    r'#include <',
                    r'using namespace std',
                    r'int main\(',
                    r'class ',
                ],
                ProgrammingLanguage.JAVASCRIPT: [
                    r'function ',
                    r'const ',
                    r'let ',
                    r'var ',
                    r'console\.log',
                ],
                ProgrammingLanguage.GO: [
                    r'package ',
                    r'import ',
                    r'func ',
                    r'fmt\.',
                ],
                ProgrammingLanguage.RUST: [
                    r'fn ',
                    r'use ',
                    r'pub ',
                    r'println!',
                ],
            }
            
            for language, language_patterns in patterns.items():
                for pattern in language_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        return language
            
        except Exception as e:
            logger.warning("Failed to detect language by content", 
                          file_path=str(file_path), 
                          error=str(e))
        
        return None
    
    def _determine_file_type(self, file_path: Path) -> CodeFileType:
        """Determine the type of code file."""
        filename = file_path.name.lower()
        extension = file_path.suffix.lower()
        
        # Test files
        if any(pattern in filename for pattern in ['test', 'spec', 'specs']):
            return CodeFileType.TEST
        
        # Header files
        if extension in ['.h', '.hpp', '.hxx']:
            return CodeFileType.HEADER
        
        # Configuration files
        if extension in ['.json', '.xml', '.yaml', '.yml', '.toml', '.ini', '.cfg']:
            return CodeFileType.CONFIG
        
        # Build files
        if any(pattern in filename for pattern in ['gradle', 'pom.xml', 'build.gradle', 'cargo.toml', 'go.mod', 'requirements.txt', 'setup.py']):
            return CodeFileType.BUILD
        
        # Documentation files
        if extension in ['.md', '.txt', '.rst', '.adoc']:
            return CodeFileType.DOCUMENTATION
        
        return CodeFileType.SOURCE
    
    def _read_file_content(self, file_path: Path) -> str:
        """Read file content with proper encoding detection."""
        try:
            # Try UTF-8 first
            return file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            try:
                # Try with error handling
                return file_path.read_text(encoding='utf-8', errors='replace')
            except Exception:
                # Fallback to binary read
                return file_path.read_bytes().decode('latin-1', errors='replace')
    
    def _should_ignore(self, file_path: Path) -> bool:
        """Check if file should be ignored based on patterns."""
        file_str = str(file_path)
        for pattern in self.ignore_patterns:
            if re.search(pattern, file_str, re.IGNORECASE):
                return True
        return False


class LanguageDetector:
    """Enhanced language detection with content analysis."""
    
    def __init__(self):
        self.language_signatures = {
            ProgrammingLanguage.COBOL: {
                'keywords': ['IDENTIFICATION', 'DIVISION', 'PROCEDURE', 'DATA', 'WORKING-STORAGE', 'PERFORM', 'END-PERFORM'],
                'patterns': [r'^\s*\d{6}\s+', r'\.\s*$'],  # Line numbers and periods
                'file_extensions': ['.cobol', '.cbl', '.cob']
            },
            ProgrammingLanguage.JAVA: {
                'keywords': ['public', 'class', 'import', 'package', 'static', 'void', 'main'],
                'patterns': [r'public\s+class', r'import\s+java\.', r'@Override'],
                'file_extensions': ['.java']
            },
            ProgrammingLanguage.PYTHON: {
                'keywords': ['def', 'import', 'from', 'class', 'if', 'for', 'while'],
                'patterns': [r'def\s+\w+\s*\(', r'import\s+\w+', r'if __name__ == "__main__"'],
                'file_extensions': ['.py']
            }
        }
    
    def detect_language(self, content: str, file_path: Optional[Path] = None) -> ProgrammingLanguage:
        """Detect programming language from content and file path."""
        # Check file extension first
        if file_path:
            extension = file_path.suffix.lower()
            for lang, sig in self.language_signatures.items():
                if extension in sig['file_extensions']:
                    return lang
        
        # Analyze content
        scores = {}
        for language, signature in self.language_signatures.items():
            score = self._calculate_language_score(content, signature)
            scores[language] = score
        
        # Return language with highest score
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        
        return ProgrammingLanguage.PYTHON  # Default fallback
    
    def _calculate_language_score(self, content: str, signature: Dict[str, Any]) -> float:
        """Calculate confidence score for a language based on content."""
        score = 0.0
        content_lower = content.lower()
        
        # Check keywords
        for keyword in signature['keywords']:
            if keyword.lower() in content_lower:
                score += 1.0
        
        # Check patterns
        for pattern in signature['patterns']:
            if re.search(pattern, content, re.IGNORECASE):
                score += 2.0
        
        return score


class CodeFormatter:
    """Formats code according to language-specific standards."""
    
    def __init__(self):
        self.formatters = {
            ProgrammingLanguage.JAVA: self._format_java,
            ProgrammingLanguage.PYTHON: self._format_python,
            ProgrammingLanguage.COBOL: self._format_cobol,
            ProgrammingLanguage.C_SHARP: self._format_csharp,
            ProgrammingLanguage.CPP: self._format_cpp,
            ProgrammingLanguage.JAVASCRIPT: self._format_javascript,
        }
    
    def format_code(self, code: str, language: ProgrammingLanguage, style: str = "standard") -> str:
        """Format code according to language and style preferences."""
        formatter = self.formatters.get(language)
        if formatter:
            return formatter(code, style)
        return code
    
    def _format_java(self, code: str, style: str) -> str:
        """Format Java code."""
        # Basic Java formatting
        lines = code.split('\n')
        formatted_lines = []
        indent_level = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                formatted_lines.append('')
                continue
            
            # Handle braces
            if stripped.endswith('{'):
                formatted_lines.append('    ' * indent_level + stripped)
                indent_level += 1
            elif stripped.startswith('}'):
                indent_level = max(0, indent_level - 1)
                formatted_lines.append('    ' * indent_level + stripped)
            else:
                formatted_lines.append('    ' * indent_level + stripped)
        
        return '\n'.join(formatted_lines)
    
    def _format_python(self, code: str, style: str) -> str:
        """Format Python code."""
        try:
            # Try to parse and format using ast
            tree = ast.parse(code)
            # Basic formatting - in a real implementation, you'd use black or autopep8
            return code
        except SyntaxError:
            return code
    
    def _format_cobol(self, code: str, style: str) -> str:
        """Format COBOL code."""
        # COBOL has specific formatting requirements
        lines = code.split('\n')
        formatted_lines = []
        
        for line in lines:
            if len(line.strip()) == 0:
                formatted_lines.append('')
                continue
            
            # COBOL line structure: 1-6: sequence, 7: indicator, 8-11: area A, 12-72: area B
            if len(line) < 7:
                formatted_lines.append(line.ljust(7))
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def _format_csharp(self, code: str, style: str) -> str:
        """Format C# code."""
        # Similar to Java formatting
        return self._format_java(code, style)
    
    def _format_cpp(self, code: str, style: str) -> str:
        """Format C++ code."""
        # Similar to Java formatting
        return self._format_java(code, style)
    
    def _format_javascript(self, code: str, style: str) -> str:
        """Format JavaScript code."""
        # Basic JavaScript formatting
        return self._format_java(code, style)


class DocumentationFormatter:
    """Formats technical documentation."""
    
    def __init__(self):
        self.templates = {
            'markdown': self._format_markdown,
            'html': self._format_html,
            'json': self._format_json,
            'text': self._format_text,
        }
    
    def format_documentation(self, content: Dict[str, Any], format_type: str = "markdown") -> str:
        """Format documentation content."""
        formatter = self.templates.get(format_type.lower())
        if formatter:
            return formatter(content)
        return str(content)
    
    def _format_markdown(self, content: Dict[str, Any]) -> str:
        """Format as Markdown."""
        md_lines = []
        
        # Title
        if 'title' in content:
            md_lines.append(f"# {content['title']}")
            md_lines.append("")
        
        # Version and metadata
        if 'version' in content:
            md_lines.append(f"**Version:** {content['version']}")
        if 'author' in content:
            md_lines.append(f"**Author:** {content['author']}")
        if 'timestamp' in content:
            md_lines.append(f"**Generated:** {content['timestamp']}")
        md_lines.append("")
        
        # Project information
        if 'project_name' in content:
            md_lines.append(f"## Project: {content['project_name']}")
        if 'project_description' in content:
            md_lines.append(content['project_description'])
        md_lines.append("")
        
        # Conversion context
        if 'source_language' in content and 'target_language' in content:
            md_lines.append("## Conversion Context")
            md_lines.append(f"- **Source Language:** {content['source_language']}")
            md_lines.append(f"- **Target Language:** {content['target_language']}")
            md_lines.append("")
        
        # Requirements
        if 'functional_requirements' in content and content['functional_requirements']:
            md_lines.append("## Functional Requirements")
            for req in content['functional_requirements']:
                md_lines.append(f"- {req}")
            md_lines.append("")
        
        if 'non_functional_requirements' in content and content['non_functional_requirements']:
            md_lines.append("## Non-Functional Requirements")
            for req in content['non_functional_requirements']:
                md_lines.append(f"- {req}")
            md_lines.append("")
        
        # Architecture
        if 'system_architecture' in content and content['system_architecture']:
            md_lines.append("## System Architecture")
            md_lines.append("```json")
            md_lines.append(json.dumps(content['system_architecture'], indent=2))
            md_lines.append("```")
            md_lines.append("")
        
        # Implementation details
        if 'file_structure' in content and content['file_structure']:
            md_lines.append("## File Structure")
            md_lines.append("```")
            md_lines.append(json.dumps(content['file_structure'], indent=2))
            md_lines.append("```")
            md_lines.append("")
        
        return '\n'.join(md_lines)
    
    def _format_html(self, content: Dict[str, Any]) -> str:
        """Format as HTML."""
        # Basic HTML formatting
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{content.get('title', 'Technical Documentation')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; margin-top: 30px; }}
        pre {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; }}
        code {{ background-color: #f5f5f5; padding: 2px 4px; border-radius: 3px; }}
    </style>
</head>
<body>
    <h1>{content.get('title', 'Technical Documentation')}</h1>
    <p><strong>Version:</strong> {content.get('version', '1.0')}</p>
    <p><strong>Author:</strong> {content.get('author', 'NeuroStack')}</p>
    <p><strong>Generated:</strong> {content.get('timestamp', '')}</p>
    
    <h2>Project Information</h2>
    <p><strong>Project:</strong> {content.get('project_name', '')}</p>
    <p>{content.get('project_description', '')}</p>
    
    <h2>Conversion Context</h2>
    <p><strong>Source Language:</strong> {content.get('source_language', '')}</p>
    <p><strong>Target Language:</strong> {content.get('target_language', '')}</p>
</body>
</html>
        """
        return html
    
    def _format_json(self, content: Dict[str, Any]) -> str:
        """Format as JSON."""
        return json.dumps(content, indent=2, default=str)
    
    def _format_text(self, content: Dict[str, Any]) -> str:
        """Format as plain text."""
        lines = []
        lines.append(f"TECHNICAL DOCUMENTATION")
        lines.append(f"=====================")
        lines.append("")
        lines.append(f"Title: {content.get('title', '')}")
        lines.append(f"Version: {content.get('version', '')}")
        lines.append(f"Author: {content.get('author', '')}")
        lines.append(f"Generated: {content.get('timestamp', '')}")
        lines.append("")
        lines.append(f"Project: {content.get('project_name', '')}")
        lines.append(f"Description: {content.get('project_description', '')}")
        lines.append("")
        lines.append(f"Source Language: {content.get('source_language', '')}")
        lines.append(f"Target Language: {content.get('target_language', '')}")
        lines.append("")
        
        return '\n'.join(lines) 