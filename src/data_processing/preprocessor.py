"""Data preprocessing utilities"""
import pandas as pd
from typing import Optional
from datetime import datetime

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class DataPreprocessor:
    """Preprocess review data"""
    
    def __init__(
        self,
        remove_duplicates: bool = True,
        min_length: int = 3,
        max_length: int = 1000,
        date_format: str = "%Y-%m-%d"
    ):
        """
        Initialize preprocessor.
        
        Args:
            remove_duplicates: Whether to remove duplicate reviews
            min_length: Minimum review text length
            max_length: Maximum review text length
            date_format: Expected date format
        """
        self.remove_duplicates = remove_duplicates
        self.min_length = min_length
        self.max_length = max_length
        self.date_format = date_format
    
    def clean_text(self, text: str) -> str:
        """
        Clean review text.
        
        Args:
            text: Raw review text
            
        Returns:
            Cleaned text
        """
        if not isinstance(text, str):
            return ""
        
        # Remove extra whitespace
        text = " ".join(text.split())
        
        # Truncate if too long
        if len(text) > self.max_length:
            text = text[:self.max_length]
        
        return text.strip()
    
    def normalize_date(self, date_str: str) -> Optional[str]:
        """
        Normalize date string to YYYY-MM-DD format.
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            Normalized date string or None
        """
        if pd.isna(date_str) or not date_str:
            return None
        
        try:
            # Try parsing the date
            if isinstance(date_str, str):
                # Handle different date formats
                for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y"]:
                    try:
                        dt = datetime.strptime(date_str, fmt)
                        return dt.strftime(self.date_format)
                    except ValueError:
                        continue
                
                # If it's already a datetime object string representation
                if 'T' in date_str:
                    dt = pd.to_datetime(date_str)
                    return dt.strftime(self.date_format)
            
            # If it's already a datetime object
            if isinstance(date_str, (datetime, pd.Timestamp)):
                return date_str.strftime(self.date_format)
            
        except Exception as e:
            logger.warning(f"Could not parse date: {date_str}, error: {str(e)}")
        
        return None
    
    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess the entire dataframe.
        
        Args:
            df: Raw review dataframe
            
        Returns:
            Preprocessed dataframe
        """
        logger.info(f"Preprocessing {len(df)} reviews")
        
        df = df.copy()
        
        # Remove duplicates
        if self.remove_duplicates:
            initial_count = len(df)
            df = df.drop_duplicates(subset=['review', 'bank', 'user_name'], keep='first')
            removed = initial_count - len(df)
            if removed > 0:
                logger.info(f"Removed {removed} duplicate reviews")
        
        # Clean review text
        df['review'] = df['review'].apply(self.clean_text)
        
        # Filter by length
        initial_count = len(df)
        df = df[
            (df['review'].str.len() >= self.min_length) &
            (df['review'].str.len() <= self.max_length)
        ]
        filtered = initial_count - len(df)
        if filtered > 0:
            logger.info(f"Filtered out {filtered} reviews by length")
        
        # Normalize dates
        df['date'] = df['date'].apply(self.normalize_date)
        
        # Handle missing data
        missing_before = df.isnull().sum().sum()
        df = df.dropna(subset=['review', 'rating', 'bank'])
        missing_after = df.isnull().sum().sum()
        if missing_before > missing_after:
            logger.info(f"Removed rows with missing critical data")
        
        # Ensure rating is integer
        df['rating'] = df['rating'].astype(int)
        
        # Ensure rating is in valid range
        df = df[(df['rating'] >= 1) & (df['rating'] <= 5)]
        
        logger.info(f"Preprocessing complete. Final count: {len(df)} reviews")
        
        return df.reset_index(drop=True)
    
    def validate_data_quality(self, df: pd.DataFrame) -> dict:
        """
        Validate data quality and return metrics.
        
        Args:
            df: Dataframe to validate
            
        Returns:
            Dictionary with quality metrics
        """
        total = len(df)
        
        metrics = {
            'total_reviews': total,
            'missing_review_text': df['review'].isna().sum(),
            'missing_rating': df['rating'].isna().sum(),
            'missing_date': df['date'].isna().sum(),
            'missing_bank': df['bank'].isna().sum(),
            'duplicate_reviews': df.duplicated(subset=['review', 'bank']).sum(),
            'invalid_ratings': ((df['rating'] < 1) | (df['rating'] > 5)).sum(),
            'reviews_per_bank': df.groupby('bank').size().to_dict(),
            'avg_rating_per_bank': df.groupby('bank')['rating'].mean().to_dict()
        }
        
        # Calculate error percentage
        errors = (
            metrics['missing_review_text'] +
            metrics['missing_rating'] +
            metrics['invalid_ratings']
        )
        metrics['error_percentage'] = (errors / total * 100) if total > 0 else 0
        
        return metrics

