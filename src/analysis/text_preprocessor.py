"""Text preprocessing for NLP analysis"""
import re
import string
from typing import List, Optional
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('omw-1.4', quiet=True)
except Exception as e:
    logger.warning(f"Error downloading NLTK data: {e}")


class TextPreprocessor:
    """Text preprocessing for NLP tasks"""
    
    def __init__(self, language: str = "english"):
        """
        Initialize text preprocessor.
        
        Args:
            language: Language for stopwords
        """
        self.language = language
        try:
            self.stop_words = set(stopwords.words(language))
        except:
            self.stop_words = set()
            logger.warning("Could not load stopwords, using empty set")
        
        self.lemmatizer = WordNetLemmatizer()
    
    def clean_text(self, text: str) -> str:
        """
        Clean text by removing special characters and normalizing.
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        if not text or pd.isna(text):
            return ""
        
        text = str(text).lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove special characters but keep spaces and basic punctuation
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words.
        
        Args:
            text: Text to tokenize
            
        Returns:
            List of tokens
        """
        if not text:
            return []
        
        try:
            tokens = word_tokenize(text)
            return tokens
        except Exception as e:
            logger.warning(f"Error tokenizing text: {e}")
            return text.split()
    
    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """
        Remove stopwords from tokens.
        
        Args:
            tokens: List of tokens
            
        Returns:
            Tokens without stopwords
        """
        return [token for token in tokens if token not in self.stop_words and len(token) > 1]
    
    def lemmatize(self, tokens: List[str]) -> List[str]:
        """
        Lemmatize tokens.
        
        Args:
            tokens: List of tokens
            
        Returns:
            Lemmatized tokens
        """
        return [self.lemmatizer.lemmatize(token) for token in tokens]
    
    def preprocess(self, text: str, remove_stopwords: bool = True, 
                   lemmatize: bool = True) -> str:
        """
        Complete preprocessing pipeline.
        
        Args:
            text: Raw text
            remove_stopwords: Whether to remove stopwords
            lemmatize: Whether to lemmatize
            
        Returns:
            Preprocessed text
        """
        # Clean
        text = self.clean_text(text)
        
        # Tokenize
        tokens = self.tokenize(text)
        
        # Remove stopwords
        if remove_stopwords:
            tokens = self.remove_stopwords(tokens)
        
        # Lemmatize
        if lemmatize:
            tokens = self.lemmatize(tokens)
        
        # Join back
        return ' '.join(tokens)
    
    def preprocess_dataframe(self, df: pd.DataFrame, text_column: str = "review",
                            output_column: str = "processed_text") -> pd.DataFrame:
        """
        Preprocess text column in dataframe.
        
        Args:
            df: DataFrame with text column
            text_column: Name of text column
            output_column: Name of output column
            
        Returns:
            DataFrame with preprocessed text
        """
        logger.info(f"Preprocessing {len(df)} texts")
        
        df_result = df.copy()
        df_result[output_column] = df_result[text_column].apply(
            lambda x: self.preprocess(x) if pd.notna(x) else ""
        )
        
        logger.info("Preprocessing complete")
        return df_result

