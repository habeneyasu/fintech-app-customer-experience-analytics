"""Verify data quality of processed reviews"""
import sys
from pathlib import Path
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data_processing.preprocessor import DataPreprocessor


def verify_data_quality(file_path: Path):
    """Verify data quality of a CSV file"""
    print(f"Verifying: {file_path}")
    print("-" * 60)
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    try:
        df = pd.read_csv(file_path)
        print(f"✅ File loaded: {len(df)} rows")
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return False
    
    # Required columns
    required_cols = ['review', 'rating', 'bank']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        print(f"❌ Missing columns: {missing_cols}")
        return False
    print(f"✅ Required columns present")
    
    # Check for missing data
    missing_review = df['review'].isna().sum()
    missing_rating = df['rating'].isna().sum()
    missing_bank = df['bank'].isna().sum()
    
    total = len(df)
    error_rate = (missing_review + missing_rating + missing_bank) / (total * 3) * 100
    
    print(f"  Missing reviews: {missing_review} ({missing_review/total*100:.2f}%)")
    print(f"  Missing ratings: {missing_rating} ({missing_rating/total*100:.2f}%)")
    print(f"  Missing banks: {missing_bank} ({missing_bank/total*100:.2f}%)")
    print(f"  Overall error rate: {error_rate:.2f}%")
    
    if error_rate < 5:
        print("✅ Error rate < 5%")
    else:
        print("⚠️  Error rate >= 5%")
    
    # Check rating validity
    invalid_ratings = df[~df['rating'].between(1, 5)]['rating'].count()
    if invalid_ratings == 0:
        print("✅ All ratings are valid (1-5)")
    else:
        print(f"❌ Invalid ratings: {invalid_ratings}")
    
    # Check duplicates
    duplicates = df.duplicated(subset=['review', 'bank']).sum()
    if duplicates == 0:
        print("✅ No duplicates found")
    else:
        print(f"⚠️  Duplicates found: {duplicates}")
    
    # Check data per bank
    print("\nReviews per bank:")
    bank_counts = df['bank'].value_counts()
    for bank, count in bank_counts.items():
        print(f"  {bank}: {count} reviews")
        if count < 400:
            print(f"    ⚠️  Less than 400 reviews (minimum requirement)")
    
    return True


def main():
    """Main verification function"""
    project_root = Path(__file__).parent.parent.parent
    
    print("=" * 60)
    print("DATA QUALITY VERIFICATION")
    print("=" * 60)
    print()
    
    # Check processed data
    processed_file = project_root / "data" / "processed" / "processed_reviews.csv"
    if processed_file.exists():
        verify_data_quality(processed_file)
    else:
        print("⚠️  Processed data file not found")
        print("   Run Task 1 to generate processed data")
    
    print()
    
    # Check analyzed data
    analyzed_file = project_root / "data" / "interim" / "analyzed_reviews.csv"
    if analyzed_file.exists():
        print()
        verify_data_quality(analyzed_file)
        
        # Check for sentiment columns
        df = pd.read_csv(analyzed_file)
        if 'sentiment_label' in df.columns and 'sentiment_score' in df.columns:
            print("✅ Sentiment analysis columns present")
            sentiment_coverage = df['sentiment_label'].notna().sum() / len(df) * 100
            print(f"   Coverage: {sentiment_coverage:.1f}%")
            if sentiment_coverage >= 90:
                print("✅ Sentiment coverage >= 90%")
            else:
                print("⚠️  Sentiment coverage < 90%")
    else:
        print("⚠️  Analyzed data file not found")
        print("   Run Task 2 to generate analyzed data")


if __name__ == "__main__":
    main()

