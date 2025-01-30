import requests
from bs4 import BeautifulSoup
import re
import json
from typing import List, Dict
import time

class DataPreprocessor:
    def __init__(self):
        # Wikipedia URLs about space missions
        self.urls = [
            "https://en.wikipedia.org/wiki/Apollo_program",
            "https://en.wikipedia.org/wiki/Artemis_program",
            "https://en.wikipedia.org/wiki/Mars_Exploration_Program",
            "https://en.wikipedia.org/wiki/International_Space_Station",
            "https://en.wikipedia.org/wiki/Space_Shuttle_program"
        ]
        
    def fetch_content(self, url: str) -> str:
        """Fetch content from a URL with retry mechanism"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                time.sleep(1)
                return response.text
            except Exception as e:
                print(f"Attempt {attempt + 1} - Error fetching {url}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                continue
        return ""

    def clean_text(self, text: str, url: str) -> str:
        """Clean and normalize text with improved handling"""
        soup = BeautifulSoup(text, 'html.parser')

        # Remove unwanted elements
        for element in soup.find_all(['div', 'table', 'sup', 'span'],
                                   class_=['reference', 'reflist', 'navbox', 'mw-editsection']):
            element.decompose()

        # Get main content
        content_div = soup.find('div', {'id': 'mw-content-text'})
        if not content_div:
            return ""

        # Extract paragraphs and headers
        content = []
        for element in content_div.find_all(['p', 'h2', 'h3']):
            text = element.get_text().strip()

            # Clean the text
            text = re.sub(r'\[[\d\w\s]+\]', '', text)  # Remove reference tags
            text = re.sub(r'\s+', ' ', text)           # Normalize whitespace
            text = re.sub(r'[^\w\s.,!?;:()\-–]', '', text)  # Remove special chars but keep some punctuation

            if text and not text.isspace():
                if element.name in ['h2', 'h3']:
                    # Add section headers with their hierarchy
                    content.append(f"\n{text}\n")
                else:
                    content.append(text)

        # Extract title from URL and add it as context
        title = url.split('/')[-1].replace('_', ' ')

        # Combine all text with proper spacing
        full_text = f"Article: {title}\n\n" + '\n'.join(content)
        return full_text

    def chunk_text(self, text: str, min_chunk_size: int = 200, max_chunk_size: int = 300) -> List[str]:
        """Split text into meaningful chunks with better size control"""
        sections = text.split('\n\n')
        chunks = []
        current_chunk = []
        current_size = 0

        for section in sections:
            section = section.strip()
            if not section:
                continue

            # Split section into sentences
            sentences = re.split(r'(?<=[.!?])\s+', section)

            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue

                sentence_words = len(sentence.split())

                if current_size + sentence_words > max_chunk_size and current_chunk:
                    # Save current chunk if it's getting too large
                    chunks.append(' '.join(current_chunk))
                    current_chunk = []
                    current_size = 0

                current_chunk.append(sentence)
                current_size += sentence_words

                # Ensure chunks are at least min_chunk_size words
                if current_size >= min_chunk_size and current_chunk:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = []
                    current_size = 0

        # Add any remaining text as the last chunk
        if current_chunk:
            chunks.append(' '.join(current_chunk))

        # Filter out chunks that are too short
        return [chunk for chunk in chunks if len(chunk.split()) >= min_chunk_size]

    def process_all_sources(self) -> List[Dict[str, str]]:
        """Process all URLs and return chunked data"""
        all_chunks = []
        
        for url in self.urls:
            print(f"Processing {url}")
            content = self.fetch_content(url)
            if content:
                cleaned_text = self.clean_text(content, url)
                chunks = self.chunk_text(cleaned_text)
                
                for chunk in chunks:
                    all_chunks.append({
                        "text": chunk,
                        "source": url,
                        "title": url.split('/')[-1].replace('_', ' ')
                    })
                print(f"Successfully processed {len(chunks)} chunks from {url}")
            else:
                print(f"Skipping {url} due to fetch error")

        return all_chunks

    def save_chunks(self, chunks: List[Dict[str, str]], output_file: str = "processed_data.json"):
        """Save processed chunks to a JSON file"""
        if not chunks:
            print("Warning: No chunks to save!")
            return
            
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)
            print(f"Saved {len(chunks)} chunks to {output_file}")

if __name__ == "__main__":
    preprocessor = DataPreprocessor()
    chunks = preprocessor.process_all_sources()
    
    if chunks:
        preprocessor.save_chunks(chunks)
        print(f"\nSuccessfully processed {len(chunks)} total chunks of text")
    else:
        print("\nError: No chunks were processed. Please check the URLs and try again.")