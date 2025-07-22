# Code Conversion Agent Example

This example demonstrates how to use NeuroStack to build a sophisticated code conversion system that can analyze, document, and convert code between different programming languages.

## 🎯 Overview

The Code Conversion Agent system consists of three specialized agents working together:

1. **CodeAnalysisAgent** - Analyzes source code structure and functionality
2. **DocumentationAgent** - Generates comprehensive technical requirements documents
3. **CodeConversionAgent** - Converts code to the target programming language
4. **ConversionOrchestrator** - Coordinates the entire conversion workflow

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Input Files   │───▶│  CodeAnalysis    │───▶│  Documentation  │
│   (ZIP/Dir)     │    │     Agent        │    │     Agent       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │  CodeConversion  │    │  Technical      │
                       │     Agent        │    │  Document       │
                       └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  Converted Code  │
                       │  + Documentation │
                       └──────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- NeuroStack library installed
- Required dependencies (see requirements.txt)

### Installation

1. **Install NeuroStack:**
   ```bash
   pip install -e ../..  # Install NeuroStack from parent directory
   ```

2. **Install additional dependencies:**
   ```bash
   pip install pydantic structlog
   ```

### Basic Usage

1. **Run with sample COBOL files:**
   ```bash
   python main.py --create-sample
   ```

2. **Convert custom code:**
   ```bash
   python main.py --input my_code.zip --source cobol --target java --project "My Project"
   ```

3. **Convert with verbose logging:**
   ```bash
   python main.py --input sample_cobol.zip --source cobol --target python --verbose
   ```

## 📋 Supported Languages

### Source Languages
- **COBOL** (.cob, .cbl, .cobol)
- **Java** (.java)
- **Python** (.py)
- **C#** (.cs)
- **C++** (.cpp, .cc, .cxx, .c)
- **JavaScript** (.js)
- **TypeScript** (.ts)
- **Go** (.go)
- **Rust** (.rs)
- **Fortran** (.f90, .f95)
- **Pascal** (.pas)
- **Basic** (.bas)
- **Assembly** (.asm, .s)
- **PHP** (.php)
- **Ruby** (.rb)
- **Scala** (.scala)
- **Kotlin** (.kt)
- **Swift** (.swift)
- **R** (.r)
- **MATLAB** (.m)

### Target Languages
- **Java** (with Spring Boot framework)
- **Python** (with FastAPI/Django)
- **C#** (with .NET Core)
- **JavaScript** (with Node.js/Express)
- **Go** (with Gin/Echo)
- **Rust** (with Actix-web)

## 🔧 Configuration

### Command Line Options

```bash
python main.py [OPTIONS]

Options:
  --input, -i PATH          Input zip file or directory
  --source, -s LANGUAGE     Source programming language
  --target, -t LANGUAGE     Target programming language
  --project, -p NAME        Project name
  --style STYLE             Output code style (standard/modern/legacy)
  --create-sample           Create sample COBOL files
  --verbose, -v             Enable verbose logging
  --help                    Show help message
```

### Environment Variables

The system uses NeuroStack's environment configuration. See the main `env.template` for available options.

## 📊 Output Structure

After conversion, the system generates:

```
converted_code_[request_id]/
├── sample_program.java          # Converted source files
├── data_processor.java
├── technical_documentation.md   # Technical requirements document
└── conversion_report.json       # Detailed conversion report
```

### Technical Documentation

The generated technical document includes:

- **Project Information** - Context and requirements
- **Conversion Context** - Source and target language details
- **Functional Requirements** - What the converted code should do
- **Non-Functional Requirements** - Performance, security, etc.
- **System Architecture** - Component mappings and structure
- **Conversion Rules** - Language-specific syntax mappings
- **Implementation Details** - File structure, naming conventions
- **Testing Requirements** - Validation criteria and test plans

### Conversion Report

The JSON report contains:

