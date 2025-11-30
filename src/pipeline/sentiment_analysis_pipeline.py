"""Pipeline for sentiment and thematic analysis"""
import pandas as pd
from pathlib import Path
from typing import Dict, Optional

from src.analysis.sentiment_analyzer import SentimentAnalyzer
from src.analysis.text_preprocessor import TextPreprocessor
from src.analysis.thematic_analyzer import ThematicAnalyzer
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class SentimentAnalysisPipeline:
    """Pipeline for sentiment and thematic analysis"""
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize the analysis pipeline.
        
        Args:
            project_root: Project root directory
        """
        self.project_root = project_root or Path(__file__).parent.parent.parent
        
        # Initialize components
        logger.info("Initializing analysis components...")
        self.text_preprocessor = TextPreprocessor()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.thematic_analyzer = ThematicAnalyzer()
        
        # Setup directories
        self._setup_directories()
    
    def _setup_directories(self) -> None:
        """Create necessary directories for output."""
        self.interim_dir = self.project_root / "data" / "interim"
        self.interim_dir.mkdir(parents=True, exist_ok=True)
        
        self.results_dir = self.project_root / "data" / "results"
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def load_processed_data(self, file_path: Optional[Path] = None) -> pd.DataFrame:
        """
        Load processed review data.
        
        Args:
            file_path: Path to processed data file
            
        Returns:
            DataFrame with reviews
        """
        if file_path is None:
            file_path = self.project_root / "data" / "processed" / "processed_reviews.csv"
        
        if not file_path.exists():
            raise FileNotFoundError(f"Processed data file not found: {file_path}")
        
        logger.info(f"Loading processed data from {file_path}")
        df = pd.read_csv(file_path)
        logger.info(f"Loaded {len(df)} reviews")
        
        # Add review_id if it doesn't exist
        if 'review_id' not in df.columns:
            df['review_id'] = range(1, len(df) + 1)
        
        return df
    
    def preprocess_texts(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess review texts.
        
        Args:
            df: DataFrame with reviews
            
        Returns:
            DataFrame with preprocessed text
        """
        logger.info("Preprocessing review texts...")
        df_processed = self.text_preprocessor.preprocess_dataframe(
            df, 
            text_column="review",
            output_column="processed_text"
        )
        return df_processed
    
    def analyze_sentiment(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze sentiment for all reviews.
        
        Args:
            df: DataFrame with reviews
            
        Returns:
            DataFrame with sentiment analysis
        """
        logger.info("Analyzing sentiment...")
        df_sentiment = self.sentiment_analyzer.analyze_dataframe(df, text_column="review")
        return df_sentiment
    
    def analyze_themes(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze themes for all reviews.
        
        Args:
            df: DataFrame with reviews and processed text
            
        Returns:
            DataFrame with theme assignments
        """
        logger.info("Analyzing themes...")
        df_themes = self.thematic_analyzer.analyze_all_banks(df, text_column="processed_text")
        return df_themes
    
    def create_aggregations(self, df: pd.DataFrame) -> Dict:
        """
        Create aggregated statistics.
        
        Args:
            df: DataFrame with analysis results
            
        Returns:
            Dictionary with aggregated statistics
        """
        logger.info("Creating aggregations...")
        
        # Sentiment by bank and rating
        sentiment_agg = self.sentiment_analyzer.aggregate_by_bank_and_rating(df)
        
        # Theme distribution by bank
        theme_dist = []
        for bank in df['bank'].unique():
            bank_df = df[df['bank'] == bank]
            theme_counts = {}
            for themes in bank_df['identified_themes']:
                if isinstance(themes, list):
                    for theme in themes:
                        theme_counts[theme] = theme_counts.get(theme, 0) + 1
            theme_dist.append({
                'bank': bank,
                'themes': theme_counts
            })
        
        return {
            'sentiment_by_bank_rating': sentiment_agg,
            'theme_distribution': theme_dist
        }
    
    def save_results(self, df: pd.DataFrame, filename: str = "analyzed_reviews.csv") -> Path:
        """
        Save analysis results.
        
        Args:
            df: DataFrame with analysis results
            filename: Output filename
            
        Returns:
            Path to saved file
        """
        # Convert theme lists to strings for CSV
        df_save = df.copy()
        if 'identified_themes' in df_save.columns:
            df_save['identified_themes'] = df_save['identified_themes'].apply(
                lambda x: ', '.join(x) if isinstance(x, list) else str(x)
            )
        
        file_path = self.interim_dir / filename
        df_save.to_csv(file_path, index=False)
        logger.info(f"Saved analysis results to {file_path} ({len(df_save)} reviews)")
        
        return file_path
    
    def save_aggregations(self, aggregations: Dict) -> Dict[str, Path]:
        """
        Save aggregated statistics.
        
        Args:
            aggregations: Dictionary with aggregated statistics
            
        Returns:
            Dictionary with paths to saved files
        """
        saved_files = {}
        
        # Save sentiment aggregations
        if 'sentiment_by_bank_rating' in aggregations:
            file_path = self.results_dir / "sentiment_by_bank_rating.csv"
            aggregations['sentiment_by_bank_rating'].to_csv(file_path, index=False)
            saved_files['sentiment_aggregation'] = file_path
            logger.info(f"Saved sentiment aggregations to {file_path}")
        
        return saved_files
    
    def run(self, input_file: Optional[Path] = None) -> Dict:
        """
        Run the complete analysis pipeline.
        
        Args:
            input_file: Optional path to input file
            
        Returns:
            Dictionary with pipeline results
        """
        logger.info("="*60)
        logger.info("Starting Sentiment and Thematic Analysis Pipeline")
        logger.info("="*60)
        
        # Step 1: Load data
        df = self.load_processed_data(input_file)
        
        # Step 2: Preprocess texts
        df = self.preprocess_texts(df)
        
        # Step 3: Analyze sentiment
        df = self.analyze_sentiment(df)
        
        # Step 4: Analyze themes
        df = self.analyze_themes(df)
        
        # Step 5: Create aggregations
        aggregations = self.create_aggregations(df)
        
        # Step 6: Save results
        results_file = self.save_results(df)
        aggregation_files = self.save_aggregations(aggregations)
        
        # Calculate metrics
        total_reviews = len(df)
        sentiment_coverage = (df['sentiment_label'].notna().sum() / total_reviews) * 100
        
        # Count themes per bank
        themes_per_bank = {}
        for bank in df['bank'].unique():
            bank_df = df[df['bank'] == bank]
            unique_themes = set()
            for themes in bank_df['identified_themes']:
                if isinstance(themes, list):
                    unique_themes.update(themes)
            themes_per_bank[bank] = len(unique_themes)
        
        logger.info("="*60)
        logger.info("PIPELINE SUMMARY")
        logger.info("="*60)
        logger.info(f"Total reviews analyzed: {total_reviews}")
        logger.info(f"Sentiment coverage: {sentiment_coverage:.2f}%")
        logger.info(f"Themes per bank:")
        for bank, count in themes_per_bank.items():
            logger.info(f"  {bank}: {count} themes")
        logger.info("="*60)
        
        return {
            'total_reviews': total_reviews,
            'sentiment_coverage': sentiment_coverage,
            'themes_per_bank': themes_per_bank,
            'results_file': results_file,
            'aggregation_files': aggregation_files
        }

