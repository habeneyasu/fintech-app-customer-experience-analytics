"""
Insights Generator - Computes per-bank drivers and pain points

This module explicitly computes drivers (positive aspects) and pain points (negative aspects)
for each bank based on review analysis. Each driver and pain point includes:
- Evidence count (number of mentions)
- Strength/severity scores
- Example reviews
- Direct ties to recommendations
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from collections import Counter
import re

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class InsightsGenerator:
    """Generate insights including drivers and pain points per bank"""
    
    # Keywords for identifying drivers (positive aspects)
    DRIVER_KEYWORDS = {
        'fast': ['fast', 'quick', 'speed', 'rapid', 'instant', 'swift'],
        'easy': ['easy', 'simple', 'user-friendly', 'intuitive', 'straightforward'],
        'reliable': ['reliable', 'stable', 'consistent', 'dependable', 'trustworthy'],
        'secure': ['secure', 'safe', 'security', 'protected', 'encrypted'],
        'good_support': ['support', 'helpful', 'responsive', 'customer service', 'assistance']
    }
    
    # Keywords for identifying pain points (negative aspects)
    PAIN_POINT_KEYWORDS = {
        'slow': ['slow', 'lag', 'loading', 'delay', 'wait', 'timeout'],
        'crash': ['crash', 'error', 'bug', 'glitch', 'freeze', 'hang', 'broken'],
        'ui_issues': ['confusing', 'complicated', 'navigation', 'interface', 'design', 'layout'],
        'network': ['network', 'connection', 'connectivity', 'offline', 'disconnect'],
        'login': ['login', 'password', 'authentication', 'access', 'sign in']
    }
    
    def __init__(self):
        """Initialize insights generator"""
        logger.info("Initializing Insights Generator")
    
    def identify_drivers(self, df: pd.DataFrame, bank_name: str) -> List[Dict[str, Any]]:
        """
        Compute drivers (positive aspects) for a specific bank.
        
        A driver is identified by:
        1. Positive reviews (rating >= 4 OR sentiment = 'positive')
        2. Keyword matching in review text
        3. Strength score = (rating_weight * 0.5) + (sentiment_score * 0.5)
        
        Args:
            df: DataFrame filtered for the specific bank
            bank_name: Name of the bank
            
        Returns:
            List of driver dictionaries with type, description, strength, mentions, examples
        """
        logger.info(f"Computing drivers for {bank_name}")
        
        # Filter positive reviews (rating >= 4 or positive sentiment)
        positive_df = df[
            (df['rating'].astype(float) >= 4.0) | 
            (df['sentiment_label'].str.lower() == 'positive')
        ].copy()
        
        if len(positive_df) == 0:
            logger.warning(f"No positive reviews found for {bank_name}")
            return []
        
        # Convert rating and sentiment_score to float
        positive_df['rating'] = positive_df['rating'].astype(float)
        positive_df['sentiment_score'] = pd.to_numeric(positive_df['sentiment_score'], errors='coerce').fillna(0.5)
        
        drivers = []
        review_text_col = 'review_text' if 'review_text' in positive_df.columns else 'review'
        
        # Check each driver keyword category
        for driver_type, keywords in self.DRIVER_KEYWORDS.items():
            mentions = 0
            evidence_reviews = []
            total_strength = 0.0
            
            # Search for keywords in review text
            for idx, row in positive_df.iterrows():
                review_text = str(row.get(review_text_col, '')).lower()
                
                # Check if any keyword appears in review
                if any(keyword in review_text for keyword in keywords):
                    mentions += 1
                    
                    # Calculate strength for this review
                    rating = float(row['rating'])
                    sentiment_score = float(row['sentiment_score'])
                    weight = (rating / 5.0) * 0.5 + sentiment_score * 0.5
                    total_strength += weight
                    
                    # Store example (limit to 3 examples)
                    if len(evidence_reviews) < 3:
                        evidence_reviews.append({
                            'text': str(row.get(review_text_col, ''))[:100],
                            'rating': rating,
                            'sentiment': str(row.get('sentiment_label', 'positive'))
                        })
            
            if mentions > 0:
                avg_strength = total_strength / mentions
                
                driver = {
                    'type': driver_type,
                    'description': self._get_driver_description(driver_type),
                    'strength': avg_strength,
                    'mentions': mentions,
                    'evidence_count': len(positive_df),
                    'examples': evidence_reviews
                }
                drivers.append(driver)
                logger.info(f"  - {driver_type}: {mentions} mentions, strength: {avg_strength:.2%}")
        
        # Sort by strength (descending)
        drivers.sort(key=lambda x: x['strength'], reverse=True)
        
        logger.info(f"Identified {len(drivers)} drivers for {bank_name}")
        return drivers
    
    def identify_pain_points(self, df: pd.DataFrame, bank_name: str) -> List[Dict[str, Any]]:
        """
        Compute pain points (negative aspects) for a specific bank.
        
        A pain point is identified by:
        1. Negative reviews (rating <= 2 OR sentiment = 'negative')
        2. Keyword matching in review text
        3. Severity score = (1 - rating_weight) * 0.5 + (1 - sentiment_score) * 0.5
        
        Args:
            df: DataFrame filtered for the specific bank
            bank_name: Name of the bank
            
        Returns:
            List of pain point dictionaries with type, description, severity, mentions, examples
        """
        logger.info(f"Computing pain points for {bank_name}")
        
        # Filter negative reviews (rating <= 2 or negative sentiment)
        negative_df = df[
            (df['rating'].astype(float) <= 2.0) | 
            (df['sentiment_label'].str.lower() == 'negative')
        ].copy()
        
        if len(negative_df) == 0:
            logger.warning(f"No negative reviews found for {bank_name}")
            return []
        
        # Convert rating and sentiment_score to float
        negative_df['rating'] = negative_df['rating'].astype(float)
        negative_df['sentiment_score'] = pd.to_numeric(negative_df['sentiment_score'], errors='coerce').fillna(0.5)
        
        pain_points = []
        review_text_col = 'review_text' if 'review_text' in negative_df.columns else 'review'
        
        # Check each pain point keyword category
        for pain_type, keywords in self.PAIN_POINT_KEYWORDS.items():
            mentions = 0
            evidence_reviews = []
            total_severity = 0.0
            
            # Search for keywords in review text
            for idx, row in negative_df.iterrows():
                review_text = str(row.get(review_text_col, '')).lower()
                
                # Check if any keyword appears in review
                if any(keyword in review_text for keyword in keywords):
                    mentions += 1
                    
                    # Calculate severity for this review
                    rating = float(row['rating'])
                    sentiment_score = float(row['sentiment_score'])
                    # Lower rating and lower sentiment = higher severity
                    severity = (1 - rating / 5.0) * 0.5 + (1 - sentiment_score) * 0.5
                    total_severity += severity
                    
                    # Store example (limit to 3 examples)
                    if len(evidence_reviews) < 3:
                        evidence_reviews.append({
                            'text': str(row.get(review_text_col, ''))[:100],
                            'rating': rating,
                            'sentiment': str(row.get('sentiment_label', 'negative'))
                        })
            
            if mentions > 0:
                avg_severity = total_severity / mentions
                
                pain_point = {
                    'type': pain_type,
                    'description': self._get_pain_point_description(pain_type),
                    'severity': avg_severity,
                    'mentions': mentions,
                    'evidence_count': len(negative_df),
                    'examples': evidence_reviews
                }
                pain_points.append(pain_point)
                logger.info(f"  - {pain_type}: {mentions} mentions, severity: {avg_severity:.2%}")
        
        # Sort by severity (descending)
        pain_points.sort(key=lambda x: x['severity'], reverse=True)
        
        logger.info(f"Identified {len(pain_points)} pain points for {bank_name}")
        return pain_points
    
    def compare_banks(self, all_insights: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare banks across key metrics.
        
        Args:
            all_insights: Dictionary with bank names as keys and their insights as values
            
        Returns:
            Comparison dictionary with metrics for each bank
        """
        logger.info("Computing bank comparison metrics")
        
        comparison = {}
        
        for bank_name, insights in all_insights.items():
            # Get statistics from insights
            stats = insights.get('statistics', {})
            
            comparison[bank_name] = {
                'average_rating': stats.get('average_rating', 0.0),
                'total_reviews': stats.get('total_reviews', 0),
                'positive_sentiment_pct': stats.get('positive_sentiment_pct', 0.0),
                'negative_sentiment_pct': stats.get('negative_sentiment_pct', 0.0),
                'top_driver': insights.get('drivers', [{}])[0].get('type', 'N/A') if insights.get('drivers') else 'N/A',
                'top_pain_point': insights.get('pain_points', [{}])[0].get('type', 'N/A') if insights.get('pain_points') else 'N/A'
            }
        
        logger.info("Bank comparison completed")
        return comparison
    
    def generate_recommendations(self, drivers: List[Dict], pain_points: List[Dict], 
                                bank_name: str) -> List[Dict[str, Any]]:
        """
        Generate actionable recommendations based on identified drivers and pain points.
        
        Each recommendation is directly tied to findings:
        - Priority based on pain point severity and mention count
        - Description addresses the specific pain point
        - Expected impact based on evidence
        - Evidence count from analysis
        
        Args:
            drivers: List of driver dictionaries
            pain_points: List of pain point dictionaries
            bank_name: Name of the bank
            
        Returns:
            List of recommendation dictionaries with priority, description, impact, evidence
        """
        logger.info(f"Generating recommendations for {bank_name}")
        
        recommendations = []
        
        # Generate recommendations from top pain points
        for pain_point in pain_points[:3]:  # Top 3 pain points
            pain_type = pain_point['type']
            mentions = pain_point['mentions']
            severity = pain_point['severity']
            
            # Determine priority based on severity and mentions
            if severity > 0.3 and mentions > 50:
                priority = 'High'
            elif severity > 0.25 or mentions > 30:
                priority = 'High'
            else:
                priority = 'Medium'
            
            # Generate recommendation based on pain point type
            recommendation = {
                'priority': priority,
                'title': self._get_recommendation_title(pain_type),
                'description': self._get_recommendation_description(pain_type),
                'expected_impact': self._get_expected_impact(pain_type),
                'evidence': f"{mentions} mentions in negative reviews",
                'pain_point_tied_to': pain_type
            }
            
            recommendations.append(recommendation)
            logger.info(f"  - {recommendation['title']} (Priority: {priority}, Evidence: {mentions} mentions)")
        
        # Ensure at least 2 recommendations
        if len(recommendations) < 2 and pain_points:
            # Add a general recommendation if we have pain points but fewer than 2 specific ones
            general_rec = {
                'priority': 'Medium',
                'title': 'Improve Overall User Experience',
                'description': 'Address user feedback systematically through regular updates and user testing',
                'expected_impact': 'Improves overall satisfaction and reduces negative reviews',
                'evidence': f"{len(pain_points)} pain points identified",
                'pain_point_tied_to': 'general'
            }
            recommendations.append(general_rec)
        
        logger.info(f"Generated {len(recommendations)} recommendations for {bank_name}")
        return recommendations
    
    def _get_driver_description(self, driver_type: str) -> str:
        """Get human-readable description for driver type"""
        descriptions = {
            'fast': 'Fast navigation and quick response times',
            'easy': 'Easy to use and user-friendly interface',
            'reliable': 'Reliable and stable app performance',
            'secure': 'Strong security features',
            'good_support': 'Good customer support and service'
        }
        return descriptions.get(driver_type, driver_type.replace('_', ' ').title())
    
    def _get_pain_point_description(self, pain_type: str) -> str:
        """Get human-readable description for pain point type"""
        descriptions = {
            'slow': 'Slow performance and loading times',
            'crash': 'App crashes and technical errors',
            'ui_issues': 'User interface and navigation problems',
            'network': 'Network connectivity issues',
            'login': 'Login and authentication problems'
        }
        return descriptions.get(pain_type, pain_type.replace('_', ' ').title())
    
    def _get_recommendation_title(self, pain_type: str) -> str:
        """Get recommendation title based on pain point type"""
        titles = {
            'slow': 'Optimize Performance',
            'crash': 'Improve App Stability',
            'ui_issues': 'Redesign User Interface',
            'network': 'Add Offline Capabilities',
            'login': 'Enhance Authentication System'
        }
        return titles.get(pain_type, 'Address User Concerns')
    
    def _get_recommendation_description(self, pain_type: str) -> str:
        """Get recommendation description based on pain point type"""
        descriptions = {
            'slow': 'Improve app speed and reduce loading times through code optimization and caching',
            'crash': 'Address app crashes and bugs through comprehensive testing and error handling',
            'ui_issues': 'Simplify navigation and improve visual design based on user feedback',
            'network': 'Implement offline mode and better error handling for network issues',
            'login': 'Simplify login process and add biometric authentication options'
        }
        return descriptions.get(pain_type, 'Address identified issues through systematic improvements')
    
    def _get_expected_impact(self, pain_type: str) -> str:
        """Get expected impact description based on pain point type"""
        impacts = {
            'slow': 'Enhances user experience and satisfaction',
            'crash': 'Reduces user frustration and negative reviews',
            'ui_issues': 'Enhances overall user experience',
            'network': 'Improves app usability in poor network conditions',
            'login': 'Reduces login-related complaints'
        }
        return impacts.get(pain_type, 'Improves user satisfaction and reduces negative feedback')

