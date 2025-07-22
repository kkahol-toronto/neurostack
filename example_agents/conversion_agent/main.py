#!/usr/bin/env python3
"""
Code Conversion Agent Example

This script demonstrates how to use the NeuroStack-based code conversion system
to convert code between different programming languages.

Example usage:
    python main.py --input sample_cobol.zip --source cobol --target java --project "Sample Project"
"""

import asyncio
import argparse
import json
import sys
from pathlib import Path
from typing import Optional
import structlog

# Import the conversion agent components
from conversion_agent import (
    ConversionOrchestrator, ConversionRequest, ProgrammingLanguage,
    CodeFile, CodeExtractor
)

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


def create_sample_cobol_files() -> Path:
    """Create sample COBOL files for demonstration."""
    sample_dir = Path("sample_cobol_project")
    sample_dir.mkdir(exist_ok=True)
    
    # Sample COBOL program
    cobol_program = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. SAMPLE-PROGRAM.
       AUTHOR. NeuroStack Conversion Agent.
       
       ENVIRONMENT DIVISION.
       CONFIGURATION SECTION.
       
       DATA DIVISION.
       WORKING-STORAGE SECTION.
           01  CUSTOMER-RECORD.
               05  CUSTOMER-ID        PIC 9(6).
               05  CUSTOMER-NAME      PIC X(30).
               05  CUSTOMER-BALANCE   PIC 9(8)V99.
           01  WS-COUNTER             PIC 9(3) VALUE 0.
           01  WS-TOTAL-BALANCE       PIC 9(10)V99 VALUE 0.
       
       PROCEDURE DIVISION.
       MAIN-LOGIC.
           DISPLAY "Starting Customer Processing Program".
           PERFORM PROCESS-CUSTOMERS UNTIL WS-COUNTER >= 10.
           DISPLAY "Total Balance: " WS-TOTAL-BALANCE.
           STOP RUN.
       
       PROCESS-CUSTOMERS.
           ADD 1 TO WS-COUNTER.
           MOVE WS-COUNTER TO CUSTOMER-ID.
           MOVE "Customer " TO CUSTOMER-NAME.
           MOVE 1000.50 TO CUSTOMER-BALANCE.
           ADD CUSTOMER-BALANCE TO WS-TOTAL-BALANCE.
           DISPLAY "Processed Customer: " CUSTOMER-ID.
       
       END PROGRAM SAMPLE-PROGRAM.
"""
    
    # Write sample files
    (sample_dir / "sample_program.cob").write_text(cobol_program)
    
    # Sample data file
    data_file = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. DATA-PROCESSOR.
       
       ENVIRONMENT DIVISION.
       
       DATA DIVISION.
       WORKING-STORAGE SECTION.
           01  INPUT-RECORD.
               05  RECORD-TYPE        PIC X(10).
               05  RECORD-DATA        PIC X(50).
           01  OUTPUT-RECORD.
               05  PROCESSED-DATA     PIC X(60).
       
       PROCEDURE DIVISION.
       PROCESS-DATA.
           DISPLAY "Processing data records".
           PERFORM READ-AND-PROCESS UNTIL RECORD-TYPE = "END".
           DISPLAY "Data processing completed".
           STOP RUN.
       
       READ-AND-PROCESS.
           ACCEPT INPUT-RECORD.
           IF RECORD-TYPE NOT = "END"
               MOVE RECORD-DATA TO PROCESSED-DATA
               DISPLAY "Processed: " PROCESSED-DATA.
       
       END PROGRAM DATA-PROCESSOR.
"""
    
    (sample_dir / "data_processor.cob").write_text(data_file)
    
    # Create a zip file
    import zipfile
    zip_path = Path("sample_cobol.zip")
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file_path in sample_dir.rglob('*'):
            if file_path.is_file():
                zipf.write(file_path, file_path.name)
    
    logger.info("Created sample COBOL files", 
               sample_dir=str(sample_dir),
               zip_file=str(zip_path))
    
    return zip_path


