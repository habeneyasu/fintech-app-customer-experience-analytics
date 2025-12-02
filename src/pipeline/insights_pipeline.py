"""
Insights Pipeline - Orchestrates Task 4 workflow

This pipeline:
1. Loads data (from database or CSV)
2. Computes per-bank drivers and pain points
3. Generates labeled visualizations (3-5 plots)
4. Creates recommendations tied to findings
5. Generates final report
"""
import pandas as pd
import json
from pathlib import Path
from typing import Dict, Any, Optional

from src.database.db_connection import DatabaseConnection
from src.insights.insights_generator import InsightsGenerator
from src.insights.visualization import Visualizer
from src.insights.report_generator import ReportGenerator
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class InsightsPipeline:
    """Pipeline for generating insights and recommendations"""
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize insights pipeline.
        
        Args:
            project_root: Project root directory
        """
        self.project_root = project_root or Path(__file__).parent.parent.parent
        
        # Initialize components
        self.insights_generator = InsightsGenerator()
        self.results_dir = self.project_root / "data" / "results"
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        self.visualizer = Visualizer(self.results_dir / "visualizations")
        self.report_generator = ReportGenerator(self.results_dir)
        
        # Data paths
        self.analyzed_data_path = self.project_root / "data" / "interim" / "analyzed_reviews.csv"
        self.processed_data_path = self.project_root / "data" / "processed" / "processed_reviews.csv"
    
    def load_data(self, use_database: bool = True) -> pd.DataFrame:
        """
        Load data from database or CSV file.
        
        Args:
            use_database: If True, load from database; otherwise from CSV
            
        Returns:
            DataFrame with review data
        """
        logger.info("Loading data...")
        
        if use_database:
            try:
                db = DatabaseConnection()
                query = """
                    SELECT r.review_text, r.rating, r.review_date, 
                           b.bank_name as bank, r.sentiment_label, r.sentiment_score
                    FROM reviews r
                    JOIN banks b ON r.bank_id = b.bank_id
                """
                df = pd.read_sql_query(query, db.get_connection())
                logger.info(f"Loaded {len(df)} reviews from database")
                return df
            except Exception as e:
                logger.warning(f"Database load failed: {e}. Falling back to CSV.")
        
        # Fallback to CSV
        if self.analyzed_data_path.exists():
            df = pd.read_csv(self.analyzed_data_path)
            logger.info(f"Loaded {len(df)} reviews from {self.analyzed_data_path}")
        elif self.processed_data_path.exists():
            df = pd.read_csv(self.processed_data_path)
            logger.info(f"Loaded {len(df)} reviews from {self.processed_data_path}")
        else:
            raise FileNotFoundError("No data file found. Run Task 1 and Task 2 first.")
        
        # Ensure bank column exists
        if 'bank_name' not in df.columns and 'bank' in df.columns:
            df['bank_name'] = df['bank']
        
        return df
    
    def generate_insights_for_all_banks(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """
        Generate insights (drivers, pain points, recommendations) for all banks.
        
        This explicitly computes per-bank drivers and pain points as required.
        
        Args:
            df: DataFrame with review data
            
        Returns:
            Dictionary with bank names as keys and insights as values
        """
        logger.info("Generating insights for all banks...")
        
        bank_col = 'bank_name' if 'bank_name' in df.columns else 'bank'
        banks = df[bank_col].unique()
        
        all_insights = {}
        
        for bank in banks:
            logger.info(f"\nProcessing {bank}...")
            bank_df = df[df[bank_col] == bank].copy()
            
            # Compute statistics
            stats = {
                'total_reviews': len(bank_df),
                'average_rating': bank_df['rating'].astype(float).mean(),
                'positive_sentiment_pct': (bank_df['sentiment_label'].str.lower() == 'positive').sum() / len(bank_df) * 100,
                'negative_sentiment_pct': (bank_df['sentiment_label'].str.lower() == 'negative').sum() / len(bank_df) * 100
            }
            
            # Compute drivers (positive aspects) - EXPLICIT PER-BANK COMPUTATION
            drivers = self.insights_generator.identify_drivers(bank_df, bank)
            
            # Compute pain points (negative aspects) - EXPLICIT PER-BANK COMPUTATION
            pain_points = self.insights_generator.identify_pain_points(bank_df, bank)
            
            # Generate recommendations tied to findings - EXPLICIT TIE TO PAIN POINTS
            recommendations = self.insights_generator.generate_recommendations(
                drivers, pain_points, bank
            )
            
            all_insights[bank] = {
                'statistics': stats,
                'drivers': drivers,
                'pain_points': pain_points,
                'recommendations': recommendations
            }
            
            logger.info(f"  - Drivers: {len(drivers)}, Pain Points: {len(pain_points)}, Recommendations: {len(recommendations)}")
        
        return all_insights
    
    def create_visualizations(self, df: pd.DataFrame, all_insights: Dict[str, Dict[str, Any]],
                            comparison_data: Dict[str, Any]) -> Dict[str, Path]:
        """
        Create all labeled visualizations (3-5 plots as required).
        
        Args:
            df: DataFrame with review data
            all_insights: Dictionary with bank insights
            comparison_data: Bank comparison metrics
            
        Returns:
            Dictionary with visualization names and paths
        """
        logger.info("Creating labeled visualizations...")
        
        visualizations = {}
        
        # 1. Sentiment distribution by bank (LABELED)
        vis_path = self.visualizer.plot_sentiment_distribution(df)
        if vis_path:
            visualizations['sentiment_distribution'] = vis_path
            logger.info(f"  ✓ Created: {vis_path.name}")
        
        # 2. Rating distribution by bank (LABELED)
        vis_path = self.visualizer.plot_rating_distribution(df)
        if vis_path:
            visualizations['rating_distribution'] = vis_path
            logger.info(f"  ✓ Created: {vis_path.name}")
        
        # 3. Sentiment trends over time (LABELED)
        vis_path = self.visualizer.plot_sentiment_trends(df)
        if vis_path:
            visualizations['sentiment_trends'] = vis_path
            logger.info(f"  ✓ Created: {vis_path.name}")
        
        # 4. Bank comparison chart (LABELED)
        vis_path = self.visualizer.plot_bank_comparison(comparison_data)
        if vis_path:
            visualizations['bank_comparison'] = vis_path
            logger.info(f"  ✓ Created: {vis_path.name}")
        
        # 5. Drivers and pain points charts per bank (LABELED)
        for bank_name, insights in all_insights.items():
            vis_path = self.visualizer.plot_drivers_pain_points(
                insights.get('drivers', []),
                insights.get('pain_points', []),
                bank_name
            )
            if vis_path:
                visualizations[f'drivers_pain_points_{bank_name}'] = vis_path
                logger.info(f"  ✓ Created: {vis_path.name}")
        
        logger.info(f"Created {len(visualizations)} labeled visualizations")
        return visualizations
    
    def run(self) -> Dict[str, Any]:
        """
        Run the complete Task 4 pipeline.
        
        Returns:
            Dictionary with pipeline results
        """
        logger.info("=" * 60)
        logger.info("Starting Task 4: Insights and Recommendations Pipeline")
        logger.info("=" * 60)
        
        try:
            # Step 1: Load data
            df = self.load_data(use_database=True)
            
            # Step 2: Generate insights for all banks (EXPLICIT PER-BANK COMPUTATION)
            all_insights = self.generate_insights_for_all_banks(df)
            
            # Step 3: Compare banks
            comparison_data = self.insights_generator.compare_banks(all_insights)
            
            # Step 4: Create labeled visualizations (3-5 plots)
            visualizations = self.create_visualizations(df, all_insights, comparison_data)
            
            # Step 5: Save insights to JSON
            insights_file = self.results_dir / "insights.json"
            with open(insights_file, 'w', encoding='utf-8') as f:
                json.dump(all_insights, f, indent=2, default=str)
            logger.info(f"Saved insights to {insights_file}")
            
            # Step 6: Generate final report (with recommendations tied to findings)
            report_path = self.report_generator.generate_report(all_insights, comparison_data)
            
            logger.info("=" * 60)
            logger.info("Task 4 completed successfully!")
            logger.info("=" * 60)
            
            return {
                'success': True,
                'insights_file': str(insights_file),
                'report_file': str(report_path),
                'visualizations': {k: str(v) for k, v in visualizations.items()},
                'banks_analyzed': len(all_insights),
                'total_visualizations': len(visualizations)
            }
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            raise

