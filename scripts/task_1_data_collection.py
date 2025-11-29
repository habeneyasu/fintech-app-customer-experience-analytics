"""
Task 1: Data Collection and Preprocessing
Scrape reviews from Google Play Store and preprocess them

This script uses an object-oriented pipeline approach for better reusability.
"""
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.pipeline.data_collection_pipeline import DataCollectionPipeline
from src.utils.config_loader import load_config
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def main():
    """Main execution function for Task 1"""
    logger.info("Starting Task 1: Data Collection and Preprocessing")
    
    # Load configuration
    config = load_config()
    
    # Initialize pipeline
    pipeline = DataCollectionPipeline(config=config, project_root=project_root)
    
    # Run complete pipeline
    results = pipeline.run()
    
    # Display summary
    logger.info("\n" + "="*60)
    logger.info("PIPELINE SUMMARY")
    logger.info("="*60)
    logger.info(f"Raw reviews collected: {results['raw_count']}")
    logger.info(f"Processed reviews: {results['processed_count']}")
    logger.info(f"Error rate: {results['quality_metrics']['error_percentage']:.2f}%")
    logger.info("="*60)
    
    logger.info("Task 1 completed successfully!")


if __name__ == "__main__":
    main()

