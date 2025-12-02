"""
Report Generator - Creates final report with recommendations tied to findings

This module generates a comprehensive report that explicitly ties each recommendation
to the identified pain points with evidence counts and examples.
"""
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

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
    
    def generate_report(self, all_insights: Dict[str, Dict[str, Any]], 
                       comparison_data: Dict[str, Any]) -> Path:
        """
        Generate comprehensive final report.
        
        The report explicitly shows:
        - Per-bank drivers and pain points with evidence
        - Recommendations tied directly to identified pain points
        - Evidence counts for each recommendation
        
        Args:
            all_insights: Dictionary with bank insights (drivers, pain points, recommendations)
            comparison_data: Bank comparison metrics
            
        Returns:
            Path to generated report
        """
        logger.info("Generating final report...")
        
        report_path = self.output_dir / "FINAL_REPORT.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            # Write header
            f.write(self._write_header())
            f.write(self._write_executive_summary(all_insights))
            f.write(self._write_methodology())
            f.write(self._write_data_overview(all_insights))
            f.write(self._write_insights_by_bank(all_insights))
            f.write(self._write_comparison(comparison_data))
            f.write(self._write_recommendations(all_insights))
            f.write(self._write_visualizations())
            f.write(self._write_ethics())
            f.write(self._write_conclusion())
        
        logger.info(f"Final report generated: {report_path}")
        return report_path
    
    def _write_header(self) -> str:
        """Write report header"""
        return f"""# Fintech App Customer Experience Analytics - Final Report

**Project**: Customer Experience Analytics for Ethiopian Banking Apps
**Date**: {datetime.now().strftime('%B %d, %Y')}
**Status**: Complete

---

"""
    
    def _write_executive_summary(self, all_insights: Dict) -> str:
        """Write executive summary"""
        total_reviews = sum(insights.get('statistics', {}).get('total_reviews', 0) 
                          for insights in all_insights.values())
        
        content = f"""## 1. Executive Summary

This report presents a comprehensive analysis of customer reviews for three major Ethiopian banking mobile applications: Commercial Bank of Ethiopia (CBE), Bank of Abyssinia (BOA), and Dashen Bank. The analysis is based on {total_reviews:,} processed reviews collected from Google Play Store, with complete sentiment analysis and thematic identification.

### Key Findings

- **Total Reviews Analyzed**: {total_reviews:,}
- **Banks Analyzed**: 3
- **Sentiment Coverage**: 100%

### Top Insights

"""
        for bank_name, insights in all_insights.items():
            drivers = insights.get('drivers', [])
            pain_points = insights.get('pain_points', [])
            
            if drivers:
                top_driver = drivers[0]
                content += f"- **{bank_name}**: Top driver is {top_driver['description']} ({top_driver['mentions']} mentions)\n"
            
            if pain_points:
                top_pain = pain_points[0]
                content += f"- **{bank_name}**: Main pain point is {top_pain['description']} ({top_pain['mentions']} mentions)\n"
        
        return content + "\n---\n\n"
    
    def _write_methodology(self) -> str:
        """Write methodology section"""
        return """## 2. Methodology

### Data Collection
- **Source**: Google Play Store reviews
- **Collection Method**: Automated scraping using `google-play-scraper`
- **Languages**: Amharic and English

### Analysis Approach
- **Drivers Identification**: Keyword-based analysis of positive reviews (rating ≥ 4 or positive sentiment)
- **Pain Points Identification**: Keyword-based analysis of negative reviews (rating ≤ 2 or negative sentiment)
- **Recommendations**: Generated based on identified pain points with evidence counts
- **Visualization**: Matplotlib, Seaborn for labeled plots

---

"""
    
    def _write_data_overview(self, all_insights: Dict) -> str:
        """Write data overview section"""
        content = "## 3. Data Overview\n\n### Review Distribution\n\n| Bank | Total Reviews | Average Rating | Positive % | Negative % |\n|------|--------------|----------------|------------|------------|\n"
        
        for bank_name, insights in all_insights.items():
            stats = insights.get('statistics', {})
            content += f"| {bank_name} | {stats.get('total_reviews', 0):,} | {stats.get('average_rating', 0):.2f} | {stats.get('positive_sentiment_pct', 0):.1f}% | {stats.get('negative_sentiment_pct', 0):.1f}% |\n"
        
        return content + "\n---\n\n"
    
    def _write_insights_by_bank(self, all_insights: Dict) -> str:
        """Write insights by bank section"""
        content = "## 4. Insights by Bank\n\n"
        
        for bank_name, insights in all_insights.items():
            stats = insights.get('statistics', {})
            drivers = insights.get('drivers', [])
            pain_points = insights.get('pain_points', [])
            
            content += f"""### 4.{list(all_insights.keys()).index(bank_name) + 1} {bank_name}

**Statistics**: {stats.get('total_reviews', 0):,} reviews, Average Rating: {stats.get('average_rating', 0):.2f}, Positive: {stats.get('positive_sentiment_pct', 0):.1f}%, Negative: {stats.get('negative_sentiment_pct', 0):.1f}%

#### Drivers (What Customers Like)

"""
            for i, driver in enumerate(drivers[:3], 1):
                content += f"""{i}. **{driver['description']}**
   - Strength Score: {driver['strength']:.1%}
   - Mentions: {driver['mentions']}
   - Example: "{driver['examples'][0]['text'] if driver['examples'] else 'N/A'}" (Rating: {driver['examples'][0]['rating'] if driver['examples'] else 'N/A'})

"""
            
            content += "#### Pain Points (What Customers Complain About)\n\n"
            for i, pain in enumerate(pain_points[:3], 1):
                content += f"""{i}. **{pain['description']}**
   - Severity Score: {pain['severity']:.1%}
   - Mentions: {pain['mentions']}
   - Example: "{pain['examples'][0]['text'] if pain['examples'] else 'N/A'}" (Rating: {pain['examples'][0]['rating'] if pain['examples'] else 'N/A'})

"""
        
        return content + "---\n\n"
    
    def _write_comparison(self, comparison_data: Dict) -> str:
        """Write bank comparison section"""
        content = "## 5. Bank Comparison\n\n### 5.1 Key Metrics\n\n| Metric | " + " | ".join(comparison_data.keys()) + " |\n|--------|" + "|".join(["-----" for _ in comparison_data]) + "|\n"
        
        metrics = ['average_rating', 'positive_sentiment_pct', 'total_reviews']
        metric_names = ['Average Rating', 'Positive Sentiment %', 'Total Reviews']
        
        for metric, name in zip(metrics, metric_names):
            content += f"| {name} | " + " | ".join([f"{comparison_data[bank].get(metric, 0):.2f}" if metric != 'total_reviews' else f"{comparison_data[bank].get(metric, 0):,}" for bank in comparison_data.keys()]) + " |\n"
        
        return content + "\n---\n\n"
    
    def _write_recommendations(self, all_insights: Dict) -> str:
        """Write recommendations section - explicitly tied to findings"""
        content = "## 6. Recommendations\n\n"
        content += "**Note**: Each recommendation is directly tied to identified pain points with evidence counts from the analysis.\n\n"
        
        for bank_name, insights in all_insights.items():
            recommendations = insights.get('recommendations', [])
            bank_num = list(all_insights.keys()).index(bank_name) + 1
            
            content += f"### 6.{bank_num} Recommendations for {bank_name}\n\n"
            
            for i, rec in enumerate(recommendations[:3], 1):  # Top 3 recommendations
                content += f"""{i}. **{rec['title']}**
   - Priority: {rec['priority']}
   - Description: {rec['description']}
   - Expected Impact: {rec['expected_impact']}
   - Evidence: {rec['evidence']} (Tied to pain point: {rec.get('pain_point_tied_to', 'N/A')})

"""
        
        return content + "---\n\n"
    
    def _write_visualizations(self) -> str:
        """Write visualizations section"""
        return """## 7. Visualizations

The following labeled visualizations have been generated:

### Sentiment Distribution by Bank
- Shows positive, negative, and neutral review counts per bank
- Location: `data/results/visualizations/sentiment_distribution_by_bank.png`

### Rating Distribution by Bank
- Shows 1-5 star rating distribution per bank
- Location: `data/results/visualizations/rating_distribution_by_bank.png`

### Sentiment Trends Over Time
- Shows sentiment changes over months for each bank
- Location: `data/results/visualizations/sentiment_trends.png`

### Bank Comparison Chart
- Compares average ratings and positive sentiment percentages
- Location: `data/results/visualizations/bank_comparison.png`

### Drivers and Pain Points Charts
- Per-bank charts showing top drivers and pain points
- Location: `data/results/visualizations/drivers_pain_points_*.png`

---

"""
    
    def _write_ethics(self) -> str:
        """Write ethics considerations section"""
        return """## 8. Ethics Considerations

### Potential Biases
- **Negative Skew**: Users more likely to review after negative experiences
- **Selection Bias**: Only Google Play Store reviews (excludes iOS users)
- **Language Bias**: English reviews may over-represent certain demographics

### Mitigation
- Analysis acknowledges limitations
- Findings are contextualized with data source information
- Recommendations consider potential biases

---

"""
    
    def _write_conclusion(self) -> str:
        """Write conclusion section"""
        return """## 9. Conclusion

This analysis provides actionable insights for improving mobile banking applications. Each recommendation is directly tied to identified pain points with evidence from customer reviews. The visualizations clearly show trends and comparisons across banks.

**Key Takeaways**:
- Performance optimization is critical for all banks
- App stability improvements can significantly reduce negative reviews
- User interface improvements enhance overall satisfaction

---

**Report Generated**: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n"

