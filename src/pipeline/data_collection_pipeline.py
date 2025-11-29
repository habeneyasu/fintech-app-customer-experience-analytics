"""Data collection and preprocessing pipeline"""
import pandas as pd
from pathlib import Path
from typing import Dict, Optional
from src.data_collection.scraper import PlayStoreScraper
from src.data_collection.data_loader import DataLoader
from src.data_processing.preprocessor import DataPreprocessor
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class DataCollectionPipeline:
    """
    Main pipeline class for data collection and preprocessing.
    Encapsulates the entire workflow in a reusable, object-oriented manner.
    """
    
    def __init__(self, config: Dict, project_root: Optional[Path] = None):
        """
        Initialize the data collection pipeline.
        
        Args:
            config: Configuration dictionary
            project_root: Project root directory (defaults to auto-detection)
        """
        self.config = config
        self.project_root = project_root or Path(__file__).parent.parent.parent
        
        # Initialize components
        self.data_loader = DataLoader(config)
        self.preprocessor = DataPreprocessor(
            remove_duplicates=config['processing']['remove_duplicates'],
            min_length=config['processing']['min_review_length'],
            max_length=config['processing']['max_review_length'],
            date_format=config['processing']['date_format']
        )
        
        # Initialize scraper (will be created if needed)
        self.scraper: Optional[PlayStoreScraper] = None
        
        # Data storage
        self.raw_data: Optional[pd.DataFrame] = None
        self.processed_data: Optional[pd.DataFrame] = None
        self.quality_metrics: Optional[Dict] = None
        
        # Setup directories
        self._setup_directories()
    
    def _setup_directories(self) -> None:
        """Create necessary directories for data storage."""
        paths = self.config['paths']
        self.raw_dir = self.project_root / paths['data_raw']
        self.processed_dir = self.project_root / paths['data_processed']
        
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
    
    def _initialize_scraper(self) -> None:
        """Initialize the scraper if not already initialized."""
        if self.scraper is None:
            scraping_config = self.config.get('scraping', {})
            self.scraper = PlayStoreScraper(
                min_reviews=scraping_config.get('min_reviews_per_bank', 400),
                max_reviews=scraping_config.get('max_reviews_per_bank', 10000),
                batch_size=scraping_config.get('batch_size', 100),
                retry_attempts=scraping_config.get('retry_attempts', 5),
                retry_delay=scraping_config.get('retry_delay', 2),
                request_delay=scraping_config.get('request_delay', 1),
                language_options=scraping_config.get('languages', None)
            )
    
    def load_existing_data(self) -> pd.DataFrame:
        """
        Load data from existing file.
        
        Returns:
            DataFrame with loaded data
        """
        data_source = self.config.get('data_source', {})
        existing_file = data_source.get('existing_data_file')
        
        if not existing_file:
            raise ValueError("No existing data file specified in config")
        
        df = self.data_loader.prepare_data(existing_file)
        return df
    
    def scrape_new_data(self) -> pd.DataFrame:
        """
        Scrape new data from Google Play Store.
        
        Returns:
            DataFrame with scraped data
        """
        self._initialize_scraper()
        banks_config = self.config['banks']
        df = self.scraper.scrape_all_banks(banks_config)
        return df
    
    def collect_data(self) -> pd.DataFrame:
        """
        Collect data (either from existing file or by scraping).
        
        Returns:
            DataFrame with collected data
        """
        data_source = self.config.get('data_source', {})
        use_existing = data_source.get('use_existing_data', False)
        scrape_new = data_source.get('scrape_new_data', False)
        
        if use_existing and not scrape_new:
            try:
                df = self.load_existing_data()
                logger.info("Successfully loaded existing data")
            except FileNotFoundError as e:
                logger.warning(f"Existing data file not found: {e}")
                logger.info("Falling back to scraping new data...")
                df = self.scrape_new_data()
        else:
            df = self.scrape_new_data()
        
        self.raw_data = df
        return df
    
    def save_raw_data(self, filename: str = "raw_reviews.csv") -> Path:
        """
        Save raw data to file.
        
        Args:
            filename: Name of the output file
            
        Returns:
            Path to saved file
        """
        if self.raw_data is None:
            raise ValueError("No raw data to save. Run collect_data() first.")
        
        file_path = self.raw_dir / filename
        self.raw_data.to_csv(file_path, index=False)
        logger.info(f"Saved raw data to {file_path} ({len(self.raw_data)} reviews)")
        
        # Log review counts by bank
        if 'bank' in self.raw_data.columns:
            bank_counts = self.raw_data['bank'].value_counts()
            logger.info("Review counts by bank:")
            for bank, count in bank_counts.items():
                logger.info(f"  {bank}: {count} reviews")
        
        return file_path
    
    def preprocess_data(self) -> pd.DataFrame:
        """
        Preprocess the collected data.
        
        Returns:
            Preprocessed DataFrame
        """
        if self.raw_data is None:
            raise ValueError("No raw data to process. Run collect_data() first.")
        
        logger.info("Preprocessing data...")
        self.processed_data = self.preprocessor.preprocess(self.raw_data)
        return self.processed_data
    
    def validate_quality(self) -> Dict:
        """
        Validate data quality.
        
        Returns:
            Dictionary with quality metrics
        """
        if self.processed_data is None:
            raise ValueError("No processed data to validate. Run preprocess_data() first.")
        
        self.quality_metrics = self.preprocessor.validate_data_quality(self.processed_data)
        logger.info(f"Data Quality Metrics: {self.quality_metrics}")
        return self.quality_metrics
    
    def save_processed_data(self, filename: str = "processed_reviews.csv") -> Path:
        """
        Save processed data to file.
        
        Args:
            filename: Name of the output file
            
        Returns:
            Path to saved file
        """
        if self.processed_data is None:
            raise ValueError("No processed data to save. Run preprocess_data() first.")
        
        file_path = self.processed_dir / filename
        self.processed_data.to_csv(file_path, index=False)
        logger.info(f"Saved processed data to {file_path}")
        return file_path
    
    def run(self) -> Dict:
        """
        Run the complete pipeline: collect, preprocess, validate, and save.
        
        Returns:
            Dictionary with pipeline results and metrics
        """
        logger.info("Starting Data Collection Pipeline")
        
        # Step 1: Collect data
        self.collect_data()
        self.save_raw_data()
        
        # Step 2: Preprocess data
        self.preprocess_data()
        
        # Step 3: Validate quality
        self.validate_quality()
        
        # Step 4: Save processed data
        self.save_processed_data()
        
        logger.info("Pipeline completed successfully!")
        
        return {
            'raw_count': len(self.raw_data) if self.raw_data is not None else 0,
            'processed_count': len(self.processed_data) if self.processed_data is not None else 0,
            'quality_metrics': self.quality_metrics
        }
    
    def get_raw_data(self) -> Optional[pd.DataFrame]:
        """Get the raw data DataFrame."""
        return self.raw_data
    
    def get_processed_data(self) -> Optional[pd.DataFrame]:
        """Get the processed data DataFrame."""
        return self.processed_data
    
    def get_quality_metrics(self) -> Optional[Dict]:
        """Get the quality metrics."""
        return self.quality_metrics

