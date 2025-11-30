"""Thematic analysis using keyword extraction and clustering"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
import spacy

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# Try to load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except OSError:
    logger.warning("spaCy model 'en_core_web_sm' not found. Install with: python -m spacy download en_core_web_sm")
    SPACY_AVAILABLE = False
    nlp = None


class ThematicAnalyzer:
    """Thematic analysis using keyword extraction and clustering"""
    
    def __init__(self, min_keyword_freq: int = 2, max_features: int = 100):
        """
        Initialize thematic analyzer.
        
        Args:
            min_keyword_freq: Minimum frequency for keywords
            max_features: Maximum number of features for TF-IDF
        """
        self.min_keyword_freq = min_keyword_freq
        self.max_features = max_features
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=(1, 3),  # Unigrams, bigrams, trigrams
            min_df=min_keyword_freq,
            stop_words='english'
        )
    
    def extract_keywords_tfidf(self, texts: List[str]) -> List[Tuple[str, float]]:
        """
        Extract keywords using TF-IDF.
        
        Args:
            texts: List of preprocessed texts
            
        Returns:
            List of (keyword, score) tuples sorted by score
        """
        try:
            # Fit and transform
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            
            # Get feature names
            feature_names = self.vectorizer.get_feature_names_out()
            
            # Calculate mean TF-IDF scores
            mean_scores = np.mean(tfidf_matrix.toarray(), axis=0)
            
            # Create keyword-score pairs
            keywords = list(zip(feature_names, mean_scores))
            keywords.sort(key=lambda x: x[1], reverse=True)
            
            return keywords
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return []
    
    def extract_keywords_spacy(self, texts: List[str]) -> List[Tuple[str, float]]:
        """
        Extract keywords using spaCy (nouns, verbs, adjectives).
        
        Args:
            texts: List of texts
            
        Returns:
            List of (keyword, frequency) tuples
        """
        if not SPACY_AVAILABLE:
            return []
        
        keywords = []
        
        for text in texts:
            if not text:
                continue
            
            try:
                doc = nlp(text)
                # Extract meaningful words (nouns, verbs, adjectives)
                for token in doc:
                    if (token.pos_ in ['NOUN', 'VERB', 'ADJ'] and 
                        not token.is_stop and 
                        not token.is_punct and
                        len(token.text) > 2):
                        keywords.append(token.lemma_.lower())
            except Exception as e:
                logger.warning(f"Error processing text with spaCy: {e}")
                continue
        
        # Count frequencies
        keyword_counts = Counter(keywords)
        
        # Filter by minimum frequency
        filtered = [(word, count) for word, count in keyword_counts.items() 
                   if count >= self.min_keyword_freq]
        filtered.sort(key=lambda x: x[1], reverse=True)
        
        return filtered
    
    def cluster_keywords_into_themes(self, keywords: List[Tuple[str, float]], 
                                     bank_name: str) -> Dict[str, List[str]]:
        """
        Cluster keywords into themes using rule-based approach.
        
        Args:
            keywords: List of (keyword, score) tuples
            bank_name: Bank name for context
            
        Returns:
            Dictionary mapping theme names to lists of keywords
        """
        # Define theme patterns
        theme_patterns = {
            'Account Access Issues': [
                'login', 'password', 'access', 'account', 'authentication', 
                'verify', 'security', 'lock', 'unlock', 'pin', 'biometric'
            ],
            'Transaction Performance': [
                'transfer', 'transaction', 'payment', 'send', 'receive', 
                'slow', 'fast', 'delay', 'timeout', 'failed', 'success',
                'money', 'balance', 'deposit', 'withdraw'
            ],
            'User Interface & Experience': [
                'ui', 'interface', 'design', 'layout', 'button', 'screen',
                'navigation', 'menu', 'easy', 'simple', 'confusing', 'clear',
                'appearance', 'look', 'feel', 'user experience'
            ],
            'Customer Support': [
                'support', 'help', 'service', 'customer', 'contact', 'response',
                'assistance', 'complaint', 'issue', 'problem', 'resolve'
            ],
            'Feature Requests': [
                'feature', 'function', 'option', 'need', 'want', 'missing',
                'add', 'improve', 'enhance', 'suggestion', 'recommend'
            ],
            'App Reliability': [
                'crash', 'error', 'bug', 'freeze', 'hang', 'close', 'close',
                'restart', 'stable', 'unstable', 'reliable', 'broken'
            ],
            'Network & Connectivity': [
                'network', 'connection', 'internet', 'wifi', 'data', 'online',
                'offline', 'connect', 'disconnect', 'loading', 'timeout'
            ]
        }
        
        # Initialize theme clusters
        themes = {theme: [] for theme in theme_patterns.keys()}
        unassigned = []
        
        # Assign keywords to themes
        for keyword, score in keywords:
            keyword_lower = keyword.lower()
            assigned = False
            
            for theme, patterns in theme_patterns.items():
                # Check if keyword matches any pattern
                for pattern in patterns:
                    if pattern in keyword_lower or keyword_lower in pattern:
                        themes[theme].append(keyword)
                        assigned = True
                        break
                
                if assigned:
                    break
            
            if not assigned:
                unassigned.append(keyword)
        
        # Filter out empty themes
        themes = {k: v for k, v in themes.items() if v}
        
        # If we have unassigned keywords, create a "Other" theme
        if unassigned:
            themes['Other'] = unassigned[:10]  # Top 10 unassigned
        
        logger.info(f"Identified {len(themes)} themes for {bank_name}")
        for theme, keywords_list in themes.items():
            logger.info(f"  {theme}: {len(keywords_list)} keywords")
        
        return themes
    
    def assign_theme_to_review(self, review_text: str, themes: Dict[str, List[str]]) -> List[str]:
        """
        Assign theme(s) to a review based on keyword matching.
        
        Args:
            review_text: Review text
            themes: Dictionary of themes and their keywords
            
        Returns:
            List of assigned theme names
        """
        if not review_text:
            return []
        
        review_lower = review_text.lower()
        assigned_themes = []
        
        for theme, keywords in themes.items():
            # Check if any keyword from this theme appears in the review
            for keyword in keywords:
                if keyword.lower() in review_lower:
                    assigned_themes.append(theme)
                    break
        
        return assigned_themes if assigned_themes else ['Other']
    
    def analyze_bank(self, df: pd.DataFrame, bank_name: str, 
                    text_column: str = "processed_text") -> Dict:
        """
        Perform thematic analysis for a specific bank.
        
        Args:
            df: DataFrame with reviews for the bank
            bank_name: Name of the bank
            text_column: Name of the text column
            
        Returns:
            Dictionary with themes and keyword assignments
        """
        logger.info(f"Analyzing themes for {bank_name} ({len(df)} reviews)")
        
        # Get texts
        texts = df[text_column].fillna("").tolist()
        
        # Extract keywords using TF-IDF
        keywords_tfidf = self.extract_keywords_tfidf(texts)
        logger.info(f"Extracted {len(keywords_tfidf)} keywords using TF-IDF")
        
        # Also try spaCy if available
        keywords_spacy = []
        if SPACY_AVAILABLE:
            keywords_spacy = self.extract_keywords_spacy(texts)
            logger.info(f"Extracted {len(keywords_spacy)} keywords using spaCy")
        
        # Combine keywords (prioritize TF-IDF)
        all_keywords = keywords_tfidf[:50]  # Top 50 from TF-IDF
        if keywords_spacy:
            # Add spaCy keywords not already in TF-IDF
            tfidf_words = {word for word, _ in all_keywords}
            for word, freq in keywords_spacy[:30]:
                if word not in tfidf_words:
                    all_keywords.append((word, freq))
        
        # Cluster into themes
        themes = self.cluster_keywords_into_themes(all_keywords, bank_name)
        
        # Assign themes to reviews
        df_result = df.copy()
        df_result['identified_themes'] = df_result[text_column].apply(
            lambda x: self.assign_theme_to_review(x, themes) if pd.notna(x) and x else ['Other']
        )
        
        return {
            'themes': themes,
            'keywords': all_keywords[:30],  # Top 30 keywords
            'dataframe': df_result
        }
    
    def analyze_all_banks(self, df: pd.DataFrame, 
                          text_column: str = "processed_text") -> pd.DataFrame:
        """
        Perform thematic analysis for all banks.
        
        Args:
            df: DataFrame with reviews
            text_column: Name of the text column
            
        Returns:
            DataFrame with theme assignments
        """
        logger.info("Starting thematic analysis for all banks")
        
        all_results = []
        all_themes = {}  # Store themes for each bank
        
        for bank in df['bank'].unique():
            bank_df = df[df['bank'] == bank].copy()
            result = self.analyze_bank(bank_df, bank, text_column)
            all_results.append(result['dataframe'])
            all_themes[bank] = result['themes']
        
        # Combine results
        result_df = pd.concat(all_results, ignore_index=True)
        
        # Store themes info for reference
        logger.info("Thematic analysis complete for all banks")
        logger.info("Theme summary:")
        for bank, themes in all_themes.items():
            logger.info(f"  {bank}: {list(themes.keys())}")
        
        return result_df

