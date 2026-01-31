"""
Advanced keyword extraction using NLP techniques.
"""
from typing import List, Dict
import re


class KeywordExtractor:
    """Advanced keyword extraction with NLP support."""
    
    def __init__(self, jd_text: str):
        """
        Initialize keyword extractor.
        
        Args:
            jd_text: Job description text
        """
        self.jd_text = jd_text
        self.jd_text_lower = jd_text.lower()
        
        # Try to load spaCy
        try:
            import spacy
            self.nlp = spacy.load('en_core_web_sm')
            self.doc = self.nlp(jd_text)
        except (OSError, ImportError):
            self.nlp = None
            self.doc = None
    
    def extract_named_entities(self) -> Dict[str, List[str]]:
        """
        Extract named entities using NLP.
        
        Returns:
            Dict with entity types and values
        """
        if not self.doc:
            return {'organizations': [], 'technologies': [], 'certifications': []}
        
        entities = {
            'organizations': [],
            'technologies': [],
            'certifications': []
        }
        
        for ent in self.doc.ents:
            if ent.label_ == 'ORG':
                entities['organizations'].append(ent.text)
            elif ent.label_ in ['PRODUCT', 'TECH']:
                entities['technologies'].append(ent.text)
        
        # Extract certifications (common patterns)
        cert_patterns = [
            r'\b([A-Z]{2,}(?:\s+[A-Z]{2,})*)\s+(?:Certification|Certified|Certificate)',
            r'\b(Certified\s+[A-Z][a-z]+)',
        ]
        
        for pattern in cert_patterns:
            matches = re.finditer(pattern, self.jd_text, re.IGNORECASE)
            entities['certifications'].extend([m.group(1) for m in matches])
        
        # Remove duplicates
        for key in entities:
            entities[key] = list(set(entities[key]))
        
        return entities
    
    def identify_key_phrases(self, top_n: int = 10) -> List[tuple]:
        """
        Identify most important phrases using TF-IDF-like approach.
        
        Args:
            top_n: Number of top phrases to return
            
        Returns:
            List of (phrase, score) tuples
        """
        # Simple approach: find noun phrases
        if not self.doc:
            return []
        
        phrases = []
        for chunk in self.doc.noun_chunks:
            if len(chunk.text.split()) >= 2 and len(chunk.text.split()) <= 5:
                phrases.append(chunk.text.lower())
        
        # Count frequency
        from collections import Counter
        phrase_counts = Counter(phrases)
        
        # Return top N
        return phrase_counts.most_common(top_n)
