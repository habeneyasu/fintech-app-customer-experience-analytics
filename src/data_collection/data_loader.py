"""Data loader for existing review data"""
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class DataLoader:
    """Load and prepare existing review data"""
    
    def __init__(self, config: Dict):
        """
        Initialize data loader.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.project_root = Path(__file__).parent.parent.parent
    
    def load_existing_data(self, file_path: str) -> pd.DataFrame:
        """
        Load existing data from CSV file.
        
        Args:
            file_path: Path to the data file
            
        Returns:
            DataFrame with loaded data
        """
        full_path = self.project_root / file_path
        
        if not full_path.exists():
            raise FileNotFoundError(f"Data file not found: {full_path}")
        
        logger.info(f"Loading existing data from {full_path}")
        df = pd.read_csv(full_path)
        logger.info(f"Loaded {len(df)} reviews from existing file")
        
        return df
    
    def standardize_bank_codes(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize bank codes in the dataframe.
        
        Args:
            df: DataFrame with bank column
            
        Returns:
            DataFrame with standardized bank codes
        """
        if 'bank' not in df.columns:
            return df
        
        bank_mapping = {
            'Dashen': 'DASHEN',
            'CBE': 'CBE',
            'BOA': 'BOA'
        }
        
        df['bank'] = df['bank'].replace(bank_mapping)
        return df
    
    def validate_columns(self, df: pd.DataFrame) -> None:
        """
        Validate that required columns exist.
        
        Args:
            df: DataFrame to validate
            
        Raises:
            ValueError: If required columns are missing
        """
        required_cols = ['review', 'rating', 'date', 'bank']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
    
    def add_missing_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add missing optional columns with default values.
        
        Args:
            df: DataFrame to enhance
            
        Returns:
            DataFrame with all required columns
        """
        # Add user_name if missing
        if 'user_name' not in df.columns:
            df['user_name'] = 'Unknown'
        
        # Add source if missing
        if 'source' not in df.columns:
            df['source'] = 'Google Play'
        
        # Add app_name if missing
        if 'app_name' not in df.columns:
            bank_to_app = {
                bank['code']: bank['app_name'] 
                for bank in self.config.get('banks', [])
            }
            df['app_name'] = df['bank'].map(bank_to_app)
        
        return df
    
    def prepare_data(self, file_path: str) -> pd.DataFrame:
        """
        Load and prepare data from file.
        
        Args:
            file_path: Path to the data file
            
        Returns:
            Prepared DataFrame
        """
        # Load data
        df = self.load_existing_data(file_path)
        
        # Standardize bank codes
        df = self.standardize_bank_codes(df)
        
        # Validate columns
        self.validate_columns(df)
        
        # Add missing columns
        df = self.add_missing_columns(df)
        
        return df

