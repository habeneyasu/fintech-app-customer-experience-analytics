"""Database loader for inserting review data into PostgreSQL"""
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, List, Any
from psycopg2.extras import execute_values
import numpy as np

from src.database.db_connection import DatabaseConnection
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class DatabaseLoader:
    """Load data from CSV files into PostgreSQL database"""
    
    def __init__(self, db_connection: DatabaseConnection):
        """
        Initialize database loader.
        
        Args:
            db_connection: DatabaseConnection instance
        """
        self.db = db_connection
        self.bank_cache: Dict[str, int] = {}  # Cache bank_name -> bank_id mapping
    
    def load_banks(self, config: Dict) -> Dict[str, int]:
        """
        Load banks from configuration into database.
        
        Args:
            config: Configuration dictionary with banks information
            
        Returns:
            Dictionary mapping bank code to bank_id
        """
        logger.info("Loading banks into database...")
        
        banks = config.get('banks', [])
        bank_mapping = {}
        
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                for bank in banks:
                    bank_name = bank['name']
                    app_name = bank.get('app_name', '')
                    code = bank.get('code', '')
                    
                    # Check if bank already exists
                    cursor.execute(
                        "SELECT bank_id FROM banks WHERE bank_name = %s",
                        (bank_name,)
                    )
                    result = cursor.fetchone()
                    
                    if result:
                        bank_id = result[0]
                        logger.info(f"Bank '{bank_name}' already exists (ID: {bank_id})")
                    else:
                        # Insert new bank
                        cursor.execute(
                            """
                            INSERT INTO banks (bank_name, app_name)
                            VALUES (%s, %s)
                            RETURNING bank_id
                            """,
                            (bank_name, app_name)
                        )
                        bank_id = cursor.fetchone()[0]
                        logger.info(f"Inserted bank '{bank_name}' (ID: {bank_id})")
                    
                    bank_mapping[code] = bank_id
                    self.bank_cache[bank_name] = bank_id
        
        return bank_mapping
    
    def get_bank_id(self, bank_name: str, bank_code: Optional[str] = None) -> Optional[int]:
        """
        Get bank_id from bank name or code.
        
        Args:
            bank_name: Name of the bank
            bank_code: Optional bank code
            
        Returns:
            bank_id if found, None otherwise
        """
        # Check cache first
        if bank_name in self.bank_cache:
            return self.bank_cache[bank_name]
        
        # Query database
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT bank_id FROM banks WHERE bank_name = %s",
                    (bank_name,)
                )
                result = cursor.fetchone()
                if result:
                    bank_id = result[0]
                    self.bank_cache[bank_name] = bank_id
                    return bank_id
        
        return None
    
    def load_reviews_from_csv(
        self,
        csv_path: Path,
        bank_mapping: Dict[str, int],
        use_analyzed_data: bool = False,
        batch_size: int = 1000
    ) -> int:
        """
        Load reviews from CSV file into database.
        
        Args:
            csv_path: Path to CSV file
            bank_mapping: Dictionary mapping bank code to bank_id
            use_analyzed_data: If True, use analyzed_reviews.csv (includes sentiment)
            batch_size: Number of reviews to insert per batch
            
        Returns:
            Number of reviews inserted
        """
        logger.info(f"Loading reviews from {csv_path}")
        
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        # Read CSV
        df = pd.read_csv(csv_path)
        logger.info(f"Loaded {len(df)} reviews from CSV")
        
        # Prepare data
        if use_analyzed_data:
            # Use analyzed_reviews.csv which has sentiment data
            reviews_data = self._prepare_analyzed_reviews(df, bank_mapping)
        else:
            # Use processed_reviews.csv (no sentiment data)
            reviews_data = self._prepare_processed_reviews(df, bank_mapping)
        
        if not reviews_data:
            logger.warning("No valid reviews to insert")
            return 0
        
        # Insert in batches
        total_inserted = 0
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                for i in range(0, len(reviews_data), batch_size):
                    batch = reviews_data[i:i + batch_size]
                    
                    # Use execute_values for efficient batch insert
                    execute_values(
                        cursor,
                        """
                        INSERT INTO reviews (
                            bank_id, review_text, rating, review_date,
                            sentiment_label, sentiment_score, source
                        )
                        VALUES %s
                        """,
                        batch,
                        template=None,
                        page_size=batch_size
                    )
                    
                    inserted = len(batch)
                    total_inserted += inserted
                    logger.info(f"Inserted batch {i//batch_size + 1}: {inserted} reviews")
        
        logger.info(f"Total reviews inserted: {total_inserted}")
        return total_inserted
    
    def _prepare_processed_reviews(
        self,
        df: pd.DataFrame,
        bank_mapping: Dict[str, int]
    ) -> List[tuple]:
        """
        Prepare processed reviews data for insertion.
        
        Args:
            df: DataFrame with processed reviews
            bank_mapping: Dictionary mapping bank code to bank_id
            
        Returns:
            List of tuples ready for insertion
        """
        reviews_data = []
        
        for _, row in df.iterrows():
            bank_code = row.get('bank', '')
            bank_id = bank_mapping.get(bank_code)
            
            if not bank_id:
                logger.warning(f"Bank code '{bank_code}' not found in mapping, skipping review")
                continue
            
            review_text = str(row.get('review', ''))
            if not review_text or pd.isna(review_text):
                continue
            
            rating = row.get('rating')
            if pd.isna(rating):
                rating = None
            else:
                rating = float(rating)
            
            review_date = row.get('date')
            if pd.isna(review_date):
                review_date = None
            
            source = row.get('source', 'Google Play')
            if pd.isna(source):
                source = 'Google Play'
            
            # No sentiment data in processed reviews
            reviews_data.append((
                bank_id,
                review_text,
                rating,
                review_date,
                None,  # sentiment_label
                None,  # sentiment_score
                source
            ))
        
        return reviews_data
    
    def _prepare_analyzed_reviews(
        self,
        df: pd.DataFrame,
        bank_mapping: Dict[str, int]
    ) -> List[tuple]:
        """
        Prepare analyzed reviews data for insertion (includes sentiment).
        
        Args:
            df: DataFrame with analyzed reviews
            bank_mapping: Dictionary mapping bank code to bank_id
            
        Returns:
            List of tuples ready for insertion
        """
        reviews_data = []
        
        for _, row in df.iterrows():
            bank_code = row.get('bank', '')
            bank_id = bank_mapping.get(bank_code)
            
            if not bank_id:
                logger.warning(f"Bank code '{bank_code}' not found in mapping, skipping review")
                continue
            
            review_text = str(row.get('review', ''))
            if not review_text or pd.isna(review_text):
                continue
            
            rating = row.get('rating')
            if pd.isna(rating):
                rating = None
            else:
                rating = float(rating)
            
            review_date = row.get('date')
            if pd.isna(review_date):
                review_date = None
            
            source = row.get('source', 'Google Play')
            if pd.isna(source):
                source = 'Google Play'
            
            # Get sentiment data if available
            sentiment_label = row.get('sentiment_label')
            if pd.isna(sentiment_label):
                sentiment_label = None
            
            sentiment_score = row.get('sentiment_score')
            if pd.isna(sentiment_score):
                sentiment_score = None
            else:
                sentiment_score = float(sentiment_score)
            
            reviews_data.append((
                bank_id,
                review_text,
                rating,
                review_date,
                sentiment_label,
                sentiment_score,
                source
            ))
        
        return reviews_data
    
    def verify_data_integrity(self) -> Dict[str, Any]:
        """
        Verify data integrity with SQL queries.
        
        Returns:
            Dictionary with verification results
        """
        logger.info("Verifying data integrity...")
        
        results = {}
        
        # Count total reviews
        total_reviews = self.db.execute_query("SELECT COUNT(*) as count FROM reviews")
        results['total_reviews'] = total_reviews[0]['count'] if total_reviews else 0
        
        # Count reviews per bank
        reviews_per_bank = self.db.execute_query("""
            SELECT b.bank_name, COUNT(r.review_id) as review_count
            FROM banks b
            LEFT JOIN reviews r ON b.bank_id = r.bank_id
            GROUP BY b.bank_id, b.bank_name
            ORDER BY review_count DESC
        """)
        results['reviews_per_bank'] = [
            {'bank': row['bank_name'], 'count': row['review_count']}
            for row in reviews_per_bank
        ]
        
        # Average rating per bank
        avg_rating = self.db.execute_query("""
            SELECT b.bank_name, AVG(r.rating) as avg_rating, COUNT(r.review_id) as count
            FROM banks b
            LEFT JOIN reviews r ON b.bank_id = r.bank_id
            WHERE r.rating IS NOT NULL
            GROUP BY b.bank_id, b.bank_name
            ORDER BY avg_rating DESC
        """)
        results['avg_rating_per_bank'] = [
            {
                'bank': row['bank_name'],
                'avg_rating': float(row['avg_rating']) if row['avg_rating'] else None,
                'count': row['count']
            }
            for row in avg_rating
        ]
        
        # Sentiment distribution
        sentiment_dist = self.db.execute_query("""
            SELECT sentiment_label, COUNT(*) as count
            FROM reviews
            WHERE sentiment_label IS NOT NULL
            GROUP BY sentiment_label
            ORDER BY count DESC
        """)
        results['sentiment_distribution'] = [
            {'sentiment': row['sentiment_label'], 'count': row['count']}
            for row in sentiment_dist
        ]
        
        # Reviews with sentiment coverage
        sentiment_coverage = self.db.execute_query("""
            SELECT 
                COUNT(*) as total,
                COUNT(sentiment_label) as with_sentiment,
                ROUND(COUNT(sentiment_label)::numeric / COUNT(*) * 100, 2) as coverage_pct
            FROM reviews
        """)
        if sentiment_coverage:
            results['sentiment_coverage'] = {
                'total': sentiment_coverage[0]['total'],
                'with_sentiment': sentiment_coverage[0]['with_sentiment'],
                'coverage_percentage': float(sentiment_coverage[0]['coverage_pct']) if sentiment_coverage[0]['coverage_pct'] else 0
            }
        
        return results

