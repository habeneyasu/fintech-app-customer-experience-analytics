"""
Test script for database insertion
This script tests the database connection and data insertion functionality
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.db_connection import DatabaseConnection
from src.database.db_loader import DatabaseLoader
from src.utils.config_loader import load_config
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def test_connection():
    """Test database connection"""
    logger.info("=" * 60)
    logger.info("TEST 1: Database Connection")
    logger.info("=" * 60)
    
    db = DatabaseConnection()
    
    try:
        if db.test_connection():
            logger.info("✅ Database connection successful!")
            return True
        else:
            logger.error("❌ Database connection failed!")
            return False
    except Exception as e:
        logger.error(f"❌ Connection error: {e}")
        logger.error("\nTroubleshooting:")
        logger.error("1. Ensure PostgreSQL is running")
        logger.error("2. Check database 'bank_reviews' exists: CREATE DATABASE bank_reviews;")
        logger.error("3. Verify .env file has correct credentials")
        logger.error("4. Check database user permissions")
        return False


def test_bank_loading():
    """Test loading banks into database"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Bank Loading")
    logger.info("=" * 60)
    
    db = DatabaseConnection()
    loader = DatabaseLoader(db)
    config = load_config()
    
    try:
        bank_mapping = loader.load_banks(config)
        
        if len(bank_mapping) > 0:
            logger.info(f"✅ Successfully loaded {len(bank_mapping)} banks:")
            for code, bank_id in bank_mapping.items():
                logger.info(f"   {code}: bank_id={bank_id}")
            return True, bank_mapping
        else:
            logger.error("❌ No banks loaded!")
            return False, {}
    except Exception as e:
        logger.error(f"❌ Bank loading failed: {e}")
        return False, {}


def test_review_insertion(bank_mapping):
    """Test inserting reviews into database"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: Review Insertion")
    logger.info("=" * 60)
    
    db = DatabaseConnection()
    loader = DatabaseLoader(db)
    
    project_root = Path(__file__).parent.parent
    processed_path = project_root / "data" / "processed" / "processed_reviews.csv"
    analyzed_path = project_root / "data" / "interim" / "analyzed_reviews.csv"
    
    # Determine which file to use
    if analyzed_path.exists():
        csv_path = analyzed_path
        use_analyzed = True
        logger.info(f"Using analyzed_reviews.csv (includes sentiment data)")
    elif processed_path.exists():
        csv_path = processed_path
        use_analyzed = False
        logger.info(f"Using processed_reviews.csv (no sentiment data)")
    else:
        logger.error("❌ No CSV file found!")
        logger.error(f"   Expected: {processed_path} or {analyzed_path}")
        return False
    
    try:
        # Insert a small batch first (100 reviews) for testing
        logger.info(f"Inserting first 100 reviews as test...")
        
        # Read CSV and get first 100 rows
        import pandas as pd
        df = pd.read_csv(csv_path, nrows=100)
        
        # Save to temporary file
        temp_path = project_root / "data" / "processed" / "test_reviews.csv"
        df.to_csv(temp_path, index=False)
        
        # Insert test reviews
        inserted = loader.load_reviews_from_csv(
            temp_path,
            bank_mapping,
            use_analyzed_data=use_analyzed,
            batch_size=100
        )
        
        # Clean up temp file
        temp_path.unlink()
        
        if inserted > 0:
            logger.info(f"✅ Successfully inserted {inserted} test reviews!")
            return True
        else:
            logger.error("❌ No reviews inserted!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Review insertion failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def test_data_verification():
    """Test data verification queries"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: Data Verification")
    logger.info("=" * 60)
    
    db = DatabaseConnection()
    loader = DatabaseLoader(db)
    
    try:
        results = loader.verify_data_integrity()
        
        logger.info(f"Total Reviews: {results.get('total_reviews', 0)}")
        
        logger.info("\nReviews per Bank:")
        for bank_data in results.get('reviews_per_bank', []):
            logger.info(f"   {bank_data['bank']}: {bank_data['count']} reviews")
        
        logger.info("\nAverage Rating per Bank:")
        for bank_data in results.get('avg_rating_per_bank', []):
            avg = bank_data['avg_rating']
            count = bank_data['count']
            logger.info(f"   {bank_data['bank']}: {avg:.2f} ({count} reviews)")
        
        if results.get('sentiment_coverage'):
            coverage = results['sentiment_coverage']
            logger.info(f"\nSentiment Coverage: {coverage['coverage_percentage']:.2f}%")
        
        logger.info("\n✅ Data verification successful!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Data verification failed: {e}")
        return False


def main():
    """Run all tests"""
    logger.info("=" * 60)
    logger.info("DATABASE INSERTION TEST SUITE")
    logger.info("=" * 60)
    logger.info("\nThis script tests:")
    logger.info("1. Database connection")
    logger.info("2. Bank loading")
    logger.info("3. Review insertion (test batch)")
    logger.info("4. Data verification")
    logger.info("\n" + "=" * 60)
    
    # Test 1: Connection
    if not test_connection():
        logger.error("\n❌ Connection test failed. Please fix connection issues first.")
        sys.exit(1)
    
    # Test 2: Bank loading
    success, bank_mapping = test_bank_loading()
    if not success:
        logger.error("\n❌ Bank loading failed.")
        sys.exit(1)
    
    # Test 3: Review insertion
    if not test_review_insertion(bank_mapping):
        logger.error("\n❌ Review insertion test failed.")
        sys.exit(1)
    
    # Test 4: Verification
    if not test_data_verification():
        logger.error("\n❌ Data verification failed.")
        sys.exit(1)
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ ALL TESTS PASSED!")
    logger.info("=" * 60)
    logger.info("\nYou can now run the full insertion:")
    logger.info("  python scripts/task_3_database_storage.py")
    logger.info("\nOr verify the database:")
    logger.info("  python scripts/verify_database.py")


if __name__ == "__main__":
    main()

