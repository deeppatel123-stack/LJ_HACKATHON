import re
import docx
import spacy
from PyPDF2 import PdfReader
from collections import Counter
from heapq import nlargest

# Load spaCy model for entity recognition
nlp = spacy.load("en_core_web_sm")

def extract_text(file_path: str) -> str:
    """Extracts text from various document types."""
    if file_path.endswith('.pdf'):
        reader = PdfReader(file_path)
        text = ''
        for page in reader.pages:
            text += page.extract_text() or ''
        return text
    elif file_path.endswith('.docx'):
        doc = docx.Document(file_path)
        return '\n'.join([para.text for para in doc.paragraphs])
    elif file_path.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def extract_metadata(text: str):
    """Extracts title, author, date, and entities using regex and spaCy."""
    metadata = {
        'title': 'Untitled',
        'author': 'Unknown',
        'date_extracted': 'Unknown',
        'entities': []
    }
    
    # 1. Title: First bold sentence or line
    # (Regex is a simple approximation, better with custom logic or font parsing)
    title_match = re.search(r'^\s*([A-Z][\w\s,]+)\s*\n', text)
    if title_match:
        metadata['title'] = title_match.group(1).strip()
    
    # 2. Author: Regex for "Author:", "By:", or email
    author_match = re.search(r'(?:Author|By):\s*([^\n]+)|[\w\.-]+@[\w\.-]+\.\w+', text, re.IGNORECASE)
    if author_match:
        metadata['author'] = author_match.group(1) if author_match.group(1) else author_match.group(0)
    
    # 3. Date: Regex-based detection
    date_match = re.search(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},\s+\d{4}', text)
    if date_match:
        metadata['date_extracted'] = date_match.group(0)

    # 4. Entities: Use spaCy
    doc = nlp(text)
    entities = {}
    for ent in doc.ents:
        if ent.label_ not in entities:
            entities[ent.label_] = []
        entities[ent.label_].append(ent.text)
    metadata['entities'] = entities
    
    return metadata

def summarize_text(text: str, num_sentences: int = 3) -> str:
    """
    Extractive summarization using a simple TF-IDF / word frequency approach.
    """
    sentences = [sentence.strip() for sentence in re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', text) if sentence.strip()]
    
    # Simple tokenization and frequency counting
    word_freq = Counter(word.lower() for word in re.findall(r'\b\w+\b', text))
    
    # Calculate sentence scores based on word frequency
    sentence_scores = {}
    for i, sentence in enumerate(sentences):
        for word in re.findall(r'\b\w+\b', sentence.lower()):
            if word in word_freq:
                if i not in sentence_scores:
                    sentence_scores[i] = word_freq[word]
                else:
                    sentence_scores[i] += word_freq[word]
    
    # Get top N sentences based on score
    top_sentences_indices = nlargest(num_sentences, sentence_scores, key=sentence_scores.get)
    
    # Reconstruct the summary in original order
    top_sentences_indices.sort()
    
    return ' '.join([sentences[i] for i in top_sentences_indices])