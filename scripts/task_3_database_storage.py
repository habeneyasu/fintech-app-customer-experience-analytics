"""
Task 3: Database Storage in PostgreSQL
Store cleaned and processed review data in PostgreSQL database

This script:
1. Connects to PostgreSQL database
2. Loads banks from configuration
3. Inserts reviews from CSV files
4. Verifies data integrity
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.pipeline.database_pipeline import DatabasePipeline
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def main():
    """Main execution function for Task 3"""
    logger.info("Starting Task 3: Database Storage in PostgreSQL")
    
    try:
        # Initialize pipeline
        pipeline = DatabasePipeline(project_root=project_root)
        
        # Run pipeline
        results = pipeline.run()
        
        # Display summary
        logger.info("\n" + "=" * 60)
        logger.info("PIPELINE SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Banks loaded: {results['banks_loaded']}")
        logger.info(f"Reviews inserted: {results['reviews_inserted']}")
        logger.info(f"Total reviews in database: {results['verification'].get('total_reviews', 0)}")
        logger.info("=" * 60)
        
        logger.info("\n✅ Task 3 completed successfully!")
        
    except Exception as e:
        logger.error(f"Task 3 failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

