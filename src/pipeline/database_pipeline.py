"""Database storage pipeline for Task 3"""
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any

from src.database.db_connection import DatabaseConnection
from src.database.db_loader import DatabaseLoader
from src.utils.config_loader import load_config
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class DatabasePipeline:
    """Pipeline for storing data in PostgreSQL database"""
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize database pipeline.
        
        Args:
            project_root: Project root directory
        """
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.config = load_config()
        
        # Initialize database connection
        self.db = DatabaseConnection()
        self.loader = DatabaseLoader(self.db)
        
        # Data paths
        self.processed_data_path = self.project_root / "data" / "processed" / "processed_reviews.csv"
        self.analyzed_data_path = self.project_root / "data" / "interim" / "analyzed_reviews.csv"
    
    def run(self) -> Dict[str, Any]:
        """
        Run the complete database storage pipeline.
        
        Returns:
            Dictionary with pipeline results
        """
        logger.info("=" * 60)
        logger.info("Starting Task 3: Database Storage Pipeline")
        logger.info("=" * 60)
        
        results = {
            'banks_loaded': 0,
            'reviews_inserted': 0,
            'verification': {}
        }
        
        try:
            # Step 1: Test connection
            logger.info("Step 1: Testing database connection...")
            if not self.db.test_connection():
                raise ConnectionError("Failed to connect to database")
            logger.info("✅ Database connection successful")
            
            # Step 2: Load banks
            logger.info("Step 2: Loading banks into database...")
            bank_mapping = self.loader.load_banks(self.config)
            results['banks_loaded'] = len(bank_mapping)
            logger.info(f"✅ Loaded {len(bank_mapping)} banks")
            
            # Step 3: Load reviews (prefer analyzed data if available)
            logger.info("Step 3: Loading reviews into database...")
            if self.analyzed_data_path.exists():
                logger.info("Using analyzed_reviews.csv (includes sentiment data)")
                reviews_inserted = self.loader.load_reviews_from_csv(
                    self.analyzed_data_path,
                    bank_mapping,
                    use_analyzed_data=True
                )
            elif self.processed_data_path.exists():
                logger.info("Using processed_reviews.csv (no sentiment data)")
                reviews_inserted = self.loader.load_reviews_from_csv(
                    self.processed_data_path,
                    bank_mapping,
                    use_analyzed_data=False
                )
            else:
                raise FileNotFoundError(
                    f"Neither {self.analyzed_data_path} nor {self.processed_data_path} found"
                )
            
            results['reviews_inserted'] = reviews_inserted
            logger.info(f"✅ Inserted {reviews_inserted} reviews")
            
            # Step 4: Verify data integrity
            logger.info("Step 4: Verifying data integrity...")
            verification = self.loader.verify_data_integrity()
            results['verification'] = verification
            
            # Log verification results
            logger.info("\n" + "=" * 60)
            logger.info("DATA INTEGRITY VERIFICATION RESULTS")
            logger.info("=" * 60)
            logger.info(f"Total Reviews: {verification.get('total_reviews', 0)}")
            
            logger.info("\nReviews per Bank:")
            for bank_data in verification.get('reviews_per_bank', []):
                logger.info(f"  {bank_data['bank']}: {bank_data['count']} reviews")
            
            logger.info("\nAverage Rating per Bank:")
            for bank_data in verification.get('avg_rating_per_bank', []):
                avg = bank_data['avg_rating']
                count = bank_data['count']
                logger.info(f"  {bank_data['bank']}: {avg:.2f} ({count} reviews)")
            
            if verification.get('sentiment_coverage'):
                coverage = verification['sentiment_coverage']
                logger.info(f"\nSentiment Coverage: {coverage['coverage_percentage']:.2f}%")
                logger.info(f"  Total: {coverage['total']}")
                logger.info(f"  With Sentiment: {coverage['with_sentiment']}")
            
            logger.info("=" * 60)
            logger.info("✅ Task 3 completed successfully!")
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise
        
        return results

