"""Insights generator for identifying drivers, pain points, and comparisons"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from collections import Counter
import re

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class InsightsGenerator:
    """Generate insights from sentiment and thematic analysis"""
    
    def __init__(self):
        """Initialize insights generator"""
        self.drivers_keywords = {
            'fast': ['fast', 'quick', 'speed', 'instant', 'rapid', 'swift'],
            'easy': ['easy', 'simple', 'convenient', 'user-friendly', 'intuitive'],
            'reliable': ['reliable', 'stable', 'consistent', 'dependable', 'trustworthy'],
            'secure': ['secure', 'safe', 'protected', 'security'],
            'features': ['feature', 'function', 'tool', 'option', 'capability'],
            'support': ['support', 'help', 'service', 'assistance', 'customer service']
        }
        
        self.pain_point_keywords = {
            'crashes': ['crash', 'freeze', 'hang', 'error', 'bug', 'glitch'],
            'slow': ['slow', 'lag', 'delay', 'wait', 'loading', 'timeout'],
            'login': ['login', 'password', 'authentication', 'access', 'sign in'],
            'transaction': ['transaction', 'payment', 'transfer', 'failed', 'declined'],
            'network': ['network', 'connection', 'internet', 'connectivity', 'offline'],
            'ui': ['interface', 'design', 'layout', 'navigation', 'confusing', 'complicated']
        }
    
    def load_data_from_database(self, db_connection) -> pd.DataFrame:
        """
        Load review data from PostgreSQL database.
        
        Args:
            db_connection: DatabaseConnection instance
            
        Returns:
            DataFrame with review data
        """
        logger.info("Loading data from database...")
        
        query = """
            SELECT 
                r.review_id,
                b.bank_name,
                r.review_text,
                r.rating,
                r.review_date,
                r.sentiment_label,
                r.sentiment_score,
                r.source
            FROM reviews r
            JOIN banks b ON r.bank_id = b.bank_id
            WHERE r.review_text IS NOT NULL
            ORDER BY r.review_date DESC
        """
        
        results = db_connection.execute_query(query)
        
        if not results:
            logger.warning("No data found in database")
            return pd.DataFrame()
        
        df = pd.DataFrame(results)
        logger.info(f"Loaded {len(df)} reviews from database")
        
        return df
    
    def load_data_from_csv(self, csv_path: str) -> pd.DataFrame:
        """
        Load review data from CSV file.
        
        Args:
            csv_path: Path to analyzed_reviews.csv
            
        Returns:
            DataFrame with review data
        """
        logger.info(f"Loading data from {csv_path}...")
        df = pd.read_csv(csv_path)
        logger.info(f"Loaded {len(df)} reviews from CSV")
        return df
    
    def identify_drivers(self, df: pd.DataFrame, bank_name: str) -> List[Dict[str, Any]]:
        """
        Identify positive drivers (what customers like) for a bank.
        
        Args:
            df: DataFrame with reviews for the bank
            bank_name: Name of the bank
            
        Returns:
            List of driver dictionaries with evidence
        """
        logger.info(f"Identifying drivers for {bank_name}...")
        
        # Filter positive reviews (rating >= 4 or positive sentiment)
        positive_df = df[
            (df['rating'] >= 4) | 
            (df['sentiment_label'] == 'positive')
        ].copy()
        
        if len(positive_df) == 0:
            return []
        
        drivers = []
        driver_scores = {}
        
        # Analyze review text for driver keywords
        for _, row in positive_df.iterrows():
            text = str(row.get('review_text', '')).lower()
            rating = float(row.get('rating', 0)) if row.get('rating') is not None else 0.0
            sentiment_score = float(row.get('sentiment_score', 0.5)) if row.get('sentiment_score') is not None else 0.5
            
            # Calculate weight based on rating and sentiment
            weight = (rating / 5.0) * 0.5 + sentiment_score * 0.5
            
            # Check for driver keywords
            for driver_type, keywords in self.drivers_keywords.items():
                for keyword in keywords:
                    if keyword in text:
                        if driver_type not in driver_scores:
                            driver_scores[driver_type] = {
                                'score': 0,
                                'count': 0,
                                'examples': []
                            }
                        driver_scores[driver_type]['score'] += weight
                        driver_scores[driver_type]['count'] += 1
                        
                        # Store example review
                        if len(driver_scores[driver_type]['examples']) < 3:
                            example_text = str(row.get('review_text', ''))[:100]
                            driver_scores[driver_type]['examples'].append({
                                'text': example_text,
                                'rating': rating,
                                'sentiment': row.get('sentiment_label', 'unknown')
                            })
        
        # Convert to driver list
        for driver_type, data in driver_scores.items():
            if data['count'] >= 5:  # Minimum mentions threshold
                drivers.append({
                    'type': driver_type,
                    'description': self._get_driver_description(driver_type),
                    'strength': min(data['score'] / data['count'], 1.0),
                    'mentions': data['count'],
                    'evidence_count': len(positive_df),
                    'examples': data['examples']
                })
        
        # Sort by strength
        drivers.sort(key=lambda x: x['strength'], reverse=True)
        
        return drivers[:5]  # Top 5 drivers
    
    def identify_pain_points(self, df: pd.DataFrame, bank_name: str) -> List[Dict[str, Any]]:
        """
        Identify pain points (what customers complain about) for a bank.
        
        Args:
            df: DataFrame with reviews for the bank
            bank_name: Name of the bank
            
        Returns:
            List of pain point dictionaries with evidence
        """
        logger.info(f"Identifying pain points for {bank_name}...")
        
        # Filter negative reviews (rating <= 2 or negative sentiment)
        negative_df = df[
            (df['rating'] <= 2) | 
            (df['sentiment_label'] == 'negative')
        ].copy()
        
        if len(negative_df) == 0:
            return []
        
        pain_points = []
        pain_point_scores = {}
        
        # Analyze review text for pain point keywords
        for _, row in negative_df.iterrows():
            text = str(row.get('review_text', '')).lower()
            rating = float(row.get('rating', 3)) if row.get('rating') is not None else 3.0
            sentiment_score = float(row.get('sentiment_score', 0.5)) if row.get('sentiment_score') is not None else 0.5
            
            # Calculate weight (lower rating = higher weight)
            weight = ((5 - rating) / 5.0) * 0.5 + (1 - sentiment_score) * 0.5
            
            # Check for pain point keywords
            for pain_type, keywords in self.pain_point_keywords.items():
                for keyword in keywords:
                    if keyword in text:
                        if pain_type not in pain_point_scores:
                            pain_point_scores[pain_type] = {
                                'score': 0,
                                'count': 0,
                                'examples': []
                            }
                        pain_point_scores[pain_type]['score'] += weight
                        pain_point_scores[pain_type]['count'] += 1
                        
                        # Store example review
                        if len(pain_point_scores[pain_type]['examples']) < 3:
                            example_text = str(row.get('review_text', ''))[:100]
                            pain_point_scores[pain_type]['examples'].append({
                                'text': example_text,
                                'rating': rating,
                                'sentiment': row.get('sentiment_label', 'unknown')
                            })
        
        # Convert to pain point list
        for pain_type, data in pain_point_scores.items():
            if data['count'] >= 5:  # Minimum mentions threshold
                pain_points.append({
                    'type': pain_type,
                    'description': self._get_pain_point_description(pain_type),
                    'severity': min(data['score'] / data['count'], 1.0),
                    'mentions': data['count'],
                    'evidence_count': len(negative_df),
                    'examples': data['examples']
                })
        
        # Sort by severity
        pain_points.sort(key=lambda x: x['severity'], reverse=True)
        
        return pain_points[:5]  # Top 5 pain points
    
    def compare_banks(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Compare banks across key metrics.
        
        Args:
            df: DataFrame with all reviews
            
        Returns:
            Dictionary with comparison metrics
        """
        logger.info("Comparing banks...")
        
        comparison = {}
        
        for bank in df['bank_name'].unique() if 'bank_name' in df.columns else df['bank'].unique():
            bank_df = df[df['bank_name' if 'bank_name' in df.columns else 'bank'] == bank].copy()
            
            # Convert Decimal types to float for calculations
            if 'rating' in bank_df.columns:
                bank_df['rating'] = bank_df['rating'].apply(lambda x: float(x) if x is not None else 0.0)
            
            avg_rating = bank_df['rating'].mean() if 'rating' in bank_df.columns else 0.0
            total = len(bank_df)
            
            comparison[bank] = {
                'total_reviews': total,
                'average_rating': float(avg_rating) if avg_rating is not None else 0.0,
                'positive_sentiment_pct': (bank_df['sentiment_label'] == 'positive').sum() / total * 100 if 'sentiment_label' in bank_df.columns and total > 0 else 0.0,
                'negative_sentiment_pct': (bank_df['sentiment_label'] == 'negative').sum() / total * 100 if 'sentiment_label' in bank_df.columns and total > 0 else 0.0,
                'neutral_sentiment_pct': (bank_df['sentiment_label'] == 'neutral').sum() / total * 100 if 'sentiment_label' in bank_df.columns and total > 0 else 0.0,
                'rating_distribution': {int(k): int(v) for k, v in bank_df['rating'].value_counts().to_dict().items()} if 'rating' in bank_df.columns else {}
            }
        
        return comparison
    
    def generate_recommendations(self, drivers: List[Dict], pain_points: List[Dict], 
                                bank_name: str) -> List[Dict[str, Any]]:
        """
        Generate improvement recommendations based on drivers and pain points.
        
        Args:
            drivers: List of identified drivers
            pain_points: List of identified pain points
            bank_name: Name of the bank
            
        Returns:
            List of recommendation dictionaries
        """
        logger.info(f"Generating recommendations for {bank_name}...")
        
        recommendations = []
        
        # Recommendations based on pain points
        for pain_point in pain_points[:3]:  # Top 3 pain points
            rec = self._get_recommendation_for_pain_point(pain_point)
            if rec:
                recommendations.append(rec)
        
        # Recommendations based on missing drivers (opportunities)
        existing_driver_types = {d['type'] for d in drivers}
        all_driver_types = set(self.drivers_keywords.keys())
        missing_drivers = all_driver_types - existing_driver_types
        
        for missing_driver in list(missing_drivers)[:2]:  # Top 2 opportunities
            rec = self._get_recommendation_for_opportunity(missing_driver)
            if rec:
                recommendations.append(rec)
        
        return recommendations
    
    def _get_driver_description(self, driver_type: str) -> str:
        """Get human-readable description for driver type"""
        descriptions = {
            'fast': 'Fast navigation and quick response times',
            'easy': 'Easy to use and user-friendly interface',
            'reliable': 'Reliable and stable app performance',
            'secure': 'Strong security features',
            'features': 'Rich feature set and functionality',
            'support': 'Good customer support and service'
        }
        return descriptions.get(driver_type, driver_type)
    
    def _get_pain_point_description(self, pain_type: str) -> str:
        """Get human-readable description for pain point type"""
        descriptions = {
            'crashes': 'App crashes and technical errors',
            'slow': 'Slow performance and loading times',
            'login': 'Login and authentication issues',
            'transaction': 'Transaction failures and payment problems',
            'network': 'Network connectivity issues',
            'ui': 'User interface and navigation problems'
        }
        return descriptions.get(pain_type, pain_type)
    
    def _get_recommendation_for_pain_point(self, pain_point: Dict) -> Optional[Dict]:
        """Generate recommendation for a specific pain point"""
        recommendations_map = {
            'crashes': {
                'title': 'Improve App Stability',
                'description': 'Address app crashes and bugs through comprehensive testing and error handling',
                'priority': 'High',
                'impact': 'Reduces user frustration and negative reviews'
            },
            'slow': {
                'title': 'Optimize Performance',
                'description': 'Improve app speed and reduce loading times through code optimization and caching',
                'priority': 'High',
                'impact': 'Enhances user experience and satisfaction'
            },
            'login': {
                'title': 'Enhance Authentication System',
                'description': 'Simplify login process and add biometric authentication options',
                'priority': 'Medium',
                'impact': 'Reduces login-related complaints'
            },
            'transaction': {
                'title': 'Improve Transaction Reliability',
                'description': 'Enhance payment processing and add transaction status notifications',
                'priority': 'High',
                'impact': 'Critical for user trust and app functionality'
            },
            'network': {
                'title': 'Add Offline Capabilities',
                'description': 'Implement offline mode and better error handling for network issues',
                'priority': 'Medium',
                'impact': 'Improves app usability in poor network conditions'
            },
            'ui': {
                'title': 'Redesign User Interface',
                'description': 'Simplify navigation and improve visual design based on user feedback',
                'priority': 'Medium',
                'impact': 'Enhances overall user experience'
            }
        }
        
        pain_type = pain_point['type']
        if pain_type in recommendations_map:
            rec = recommendations_map[pain_type].copy()
            rec['evidence'] = f"{pain_point['mentions']} mentions in negative reviews"
            rec['severity'] = pain_point['severity']
            return rec
        
        return None
    
    def _get_recommendation_for_opportunity(self, opportunity_type: str) -> Optional[Dict]:
        """Generate recommendation for a missing driver (opportunity)"""
        opportunities_map = {
            'fast': {
                'title': 'Add Performance Optimization Features',
                'description': 'Implement caching and optimize app performance to improve speed',
                'priority': 'Medium',
                'impact': 'Could become a key differentiator'
            },
            'easy': {
                'title': 'Improve User Onboarding',
                'description': 'Create tutorials and simplify initial setup process',
                'priority': 'Medium',
                'impact': 'Reduces learning curve for new users'
            },
            'reliable': {
                'title': 'Enhance App Reliability',
                'description': 'Invest in testing and monitoring to improve app stability',
                'priority': 'High',
                'impact': 'Builds user trust and reduces complaints'
            },
            'secure': {
                'title': 'Strengthen Security Features',
                'description': 'Add two-factor authentication and security notifications',
                'priority': 'High',
                'impact': 'Critical for financial app user trust'
            },
            'features': {
                'title': 'Add Budgeting Tools',
                'description': 'Implement expense tracking and budgeting features',
                'priority': 'Low',
                'impact': 'Differentiates from competitors'
            },
            'support': {
                'title': 'Enhance Customer Support',
                'description': 'Add in-app chat support and improve response times',
                'priority': 'Medium',
                'impact': 'Improves customer satisfaction'
            }
        }
        
        if opportunity_type in opportunities_map:
            rec = opportunities_map[opportunity_type].copy()
            rec['opportunity'] = True
            return rec
        
        return None

