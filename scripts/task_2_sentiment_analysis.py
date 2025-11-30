"""
Task 2: Sentiment and Thematic Analysis
Analyze sentiment and identify themes in bank reviews

This script performs:
1. Sentiment analysis using DistilBERT
2. Thematic analysis using keyword extraction and clustering
3. Aggregation by bank and rating
"""
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.pipeline.sentiment_analysis_pipeline import SentimentAnalysisPipeline
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def main():
    """Main execution function for Task 2"""
    logger.info("Starting Task 2: Sentiment and Thematic Analysis")
    
    # Initialize pipeline
    pipeline = SentimentAnalysisPipeline(project_root=project_root)
    
    # Run complete pipeline
    results = pipeline.run()
    
    # Display summary
    logger.info("\n" + "="*60)
    logger.info("TASK 2 SUMMARY")
    logger.info("="*60)
    logger.info(f"Total reviews analyzed: {results['total_reviews']}")
    logger.info(f"Sentiment coverage: {results['sentiment_coverage']:.2f}%")
    logger.info(f"\nThemes per bank:")
    for bank, count in results['themes_per_bank'].items():
        logger.info(f"  {bank}: {count} themes")
    logger.info(f"\nResults saved to: {results['results_file']}")
    logger.info("="*60)
    
    # Check KPIs
    logger.info("\nKPI CHECK:")
    if results['sentiment_coverage'] >= 90:
        logger.info(f"✅ Sentiment coverage: {results['sentiment_coverage']:.2f}% (>= 90%)")
    else:
        logger.warning(f"⚠️  Sentiment coverage: {results['sentiment_coverage']:.2f}% (< 90%)")
    
    all_banks_meet_minimum = all(count >= 3 for count in results['themes_per_bank'].values())
    if all_banks_meet_minimum:
        logger.info(f"✅ All banks have 3+ themes")
    else:
        logger.warning(f"⚠️  Some banks have < 3 themes")
    
    logger.info("\nTask 2 completed successfully!")


if __name__ == "__main__":
    main()

