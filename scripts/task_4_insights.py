"""
Task 4: Insights and Recommendations
Generate insights, create visualizations, and provide recommendations
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.pipeline.insights_pipeline import InsightsPipeline
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def main():
    """Main execution function for Task 4"""
    logger.info("Starting Task 4: Insights and Recommendations")
    
    try:
        # Initialize pipeline
        pipeline = InsightsPipeline(project_root=project_root, use_database=True)
        
        # Run pipeline
        results = pipeline.run()
        
        # Display summary
        logger.info("\n" + "=" * 60)
        logger.info("PIPELINE SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Banks Analyzed: {len(results['insights'])}")
        logger.info(f"Visualizations Created: {len(results['visualizations'])}")
        logger.info(f"Insights File: {results.get('insights_file', 'N/A')}")
        logger.info("=" * 60)
        
        logger.info("\n✅ Task 4 completed successfully!")
        logger.info("\nNext steps:")
        logger.info("1. Review visualizations in data/results/visualizations/")
        logger.info("2. Check insights in data/results/insights.json")
        logger.info("3. Generate final report using report generator")
        
    except Exception as e:
        logger.error(f"Task 4 failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()

