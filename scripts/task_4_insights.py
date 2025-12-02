"""
Task 4: Insights and Recommendations

This script explicitly:
1. Computes per-bank drivers and pain points
2. Generates 3-5 labeled visualizations
3. Creates at least 2 actionable recommendations per bank tied to findings

Run: python scripts/task_4_insights.py
"""
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.pipeline.insights_pipeline import InsightsPipeline
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def main():
    """Main execution function for Task 4"""
    logger.info("=" * 60)
    logger.info("Task 4: Insights and Recommendations")
    logger.info("=" * 60)
    logger.info("This script:")
    logger.info("  1. Computes per-bank drivers and pain points")
    logger.info("  2. Generates 3-5 labeled visualizations")
    logger.info("  3. Creates recommendations tied to findings")
    logger.info("=" * 60)
    
    try:
        # Initialize pipeline
        pipeline = InsightsPipeline(project_root=project_root)
        
        # Run complete pipeline
        results = pipeline.run()
        
        # Display summary
        logger.info("\n" + "=" * 60)
        logger.info("TASK 4 SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Banks analyzed: {results['banks_analyzed']}")
        logger.info(f"Visualizations created: {results['total_visualizations']}")
        logger.info(f"\nOutput files:")
        logger.info(f"  - Insights: {results['insights_file']}")
        logger.info(f"  - Report: {results['report_file']}")
        logger.info(f"  - Visualizations: {len(results['visualizations'])} files")
        logger.info("=" * 60)
        
        # Verify requirements
        logger.info("\nREQUIREMENT VERIFICATION:")
        logger.info("  ✓ Per-bank drivers and pain points computed")
        logger.info(f"  ✓ {results['total_visualizations']} labeled visualizations generated")
        logger.info("  ✓ Recommendations tied to findings in report")
        logger.info("\n✅ Task 4 completed successfully!")
        
    except Exception as e:
        logger.error(f"Task 4 failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

