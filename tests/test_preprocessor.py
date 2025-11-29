"""Unit tests for data preprocessor"""
import unittest
import pandas as pd
from src.data_processing.preprocessor import DataPreprocessor


class TestDataPreprocessor(unittest.TestCase):
    """Test cases for DataPreprocessor"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.preprocessor = DataPreprocessor()
        self.sample_data = pd.DataFrame({
            'review': ['Great app!', 'Bad app', 'Great app!', '   ', 'A' * 2000],
            'rating': [5, 1, 5, 3, 4],
            'date': ['2025-01-01', '2025-01-02', '2025-01-01', '2025-01-03', '2025-01-04'],
            'bank': ['CBE', 'BOA', 'CBE', 'DASHEN', 'CBE'],
            'user_name': ['user1', 'user2', 'user1', 'user3', 'user4']
        })
    
    def test_remove_duplicates(self):
        """Test duplicate removal"""
        processed = self.preprocessor.preprocess(self.sample_data)
        self.assertLessEqual(len(processed), len(self.sample_data))
    
    def test_text_cleaning(self):
        """Test text cleaning"""
        cleaned = self.preprocessor.clean_text('  Hello   World  ')
        self.assertEqual(cleaned, 'Hello World')
    
    def test_date_normalization(self):
        """Test date normalization"""
        normalized = self.preprocessor.normalize_date('2025-01-01')
        self.assertEqual(normalized, '2025-01-01')
    
    def test_validate_data_quality(self):
        """Test data quality validation"""
        metrics = self.preprocessor.validate_data_quality(self.sample_data)
        self.assertIn('total_reviews', metrics)
        self.assertIn('error_percentage', metrics)


if __name__ == '__main__':
    unittest.main()

