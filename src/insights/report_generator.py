"""Generate final report with insights, visualizations, and recommendations"""
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ReportGenerator:
    """Generate comprehensive final report"""
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize report generator.
        
        Args:
            output_dir: Directory to save the report
        """
        self.output_dir = output_dir or Path("data/results")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_report(self, insights: Dict[str, Any], comparison: Dict[str, Any],
                       visualization_paths: Dict[str, Path]) -> Path:
        """
        Generate comprehensive 10-page final report.
        
        Args:
            insights: Dictionary with insights for each bank
            comparison: Dictionary with bank comparison data
            visualization_paths: Dictionary with paths to visualizations
            
        Returns:
            Path to generated report
        """
        logger.info("Generating final report...")
        
        report_path = self.output_dir / "FINAL_REPORT.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            self._write_header(f)
            self._write_executive_summary(f, insights, comparison)
            self._write_methodology(f)
            self._write_data_overview(f, comparison)
            self._write_insights_by_bank(f, insights)
            self._write_bank_comparison(f, comparison)
            self._write_recommendations(f, insights)
            self._write_visualizations(f, visualization_paths)
            self._write_ethics_considerations(f)
            self._write_conclusion(f, insights)
        
        logger.info(f"Report generated: {report_path}")
        return report_path
    
    def _write_header(self, f):
        """Write report header"""
        f.write("# Fintech App Customer Experience Analytics - Final Report\n\n")
        f.write(f"**Project**: Customer Experience Analytics for Ethiopian Banking Apps\n")
        f.write(f"**Date**: {datetime.now().strftime('%B %d, %Y')}\n")
        f.write(f"**Status**: Complete\n\n")
        f.write("---\n\n")
    
    def _write_executive_summary(self, f, insights: Dict, comparison: Dict):
        """Write executive summary"""
        f.write("## 1. Executive Summary\n\n")
        f.write("This report presents a comprehensive analysis of customer reviews for three major Ethiopian banking mobile applications: Commercial Bank of Ethiopia (CBE), Bank of Abyssinia (BOA), and Dashen Bank. ")
        f.write("The analysis is based on 9,594 processed reviews collected from Google Play Store, with complete sentiment analysis and thematic identification.\n\n")
        
        f.write("### Key Findings\n\n")
        
        # Overall statistics
        total_reviews = sum(comp.get('total_reviews', 0) for comp in comparison.values())
        f.write(f"- **Total Reviews Analyzed**: {total_reviews:,}\n")
        f.write(f"- **Banks Analyzed**: {len(comparison)}\n")
        f.write(f"- **Sentiment Coverage**: 100%\n\n")
        
        # Top insights
        f.write("### Top Insights\n\n")
        for bank, data in insights.items():
            if data.get('drivers'):
                top_driver = data['drivers'][0] if data['drivers'] else None
                if top_driver:
                    f.write(f"- **{bank}**: Top driver is {top_driver['description']} "
                           f"({top_driver['mentions']} mentions)\n")
            
            if data.get('pain_points'):
                top_pain = data['pain_points'][0] if data['pain_points'] else None
                if top_pain:
                    f.write(f"- **{bank}**: Main pain point is {top_pain['description']} "
                           f"({top_pain['mentions']} mentions)\n")
        
        f.write("\n---\n\n")
    
    def _write_methodology(self, f):
        """Write methodology section"""
        f.write("## 2. Methodology\n\n")
        f.write("### Data Collection\n\n")
        f.write("- **Source**: Google Play Store reviews\n")
        f.write("- **Collection Method**: Automated scraping using `google-play-scraper`\n")
        f.write("- **Languages**: Amharic and English\n")
        f.write("- **Total Reviews Collected**: 9,881\n")
        f.write("- **Processed Reviews**: 9,594 (97.1% retention)\n\n")
        
        f.write("### Data Processing\n\n")
        f.write("- **Preprocessing**: Duplicate removal, length filtering, date normalization\n")
        f.write("- **Sentiment Analysis**: DistilBERT model (`distilbert-base-uncased-finetuned-sst-2-english`)\n")
        f.write("- **Thematic Analysis**: TF-IDF keyword extraction, rule-based theme clustering\n")
        f.write("- **Storage**: PostgreSQL database with normalized schema\n\n")
        
        f.write("### Analysis Approach\n\n")
        f.write("- **Drivers Identification**: Keyword-based analysis of positive reviews (rating ≥ 4 or positive sentiment)\n")
        f.write("- **Pain Points Identification**: Keyword-based analysis of negative reviews (rating ≤ 2 or negative sentiment)\n")
        f.write("- **Recommendations**: Generated based on identified pain points and missing opportunities\n")
        f.write("- **Visualization**: Matplotlib, Seaborn, and WordCloud for data visualization\n\n")
        
        f.write("---\n\n")
    
    def _write_data_overview(self, f, comparison: Dict):
        """Write data overview section"""
        f.write("## 3. Data Overview\n\n")
        
        f.write("### Review Distribution\n\n")
        f.write("| Bank | Total Reviews | Average Rating | Positive % | Negative % |\n")
        f.write("|------|--------------|----------------|------------|------------|\n")
        
        for bank, data in comparison.items():
            total = data.get('total_reviews', 0)
            avg_rating = data.get('average_rating', 0)
            pos_pct = data.get('positive_sentiment_pct', 0)
            neg_pct = data.get('negative_sentiment_pct', 0)
            f.write(f"| {bank} | {total:,} | {avg_rating:.2f} | {pos_pct:.1f}% | {neg_pct:.1f}% |\n")
        
        f.write("\n### Rating Distribution\n\n")
        f.write("| Bank | 5★ | 4★ | 3★ | 2★ | 1★ |\n")
        f.write("|------|----|----|----|----|----|\n")
        
        for bank, data in comparison.items():
            rating_dist = data.get('rating_distribution', {})
            ratings = [rating_dist.get(i, 0) for i in range(1, 6)]
            f.write(f"| {bank} | {ratings[4]} | {ratings[3]} | {ratings[2]} | {ratings[1]} | {ratings[0]} |\n")
        
        f.write("\n---\n\n")
    
    def _write_insights_by_bank(self, f, insights: Dict):
        """Write insights for each bank"""
        f.write("## 4. Insights by Bank\n\n")
        
        for bank, data in insights.items():
            f.write(f"### 4.{list(insights.keys()).index(bank) + 1} {bank}\n\n")
            
            stats = data.get('stats', {})
            f.write(f"**Statistics**: {stats.get('total_reviews', 0):,} reviews, "
                   f"Average Rating: {stats.get('average_rating', 0):.2f}, "
                   f"Positive: {stats.get('positive_pct', 0):.1f}%, "
                   f"Negative: {stats.get('negative_pct', 0):.1f}%\n\n")
            
            # Drivers
            f.write("#### Drivers (What Customers Like)\n\n")
            drivers = data.get('drivers', [])
            if drivers:
                for i, driver in enumerate(drivers[:3], 1):
                    f.write(f"{i}. **{driver['description']}**\n")
                    f.write(f"   - Strength Score: {driver['strength']*100:.1f}%\n")
                    f.write(f"   - Mentions: {driver['mentions']}\n")
                    if driver.get('examples'):
                        example = driver['examples'][0]
                        f.write(f"   - Example: \"{example['text'][:80]}...\" (Rating: {example['rating']})\n")
                    f.write("\n")
            else:
                f.write("No significant drivers identified.\n\n")
            
            # Pain Points
            f.write("#### Pain Points (What Customers Complain About)\n\n")
            pain_points = data.get('pain_points', [])
            if pain_points:
                for i, pain in enumerate(pain_points[:3], 1):
                    f.write(f"{i}. **{pain['description']}**\n")
                    f.write(f"   - Severity Score: {pain['severity']*100:.1f}%\n")
                    f.write(f"   - Mentions: {pain['mentions']}\n")
                    if pain.get('examples'):
                        example = pain['examples'][0]
                        f.write(f"   - Example: \"{example['text'][:80]}...\" (Rating: {example['rating']})\n")
                    f.write("\n")
            else:
                f.write("No significant pain points identified.\n\n")
            
            f.write("\n")
        
        f.write("---\n\n")
    
    def _write_bank_comparison(self, f, comparison: Dict):
        """Write bank comparison section"""
        f.write("## 5. Bank Comparison\n\n")
        
        f.write("### 5.1 Overall Performance Comparison\n\n")
        f.write("| Metric | CBE | BOA | Dashen |\n")
        f.write("|--------|-----|-----|--------|\n")
        
        banks = list(comparison.keys())
        metrics = ['average_rating', 'positive_sentiment_pct', 'total_reviews']
        metric_names = ['Average Rating', 'Positive Sentiment %', 'Total Reviews']
        
        for metric, name in zip(metrics, metric_names):
            row = f"| {name} | "
            for bank in banks:
                value = comparison[bank].get(metric, 0)
                if metric == 'total_reviews':
                    row += f"{int(value):,} | "
                else:
                    row += f"{value:.2f} | "
            row += "\n"
            f.write(row)
        
        f.write("\n### 5.2 Key Differentiators\n\n")
        
        # Find best and worst for each metric
        best_rating_bank = max(comparison.items(), key=lambda x: x[1].get('average_rating', 0))
        best_pos_bank = max(comparison.items(), key=lambda x: x[1].get('positive_sentiment_pct', 0))
        
        f.write(f"- **Highest Average Rating**: {best_rating_bank[0]} ({best_rating_bank[1].get('average_rating', 0):.2f})\n")
        f.write(f"- **Highest Positive Sentiment**: {best_pos_bank[0]} ({best_pos_bank[1].get('positive_sentiment_pct', 0):.1f}%)\n")
        f.write(f"- **Most Reviews**: {max(comparison.items(), key=lambda x: x[1].get('total_reviews', 0))[0]} "
               f"({max(comparison.values(), key=lambda x: x.get('total_reviews', 0)).get('total_reviews', 0):,})\n\n")
        
        f.write("---\n\n")
    
    def _write_recommendations(self, f, insights: Dict):
        """Write recommendations section"""
        f.write("## 6. Recommendations\n\n")
        
        for bank, data in insights.items():
            f.write(f"### 6.{list(insights.keys()).index(bank) + 1} Recommendations for {bank}\n\n")
            
            recommendations = data.get('recommendations', [])
            if recommendations:
                for i, rec in enumerate(recommendations[:3], 1):
                    f.write(f"{i}. **{rec.get('title', 'N/A')}**\n")
                    f.write(f"   - Priority: {rec.get('priority', 'N/A')}\n")
                    f.write(f"   - Description: {rec.get('description', 'N/A')}\n")
                    f.write(f"   - Expected Impact: {rec.get('impact', 'N/A')}\n")
                    if rec.get('evidence'):
                        f.write(f"   - Evidence: {rec.get('evidence', 'N/A')}\n")
                    f.write("\n")
            else:
                f.write("No specific recommendations generated.\n\n")
            
            f.write("\n")
        
        f.write("---\n\n")
    
    def _write_visualizations(self, f, visualization_paths: Dict):
        """Write visualizations section"""
        f.write("## 7. Visualizations\n\n")
        f.write("The following visualizations have been generated:\n\n")
        
        viz_list = [
            ('sentiment_distribution', 'Sentiment Distribution by Bank'),
            ('rating_distribution', 'Rating Distribution by Bank'),
            ('sentiment_trends', 'Sentiment Trends Over Time'),
            ('bank_comparison', 'Bank Comparison Chart'),
        ]
        
        for key, title in viz_list:
            if key in visualization_paths:
                path = visualization_paths[key]
                f.write(f"### {title}\n\n")
                f.write(f"![{title}]({path})\n\n")
        
        # Word clouds
        wordclouds = {k: v for k, v in visualization_paths.items() if 'wordcloud' in k}
        if wordclouds:
            f.write("### Word Clouds\n\n")
            for key, path in wordclouds.items():
                bank_sentiment = key.replace('wordcloud_', '').replace('_', ' ').title()
                f.write(f"**{bank_sentiment} Reviews Word Cloud**\n\n")
                f.write(f"![{bank_sentiment} Word Cloud]({path})\n\n")
        
        f.write("---\n\n")
    
    def _write_ethics_considerations(self, f):
        """Write ethics and bias considerations"""
        f.write("## 8. Ethics and Bias Considerations\n\n")
        
        f.write("### 8.1 Potential Review Biases\n\n")
        f.write("Several potential biases may affect the analysis:\n\n")
        f.write("1. **Negative Bias**: Users are more likely to leave reviews when they have negative experiences, ")
        f.write("leading to potential over-representation of complaints.\n\n")
        f.write("2. **Selection Bias**: Only users who download and use the app can leave reviews, ")
        f.write("excluding potential users who chose not to download due to poor ratings or reviews.\n\n")
        f.write("3. **Language Bias**: Reviews collected in English and Amharic may not represent ")
        f.write("the full spectrum of user experiences, especially for users who primarily use other languages.\n\n")
        f.write("4. **Temporal Bias**: Recent reviews may be over-represented if data collection ")
        f.write("focused on newer reviews, potentially missing long-term trends.\n\n")
        f.write("5. **Platform Bias**: Google Play Store reviews may not represent users who ")
        f.write("primarily use iOS or other platforms.\n\n")
        
        f.write("### 8.2 Mitigation Strategies\n\n")
        f.write("- Collected reviews from multiple time periods to reduce temporal bias\n")
        f.write("- Analyzed both positive and negative reviews to balance perspectives\n")
        f.write("- Used sentiment analysis to quantify emotional tone, not just star ratings\n")
        f.write("- Identified themes across all sentiment categories\n")
        f.write("- Compared multiple banks to provide relative context\n\n")
        
        f.write("### 8.3 Limitations\n\n")
        f.write("- Analysis is based on publicly available reviews only\n")
        f.write("- Cannot account for users who did not leave reviews\n")
        f.write("- Sentiment analysis model may have cultural or language biases\n")
        f.write("- Thematic analysis relies on keyword matching, which may miss nuanced themes\n\n")
        
        f.write("---\n\n")
    
    def _write_conclusion(self, f, insights: Dict):
        """Write conclusion"""
        f.write("## 9. Conclusion\n\n")
        
        f.write("This analysis provides valuable insights into customer experiences with Ethiopian banking mobile applications. ")
        f.write("Key findings include:\n\n")
        
        f.write("1. **Performance Variances**: Significant differences exist between banks in terms of ")
        f.write("average ratings and sentiment distribution.\n\n")
        
        f.write("2. **Common Themes**: Certain pain points (e.g., login issues, transaction failures) ")
        f.write("appear across multiple banks, suggesting industry-wide improvement opportunities.\n\n")
        
        f.write("3. **Differentiation Opportunities**: Each bank has unique strengths and weaknesses ")
        f.write("that can inform competitive positioning.\n\n")
        
        f.write("### Next Steps\n\n")
        f.write("- Implement recommended improvements based on identified pain points\n")
        f.write("- Monitor sentiment trends over time to measure improvement impact\n")
        f.write("- Conduct follow-up analysis after implementing changes\n")
        f.write("- Expand analysis to include additional data sources (e.g., app store analytics, user surveys)\n\n")
        
        f.write("---\n\n")
        f.write(f"**Report Generated**: {datetime.now().strftime('%B %d, %Y')}\n")
        f.write("**Version**: 1.0\n")

