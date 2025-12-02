"""Pipeline for generating insights, visualizations, and recommendations"""
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Any
import json

from src.insights.insights_generator import InsightsGenerator
from src.insights.visualization import Visualizer
from src.insights.report_generator import ReportGenerator
from src.database.db_connection import DatabaseConnection
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class InsightsPipeline:
    """Pipeline for generating insights and visualizations"""
    
    def __init__(self, project_root: Optional[Path] = None, use_database: bool = True):
        """
        Initialize insights pipeline.
        
        Args:
            project_root: Project root directory
            use_database: If True, load from database; if False, load from CSV
        """
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.use_database = use_database
        
        # Setup directories
        self.results_dir = self.project_root / "data" / "results"
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.insights_generator = InsightsGenerator()
        self.visualizer = Visualizer(output_dir=self.project_root / "data" / "results" / "visualizations")
        self.report_generator = ReportGenerator(output_dir=self.results_dir)
    
    def load_data(self) -> pd.DataFrame:
        """Load data from database or CSV"""
        if self.use_database:
            db = DatabaseConnection()
            if db.test_connection():
                df = self.insights_generator.load_data_from_database(db)
                if len(df) > 0:
                    return df
                logger.warning("Database empty, trying CSV fallback...")
        
        # Fallback to CSV
        csv_path = self.project_root / "data" / "interim" / "analyzed_reviews.csv"
        if csv_path.exists():
            return self.insights_generator.load_data_from_csv(str(csv_path))
        
        raise FileNotFoundError("No data source available (database or CSV)")
    
    def generate_insights_for_all_banks(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate insights for all banks.
        
        Args:
            df: DataFrame with review data
            
        Returns:
            Dictionary with insights for each bank
        """
        logger.info("Generating insights for all banks...")
        
        # Determine bank column name
        bank_col = 'bank_name' if 'bank_name' in df.columns else 'bank'
        
        all_insights = {}
        
        for bank in df[bank_col].unique():
            logger.info(f"\n{'='*60}")
            logger.info(f"Analyzing {bank}")
            logger.info(f"{'='*60}")
            
            bank_df = df[df[bank_col] == bank].copy()
            
            # Generate insights
            drivers = self.insights_generator.identify_drivers(bank_df, bank)
            pain_points = self.insights_generator.identify_pain_points(bank_df, bank)
            recommendations = self.insights_generator.generate_recommendations(
                drivers, pain_points, bank
            )
            
            # Convert Decimal types to float for calculations
            bank_df_calc = bank_df.copy()
            if 'rating' in bank_df_calc.columns:
                bank_df_calc['rating'] = bank_df_calc['rating'].apply(lambda x: float(x) if x is not None else 0.0)
            
            total = len(bank_df_calc)
            avg_rating = bank_df_calc['rating'].mean() if 'rating' in bank_df_calc.columns else 0.0
            
            all_insights[bank] = {
                'drivers': drivers,
                'pain_points': pain_points,
                'recommendations': recommendations,
                'stats': {
                    'total_reviews': total,
                    'average_rating': float(avg_rating) if avg_rating is not None else 0.0,
                    'positive_pct': (bank_df_calc['sentiment_label'] == 'positive').sum() / total * 100 if 'sentiment_label' in bank_df_calc.columns and total > 0 else 0.0,
                    'negative_pct': (bank_df_calc['sentiment_label'] == 'negative').sum() / total * 100 if 'sentiment_label' in bank_df_calc.columns and total > 0 else 0.0
                }
            }
            
            # Log summary
            logger.info(f"\n{bank} Summary:")
            logger.info(f"  Total Reviews: {len(bank_df)}")
            logger.info(f"  Average Rating: {all_insights[bank]['stats']['average_rating']:.2f}")
            logger.info(f"  Drivers Identified: {len(drivers)}")
            logger.info(f"  Pain Points Identified: {len(pain_points)}")
            logger.info(f"  Recommendations: {len(recommendations)}")
        
        return all_insights
    
    def create_visualizations(self, df: pd.DataFrame, insights: Dict[str, Any]) -> Dict[str, Path]:
        """
        Create all visualizations.
        
        Args:
            df: DataFrame with review data
            insights: Dictionary with insights for each bank
            
        Returns:
            Dictionary with paths to saved visualizations
        """
        logger.info("\nCreating visualizations...")
        
        visualization_paths = {}
        
        # 1. Sentiment distribution
        try:
            path = self.visualizer.plot_sentiment_distribution(df)
            visualization_paths['sentiment_distribution'] = path
        except Exception as e:
            logger.error(f"Failed to create sentiment distribution: {e}")
        
        # 2. Rating distribution
        try:
            path = self.visualizer.plot_rating_distribution(df)
            visualization_paths['rating_distribution'] = path
        except Exception as e:
            logger.error(f"Failed to create rating distribution: {e}")
        
        # 3. Sentiment trends
        try:
            path = self.visualizer.plot_sentiment_trends(df)
            visualization_paths['sentiment_trends'] = path
        except Exception as e:
            logger.error(f"Failed to create sentiment trends: {e}")
        
        # 4. Bank comparison
        try:
            comparison_data = self.insights_generator.compare_banks(df)
            path = self.visualizer.plot_bank_comparison(comparison_data)
            visualization_paths['bank_comparison'] = path
        except Exception as e:
            logger.error(f"Failed to create bank comparison: {e}")
        
        # 5. Word clouds for each bank
        bank_col = 'bank_name' if 'bank_name' in df.columns else 'bank'
        for bank in df[bank_col].unique():
            try:
                # Positive reviews word cloud
                path = self.visualizer.create_wordcloud(df, bank_name=bank, sentiment='positive')
                visualization_paths[f'wordcloud_{bank}_positive'] = path
            except Exception as e:
                logger.error(f"Failed to create word cloud for {bank} positive: {e}")
            
            try:
                # Negative reviews word cloud
                path = self.visualizer.create_wordcloud(df, bank_name=bank, sentiment='negative')
                visualization_paths[f'wordcloud_{bank}_negative'] = path
            except Exception as e:
                logger.error(f"Failed to create word cloud for {bank} negative: {e}")
        
        # 6. Drivers and pain points for each bank
        for bank, bank_insights in insights.items():
            try:
                path = self.visualizer.plot_drivers_pain_points(
                    bank_insights['drivers'],
                    bank_insights['pain_points'],
                    bank
                )
                visualization_paths[f'drivers_pain_points_{bank}'] = path
            except Exception as e:
                logger.error(f"Failed to create drivers/pain points plot for {bank}: {e}")
        
        logger.info(f"\nCreated {len(visualization_paths)} visualizations")
        return visualization_paths
    
    def save_insights(self, insights: Dict[str, Any], filename: str = "insights.json") -> Path:
        """
        Save insights to JSON file.
        
        Args:
            insights: Dictionary with insights
            filename: Output filename
            
        Returns:
            Path to saved file
        """
        file_path = self.results_dir / filename
        
        # Convert to JSON-serializable format
        insights_json = {}
        for bank, data in insights.items():
            insights_json[bank] = {
                'drivers': data['drivers'],
                'pain_points': data['pain_points'],
                'recommendations': data['recommendations'],
                'stats': data['stats']
            }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(insights_json, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved insights to {file_path}")
        return file_path
    
    def run(self) -> Dict[str, Any]:
        """
        Run the complete insights pipeline.
        
        Returns:
            Dictionary with results
        """
        logger.info("=" * 60)
        logger.info("Starting Task 4: Insights and Recommendations Pipeline")
        logger.info("=" * 60)
        
        results = {
            'insights': {},
            'visualizations': {},
            'comparison': {}
        }
        
        try:
            # Step 1: Load data
            logger.info("\nStep 1: Loading data...")
            df = self.load_data()
            logger.info(f"✅ Loaded {len(df)} reviews")
            
            # Step 2: Generate insights
            logger.info("\nStep 2: Generating insights...")
            insights = self.generate_insights_for_all_banks(df)
            results['insights'] = insights
            
            # Step 3: Bank comparison
            logger.info("\nStep 3: Comparing banks...")
            comparison = self.insights_generator.compare_banks(df)
            results['comparison'] = comparison
            
            # Step 4: Create visualizations
            logger.info("\nStep 4: Creating visualizations...")
            visualizations = self.create_visualizations(df, insights)
            results['visualizations'] = visualizations
            
            # Step 5: Save insights
            logger.info("\nStep 5: Saving insights...")
            insights_path = self.save_insights(insights)
            results['insights_file'] = insights_path
            
            # Step 6: Generate final report
            logger.info("\nStep 6: Generating final report...")
            report_path = self.report_generator.generate_report(insights, comparison, visualizations)
            results['report_file'] = report_path
            
            logger.info("\n" + "=" * 60)
            logger.info("✅ Task 4 completed successfully!")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise
        
        return results

