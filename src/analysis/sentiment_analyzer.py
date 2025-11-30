"""Sentiment analysis using DistilBERT model"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from tqdm import tqdm

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class SentimentAnalyzer:
    """Sentiment analysis using DistilBERT model"""
    
    def __init__(self, model_name: str = "distilbert-base-uncased-finetuned-sst-2-english"):
        """
        Initialize sentiment analyzer.
        
        Args:
            model_name: HuggingFace model name for sentiment analysis
        """
        self.model_name = model_name
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Initializing sentiment analyzer with model: {model_name}")
        logger.info(f"Using device: {self.device}")
        
        # Load model and tokenizer
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            self.model.to(self.device)
            self.model.eval()
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def predict_sentiment(self, text: str) -> Dict[str, float]:
        """
        Predict sentiment for a single text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment label and score
        """
        if not text or pd.isna(text):
            return {"label": "neutral", "score": 0.5}
        
        try:
            # Tokenize and encode
            inputs = self.tokenizer(
                text,
                truncation=True,
                padding=True,
                max_length=512,
                return_tensors="pt"
            ).to(self.device)
            
            # Predict
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            # Get results
            scores = predictions[0].cpu().numpy()
            labels = ["negative", "positive"]
            
            # Get highest score
            max_idx = np.argmax(scores)
            label = labels[max_idx]
            score = float(scores[max_idx])
            
            # Determine neutral if score is close to 0.5
            if abs(score - 0.5) < 0.1:
                label = "neutral"
            
            return {
                "label": label,
                "score": score,
                "positive_score": float(scores[1]),
                "negative_score": float(scores[0])
            }
        except Exception as e:
            logger.warning(f"Error analyzing sentiment for text: {str(e)}")
            return {"label": "neutral", "score": 0.5, "positive_score": 0.5, "negative_score": 0.5}
    
    def analyze_batch(self, texts: List[str], batch_size: int = 32) -> List[Dict[str, float]]:
        """
        Analyze sentiment for a batch of texts.
        
        Args:
            texts: List of texts to analyze
            batch_size: Batch size for processing
            
        Returns:
            List of sentiment dictionaries
        """
        results = []
        
        for i in tqdm(range(0, len(texts), batch_size), desc="Analyzing sentiment"):
            batch = texts[i:i + batch_size]
            batch_results = [self.predict_sentiment(text) for text in batch]
            results.extend(batch_results)
        
        return results
    
    def analyze_dataframe(self, df: pd.DataFrame, text_column: str = "review") -> pd.DataFrame:
        """
        Analyze sentiment for all reviews in a dataframe.
        
        Args:
            df: DataFrame with reviews
            text_column: Name of the column containing review text
            
        Returns:
            DataFrame with added sentiment columns
        """
        logger.info(f"Analyzing sentiment for {len(df)} reviews")
        
        # Get texts
        texts = df[text_column].fillna("").tolist()
        
        # Analyze
        sentiment_results = self.analyze_batch(texts)
        
        # Add to dataframe
        df_result = df.copy()
        df_result["sentiment_label"] = [r["label"] for r in sentiment_results]
        df_result["sentiment_score"] = [r["score"] for r in sentiment_results]
        df_result["positive_score"] = [r.get("positive_score", 0.5) for r in sentiment_results]
        df_result["negative_score"] = [r.get("negative_score", 0.5) for r in sentiment_results]
        
        # Calculate coverage
        coverage = (df_result["sentiment_label"].notna().sum() / len(df_result)) * 100
        logger.info(f"Sentiment analysis complete. Coverage: {coverage:.2f}%")
        
        return df_result
    
    def aggregate_by_bank_and_rating(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate sentiment scores by bank and rating.
        
        Args:
            df: DataFrame with sentiment analysis results
            
        Returns:
            Aggregated DataFrame
        """
        if "sentiment_score" not in df.columns:
            raise ValueError("DataFrame must have sentiment_score column")
        
        aggregation = {
            "sentiment_score": ["mean", "std", "count"],
            "positive_score": "mean",
            "negative_score": "mean"
        }
        
        # Group by bank and rating
        grouped = df.groupby(["bank", "rating"]).agg(aggregation).reset_index()
        grouped.columns = ["bank", "rating", "mean_sentiment", "std_sentiment", "count", 
                          "mean_positive", "mean_negative"]
        
        # Add sentiment distribution
        sentiment_dist = df.groupby(["bank", "rating", "sentiment_label"]).size().reset_index(name="count")
        sentiment_dist = sentiment_dist.pivot_table(
            index=["bank", "rating"],
            columns="sentiment_label",
            values="count",
            fill_value=0
        ).reset_index()
        
        # Merge
        result = grouped.merge(sentiment_dist, on=["bank", "rating"], how="left")
        
        return result

