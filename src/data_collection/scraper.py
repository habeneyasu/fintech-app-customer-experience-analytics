"""Google Play Store review scraper"""
from google_play_scraper import app, reviews, Sort
from typing import List, Dict, Optional
import pandas as pd
from tqdm import tqdm
import time

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class PlayStoreScraper:
    """Scraper for Google Play Store reviews with multi-language support"""
    
    def __init__(
        self, 
        min_reviews: int = 400, 
        max_reviews: int = 1000,
        batch_size: int = 100,
        retry_attempts: int = 5,
        retry_delay: int = 2,
        request_delay: int = 1,
        language_options: List[Dict] = None
    ):
        """
        Initialize the scraper.
        
        Args:
            min_reviews: Minimum number of reviews to collect per app
            max_reviews: Maximum number of reviews to collect per app
            batch_size: Number of reviews per API request (max 100)
            retry_attempts: Number of retry attempts for failed requests
            retry_delay: Seconds to wait between retries
            request_delay: Seconds to wait between successful requests
            language_options: List of dicts with 'lang' and 'country' keys
        """
        self.min_reviews = min_reviews
        self.max_reviews = max_reviews
        self.batch_size = min(batch_size, 100)  # API limit is 100
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.request_delay = request_delay
        
        # Default language options if not provided
        self.language_options = language_options or [
            {"lang": "am", "country": "ET"},  # Amharic / Ethiopia
            {"lang": "en", "country": "US"}   # English / US fallback
        ]
    
    def get_app_id(self, bank_config: Dict) -> Optional[str]:
        """
        Get app ID from bank configuration.
        
        Args:
            bank_config: Bank configuration dictionary with 'app_id' key
            
        Returns:
            App ID if found, None otherwise
        """
        return bank_config.get('app_id')
    
    def scrape_reviews(
        self, 
        app_id: str, 
        app_name: str, 
        bank_code: str,
        sort_by: str = "newest"
    ) -> pd.DataFrame:
        """
        Scrape reviews for a specific app with multi-language support.
        
        Args:
            app_id: Google Play Store app ID
            app_name: Name of the app
            bank_code: Bank code (CBE, BOA, DASHEN)
            sort_by: Sort order ("newest", "rating", "helpfulness")
            
        Returns:
            DataFrame containing reviews
        """
        logger.info(f"Scraping reviews for {app_name} (ID: {app_id})")
        
        # Map sort options
        sort_map = {
            "newest": Sort.NEWEST,
            "rating": Sort.RATING,
            "helpfulness": Sort.MOST_RELEVANT
        }
        sort_option = sort_map.get(sort_by, Sort.NEWEST)
        
        all_reviews = []
        
        # Loop through language-country options
        for lc in self.language_options:
            logger.info(f"Fetching reviews for lang={lc['lang']}, country={lc['country']}")
            fetched = []
            token = None
            attempts = 0
            
            while len(fetched) < self.max_reviews:
                try:
                    result, token = reviews(
                        app_id,
                        count=self.batch_size,
                        sort=sort_option,
                        continuation_token=token,
                        lang=lc["lang"],
                        country=lc["country"]
                    )
                    
                    if not result:
                        attempts += 1
                        if attempts >= self.retry_attempts:
                            logger.warning(
                                f"No more results for lang={lc['lang']}, "
                                f"country={lc['country']} after {attempts} attempts"
                            )
                            break
                        logger.warning(
                            f"No results for lang={lc['lang']}, "
                            f"country={lc['country']}... retrying ({attempts}/{self.retry_attempts})..."
                        )
                        time.sleep(self.retry_delay)
                        continue
                    
                    # Reset attempts after successful fetch
                    attempts = 0
                    fetched.extend(result)
                    
                    logger.info(f"  → Total fetched for {lc['lang']}: {len(fetched)}")
                    
                    # Check if we've reached the limit
                    if len(fetched) >= self.max_reviews:
                        fetched = fetched[:self.max_reviews]
                        break
                    
                    # If no continuation token, we've reached the end
                    if not token:
                        logger.info(f"End of reviews for lang={lc['lang']}, country={lc['country']}")
                        break
                    
                    # Rate limiting between requests
                    time.sleep(self.request_delay)
                    
                except Exception as e:
                    logger.error(f"Error fetching reviews for {app_name} ({lc['lang']}): {str(e)}")
                    attempts += 1
                    if attempts >= self.retry_attempts:
                        logger.warning(f"Max retry attempts reached for {lc['lang']}")
                        break
                    time.sleep(self.retry_delay)
            
            # Convert to cleaned format
            for review in fetched:
                all_reviews.append({
                    'review': review.get('content', ''),
                    'rating': review.get('score', 0),
                    'date': review.get('at', '').strftime('%Y-%m-%d') if review.get('at') else '',
                    'user_name': review.get('userName', ''),
                    'bank': bank_code,
                    'app_name': app_name,
                    'source': 'Google Play'
                })
        
        # Remove duplicates (same review might appear in different languages)
        seen = set()
        unique_reviews = []
        for review in all_reviews:
            # Use review text + bank + date as unique key
            key = (review['review'], review['bank'], review['date'])
            if key not in seen:
                seen.add(key)
                unique_reviews.append(review)
        
        review_count = len(unique_reviews)
        
        if review_count < self.min_reviews:
            logger.warning(
                f"Only collected {review_count} reviews for {app_name}, "
                f"minimum was {self.min_reviews}"
            )
        
        df = pd.DataFrame(unique_reviews)
        logger.info(f"Successfully scraped {len(df)} unique reviews for {app_name}")
        
        return df
    
    def scrape_all_banks(self, banks_config: List[Dict]) -> pd.DataFrame:
        """
        Scrape reviews for all banks.
        
        Args:
            banks_config: List of bank configuration dictionaries
            
        Returns:
            Combined DataFrame with all reviews
        """
        all_dfs = []
        
        for bank in tqdm(banks_config, desc="Scraping banks"):
            app_id = self.get_app_id(bank)
            if not app_id:
                logger.warning(f"App ID not found for {bank.get('app_name', 'Unknown')}, skipping")
                continue
            
            df = self.scrape_reviews(
                app_id=app_id,
                app_name=bank.get('app_name', 'Unknown'),
                bank_code=bank.get('code', 'UNKNOWN')
            )
            all_dfs.append(df)
        
        combined_df = pd.concat(all_dfs, ignore_index=True)
        logger.info(f"Total reviews collected: {len(combined_df)}")
        
        return combined_df

