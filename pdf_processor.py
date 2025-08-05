"""PDF processing and name extraction functionality."""

import re
import zipfile
from pathlib import Path
from typing import List, Set, Tuple
import PyPDF2
import pdfplumber
from tqdm import tqdm
import spacy
from colorama import Fore, Style

class PDFProcessor:
    """Handles PDF reading and name extraction."""
    
    def __init__(self):
        """Initialize the PDF processor."""
        self.names = set()
        self.nlp = None
        self._load_nlp_model()
    
    def _load_nlp_model(self):
        """Load the spaCy NLP model for name extraction."""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print(f"{Fore.YELLOW}Warning: spaCy English model not found.{Style.RESET_ALL}")
            print("Install it with: python -m spacy download en_core_web_sm")
            print("Falling back to regex-based name extraction.")
    
    def extract_names_from_text(self, text: str) -> Set[str]:
        """Extract names from text using NLP and regex patterns."""
        names = set()
        
        if self.nlp:
            # Use spaCy for named entity recognition
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    # Clean and validate the name
                    name = self._clean_name(ent.text)
                    if self._is_valid_name(name):
                        names.add(name)
        
        # Fallback regex patterns for common name formats
        regex_names = self._extract_names_regex(text)
        names.update(regex_names)
        
        return names
    
    def _extract_names_regex(self, text: str) -> Set[str]:
        """Extract names using regex patterns."""
        names = set()
        
        # Pattern for "First Last" format (2-3 words)
        name_pattern = r'\b[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b'
        matches = re.findall(name_pattern, text)
        
        for match in matches:
            name = self._clean_name(match)
            if self._is_valid_name(name) and len(name.split()) <= 3:
                names.add(name)
        
        # Pattern for "Last, First" format
        last_first_pattern = r'\b[A-Z][a-z]+,\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b'
        matches = re.findall(last_first_pattern, text)
        
        for match in matches:
            # Convert "Last, First" to "First Last"
            parts = match.split(',')
            if len(parts) == 2:
                name = f"{parts[1].strip()} {parts[0].strip()}"
                name = self._clean_name(name)
                if self._is_valid_name(name):
                    names.add(name)
        
        return names
    
    def _clean_name(self, name: str) -> str:
        """Clean and normalize a name."""
        # Remove extra whitespace and punctuation
        name = re.sub(r'[^\w\s]', '', name)
        name = ' '.join(name.split())
        return name.title()
    
    def _is_valid_name(self, name: str) -> bool:
        """Validate if a string is likely a person's name."""
        if not name or len(name) < 3:
            return False
        
        parts = name.split()
        if len(parts) < 2:
            return False
        
        # Skip common non-names
        skip_words = {
            'United States', 'New York', 'Los Angeles', 'Court', 'Department',
            'Company', 'Corporation', 'Inc', 'LLC', 'Ltd', 'University',
            'College', 'School', 'Hospital', 'Medical', 'Center'
        }
        
        if any(word in name for word in skip_words):
            return False
        
        return True
    
    def read_pdf(self, file_path: Path) -> str:
        """Read text from a PDF file."""
        text = ""
        
        try:
            # Try pdfplumber first (better for complex layouts)
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"{Fore.YELLOW}Warning: pdfplumber failed for {file_path}, trying PyPDF2: {e}{Style.RESET_ALL}")
            
            # Fallback to PyPDF2
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
            except Exception as e2:
                print(f"{Fore.RED}Error reading PDF {file_path}: {e2}{Style.RESET_ALL}")
        
        return text
    
    def process_pdf_file(self, file_path: Path) -> Set[str]:
        """Process a single PDF file and extract names."""
        print(f"Processing: {file_path.name}")
        text = self.read_pdf(file_path)
        names = self.extract_names_from_text(text)
        return names
    
    def process_archive(self, archive_path: Path) -> Set[str]:
        """Process a ZIP archive of PDF files."""
        all_names = set()
        
        with zipfile.ZipFile(archive_path, 'r') as zip_file:
            pdf_files = [f for f in zip_file.namelist() if f.lower().endswith('.pdf')]
            
            for pdf_file in tqdm(pdf_files, desc="Processing PDFs"):
                try:
                    # Extract to temporary location
                    zip_file.extract(pdf_file, '/tmp/pdf_extract')
                    temp_path = Path('/tmp/pdf_extract') / pdf_file
                    
                    names = self.process_pdf_file(temp_path)
                    all_names.update(names)
                    
                    # Clean up
                    temp_path.unlink()
                    
                except Exception as e:
                    print(f"{Fore.RED}Error processing {pdf_file}: {e}{Style.RESET_ALL}")
        
        return all_names
    
    def process_directory(self, directory_path: Path) -> Set[str]:
        """Process all PDF files in a directory."""
        all_names = set()
        pdf_files = list(directory_path.glob("*.pdf"))
        
        for pdf_file in tqdm(pdf_files, desc="Processing PDFs"):
            names = self.process_pdf_file(pdf_file)
            all_names.update(names)
        
        return all_names
    
    def process_input(self, input_path: Path) -> Set[str]:
        """Process input (file, directory, or archive)."""
        if not input_path.exists():
            raise FileNotFoundError(f"Input path does not exist: {input_path}")
        
        if input_path.is_file():
            if input_path.suffix.lower() == '.pdf':
                return self.process_pdf_file(input_path)
            elif input_path.suffix.lower() == '.zip':
                return self.process_archive(input_path)
            else:
                raise ValueError(f"Unsupported file type: {input_path.suffix}")
        elif input_path.is_dir():
            return self.process_directory(input_path)
        else:
            raise ValueError(f"Invalid input path: {input_path}")