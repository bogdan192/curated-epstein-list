# Epstein List Extractor

A Python tool for extracting names from PDF documents and enriching them with publicly available information from Wikipedia, Google, and AI services.

## Features

- **PDF Processing**: Extract names from single PDFs, directories of PDFs, or ZIP archives
- **Name Recognition**: Uses spaCy NLP and regex patterns to identify person names
- **Data Enrichment**: Automatically searches Wikipedia, Google, and queries AI for additional information
- **Excel Export**: Outputs results to formatted Excel files with summary statistics
- **CLI Interface**: Easy-to-use command-line interface

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd curated-epstein-list
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Download spaCy English model (optional, but recommended):
```bash
python -m spacy download en_core_web_sm
```

4. Set up configuration:
```bash
python main.py setup
```

5. Edit the `.env` file to add your API keys:
```bash
# Optional: Add API keys for enhanced functionality
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CSE_ID=your_google_custom_search_engine_id_here
```

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run setup**:
   ```bash
   python main.py setup
   ```

3. **Extract names from a PDF**:
   ```bash
   python main.py extract your_document.pdf
   ```

4. **Extract names without enrichment (faster)**:
   ```bash
   python main.py extract your_document.pdf --no-enrichment
   ```

5. **Test with sample names**:
   ```bash
   python main.py enrich "John Doe" "Jane Smith"
   ```

## Usage

### Basic PDF Processing
Extract names from a PDF file:
```bash
python main.py extract document.pdf
```

Extract names from a directory of PDFs:
```bash
python main.py extract /path/to/pdf/directory
```

Extract names from a ZIP archive:
```bash
python main.py extract archive.zip
```

### Advanced Options

Skip data enrichment (faster, names only):
```bash
python main.py extract document.pdf --no-enrichment
```

Specify custom output file:
```bash
python main.py extract document.pdf --output custom_results.xlsx
```

Export to CSV format:
```bash
python main.py extract document.pdf --format csv
```

Limit processing for testing:
```bash
python main.py extract document.pdf --max-names 10
```

### Enrich Specific Names
You can also enrich specific names without PDF processing:
```bash
python main.py enrich "John Doe" "Jane Smith" "Robert Johnson"
```

### Test the Setup
Run a quick test with sample data:
```bash
python main.py test
```

## Output

The tool generates Excel files with the following information:
- **Names**: Extracted person names
- **Wikipedia Summary**: Brief biographical information from Wikipedia
- **Wikipedia URL**: Link to Wikipedia page (if found)
- **Google Results**: Top search results from Google
- **AI Analysis**: AI-generated analysis of publicly available information
- **Known Details**: Structured details extracted from various sources

## Configuration

The application uses environment variables for configuration:

- `OPENAI_API_KEY`: OpenAI API key for AI analysis
- `GOOGLE_API_KEY`: Google Custom Search API key
- `GOOGLE_CSE_ID`: Google Custom Search Engine ID
- `OUTPUT_DIRECTORY`: Directory for output files (default: "output")
- `MAX_CONCURRENT_REQUESTS`: Rate limiting for API calls
- `REQUEST_DELAY`: Delay between API requests

## Privacy and Ethics

This tool is designed to work only with publicly available information. It:
- Only searches public sources (Wikipedia, Google, AI knowledge bases)
- Does not access private or confidential data
- Respects rate limits and terms of service for all APIs
- Focuses on factual, publicly available information

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`
- Optional: OpenAI API key for AI analysis
- Optional: Google Custom Search API for enhanced search results

## License

MIT License - see LICENSE file for details.
