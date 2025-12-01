"""
Verification script for database integrity
Run SQL queries to verify data was loaded correctly
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.db_connection import DatabaseConnection
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def verify_database():
    """Run verification queries on the database"""
    logger.info("=" * 60)
    logger.info("DATABASE VERIFICATION")
    logger.info("=" * 60)
    
    db = DatabaseConnection()
    
    try:
        # Test connection
        if not db.test_connection():
            logger.error("Failed to connect to database")
            return False
        
        # 1. Count total reviews
        logger.info("\n1. Total Reviews:")
        result = db.execute_query("SELECT COUNT(*) as count FROM reviews")
        total_reviews = result[0]['count'] if result else 0
        logger.info(f"   Total: {total_reviews}")
        
        if total_reviews < 400:
            logger.warning(f"   ⚠️  Less than 400 reviews (minimum requirement)")
        else:
            logger.info(f"   ✅ Meets minimum requirement (400+)")
        
        # 2. Count reviews per bank
        logger.info("\n2. Reviews per Bank:")
        reviews_per_bank = db.execute_query("""
            SELECT b.bank_name, COUNT(r.review_id) as review_count
            FROM banks b
            LEFT JOIN reviews r ON b.bank_id = r.bank_id
            GROUP BY b.bank_id, b.bank_name
            ORDER BY review_count DESC
        """)
        
        for row in reviews_per_bank:
            count = row['review_count']
            logger.info(f"   {row['bank_name']}: {count} reviews")
            if count < 400:
                logger.warning(f"      ⚠️  Less than 400 reviews")
            else:
                logger.info(f"      ✅ Meets minimum requirement")
        
        # 3. Average rating per bank
        logger.info("\n3. Average Rating per Bank:")
        avg_ratings = db.execute_query("""
            SELECT b.bank_name, AVG(r.rating) as avg_rating, COUNT(r.review_id) as count
            FROM banks b
            LEFT JOIN reviews r ON b.bank_id = r.bank_id
            WHERE r.rating IS NOT NULL
            GROUP BY b.bank_id, b.bank_name
            ORDER BY avg_rating DESC
        """)
        
        for row in avg_ratings:
            avg = float(row['avg_rating']) if row['avg_rating'] else None
            count = row['count']
            logger.info(f"   {row['bank_name']}: {avg:.2f} ({count} reviews)")
        
        # 4. Sentiment distribution
        logger.info("\n4. Sentiment Distribution:")
        sentiment_dist = db.execute_query("""
            SELECT sentiment_label, COUNT(*) as count
            FROM reviews
            WHERE sentiment_label IS NOT NULL
            GROUP BY sentiment_label
            ORDER BY count DESC
        """)
        
        if sentiment_dist:
            for row in sentiment_dist:
                logger.info(f"   {row['sentiment_label']}: {row['count']} reviews")
        else:
            logger.info("   No sentiment data available")
        
        # 5. Sentiment coverage
        logger.info("\n5. Sentiment Coverage:")
        coverage = db.execute_query("""
            SELECT 
                COUNT(*) as total,
                COUNT(sentiment_label) as with_sentiment,
                ROUND(COUNT(sentiment_label)::numeric / COUNT(*) * 100, 2) as coverage_pct
            FROM reviews
        """)
        
        if coverage:
            total = coverage[0]['total']
            with_sentiment = coverage[0]['with_sentiment']
            pct = float(coverage[0]['coverage_pct']) if coverage[0]['coverage_pct'] else 0
            logger.info(f"   Total reviews: {total}")
            logger.info(f"   With sentiment: {with_sentiment}")
            logger.info(f"   Coverage: {pct:.2f}%")
            
            if pct >= 90:
                logger.info("   ✅ Meets requirement (90%+)")
            else:
                logger.warning(f"   ⚠️  Below requirement (90%)")
        
        # 6. Data integrity checks
        logger.info("\n6. Data Integrity Checks:")
        
        # Check for NULL ratings
        null_ratings = db.execute_query("SELECT COUNT(*) as count FROM reviews WHERE rating IS NULL")
        null_count = null_ratings[0]['count'] if null_ratings else 0
        logger.info(f"   Reviews with NULL rating: {null_count}")
        
        # Check for invalid ratings
        invalid_ratings = db.execute_query("""
            SELECT COUNT(*) as count 
            FROM reviews 
            WHERE rating IS NOT NULL AND (rating < 1 OR rating > 5)
        """)
        invalid_count = invalid_ratings[0]['count'] if invalid_ratings else 0
        if invalid_count == 0:
            logger.info("   ✅ All ratings are valid (1-5)")
        else:
            logger.warning(f"   ⚠️  {invalid_count} reviews with invalid ratings")
        
        # Check for empty review text
        empty_text = db.execute_query("SELECT COUNT(*) as count FROM reviews WHERE review_text IS NULL OR review_text = ''")
        empty_count = empty_text[0]['count'] if empty_text else 0
        if empty_count == 0:
            logger.info("   ✅ All reviews have text")
        else:
            logger.warning(f"   ⚠️  {empty_count} reviews with empty text")
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ Verification complete!")
        
        return True
        
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        return False


if __name__ == "__main__":
    success = verify_database()
    sys.exit(0 if success else 1)