- **Analysis Results** - Code structure, complexity metrics
- **Conversion Metrics** - Accuracy, coverage, performance
- **Issues and Warnings** - Problems encountered during conversion
- **Recommendations** - Next steps for the converted code

## 🎯 Example: COBOL to Java Conversion

### Input COBOL Code

```cobol
       IDENTIFICATION DIVISION.
       PROGRAM-ID. SAMPLE-PROGRAM.
       
       DATA DIVISION.
       WORKING-STORAGE SECTION.
           01  CUSTOMER-RECORD.
               05  CUSTOMER-ID        PIC 9(6).
               05  CUSTOMER-NAME      PIC X(30).
               05  CUSTOMER-BALANCE   PIC 9(8)V99.
       
       PROCEDURE DIVISION.
       MAIN-LOGIC.
           DISPLAY "Starting Customer Processing".
           MOVE 123456 TO CUSTOMER-ID.
           MOVE "John Doe" TO CUSTOMER-NAME.
           MOVE 1000.50 TO CUSTOMER-BALANCE.
           DISPLAY "Customer: " CUSTOMER-NAME.
           STOP RUN.
```

### Output Java Code

```java
import java.util.*;
import java.io.*;

public class ConvertedCobolProgram {
    public static void main(String[] args) {
        // Converted from COBOL
        try {
            System.out.println("Starting Customer Processing");
            int customerId = 123456;
            String customerName = "John Doe";
            double customerBalance = 1000.50;
            System.out.println("Customer: " + customerName);
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
        }
    }
}
```

## 🔍 Code Analysis Features

### Language Detection
- **File Extension Analysis** - Primary detection method
- **Content Pattern Matching** - Fallback for unknown extensions
- **Keyword Frequency Analysis** - Language-specific signature detection

### Structural Analysis
- **Function/Procedure Extraction** - Identifies main logic blocks
- **Class and Object Detection** - Maps object-oriented structures
- **Dependency Analysis** - Tracks imports and external references
- **Control Flow Analysis** - Maps loops, conditionals, and branches

### Complexity Metrics
- **Cyclomatic Complexity** - Measures code complexity
- **Lines of Code** - File and function-level metrics
- **Comment Ratio** - Documentation coverage
- **Code Coverage** - Conversion completeness

## 📝 Documentation Generation

### Technical Requirements Document

The DocumentationAgent generates comprehensive technical documents that include:

1. **Conversion Rules** - Language-specific syntax mappings
2. **Architecture Patterns** - Target language best practices
3. **Data Structure Mappings** - Type conversions and equivalents
4. **API Mappings** - Library and framework equivalents
5. **Testing Requirements** - Validation criteria and test plans

### Example Document Structure

```markdown
# Technical Requirements: COBOL to Java Conversion

## Project Information
- **Project:** Legacy System Modernization
- **Source Language:** COBOL
- **Target Language:** Java

## Functional Requirements
- Convert 5 COBOL programs to Java
- Preserve business logic and data flow
- Maintain customer record processing functionality

## Conversion Rules
- COBOL PERFORM → Java for/while loops
- COBOL IF-ELSE → Java if-else statements
- COBOL DISPLAY → System.out.println
- COBOL ACCEPT → Scanner input

## Implementation Details
- Use Spring Boot framework
- Follow Java naming conventions
- Implement proper exception handling
```

## 🔧 Code Conversion Features

### Language-Specific Conversions

#### COBOL to Java
- **PERFORM loops** → **for/while loops**
- **IF-ELSE statements** → **if-else blocks**
- **DISPLAY statements** → **System.out.println**
- **ACCEPT statements** → **Scanner input**
- **Data structures** → **Java classes and objects**

#### COBOL to Python
- **PERFORM loops** → **for/while loops**
- **IF-ELSE statements** → **if-else blocks**
- **DISPLAY statements** → **print()**
- **ACCEPT statements** → **input()**
- **Data structures** → **Python classes and dictionaries**

### Code Quality Features
- **Automatic Formatting** - Language-specific style guides
- **Error Handling** - Proper exception management
- **Documentation** - Generated comments and docstrings
- **Type Safety** - Appropriate type annotations

