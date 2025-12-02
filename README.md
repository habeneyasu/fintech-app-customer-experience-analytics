# Customer Experience Analytics - Fintech App Review Analysis

A professional data engineering and analytics project for collecting, analyzing, and deriving insights from Google Play Store reviews of Ethiopian banking mobile applications.

## Table of Contents

- [Project Overview](#project-overview)
- [Business Objective](#business-objective)
- [Dataset Overview](#dataset-overview)
- [Setup & Installation](#setup--installation)
- [Tasks Completed](#tasks-completed)
- [Technologies Used](#technologies-used)
- [Key Observations](#key-observations)
- [Best Practices](#best-practices)

---

## Project Overview

End-to-end analysis of customer reviews for three Ethiopian banking mobile applications:

- **Commercial Bank of Ethiopia (CBE)**
- **Bank of Abyssinia (BOA)**
- **Dashen Bank**

**Four Main Tasks:**
1. **Data Collection and Preprocessing**: Scrape and clean Google Play Store reviews
2. **Sentiment and Thematic Analysis**: Analyze sentiment using DistilBERT and identify themes
3. **Database Storage**: Store processed data in PostgreSQL
4. **Insights and Recommendations**: Generate actionable insights, visualizations, and recommendations

---

## Business Objective

Enhance mobile banking applications' user experience by providing:
- Customer sentiment analysis and trends
- Pain point identification
- Competitive benchmarking across banks
- Data-driven improvement recommendations
- Trend monitoring capabilities

---

## Dataset Overview

### Data Collection

- **Multi-language Support**: Amharic (Ethiopia) and English (US)
- **Batch Processing**: 100 reviews per API request
- **Total Reviews Collected**: 9,881 reviews

| Bank | App ID | Reviews Collected | Processed Reviews | Avg Rating |
|------|--------|------------------|-------------------|------------|
| Commercial Bank of Ethiopia | `com.combanketh.mobilebanking` | 8,174 | 7,931 | 4.05 |
| Bank of Abyssinia | `com.boa.boaMobileBanking` | 1,200 | 1,168 | 3.10 |
| Dashen Bank | `com.cr2.amolelight` | 507 | 495 | 4.11 |

**Final Processed Reviews**: 9,594

### Data Quality

- **Error Rate**: 0.0% (meets < 5% requirement)
- **Data Completeness**: 100%
- **Sentiment Coverage**: 100% (all reviews analyzed)

### Dataset Columns

`review_text`, `rating`, `review_date`, `bank`, `user_name`, `sentiment_label`, `sentiment_score`, `themes`

---

## Setup & Installation

### 1. Clone and Setup

```bash
git clone https://github.com/habeneyasu/fintech-app-customer-experience-analytics.git
cd fintech-app-customer-experience-analytics

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install PyTorch (CPU version)
pip install torch==2.2.2+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables

```bash
cp .env.example .env
# Edit .env with your database credentials
```

`.env` file:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=bank_reviews
DB_USER=postgres
DB_PASSWORD=your_password_here
```

### 3. PostgreSQL Setup

```bash
createdb bank_reviews
# Schema created automatically when running Task 3
```

### 4. Verify Setup

```bash
python tests/verification/verify_setup.py
```

---

## Tasks Completed

### Task 1: Data Collection and Preprocessing

**Objective**: Collect and preprocess Google Play Store reviews.

**Activities**: Multi-language collection, duplicate removal (41), length filtering (246), date normalization, data validation.

**Results**:
- ✅ 9,594 processed reviews (exceeds 1,200+ requirement)
- ✅ Error rate: 0.0%
- ✅ All banks exceed minimum (CBE: 7,931, BOA: 1,168, Dashen: 495)

**Run**: `python scripts/task_1_data_collection.py`

**Output**: `data/processed/processed_reviews.csv`

---

### Task 2: Sentiment and Thematic Analysis

**Objective**: Analyze sentiment using DistilBERT and identify recurring themes.

**Activities**:
- **Sentiment Analysis**: DistilBERT model (`distilbert-base-uncased-finetuned-sst-2-english`)
- **Text Preprocessing**: Tokenization, lemmatization, POS tagging (spaCy)
- **Thematic Analysis**: TF-IDF keyword extraction, rule-based clustering
- **7 Themes Identified**: Account Access, Transaction Performance, UI/UX, Customer Support, Feature Requests, App Reliability, Network & Connectivity

**Results**:
- ✅ 100% sentiment coverage (all 9,594 reviews analyzed)
- ✅ 2+ themes per bank identified

**Run**: `python scripts/task_2_sentiment_analysis.py`

**Output**: `data/interim/analyzed_reviews.csv`

---

### Task 3: Database Storage in PostgreSQL

**Objective**: Store processed data in PostgreSQL for persistent storage.

**Database Schema**:
- **Banks Table**: `bank_id`, `bank_name`, `app_name`, `description`, `created_at`
- **Reviews Table**: `review_id`, `bank_id` (FK), `review_text`, `rating`, `review_date`, `sentiment_label`, `sentiment_score`, `source`, `created_at`

**Activities**: Connection management, batch insertion (1000 per batch), data integrity verification, automatic schema creation.

**Results**:
- ✅ 9,594+ reviews inserted
- ✅ 3 banks loaded with foreign key relationships
- ✅ 100% data integrity verified

**Test**: `python scripts/test_database_insertion.py`

**Run**: `python scripts/task_3_database_storage.py`

**Verify**: `python scripts/verify_database.py`

**Schema**: `database/schema.sql`

---

### Task 4: Insights and Recommendations

**Objective**: Derive insights, create visualizations, and provide recommendations.

**Activities**:
- **Insights**: Identify 2+ drivers and pain points per bank, bank comparison
- **Visualizations**: Sentiment distribution, rating distribution, sentiment trends, bank comparison, word clouds, drivers/pain points charts
- **Recommendations**: 2+ improvement suggestions per bank with priority and expected impact
- **Ethics**: Notes on review biases and mitigation strategies

**Results**:
- ✅ 2+ drivers and pain points per bank with evidence
- ✅ 3-5 visualizations generated
- ✅ Practical recommendations for each bank
- ✅ 10-page final report with insights, visualizations, and ethics considerations

**Run**: `python scripts/task_4_insights.py`

**Output**:
- `data/results/visualizations/` - All charts and plots
- `data/results/insights.json` - Structured insights
- `data/results/FINAL_REPORT.md` - 10-page comprehensive report

---

## Technologies Used

### Core
- **Python 3.8+**, **PostgreSQL 15+**, **Git & GitHub**

### Data Processing
- **Pandas**, **NumPy**, **scikit-learn** (TF-IDF)

### NLP
- **Transformers (Hugging Face)** - DistilBERT sentiment analysis
- **spaCy** - Advanced NLP and POS tagging
- **NLTK** - Text preprocessing

### Visualization
- **Matplotlib**, **Seaborn**, **WordCloud**, **Pillow**

### Database & Infrastructure
- **psycopg2-binary**, **python-dotenv**

### Web Scraping
- **google-play-scraper**

### Utilities
- **PyYAML**, **tqdm**, **logging**

---

## Key Observations

### Data & Quality
- CBE dominates review volume (7,931 reviews, 82.6% of total)
- 0.0% error rate achieved through robust preprocessing
- Successfully collected multi-language reviews (Amharic and English)

### Sentiment Analysis
- Overall positive sentiment: CBE (4.05), Dashen (4.11) show strong satisfaction
- BOA lower ratings (3.10) suggest improvement opportunities
- 100% sentiment coverage with DistilBERT

### Thematic Insights
- Common pain points: Account access issues, transaction performance, network connectivity
- Feature requests: Budgeting tools and enhanced security
- Mixed UI/UX feedback on navigation and interface design

### Bank Comparison
- Dashen leads in ratings (4.11 average)
- CBE has highest volume (largest user base)
- BOA shows improvement opportunity (lower ratings)

### Database & Performance
- Efficient batch processing (1000 records per batch)
- 100% data integrity with validated foreign keys
- Scalable schema supports future expansion

### Visualization Insights
- Positive sentiment trending upward for CBE and Dashen
- Rating distribution clusters around 4-5 stars
- Word clouds: "easy", "fast", "good" (positive); "slow", "crash", "error" (negative)

### Ethics & Biases
- Potential negative skew (users more likely to review after negative experiences)
- Selection bias (Google Play only, excludes iOS)
- Language bias (English reviews may over-represent certain demographics)
- Mitigation: Analysis acknowledges limitations and provides context

---

## Best Practices

### Git & GitHub Workflow

**Branch Strategy**:
- `main`: Stable, production-ready code (merged via PRs only)
- `task-*`: Feature branches for specific tasks

**Workflow**:
1. Create feature branch from `main`
2. Develop and commit with descriptive messages
3. Create PR with scope, testing, and impact analysis
4. Review and merge to `main`

**PR Requirements**: Complete description, scope, testing results, impact analysis, all checklist items completed.

**Benefits**: Clear history, better change isolation, review habits, professional practices.

### Code Best Practices

**Architecture**: Object-oriented design with clear separation of concerns, modular structure, pipeline pattern.

**Code Quality**: PEP 8 compliance, comprehensive error handling, type hints, proper docstrings.

**Testing**: Unit tests for components, integration tests for pipelines, verification scripts for setup and data quality.

**Documentation**: Docstrings for all classes/functions, inline comments for complex logic, comprehensive README.

**Security**: Environment variables for credentials, `.env` excluded from Git, no PII storage.

**Performance**: Batch processing, lazy loading, progress bars, context managers for resources.

**Maintainability**: Configuration-driven (YAML), comprehensive logging, clear commit history, feature branches.

---

## Project Structure

```
fintech-app-customer-experience-analytics/
├── config/              # Configuration files
├── data/                # Data directories (raw, processed, interim, results)
├── database/            # Database schema
├── src/                 # Source code
│   ├── data_collection/
│   ├── data_processing/
│   ├── analysis/        # Task 2: Sentiment & thematic analysis
│   ├── database/        # Task 3: PostgreSQL integration
│   ├── insights/        # Task 4: Insights & visualizations
│   ├── pipeline/        # Pipeline orchestration
│   └── utils/           # Utilities
├── scripts/             # Execution scripts (task_1-4)
├── tests/               # Test suite
├── logs/                # Application logs
├── .env.example         # Environment variables template
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

---

## Testing

```bash
# Unit tests
python -m unittest discover tests -v

# Verify setup
python tests/verification/verify_setup.py

# Verify data quality
python tests/verification/verify_data_quality.py

# Test database connection
python scripts/test_database_insertion.py
```

---

## Configuration

YAML-based configuration in `config/config.yaml`:
- Bank configuration (App IDs, bank codes)
- Data source settings
- Scraping parameters (languages, batch sizes, retries)
- Processing options (filters, date formats)
- Path configuration

---

## License

This project is part of a training portfolio for data engineering and analytics.

---

**Last Updated**: December 2025  
**Status**: Task 1 Complete ✅ | Task 2 Complete ✅ | Task 3 Complete ✅ | Task 4 Complete ✅
