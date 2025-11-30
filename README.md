# Customer Experience Analytics - Fintech App Review Analysis

A professional data engineering and NLP project for analyzing Google Play Store reviews of Ethiopian banking mobile applications. This project implements end-to-end data collection, preprocessing, sentiment analysis, and thematic analysis.

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Quick Start](#quick-start)
- [Project Setup](#project-setup)
- [Tasks Overview](#tasks-overview)
- [Task 1: Data Collection and Preprocessing](#task-1-data-collection-and-preprocessing)
- [Task 2: Sentiment and Thematic Analysis](#task-2-sentiment-and-thematic-analysis)
- [Project Structure](#project-structure)
- [Usage Guide](#usage-guide)
- [Architecture](#architecture)
- [Testing](#testing)
- [Configuration](#configuration)
- [Development Guide](#development-guide)

## Project Overview

This project analyzes user reviews from Google Play Store for three Ethiopian banking mobile applications:

- **Commercial Bank of Ethiopia (CBE)**
- **Bank of Abyssinia (BOA)**
- **Dashen Bank**

### Objectives

1. **Data Collection**: Gather comprehensive review data from Google Play Store
2. **Data Preprocessing**: Clean and standardize review data
3. **Sentiment Analysis**: Quantify review sentiment using DistilBERT
4. **Thematic Analysis**: Identify recurring themes and pain points
5. **Insights Generation**: Prepare data for visualization and reporting

## Quick Start

```bash
# 1. Clone the repository
git clone <repository-url>
cd fintech-app-customer-experience-analytics

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install PyTorch (CPU version)
pip install torch==2.2.2+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html

# 4. Install dependencies
pip install -r requirements.txt

# 5. Download spaCy model
python -m spacy download en_core_web_sm

# 6. Run Task 1: Data Collection and Preprocessing
python scripts/task_1_data_collection.py

# 7. Run Task 2: Sentiment and Thematic Analysis
python scripts/task_2_sentiment_analysis.py
```

## Project Setup

### Prerequisites

- **Python**: 3.8 or higher
- **Git**: For version control
- **Virtual Environment**: Python venv support
- **Memory**: ~4GB RAM recommended (for NLP models)
- **Disk Space**: ~2GB for dependencies and models

### Installation Steps

#### 1. Virtual Environment Setup

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows
```

#### 2. Install PyTorch (CPU Version)

For resource efficiency, we use CPU-only PyTorch:

```bash
pip install torch==2.2.2+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html
```

#### 3. Install Project Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Download NLP Models

```bash
# Download spaCy English model
python -m spacy download en_core_web_sm

# NLTK data will be downloaded automatically on first use
```

### Dependencies

#### Core Dependencies
- `pandas>=2.0.0` - Data manipulation and analysis
- `numpy>=1.24.0,<2.0.0` - Numerical operations
- `pyyaml>=6.0` - Configuration file parsing

#### Data Collection
- `google-play-scraper>=1.2.2` - Google Play Store review scraping

#### NLP and Machine Learning
- `transformers>=4.30.0` - HuggingFace Transformers (DistilBERT)
- `torch>=2.0.0` - PyTorch deep learning framework
- `scikit-learn>=1.3.0` - TF-IDF vectorization
- `spacy>=3.5.0` - Advanced NLP processing
- `nltk>=3.8.0` - Text preprocessing utilities

#### Utilities
- `tqdm>=4.65.0` - Progress bars
- `python-dotenv>=1.0.0` - Environment variable management

## Tasks Overview

| Task | Status | Description | Output |
|------|--------|-------------|--------|
| **Task 1** | ✅ Complete | Data Collection and Preprocessing | `data/processed/processed_reviews.csv` |
| **Task 2** | ✅ Complete | Sentiment and Thematic Analysis | `data/interim/analyzed_reviews.csv` |
| **Task 3** | 🔄 Pending | Database Storage (PostgreSQL) | Database tables |
| **Task 4** | 🔄 Pending | Insights and Visualization | Reports and dashboards |

## Task 1: Data Collection and Preprocessing

### Overview

Collects and preprocesses Google Play Store reviews for three Ethiopian banking apps.

### Features

- **Multi-language Support**: Collects reviews in Amharic (Ethiopia) and English (US)
- **Batch Processing**: Processes reviews in batches of 100 per API request
- **Retry Logic**: Automatic retry with up to 5 attempts for failed requests
- **Data Cleaning**: Duplicate removal, length filtering, date normalization
- **Quality Validation**: Ensures data completeness and validity

### Data Collection Results

| Bank | App ID | Reviews Collected | Processed Reviews | Average Rating |
|------|--------|-------------------|-------------------|----------------|
| CBE | `com.combanketh.mobilebanking` | 8,174 | 7,931 | 4.05 |
| BOA | `com.boa.boaMobileBanking` | 1,200 | 1,168 | 3.10 |
| Dashen | `com.cr2.amolelight` | 507 | 495 | 4.11 |
| **Total** | - | **9,881** | **9,594** | **3.95** |

### Preprocessing Steps

1. **Duplicate Removal**: Removed 41 duplicates (based on review text, bank, user name)
2. **Length Filtering**: Filtered 246 reviews (< 3 or > 1000 characters)
3. **Date Normalization**: Standardized to YYYY-MM-DD format
4. **Data Validation**: Ensured ratings are 1-5, removed missing critical fields

### Quality Metrics

- ✅ **Error Rate**: 0.0% (meets < 5% requirement)
- ✅ **Missing Data**: 0 (all critical fields present)
- ✅ **Invalid Ratings**: 0 (all ratings within 1-5 range)
- ✅ **Data Completeness**: 100%

### Usage

```bash
python scripts/task_1_data_collection.py
```

### Output Files

- `data/raw/raw_reviews.csv` - Original collected reviews (9,881 rows)
- `data/processed/processed_reviews.csv` - Cleaned and processed reviews (9,594 rows)
- `logs/YYYYMMDD.log` - Execution logs

## Task 2: Sentiment and Thematic Analysis

### Overview

Performs sentiment analysis using DistilBERT and identifies recurring themes using keyword extraction and clustering.

### Components

#### 1. Sentiment Analysis

- **Model**: `distilbert-base-uncased-finetuned-sst-2-english`
- **Method**: Transformer-based deep learning model
- **Outputs**:
  - `sentiment_label`: positive, negative, or neutral
  - `sentiment_score`: Confidence score (0-1)
  - `positive_score`: Probability of positive sentiment
  - `negative_score`: Probability of negative sentiment

#### 2. Text Preprocessing

- **Tokenization**: NLTK word tokenization
- **Stop-word Removal**: Removes common English stop words
- **Lemmatization**: Reduces words to root forms
- **Text Cleaning**: Removes URLs, emails, special characters

#### 3. Thematic Analysis

- **Keyword Extraction**:
  - **TF-IDF**: Extracts significant n-grams (unigrams, bigrams, trigrams)
  - **spaCy**: Extracts nouns, verbs, adjectives using POS tagging
- **Theme Clustering**: Rule-based clustering into 7 predefined themes:
  1. Account Access Issues
  2. Transaction Performance
  3. User Interface & Experience
  4. Customer Support
  5. Feature Requests
  6. App Reliability
  7. Network & Connectivity

### Features

- ✅ **Batch Processing**: Efficient processing of large datasets
- ✅ **Multi-bank Analysis**: Performs analysis per bank with bank-specific themes
- ✅ **Aggregation**: Creates sentiment statistics by bank and rating
- ✅ **Modular Design**: Reusable components for different use cases

### Usage

```bash
python scripts/task_2_sentiment_analysis.py
```

### Output Files

- `data/interim/analyzed_reviews.csv` - Full analysis results with sentiment and themes
- `data/results/sentiment_by_bank_rating.csv` - Aggregated sentiment statistics

### Output Schema

The `analyzed_reviews.csv` file contains:

| Column | Description |
|--------|-------------|
| `review_id` | Unique identifier for each review |
| `review` | Original review text |
| `processed_text` | Preprocessed text (tokenized, lemmatized) |
| `sentiment_label` | positive, negative, or neutral |
| `sentiment_score` | Confidence score (0-1) |
| `positive_score` | Probability of positive sentiment |
| `negative_score` | Probability of negative sentiment |
| `identified_themes` | Comma-separated list of assigned themes |
| `bank` | Bank code (CBE, BOA, DASHEN) |
| `rating` | Star rating (1-5) |
| `date` | Review date (YYYY-MM-DD) |
| `user_name` | Reviewer name |
| `source` | Data source (Google Play) |
| `app_name` | Application name |

### Success Criteria

- ✅ **Sentiment Coverage**: 90%+ of reviews analyzed
- ✅ **Themes per Bank**: 3+ themes identified per bank
- ✅ **Modular Code**: Separate, reusable components
- ✅ **Minimum Requirements**:
  - Sentiment scores for 400+ reviews
  - 2+ themes per bank via keywords

## Project Structure

```
fintech-app-customer-experience-analytics/
│
├── config/                          # Configuration files
│   └── config.yaml                  # Main configuration (banks, paths, settings)
│
├── data/                            # Data directories
│   ├── all_banks_reviews.csv       # Original collected data
│   ├── raw/                        # Raw data storage
│   │   └── raw_reviews.csv
│   ├── processed/                  # Processed data storage
│   │   └── processed_reviews.csv
│   ├── interim/                   # Intermediate analysis results
│   │   └── analyzed_reviews.csv
│   └── results/                    # Aggregated results
│       └── sentiment_by_bank_rating.csv
│
├── src/                             # Source code
│   ├── data_collection/            # Data collection modules
│   │   ├── scraper.py             # Google Play Store scraper
│   │   └── data_loader.py          # Data loading utilities
│   ├── data_processing/           # Data processing modules
│   │   └── preprocessor.py        # Data preprocessing pipeline
│   ├── analysis/                   # Analysis modules (Task 2)
│   │   ├── sentiment_analyzer.py  # DistilBERT sentiment analysis
│   │   ├── thematic_analyzer.py   # Keyword extraction and theme clustering
│   │   └── text_preprocessor.py   # NLP text preprocessing
│   ├── pipeline/                   # Pipeline orchestration
│   │   ├── data_collection_pipeline.py      # Task 1 pipeline
│   │   └── sentiment_analysis_pipeline.py   # Task 2 pipeline
│   └── utils/                      # Utility modules
│       ├── config_loader.py        # Configuration management
│       └── logger.py               # Logging utilities
│
├── scripts/                         # Execution scripts
│   ├── task_1_data_collection.py  # Task 1 execution script
│   └── task_2_sentiment_analysis.py # Task 2 execution script
│
├── tests/                          # Test suite
│   ├── test_preprocessor.py       # Preprocessor unit tests
│   ├── test_sentiment_analysis.py # Sentiment analysis tests
│   └── verification/              # Verification scripts
│       ├── verify_setup.py
│       └── verify_data_quality.py
│
├── logs/                           # Application logs
│   └── YYYYMMDD.log
│
├── requirements.txt                # Python dependencies
├── .gitignore                      # Git ignore rules
├── TASK2_SUMMARY.md               # Task 2 implementation details
└── README.md                       # This file
```

## Usage Guide

### Running Individual Tasks

#### Task 1: Data Collection and Preprocessing

```bash
# Activate virtual environment
source venv/bin/activate

# Run Task 1
python scripts/task_1_data_collection.py
```

**Expected Output**:
- Raw data: `data/raw/raw_reviews.csv`
- Processed data: `data/processed/processed_reviews.csv`
- Logs: `logs/YYYYMMDD.log`

#### Task 2: Sentiment and Thematic Analysis

```bash
# Ensure Task 1 output exists
ls data/processed/processed_reviews.csv

# Run Task 2
python scripts/task_2_sentiment_analysis.py
```

**Expected Output**:
- Analyzed reviews: `data/interim/analyzed_reviews.csv`
- Aggregations: `data/results/sentiment_by_bank_rating.csv`

### Running Complete Pipeline

```bash
# Run both tasks sequentially
python scripts/task_1_data_collection.py && \
python scripts/task_2_sentiment_analysis.py
```

### Using Python API

You can also use the pipeline classes programmatically:

```python
from src.pipeline.data_collection_pipeline import DataCollectionPipeline
from src.pipeline.sentiment_analysis_pipeline import SentimentAnalysisPipeline
from src.utils.config_loader import load_config
from pathlib import Path

# Task 1
config = load_config()
project_root = Path(__file__).parent
pipeline1 = DataCollectionPipeline(config=config, project_root=project_root)
results1 = pipeline1.run()

# Task 2
pipeline2 = SentimentAnalysisPipeline(project_root=project_root)
results2 = pipeline2.run()
```

## Architecture

### Design Principles

- **Object-Oriented Design**: Clear class-based structure
- **Separation of Concerns**: Each module has a single responsibility
- **Modularity**: Components can be used independently
- **Testability**: Easy to unit test individual components
- **Extensibility**: Easy to add new features or modify behavior

### Key Components

#### Task 1 Components

- **`DataCollectionPipeline`**: Main orchestrator for data collection and preprocessing
- **`PlayStoreScraper`**: Handles web scraping with multi-language support
- **`DataLoader`**: Manages loading and preparation of existing data files
- **`DataPreprocessor`**: Implements data cleaning and validation logic

#### Task 2 Components

- **`SentimentAnalysisPipeline`**: Orchestrates sentiment and thematic analysis
- **`SentimentAnalyzer`**: DistilBERT-based sentiment classification
- **`ThematicAnalyzer`**: Keyword extraction and theme clustering
- **`TextPreprocessor`**: NLP text preprocessing (tokenization, lemmatization)

### Data Flow

```
Google Play Store
    ↓
[Task 1: Data Collection]
    ↓
Raw Reviews (CSV)
    ↓
[Task 1: Preprocessing]
    ↓
Processed Reviews (CSV)
    ↓
[Task 2: Text Preprocessing]
    ↓
[Task 2: Sentiment Analysis]
    ↓
[Task 2: Thematic Analysis]
    ↓
Analyzed Reviews (CSV)
    ↓
[Task 3: Database Storage] (Pending)
    ↓
[Task 4: Visualization] (Pending)
```

## Testing

### Run All Tests

```bash
python -m unittest discover tests -v
```

### Run Specific Test Suites

```bash
# Task 1 tests
python -m unittest tests.test_preprocessor -v

# Task 2 tests
python -m unittest tests.test_sentiment_analysis -v
```

### Verification Scripts

```bash
# Verify setup and dependencies
python tests/verification/verify_setup.py

# Verify data quality
python tests/verification/verify_data_quality.py
```

### Test Coverage

- ✅ Data preprocessing (duplicate removal, text cleaning, date normalization)
- ✅ Sentiment analyzer initialization and prediction
- ✅ Text preprocessing (tokenization, stopwords, lemmatization)
- ✅ Thematic analyzer and keyword extraction

## Configuration

The project uses a YAML-based configuration system located in `config/config.yaml`.

### Key Configuration Areas

#### Bank Configuration
```yaml
banks:
  - name: "Commercial Bank of Ethiopia"
    app_id: "com.combanketh.mobilebanking"
    code: "CBE"
```

#### Data Source Settings
```yaml
data_source:
  use_existing_data: true
  existing_data_file: "data/all_banks_reviews.csv"
  scrape_new_data: false
```

#### Scraping Parameters
```yaml
scraping:
  min_reviews_per_bank: 400
  batch_size: 100
  retry_attempts: 5
  languages:
    - lang: "am"
      country: "ET"
    - lang: "en"
      country: "US"
```

#### Processing Options
```yaml
processing:
  remove_duplicates: true
  min_review_length: 3
  max_review_length: 1000
  date_format: "%Y-%m-%d"
```

## Development Guide

### Adding New Features

1. **Create a new module** in the appropriate `src/` subdirectory
2. **Write unit tests** in `tests/`
3. **Update configuration** if needed
4. **Document** in README or module docstrings
5. **Commit** with descriptive messages

### Code Style

- Follow PEP 8 Python style guide
- Use type hints where appropriate
- Write docstrings for all classes and functions
- Keep functions focused and single-purpose

### Git Workflow

```bash
# Create feature branch
git checkout -b task-2

# Make changes and commit
git add .
git commit -m "Descriptive commit message"

# Push to remote
git push origin task-2

# Create pull request for review
```

### Branch Strategy

- **`main`**: Stable production code
- **`task-1`**: Task 1 development
- **`task-2`**: Task 2 development
- **Feature branches**: For specific features or fixes

### Debugging

Enable debug logging by modifying the logger level in `src/utils/logger.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

### Performance Optimization

- **Sentiment Analysis**: Uses batch processing (default: 32 reviews per batch)
- **Memory Management**: Processes data in chunks for large datasets
- **Caching**: Model loading is done once per pipeline run

### Common Issues and Solutions

#### Issue: NumPy version compatibility
```bash
pip install "numpy>=1.24.0,<2.0.0"
```

#### Issue: spaCy model not found
```bash
python -m spacy download en_core_web_sm
```

#### Issue: NLTK data missing
The code automatically downloads NLTK data on first use. If issues persist:
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
```

## Next Steps

After completing Task 1 and Task 2:

- **Task 3**: Database storage in PostgreSQL
- **Task 4**: Insights generation and visualization

## Version Control

The project uses Git for version control with a branch-based workflow:

- **Main Branch**: Stable production code
- **Task Branches**: Feature development (task-1, task-2, etc.)
- **Commit Strategy**: Meaningful commit messages with logical groupings

## License

This project is part of a training portfolio for data engineering and analytics.

## Contact

For questions or support, please refer to the project facilitators or the designated communication channels.

---

**Last Updated**: November 2025  
**Status**: Task 1 Complete ✅ | Task 2 Complete ✅
