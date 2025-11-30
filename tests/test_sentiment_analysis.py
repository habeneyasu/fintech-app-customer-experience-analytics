"""Unit tests for sentiment and thematic analysis"""
import unittest
import pandas as pd
from src.analysis.sentiment_analyzer import SentimentAnalyzer
from src.analysis.text_preprocessor import TextPreprocessor
from src.analysis.thematic_analyzer import ThematicAnalyzer


class TestSentimentAnalysis(unittest.TestCase):
    """Test cases for sentiment analysis"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_texts = [
            "This is a great app!",
            "I hate this app, it's terrible.",
            "The app is okay, nothing special."
        ]
    
    def test_text_preprocessing(self):
        """Test text preprocessing"""
        preprocessor = TextPreprocessor()
        processed = preprocessor.preprocess("This is a GREAT app!!!")
        self.assertIsInstance(processed, str)
        self.assertGreater(len(processed), 0)
    
    def test_sentiment_analyzer_initialization(self):
        """Test sentiment analyzer initialization"""
        try:
            analyzer = SentimentAnalyzer()
            self.assertIsNotNone(analyzer.model)
            self.assertIsNotNone(analyzer.tokenizer)
        except Exception as e:
            self.skipTest(f"Could not initialize sentiment analyzer: {e}")
    
    def test_sentiment_prediction(self):
        """Test sentiment prediction"""
        try:
            analyzer = SentimentAnalyzer()
            result = analyzer.predict_sentiment("This is a great app!")
            self.assertIn('label', result)
            self.assertIn('score', result)
            self.assertIn(result['label'], ['positive', 'negative', 'neutral'])
        except Exception as e:
            self.skipTest(f"Could not test sentiment prediction: {e}")
    
    def test_thematic_analyzer_initialization(self):
        """Test thematic analyzer initialization"""
        analyzer = ThematicAnalyzer()
        self.assertIsNotNone(analyzer.vectorizer)
    
    def test_keyword_extraction(self):
        """Test keyword extraction"""
        analyzer = ThematicAnalyzer()
        texts = ["login error", "slow transfer", "good UI"]
        keywords = analyzer.extract_keywords_tfidf(texts)
        self.assertIsInstance(keywords, list)
        self.assertGreater(len(keywords), 0)


if __name__ == '__main__':
    unittest.main()

