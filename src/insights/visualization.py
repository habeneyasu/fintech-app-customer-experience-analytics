"""Visualization module for creating charts and plots"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from pathlib import Path
from typing import Dict, List, Optional, Any
import re
from collections import Counter

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10


class Visualizer:
    """Create visualizations for insights and analysis"""
    
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
        Create sentiment distribution bar chart.
        
        Args:
            df: DataFrame with sentiment_label column
            save_path: Optional path to save the plot
            
        Returns:
            Path to saved plot
        """
        logger.info("Creating sentiment distribution plot...")
        
        if 'sentiment_label' not in df.columns:
            logger.warning("sentiment_label column not found")
            return None
        
        # Count sentiment by bank
        if 'bank_name' in df.columns:
            sentiment_by_bank = df.groupby(['bank_name', 'sentiment_label']).size().unstack(fill_value=0)
        elif 'bank' in df.columns:
            sentiment_by_bank = df.groupby(['bank', 'sentiment_label']).size().unstack(fill_value=0)
        else:
            # Overall sentiment
            sentiment_counts = df['sentiment_label'].value_counts()
            fig, ax = plt.subplots(figsize=(10, 6))
            sentiment_counts.plot(kind='bar', ax=ax, color=['#2ecc71', '#e74c3c', '#f39c12'])
            ax.set_title('Overall Sentiment Distribution', fontsize=14, fontweight='bold')
            ax.set_xlabel('Sentiment', fontsize=12)
            ax.set_ylabel('Number of Reviews', fontsize=12)
            ax.tick_params(axis='x', rotation=0)
            plt.tight_layout()
            
            if save_path is None:
                save_path = self.output_dir / "sentiment_distribution.png"
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            return save_path
        
        # Plot by bank
        fig, ax = plt.subplots(figsize=(12, 6))
        sentiment_by_bank.plot(kind='bar', ax=ax, color=['#2ecc71', '#e74c3c', '#f39c12'], 
                               width=0.8)
        ax.set_title('Sentiment Distribution by Bank', fontsize=14, fontweight='bold')
        ax.set_xlabel('Bank', fontsize=12)
        ax.set_ylabel('Number of Reviews', fontsize=12)
        ax.legend(title='Sentiment', labels=['Positive', 'Negative', 'Neutral'])
        ax.tick_params(axis='x', rotation=45)
        plt.setp(ax.xaxis.get_majorticklabels(), ha='right')
        plt.tight_layout()
        
        if save_path is None:
            save_path = self.output_dir / "sentiment_distribution_by_bank.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved sentiment distribution plot to {save_path}")
        return save_path
    
    def plot_rating_distribution(self, df: pd.DataFrame, save_path: Optional[Path] = None) -> Path:
        """
        Create rating distribution chart.
        
        Args:
            df: DataFrame with rating column
            save_path: Optional path to save the plot
            
        Returns:
            Path to saved plot
        """
        logger.info("Creating rating distribution plot...")
        
        if 'rating' not in df.columns:
            logger.warning("rating column not found")
            return None
        
        # Group by bank if available
        if 'bank_name' in df.columns:
            rating_by_bank = df.groupby(['bank_name', 'rating']).size().unstack(fill_value=0)
        elif 'bank' in df.columns:
            rating_by_bank = df.groupby(['bank', 'rating']).size().unstack(fill_value=0)
        else:
            # Overall rating distribution
            rating_counts = df['rating'].value_counts().sort_index()
            fig, ax = plt.subplots(figsize=(10, 6))
            colors = ['#e74c3c', '#e67e22', '#f39c12', '#3498db', '#2ecc71']
            rating_counts.plot(kind='bar', ax=ax, color=[colors[int(r-1)] for r in rating_counts.index])
            ax.set_title('Overall Rating Distribution', fontsize=14, fontweight='bold')
            ax.set_xlabel('Rating (Stars)', fontsize=12)
            ax.set_ylabel('Number of Reviews', fontsize=12)
            ax.tick_params(axis='x', rotation=0)
            plt.tight_layout()
            
            if save_path is None:
                save_path = self.output_dir / "rating_distribution.png"
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            return save_path
        
        # Plot by bank
        fig, ax = plt.subplots(figsize=(12, 6))
        colors = ['#e74c3c', '#e67e22', '#f39c12', '#3498db', '#2ecc71']
        rating_by_bank.plot(kind='bar', ax=ax, color=colors, width=0.8)
        ax.set_title('Rating Distribution by Bank', fontsize=14, fontweight='bold')
        ax.set_xlabel('Bank', fontsize=12)
        ax.set_ylabel('Number of Reviews', fontsize=12)
        ax.legend(title='Rating', labels=['1★', '2★', '3★', '4★', '5★'], ncol=5)
        ax.tick_params(axis='x', rotation=45)
        plt.setp(ax.xaxis.get_majorticklabels(), ha='right')
        plt.tight_layout()
        
        if save_path is None:
            save_path = self.output_dir / "rating_distribution_by_bank.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved rating distribution plot to {save_path}")
        return save_path
    
    def plot_sentiment_trends(self, df: pd.DataFrame, save_path: Optional[Path] = None) -> Path:
        """
        Create sentiment trends over time.
        
        Args:
            df: DataFrame with review_date and sentiment_label columns
            save_path: Optional path to save the plot
            
        Returns:
            Path to saved plot
        """
        logger.info("Creating sentiment trends plot...")
        
        if 'review_date' not in df.columns or 'sentiment_label' not in df.columns:
            logger.warning("Required columns not found")
            return None
        
        # Convert date column
        df['review_date'] = pd.to_datetime(df['review_date'], errors='coerce')
        df = df.dropna(subset=['review_date'])
        
        # Group by month and sentiment
        df['year_month'] = df['review_date'].dt.to_period('M')
        
        if 'bank_name' in df.columns:
            bank_col = 'bank_name'
        elif 'bank' in df.columns:
            bank_col = 'bank'
        else:
            bank_col = None
        
        if bank_col:
            # Plot trends for each bank
            fig, axes = plt.subplots(len(df[bank_col].unique()), 1, 
                                    figsize=(14, 4 * len(df[bank_col].unique())))
            if len(df[bank_col].unique()) == 1:
                axes = [axes]
            
            for idx, bank in enumerate(df[bank_col].unique()):
                bank_df = df[df[bank_col] == bank]
                sentiment_trends = bank_df.groupby(['year_month', 'sentiment_label']).size().unstack(fill_value=0)
                
                sentiment_trends.plot(kind='line', ax=axes[idx], 
                                      color=['#2ecc71', '#e74c3c', '#f39c12'],
                                      marker='o', linewidth=2, markersize=4)
                axes[idx].set_title(f'Sentiment Trends - {bank}', fontsize=12, fontweight='bold')
                axes[idx].set_xlabel('Month', fontsize=10)
                axes[idx].set_ylabel('Number of Reviews', fontsize=10)
                axes[idx].legend(title='Sentiment', labels=['Positive', 'Negative', 'Neutral'])
                axes[idx].grid(True, alpha=0.3)
        else:
            # Overall trends
            fig, ax = plt.subplots(figsize=(14, 6))
            sentiment_trends = df.groupby(['year_month', 'sentiment_label']).size().unstack(fill_value=0)
            sentiment_trends.plot(kind='line', ax=ax, 
                                 color=['#2ecc71', '#e74c3c', '#f39c12'],
                                 marker='o', linewidth=2, markersize=4)
            ax.set_title('Sentiment Trends Over Time', fontsize=14, fontweight='bold')
            ax.set_xlabel('Month', fontsize=12)
            ax.set_ylabel('Number of Reviews', fontsize=12)
            ax.legend(title='Sentiment', labels=['Positive', 'Negative', 'Neutral'])
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path is None:
            save_path = self.output_dir / "sentiment_trends.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved sentiment trends plot to {save_path}")
        return save_path
    
    def plot_bank_comparison(self, comparison_data: Dict[str, Any], 
                            save_path: Optional[Path] = None) -> Path:
        """
        Create bank comparison chart.
        
        Args:
            comparison_data: Dictionary with bank comparison metrics
            save_path: Optional path to save the plot
            
        Returns:
            Path to saved plot
        """
        logger.info("Creating bank comparison plot...")
        
        banks = list(comparison_data.keys())
        avg_ratings = [comparison_data[bank]['average_rating'] for bank in banks]
        positive_pct = [comparison_data[bank]['positive_sentiment_pct'] for bank in banks]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Average ratings
        bars1 = ax1.bar(banks, avg_ratings, color=['#3498db', '#2ecc71', '#e67e22'])
        ax1.set_title('Average Rating by Bank', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Average Rating', fontsize=10)
        ax1.set_ylim(0, 5)
        ax1.tick_params(axis='x', rotation=45)
        plt.setp(ax1.xaxis.get_majorticklabels(), ha='right')
        
        # Add value labels on bars
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}', ha='center', va='bottom')
        
        # Positive sentiment percentage
        bars2 = ax2.bar(banks, positive_pct, color=['#2ecc71', '#27ae60', '#229954'])
        ax2.set_title('Positive Sentiment Percentage', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Percentage (%)', fontsize=10)
        ax2.set_ylim(0, 100)
        ax2.tick_params(axis='x', rotation=45)
        plt.setp(ax2.xaxis.get_majorticklabels(), ha='right')
        
        # Add value labels on bars
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%', ha='center', va='bottom')
        
        plt.tight_layout()
        
        if save_path is None:
            save_path = self.output_dir / "bank_comparison.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved bank comparison plot to {save_path}")
        return save_path
    
    def create_wordcloud(self, df: pd.DataFrame, bank_name: Optional[str] = None,
                        sentiment: Optional[str] = None, save_path: Optional[Path] = None) -> Path:
        """
        Create word cloud from review text.
        
        Args:
            df: DataFrame with review_text column
            bank_name: Optional bank name to filter
            sentiment: Optional sentiment to filter ('positive', 'negative', 'neutral')
            save_path: Optional path to save the word cloud
            
        Returns:
            Path to saved word cloud
        """
        logger.info(f"Creating word cloud for {bank_name or 'all'} ({sentiment or 'all'} reviews)...")
        
        # Filter data
        filtered_df = df.copy()
        
        if bank_name:
            if 'bank_name' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['bank_name'] == bank_name]
            elif 'bank' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['bank'] == bank_name]
        
        if sentiment and 'sentiment_label' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['sentiment_label'] == sentiment]
        
        # Combine all review text
        text_column = 'review_text' if 'review_text' in filtered_df.columns else 'review'
        all_text = ' '.join(filtered_df[text_column].fillna('').astype(str).tolist())
        
        if not all_text.strip():
            logger.warning("No text available for word cloud")
            return None
        
        # Create word cloud
        wordcloud = WordCloud(
            width=1200,
            height=600,
            background_color='white',
            max_words=100,
            colormap='viridis',
            relative_scaling=0.5,
            random_state=42
        ).generate(all_text)
        
        # Plot
        fig, ax = plt.subplots(figsize=(14, 7))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        
        title = f"Word Cloud"
        if bank_name:
            title += f" - {bank_name}"
        if sentiment:
            title += f" ({sentiment.capitalize()} Reviews)"
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        if save_path is None:
            filename = f"wordcloud_{bank_name or 'all'}_{sentiment or 'all'}.png"
            save_path = self.output_dir / filename
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved word cloud to {save_path}")
        return save_path
    
    def plot_drivers_pain_points(self, drivers: List[Dict], pain_points: List[Dict],
                                bank_name: str, save_path: Optional[Path] = None) -> Path:
        """
        Create chart showing top drivers and pain points.
        
        Args:
            drivers: List of driver dictionaries
            pain_points: List of pain point dictionaries
            bank_name: Name of the bank
            save_path: Optional path to save the plot
            
        Returns:
            Path to saved plot
        """
        logger.info(f"Creating drivers and pain points plot for {bank_name}...")
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Top drivers
        if drivers:
            driver_types = [d['type'].replace('_', ' ').title() for d in drivers[:5]]
            driver_strengths = [d['strength'] * 100 for d in drivers[:5]]
            
            bars1 = ax1.barh(driver_types, driver_strengths, color='#2ecc71')
            ax1.set_title(f'Top Drivers - {bank_name}', fontsize=12, fontweight='bold')
            ax1.set_xlabel('Strength Score (%)', fontsize=10)
            ax1.set_xlim(0, 100)
            
            # Add value labels
            for i, bar in enumerate(bars1):
                width = bar.get_width()
                ax1.text(width, bar.get_y() + bar.get_height()/2,
                        f'{width:.1f}%', ha='left', va='center')
        else:
            ax1.text(0.5, 0.5, 'No drivers identified', 
                    ha='center', va='center', transform=ax1.transAxes)
            ax1.set_title(f'Top Drivers - {bank_name}', fontsize=12, fontweight='bold')
        
        # Top pain points
        if pain_points:
            pain_types = [p['type'].replace('_', ' ').title() for p in pain_points[:5]]
            pain_severities = [p['severity'] * 100 for p in pain_points[:5]]
            
            bars2 = ax2.barh(pain_types, pain_severities, color='#e74c3c')
            ax2.set_title(f'Top Pain Points - {bank_name}', fontsize=12, fontweight='bold')
            ax2.set_xlabel('Severity Score (%)', fontsize=10)
            ax2.set_xlim(0, 100)
            
            # Add value labels
            for i, bar in enumerate(bars2):
                width = bar.get_width()
                ax2.text(width, bar.get_y() + bar.get_height()/2,
                        f'{width:.1f}%', ha='left', va='center')
        else:
            ax2.text(0.5, 0.5, 'No pain points identified', 
                    ha='center', va='center', transform=ax2.transAxes)
            ax2.set_title(f'Top Pain Points - {bank_name}', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        
        if save_path is None:
            save_path = self.output_dir / f"drivers_pain_points_{bank_name.replace(' ', '_')}.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved drivers and pain points plot to {save_path}")
        return save_path

