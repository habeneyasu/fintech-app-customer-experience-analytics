"""
Visualization Module - Creates labeled plots for insights

This module generates 3-5 labeled visualizations:
1. Sentiment distribution by bank (labeled)
2. Rating distribution by bank (labeled)
3. Sentiment trends over time (labeled)
4. Bank comparison chart (labeled)
5. Drivers and pain points charts per bank (labeled)
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from pathlib import Path
from typing import Dict, List, Optional, Any

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10


class Visualizer:
    """Create labeled visualizations for insights and analysis"""
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize visualizer.
        
        Args:
            output_dir: Directory to save visualizations
        """
        self.output_dir = output_dir or Path("data/results/visualizations")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def plot_sentiment_distribution(self, df: pd.DataFrame, save_path: Optional[Path] = None) -> Path:
        """
        Create labeled sentiment distribution bar chart by bank.
        
        This visualization shows the count of positive, negative, and neutral reviews
        for each bank with clear labels and legend.
        
        Args:
            df: DataFrame with sentiment_label and bank_name columns
            save_path: Optional path to save the plot
            
        Returns:
            Path to saved plot
        """
        logger.info("Creating labeled sentiment distribution plot...")
        
        if 'sentiment_label' not in df.columns:
            logger.warning("sentiment_label column not found")
            return None
        
        # Count sentiment by bank
        bank_col = 'bank_name' if 'bank_name' in df.columns else 'bank'
        if bank_col not in df.columns:
            logger.warning(f"{bank_col} column not found")
            return None
        
        sentiment_by_bank = df.groupby([bank_col, 'sentiment_label']).size().unstack(fill_value=0)
        
        # Plot by bank with labels
        fig, ax = plt.subplots(figsize=(12, 6))
        sentiment_by_bank.plot(kind='bar', ax=ax, color=['#2ecc71', '#e74c3c', '#f39c12'], 
                               width=0.8)
        
        # Add labels
        ax.set_title('Sentiment Distribution by Bank', fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('Bank', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Reviews', fontsize=12, fontweight='bold')
        ax.legend(title='Sentiment', labels=['Positive', 'Negative', 'Neutral'], 
                  title_fontsize=11, fontsize=10)
        ax.tick_params(axis='x', rotation=45)
        plt.setp(ax.xaxis.get_majorticklabels(), ha='right')
        
        # Add value labels on bars
        for container in ax.containers:
            ax.bar_label(container, fmt='%d', label_type='edge', fontsize=8)
        
        plt.tight_layout()
        
        if save_path is None:
            save_path = self.output_dir / "sentiment_distribution_by_bank.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved labeled sentiment distribution plot to {save_path}")
        return save_path
    
    def plot_rating_distribution(self, df: pd.DataFrame, save_path: Optional[Path] = None) -> Path:
        """
        Create labeled rating distribution chart by bank.
        
        This visualization shows the distribution of star ratings (1-5) for each bank
        with clear labels, colors, and legend.
        
        Args:
            df: DataFrame with rating and bank_name columns
            save_path: Optional path to save the plot
            
        Returns:
            Path to saved plot
        """
        logger.info("Creating labeled rating distribution plot...")
        
        if 'rating' not in df.columns:
            logger.warning("rating column not found")
            return None
        
        bank_col = 'bank_name' if 'bank_name' in df.columns else 'bank'
        if bank_col not in df.columns:
            logger.warning(f"{bank_col} column not found")
            return None
        
        rating_by_bank = df.groupby([bank_col, 'rating']).size().unstack(fill_value=0)
        
        # Plot by bank with labels
        fig, ax = plt.subplots(figsize=(12, 6))
        colors = ['#e74c3c', '#e67e22', '#f39c12', '#3498db', '#2ecc71']
        rating_by_bank.plot(kind='bar', ax=ax, color=colors, width=0.8)
        
        # Add labels
        ax.set_title('Rating Distribution by Bank', fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('Bank', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Reviews', fontsize=12, fontweight='bold')
        ax.legend(title='Rating', labels=['1★', '2★', '3★', '4★', '5★'], ncol=5, 
                  title_fontsize=11, fontsize=10)
        ax.tick_params(axis='x', rotation=45)
        plt.setp(ax.xaxis.get_majorticklabels(), ha='right')
        
        # Add value labels on bars
        for container in ax.containers:
            ax.bar_label(container, fmt='%d', label_type='edge', fontsize=8)
        
        plt.tight_layout()
        
        if save_path is None:
            save_path = self.output_dir / "rating_distribution_by_bank.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved labeled rating distribution plot to {save_path}")
        return save_path
    
    def plot_sentiment_trends(self, df: pd.DataFrame, save_path: Optional[Path] = None) -> Path:
        """
        Create labeled sentiment trends over time.
        
        This visualization shows how sentiment (positive, negative, neutral) changes
        over time for each bank with clear labels, legend, and grid.
        
        Args:
            df: DataFrame with review_date, sentiment_label, and bank_name columns
            save_path: Optional path to save the plot
            
        Returns:
            Path to saved plot
        """
        logger.info("Creating labeled sentiment trends plot...")
        
        if 'review_date' not in df.columns or 'sentiment_label' not in df.columns:
            logger.warning("Required columns not found")
            return None
        
        # Convert date column
        df['review_date'] = pd.to_datetime(df['review_date'], errors='coerce')
        df = df.dropna(subset=['review_date'])
        
        # Group by month and sentiment
        df['year_month'] = df['review_date'].dt.to_period('M')
        
        bank_col = 'bank_name' if 'bank_name' in df.columns else 'bank'
        
        if bank_col in df.columns:
            # Plot trends for each bank
            banks = df[bank_col].unique()
            fig, axes = plt.subplots(len(banks), 1, 
                                    figsize=(14, 4 * len(banks)))
            if len(banks) == 1:
                axes = [axes]
            
            for idx, bank in enumerate(banks):
                bank_df = df[df[bank_col] == bank]
                sentiment_trends = bank_df.groupby(['year_month', 'sentiment_label']).size().unstack(fill_value=0)
                
                sentiment_trends.plot(kind='line', ax=axes[idx], 
                                      color=['#2ecc71', '#e74c3c', '#f39c12'],
                                      marker='o', linewidth=2, markersize=4)
                
                # Add labels
                axes[idx].set_title(f'Sentiment Trends Over Time - {bank}', 
                                   fontsize=12, fontweight='bold', pad=10)
                axes[idx].set_xlabel('Month', fontsize=10, fontweight='bold')
                axes[idx].set_ylabel('Number of Reviews', fontsize=10, fontweight='bold')
                axes[idx].legend(title='Sentiment', labels=['Positive', 'Negative', 'Neutral'],
                                title_fontsize=10, fontsize=9)
                axes[idx].grid(True, alpha=0.3)
        else:
            # Overall trends
            fig, ax = plt.subplots(figsize=(14, 6))
            sentiment_trends = df.groupby(['year_month', 'sentiment_label']).size().unstack(fill_value=0)
            sentiment_trends.plot(kind='line', ax=ax, 
                                 color=['#2ecc71', '#e74c3c', '#f39c12'],
                                 marker='o', linewidth=2, markersize=4)
            
            # Add labels
            ax.set_title('Sentiment Trends Over Time', fontsize=14, fontweight='bold', pad=15)
            ax.set_xlabel('Month', fontsize=12, fontweight='bold')
            ax.set_ylabel('Number of Reviews', fontsize=12, fontweight='bold')
            ax.legend(title='Sentiment', labels=['Positive', 'Negative', 'Neutral'],
                     title_fontsize=11, fontsize=10)
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path is None:
            save_path = self.output_dir / "sentiment_trends.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved labeled sentiment trends plot to {save_path}")
        return save_path
    
    def plot_bank_comparison(self, comparison_data: Dict[str, Any], 
                            save_path: Optional[Path] = None) -> Path:
        """
        Create labeled bank comparison chart.
        
        This visualization compares banks across key metrics (average rating and
        positive sentiment percentage) with clear labels, value annotations, and legend.
        
        Args:
            comparison_data: Dictionary with bank comparison metrics
            save_path: Optional path to save the plot
            
        Returns:
            Path to saved plot
        """
        logger.info("Creating labeled bank comparison plot...")
        
        banks = list(comparison_data.keys())
        avg_ratings = [comparison_data[bank]['average_rating'] for bank in banks]
        positive_pct = [comparison_data[bank]['positive_sentiment_pct'] for bank in banks]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Average ratings with labels
        bars1 = ax1.bar(banks, avg_ratings, color=['#3498db', '#2ecc71', '#e67e22'])
        ax1.set_title('Average Rating by Bank', fontsize=12, fontweight='bold', pad=10)
        ax1.set_ylabel('Average Rating', fontsize=10, fontweight='bold')
        ax1.set_ylim(0, 5)
        ax1.tick_params(axis='x', rotation=45)
        plt.setp(ax1.xaxis.get_majorticklabels(), ha='right')
        
        # Add value labels on bars
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}', ha='center', va='bottom', fontweight='bold')
        
        # Positive sentiment percentage with labels
        bars2 = ax2.bar(banks, positive_pct, color=['#2ecc71', '#27ae60', '#229954'])
        ax2.set_title('Positive Sentiment Percentage by Bank', fontsize=12, fontweight='bold', pad=10)
        ax2.set_ylabel('Percentage (%)', fontsize=10, fontweight='bold')
        ax2.set_ylim(0, 100)
        ax2.tick_params(axis='x', rotation=45)
        plt.setp(ax2.xaxis.get_majorticklabels(), ha='right')
        
        # Add value labels on bars
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        
        if save_path is None:
            save_path = self.output_dir / "bank_comparison.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved labeled bank comparison plot to {save_path}")
        return save_path
    
    def plot_drivers_pain_points(self, drivers: List[Dict], pain_points: List[Dict],
                                bank_name: str, save_path: Optional[Path] = None) -> Path:
        """
        Create labeled chart showing top drivers and pain points for a bank.
        
        This visualization shows the top 5 drivers (positive) and top 5 pain points
        (negative) with clear labels, values, and titles.
        
        Args:
            drivers: List of driver dictionaries
            pain_points: List of pain point dictionaries
            bank_name: Name of the bank
            save_path: Optional path to save the plot
            
        Returns:
            Path to saved plot
        """
        logger.info(f"Creating labeled drivers and pain points plot for {bank_name}...")
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Top drivers with labels
        if drivers:
            driver_types = [d['type'].replace('_', ' ').title() for d in drivers[:5]]
            driver_strengths = [d['strength'] * 100 for d in drivers[:5]]
            
            bars1 = ax1.barh(driver_types, driver_strengths, color='#2ecc71')
            ax1.set_title(f'Top Drivers - {bank_name}', fontsize=12, fontweight='bold', pad=10)
            ax1.set_xlabel('Strength Score (%)', fontsize=10, fontweight='bold')
            ax1.set_xlim(0, 100)
            
            # Add value labels
            for i, bar in enumerate(bars1):
                width = bar.get_width()
                ax1.text(width, bar.get_y() + bar.get_height()/2,
                        f'{width:.1f}%', ha='left', va='center', fontweight='bold')
        else:
            ax1.text(0.5, 0.5, 'No drivers identified', 
                    ha='center', va='center', transform=ax1.transAxes, fontsize=12)
            ax1.set_title(f'Top Drivers - {bank_name}', fontsize=12, fontweight='bold')
        
        # Top pain points with labels
        if pain_points:
            pain_types = [p['type'].replace('_', ' ').title() for p in pain_points[:5]]
            pain_severities = [p['severity'] * 100 for p in pain_points[:5]]
            
            bars2 = ax2.barh(pain_types, pain_severities, color='#e74c3c')
            ax2.set_title(f'Top Pain Points - {bank_name}', fontsize=12, fontweight='bold', pad=10)
            ax2.set_xlabel('Severity Score (%)', fontsize=10, fontweight='bold')
            ax2.set_xlim(0, 100)
            
            # Add value labels
            for i, bar in enumerate(bars2):
                width = bar.get_width()
                ax2.text(width, bar.get_y() + bar.get_height()/2,
                        f'{width:.1f}%', ha='left', va='center', fontweight='bold')
        else:
            ax2.text(0.5, 0.5, 'No pain points identified', 
                    ha='center', va='center', transform=ax2.transAxes, fontsize=12)
            ax2.set_title(f'Top Pain Points - {bank_name}', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        
        if save_path is None:
            save_path = self.output_dir / f"drivers_pain_points_{bank_name.replace(' ', '_')}.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved labeled drivers and pain points plot to {save_path}")
        return save_path