async def run_conversion_example(input_path: Path, 
                               source_lang: ProgrammingLanguage,
                               target_lang: ProgrammingLanguage,
                               project_name: str) -> None:
    """
    Run the code conversion example.
    
    Args:
        input_path: Path to input zip file or directory
        source_lang: Source programming language
        target_lang: Target programming language
        project_name: Name of the project
    """
    logger.info("Starting code conversion example",
               input_path=str(input_path),
               source_language=source_lang.value,
               target_language=target_lang.value,
               project_name=project_name)
    
    try:
        # Create conversion request
        request = ConversionRequest(
            source_language=source_lang,
            target_language=target_lang,
            project_name=project_name,
            description=f"Converting {source_lang.value} code to {target_lang.value}",
            input_zip_path=input_path if input_path.suffix.lower() == '.zip' else None,
            preserve_structure=True,
            include_tests=True,
            include_documentation=True,
            optimization_level="balanced",
            output_format="standard",
            naming_convention="camelCase",
            code_style="standard"
        )
        
        # Initialize orchestrator
        orchestrator = ConversionOrchestrator()
        
        # Execute conversion
        logger.info("Executing code conversion workflow")
        result = await orchestrator.convert_code(request)
        
        # Display results
        print("\n" + "="*60)
        print("CODE CONVERSION RESULTS")
        print("="*60)
        
        print(f"\n📊 Conversion Summary:")
        print(f"   Source Language: {result.code_analysis.source_language.value}")
        print(f"   Target Language: {result.code_analysis.target_language.value}")
        print(f"   Files Analyzed: {result.code_analysis.total_files}")
        print(f"   Files Converted: {len(result.converted_files)}")
        print(f"   Total Lines: {result.code_analysis.total_lines}")
        print(f"   Conversion Accuracy: {result.conversion_accuracy:.2%}")
        print(f"   Code Coverage: {result.code_coverage:.2%}")
        print(f"   Total Duration: {result.total_duration:.2f} seconds")
        
        print(f"\n📁 Output Directory: {result.output_directory}")
        
        if result.technical_document:
            print(f"\n📋 Technical Document Generated:")
            print(f"   Title: {result.technical_document.title}")
            print(f"   Functional Requirements: {len(result.technical_document.functional_requirements)}")
            print(f"   Non-Functional Requirements: {len(result.technical_document.non_functional_requirements)}")
            print(f"   Language Mappings: {len(result.technical_document.language_mappings)}")
        
        print(f"\n🔧 Converted Files:")
        for i, code_file in enumerate(result.converted_files, 1):
            print(f"   {i}. {code_file.path} ({code_file.language.value})")
            print(f"      Lines: {code_file.line_count}, Size: {code_file.size_bytes} bytes")
        
        if result.conversion_issues:
            print(f"\n⚠️  Conversion Issues:")
            for issue in result.conversion_issues:
                print(f"   - {issue.get('message', 'Unknown issue')}")
        
        if result.recommendations:
            print(f"\n💡 Recommendations:")
            for rec in result.recommendations:
                print(f"   - {rec}")
        
        print(f"\n✅ Conversion completed successfully!")
        
        # Show sample of converted code
        if result.converted_files:
            print(f"\n📝 Sample Converted Code:")
            sample_file = result.converted_files[0]
            print(f"File: {sample_file.path}")
            print("-" * 40)
            lines = sample_file.content.split('\n')[:20]  # Show first 20 lines
            for line in lines:
                print(f"  {line}")
            if len(sample_file.content.split('\n')) > 20:
                print(f"  ... ({len(sample_file.content.split('\n')) - 20} more lines)")
        
    except Exception as e:
        logger.error("Code conversion example failed", error=str(e))
        print(f"\n❌ Conversion failed: {e}")
        raise


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Code Conversion Agent Example",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert sample COBOL to Java
  python main.py --input sample_cobol.zip --source cobol --target java --project "Sample Project"
  
  # Convert with custom settings
  python main.py --input my_code.zip --source python --target javascript --project "My Project" --style modern
        """
    )
    
    parser.add_argument(
        "--input", "-i",
        type=Path,
        help="Input zip file or directory containing source code"
    )
    
    parser.add_argument(
        "--source", "-s",
        type=str,
        choices=[lang.value for lang in ProgrammingLanguage],
        default="cobol",
        help="Source programming language"
    )
    
    parser.add_argument(
        "--target", "-t", 
        type=str,
        choices=[lang.value for lang in ProgrammingLanguage],
        default="java",
        help="Target programming language"
    )
    
    parser.add_argument(
        "--project", "-p",
        type=str,
        default="Code Conversion Project",
        help="Project name"
    )
    
    parser.add_argument(
        "--style",
        type=str,
        choices=["standard", "modern", "legacy"],
        default="standard",
        help="Output code style"
    )
    
    parser.add_argument(
        "--create-sample",
        action="store_true",
        help="Create sample COBOL files for demonstration"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    return parser.parse_args()


async def main():
    """Main function."""
    args = parse_arguments()
    
    # Set up logging level
    if args.verbose:
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.ConsoleRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
    
    print("🚀 NeuroStack Code Conversion Agent Example")
    print("=" * 50)
    
    try:
        # Handle input
        input_path = args.input
        if args.create_sample or input_path is None:
            print("📁 Creating sample COBOL files...")
            input_path = create_sample_cobol_files()
            print(f"✅ Created sample files: {input_path}")
        
        # Validate input
        if not input_path.exists():
            print(f"❌ Input path does not exist: {input_path}")
            sys.exit(1)
        
        # Convert string arguments to enums
        source_lang = ProgrammingLanguage(args.source)
        target_lang = ProgrammingLanguage(args.target)
        
        # Run conversion
        await run_conversion_example(
            input_path=input_path,
            source_lang=source_lang,
            target_lang=target_lang,
            project_name=args.project
        )
        
    except KeyboardInterrupt:
        print("\n⚠️  Conversion interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 