## 🧪 Testing and Validation

### Quality Metrics
- **Conversion Accuracy** - Percentage of successfully converted code
- **Code Coverage** - Lines of code converted vs. total
- **Functional Preservation** - Business logic verification
- **Performance Impact** - Runtime efficiency analysis

### Validation Process
1. **Syntax Validation** - Ensure converted code compiles
2. **Functional Testing** - Verify business logic preservation
3. **Integration Testing** - Test with external dependencies
4. **Performance Testing** - Measure runtime characteristics

## 🚀 Advanced Features

### Custom Mappings
```python
request = ConversionRequest(
    source_language=ProgrammingLanguage.COBOL,
    target_language=ProgrammingLanguage.JAVA,
    custom_mappings={
        "CUSTOMER-TABLE": "CustomerRepository",
        "FILE-IO": "FileService"
    }
)
```

### Optimization Levels
- **Minimal** - Basic conversion with minimal changes
- **Balanced** - Standard conversion with optimizations
- **Aggressive** - Advanced optimizations and modern patterns

### Output Formats
- **Standard** - Traditional language patterns
- **Modern** - Contemporary best practices
- **Legacy** - Backward compatibility focus

## 🔧 Extending the System

### Adding New Languages

1. **Update Language Enum:**
   ```python
   class ProgrammingLanguage(str, Enum):
       NEW_LANGUAGE = "new_language"
   ```

2. **Add File Extensions:**
   ```python
   self.supported_extensions = {
       '.new': ProgrammingLanguage.NEW_LANGUAGE,
   }
   ```

3. **Implement Analysis:**
   ```python
   def _analyze_new_language_file(self, code_file: CodeFile, analysis: CodeAnalysis):
       # Language-specific analysis logic
   ```

4. **Add Conversion Rules:**
   ```python
   def _convert_new_language_to_target(self, content: str, technical_doc: TechnicalDocument) -> str:
       # Conversion logic
   ```

### Custom Conversion Rules

```python
# Add to technical document
document.language_mappings.update({
    "CUSTOM-PATTERN": "TARGET-PATTERN",
    "SPECIAL-SYNTAX": "EQUIVALENT-SYNTAX"
})
```

## 🐛 Troubleshooting

### Common Issues

1. **Language Detection Fails**
   - Check file extensions
   - Verify content patterns
   - Use explicit language specification

2. **Conversion Errors**
   - Review conversion rules
   - Check for unsupported syntax
   - Validate input code structure

3. **Performance Issues**
   - Reduce file size
   - Use optimization settings
   - Check memory usage

### Debug Mode

Enable verbose logging for detailed analysis:

```bash
python main.py --input code.zip --source cobol --target java --verbose
```

## 📚 API Reference

### ConversionOrchestrator

```python
orchestrator = ConversionOrchestrator()
result = await orchestrator.convert_code(request)
```

### ConversionRequest

```python
request = ConversionRequest(
    source_language=ProgrammingLanguage.COBOL,
    target_language=ProgrammingLanguage.JAVA,
    project_name="My Project",
    input_zip_path=Path("code.zip"),
    preserve_structure=True,
    include_tests=True,
    optimization_level="balanced"
)
```

### ConversionResult

```python
result = await orchestrator.convert_code(request)
print(f"Accuracy: {result.conversion_accuracy}")
print(f"Files: {len(result.converted_files)}")
print(f"Duration: {result.total_duration}")
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
3. **Add language support or improvements**
4. **Write tests for new functionality**
5. **Submit a pull request**

## 📄 License

This example is part of the NeuroStack project and follows the same license terms.

## 🆘 Support

- **Documentation** - Check the main NeuroStack documentation
- **Issues** - Report bugs and feature requests
- **Examples** - See other NeuroStack examples for patterns

---

**NeuroStack Code Conversion Agent** - Transforming legacy code into modern applications 🚀 