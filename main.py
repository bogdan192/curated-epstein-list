#!/usr/bin/env python3
"""
Epstein List Extractor - A tool for extracting names from PDFs and enriching them with public information.
"""

import sys
from pathlib import Path
import click
from colorama import init, Fore, Style
from config import Config
from pdf_processor import PDFProcessor
from data_enricher import DataEnricher
from excel_exporter import ExcelExporter

# Initialize colorama
init()

@click.group()
@click.version_option(version="1.0.0", prog_name="Epstein List Extractor")
def cli():
    """Extract names from PDFs and enrich with public information."""
    Config.validate()

@cli.command()
@click.argument('input_path', type=click.Path(exists=True, path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path), 
              help='Output Excel file path')
@click.option('--no-enrichment', is_flag=True, 
              help='Skip data enrichment, only extract names')
@click.option('--format', 'output_format', type=click.Choice(['xlsx', 'csv']), 
              default='xlsx', help='Output format')
@click.option('--max-names', type=int, default=None, 
              help='Maximum number of names to process (for testing)')
def extract(input_path, output, no_enrichment, output_format, max_names):
    """Extract names from PDF files and optionally enrich with additional data.
    
    INPUT_PATH can be:
    - A single PDF file
    - A directory containing PDF files  
    - A ZIP archive containing PDF files
    """
    
    print(f"{Fore.CYAN}🔍 Starting Epstein List Extractor{Style.RESET_ALL}")
    print(f"Input: {input_path}")
    print(f"Enrichment: {'Disabled' if no_enrichment else 'Enabled'}")
    print()
    
    try:
        # Step 1: Extract names from PDFs
        print(f"{Fore.YELLOW}📖 Extracting names from PDFs...{Style.RESET_ALL}")
        processor = PDFProcessor()
        names = processor.process_input(input_path)
        
        if not names:
            print(f"{Fore.RED}❌ No names found in the provided input{Style.RESET_ALL}")
            return
        
        names_list = sorted(list(names))
        
        # Limit names if specified (for testing)
        if max_names and len(names_list) > max_names:
            print(f"{Fore.YELLOW}⚠️  Limiting to {max_names} names for processing{Style.RESET_ALL}")
            names_list = names_list[:max_names]
        
        print(f"{Fore.GREEN}✅ Found {len(names_list)} unique names{Style.RESET_ALL}")
        
        # Display sample names
        print(f"\n{Fore.CYAN}Sample names found:{Style.RESET_ALL}")
        for name in names_list[:10]:
            print(f"  • {name}")
        if len(names_list) > 10:
            print(f"  ... and {len(names_list) - 10} more")
        print()
        
        # Step 2: Export or enrich data
        exporter = ExcelExporter()
        
        if no_enrichment:
            # Simple export without enrichment
            print(f"{Fore.YELLOW}📝 Exporting names list...{Style.RESET_ALL}")
            
            if output_format == 'xlsx':
                output_file = exporter.export_simple_list(names_list, output)
            else:
                # For CSV, create simple DataFrame
                import pandas as pd
                df = pd.DataFrame({'Names': names_list})
                output_file = output or (Config.OUTPUT_DIRECTORY / "simple_names_list.csv")
                df.to_csv(output_file, index=False)
                print(f"{Fore.GREEN}CSV file exported to: {output_file}{Style.RESET_ALL}")
        else:
            # Full enrichment process
            print(f"{Fore.YELLOW}🔍 Enriching data with Wikipedia, Google, and AI...{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}⏱️  This may take several minutes...{Style.RESET_ALL}")
            
            enricher = DataEnricher()
            enriched_data = enricher.enrich_all_names(names_list)
            
            print(f"{Fore.YELLOW}📊 Exporting enriched data...{Style.RESET_ALL}")
            
            if output_format == 'xlsx':
                output_file = exporter.export_to_excel(enriched_data, output)
            else:
                output_file = exporter.export_csv(enriched_data, output)
        
        print(f"\n{Fore.GREEN}🎉 Processing complete!{Style.RESET_ALL}")
        print(f"Output saved to: {output_file}")
        
    except Exception as e:
        print(f"\n{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        if click.get_current_context().obj and click.get_current_context().obj.get('debug'):
            import traceback
            traceback.print_exc()
        sys.exit(1)

@cli.command()
@click.argument('names', nargs=-1, required=True)
@click.option('--output', '-o', type=click.Path(path_type=Path),
              help='Output Excel file path')
def enrich(names, output):
    """Enrich specific names with additional information.
    
    NAMES: One or more names to look up information for.
    
    Example: python main.py enrich "John Doe" "Jane Smith"
    """
    
    print(f"{Fore.CYAN}🔍 Enriching {len(names)} names...{Style.RESET_ALL}")
    
    try:
        enricher = DataEnricher()
        enriched_data = enricher.enrich_all_names(list(names))
        
        exporter = ExcelExporter()
        output_file = exporter.export_to_excel(enriched_data, output)
        
        print(f"\n{Fore.GREEN}🎉 Enrichment complete!{Style.RESET_ALL}")
        print(f"Output saved to: {output_file}")
        
    except Exception as e:
        print(f"\n{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        sys.exit(1)

@cli.command()
def setup():
    """Setup the application by creating configuration files and checking dependencies."""
    
    print(f"{Fore.CYAN}🔧 Setting up Epstein List Extractor...{Style.RESET_ALL}")
    
    # Create .env file if it doesn't exist
    env_file = Path('.env')
    if not env_file.exists():
        import shutil
        shutil.copy('.env.example', '.env')
        print(f"{Fore.GREEN}✅ Created .env file from template{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⚠️  Please edit .env file to add your API keys{Style.RESET_ALL}")
    else:
        print(f"{Fore.BLUE}ℹ️  .env file already exists{Style.RESET_ALL}")
    
    # Create output directory
    Config.OUTPUT_DIRECTORY.mkdir(exist_ok=True)
    print(f"{Fore.GREEN}✅ Created output directory: {Config.OUTPUT_DIRECTORY}{Style.RESET_ALL}")
    
    # Check Python dependencies
    print(f"\n{Fore.CYAN}🔍 Checking dependencies...{Style.RESET_ALL}")
    
    required_packages = [
        'PyPDF2', 'pdfplumber', 'openpyxl', 'pandas', 'requests', 
        'beautifulsoup4', 'openai', 'click', 'colorama', 'tqdm'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.lower().replace('-', '_'))
            print(f"{Fore.GREEN}✅ {package}{Style.RESET_ALL}")
        except ImportError:
            print(f"{Fore.RED}❌ {package}{Style.RESET_ALL}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n{Fore.YELLOW}⚠️  Missing packages detected{Style.RESET_ALL}")
        print(f"Install them with: pip install {' '.join(missing_packages)}")
    
    # Check spaCy model
    try:
        import spacy
        spacy.load("en_core_web_sm")
        print(f"{Fore.GREEN}✅ spaCy English model{Style.RESET_ALL}")
    except (ImportError, OSError):
        print(f"{Fore.YELLOW}⚠️  spaCy English model not found{Style.RESET_ALL}")
        print("Install it with: python -m spacy download en_core_web_sm")
    
    print(f"\n{Fore.GREEN}🎉 Setup complete!{Style.RESET_ALL}")
    print(f"\nNext steps:")
    print(f"1. Edit .env file to add your API keys")
    print(f"2. Run: python main.py extract <pdf_file_or_directory>")

@cli.command()
def test():
    """Run a quick test with sample data."""
    
    print(f"{Fore.CYAN}🧪 Running test with sample names...{Style.RESET_ALL}")
    
    sample_names = ["John Smith", "Jane Doe", "Robert Johnson"]
    
    try:
        enricher = DataEnricher()
        enriched_data = enricher.enrich_all_names(sample_names)
        
        exporter = ExcelExporter()
        output_file = Config.OUTPUT_DIRECTORY / "test_output.xlsx"
        exporter.export_to_excel(enriched_data, output_file)
        
        print(f"\n{Fore.GREEN}🎉 Test complete!{Style.RESET_ALL}")
        print(f"Test output saved to: {output_file}")
        
    except Exception as e:
        print(f"\n{Fore.RED}❌ Test failed: {e}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == '__main__':
    cli()