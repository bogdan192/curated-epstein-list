"""Data enrichment through Wikipedia, Google, and AI services."""

import time
import requests
from typing import Dict, Optional, List
from urllib.parse import quote
import json
from bs4 import BeautifulSoup
from openai import OpenAI
from colorama import Fore, Style
from config import Config

class PersonInfo:
    """Container for person information."""
    
    def __init__(self, name: str):
        self.name = name
        self.wikipedia_summary = ""
        self.wikipedia_url = ""
        self.google_results = []
        self.ai_analysis = ""
        self.known_details = {}
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for export."""
        return {
            'Name': self.name,
            'Wikipedia Summary': self.wikipedia_summary,
            'Wikipedia URL': self.wikipedia_url,
            'Google Results': '; '.join(self.google_results[:3]),  # Top 3 results
            'AI Analysis': self.ai_analysis,
            'Known Details': json.dumps(self.known_details) if self.known_details else ""
        }

class DataEnricher:
    """Enriches name data with information from various sources."""
    
    def __init__(self):
        """Initialize the data enricher."""
        self.openai_client = None
        if Config.OPENAI_API_KEY:
            try:
                self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
            except Exception as e:
                print(f"{Fore.YELLOW}Warning: Failed to initialize OpenAI client: {e}{Style.RESET_ALL}")
    
    def search_wikipedia(self, name: str) -> Dict[str, str]:
        """Search Wikipedia for information about a person."""
        try:
            # Wikipedia API search
            search_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(name)}"
            
            response = requests.get(search_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'summary': data.get('extract', ''),
                    'url': data.get('content_urls', {}).get('desktop', {}).get('page', '')
                }
            else:
                # Try search if direct lookup fails
                search_query_url = f"https://en.wikipedia.org/w/api.php"
                params = {
                    'action': 'query',
                    'format': 'json',
                    'list': 'search',
                    'srsearch': name,
                    'srlimit': 1
                }
                
                search_response = requests.get(search_query_url, params=params, timeout=10)
                if search_response.status_code == 200:
                    search_data = search_response.json()
                    if search_data.get('query', {}).get('search'):
                        page_title = search_data['query']['search'][0]['title']
                        return self.search_wikipedia(page_title)
        
        except Exception as e:
            print(f"{Fore.YELLOW}Wikipedia search failed for {name}: {e}{Style.RESET_ALL}")
        
        return {'summary': '', 'url': ''}
    
    def search_google(self, name: str) -> List[str]:
        """Search Google for information about a person."""
        results = []
        
        if not Config.GOOGLE_API_KEY or not Config.GOOGLE_CSE_ID:
            print(f"{Fore.YELLOW}Google API credentials not configured{Style.RESET_ALL}")
            return results
        
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': Config.GOOGLE_API_KEY,
                'cx': Config.GOOGLE_CSE_ID,
                'q': f'"{name}" person biography',
                'num': 5
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                for item in data.get('items', []):
                    title = item.get('title', '')
                    snippet = item.get('snippet', '')
                    link = item.get('link', '')
                    results.append(f"{title}: {snippet} ({link})")
            
        except Exception as e:
            print(f"{Fore.YELLOW}Google search failed for {name}: {e}{Style.RESET_ALL}")
        
        return results
    
    def get_ai_analysis(self, name: str, context_info: str = "") -> str:
        """Get AI analysis of a person using OpenAI."""
        if not self.openai_client:
            return "OpenAI API not configured"
        
        try:
            prompt = f"""
            Analyze the following person and provide known public information about them:
            
            Name: {name}
            Context Information: {context_info}
            
            Please provide:
            1. Basic biographical information (if publicly known)
            2. Professional background or notable achievements
            3. Any significant public connections or associations
            4. Notable events or controversies (if any)
            
            Focus only on factual, publicly available information. Be concise and objective.
            If no reliable information is available, state that clearly.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that provides factual, publicly available information about people. Be objective and cite sources when possible."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"{Fore.YELLOW}AI analysis failed for {name}: {e}{Style.RESET_ALL}")
            return f"AI analysis unavailable: {str(e)}"
    
    def enrich_person_data(self, name: str) -> PersonInfo:
        """Enrich data for a single person."""
        print(f"Enriching data for: {name}")
        person = PersonInfo(name)
        
        # Search Wikipedia
        wiki_info = self.search_wikipedia(name)
        person.wikipedia_summary = wiki_info['summary']
        person.wikipedia_url = wiki_info['url']
        
        # Wait to avoid rate limiting
        time.sleep(Config.REQUEST_DELAY)
        
        # Search Google
        person.google_results = self.search_google(name)
        
        # Wait to avoid rate limiting
        time.sleep(Config.REQUEST_DELAY)
        
        # Get AI analysis
        context = f"Wikipedia: {person.wikipedia_summary[:200]}... Google results: {person.google_results[0] if person.google_results else 'None'}"
        person.ai_analysis = self.get_ai_analysis(name, context)
        
        # Extract structured details from AI analysis
        person.known_details = self._extract_structured_details(person.ai_analysis)
        
        return person
    
    def _extract_structured_details(self, ai_analysis: str) -> Dict[str, str]:
        """Extract structured details from AI analysis."""
        details = {}
        
        # Simple parsing - look for common patterns
        lines = ai_analysis.split('\n')
        current_section = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for section headers
            if line.endswith(':') and len(line.split()) <= 3:
                current_section = line[:-1]
            elif current_section and not line.startswith(('1.', '2.', '3.', '4.', '-', '*')):
                if current_section not in details:
                    details[current_section] = line
                else:
                    details[current_section] += " " + line
        
        return details
    
    def enrich_all_names(self, names: List[str]) -> List[PersonInfo]:
        """Enrich data for all names with progress tracking."""
        enriched_data = []
        
        from tqdm import tqdm
        for name in tqdm(names, desc="Enriching person data"):
            try:
                person_info = self.enrich_person_data(name)
                enriched_data.append(person_info)
            except Exception as e:
                print(f"{Fore.RED}Error enriching data for {name}: {e}{Style.RESET_ALL}")
                # Add basic info even if enrichment fails
                person = PersonInfo(name)
                person.ai_analysis = f"Error occurred during data enrichment: {str(e)}"
                enriched_data.append(person)
        
        return enriched_data