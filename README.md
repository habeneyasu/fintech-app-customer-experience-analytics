# Customer Experience Analytics - Fintech App Review Analysis

A professional data engineering and analytics project for collecting, analyzing, and deriving insights from Google Play Store reviews of Ethiopian banking mobile applications.

## Table of Contents

- [Project Overview](#project-overview)
- [Business Objective](#business-objective)
- [Dataset Overview](#dataset-overview)
- [Folder Structure](#folder-structure)
- [Setup & Installation](#setup--installation)
- [Tasks Completed](#tasks-completed)
- [Technologies Used](#technologies-used)
- [Key Observations](#key-observations)
- [Git & GitHub Best Practices](#git--github-best-practices)
- [Code Best Practices](#code-best-practices)

---

## Project Overview

This project focuses on end-to-end analysis of customer reviews for three Ethiopian banking mobile applications:

- **Commercial Bank of Ethiopia (CBE)**
- **Bank of Abyssinia (BOA)**
- **Dashen Bank**

The project encompasses four main tasks:

1. **Data Collection and Preprocessing**: Scrape and clean Google Play Store reviews
2. **Sentiment and Thematic Analysis**: Analyze sentiment using DistilBERT and identify themes
3. **Database Storage**: Store processed data in PostgreSQL for persistent storage
4. **Insights and Recommendations**: Generate actionable insights, visualizations, and recommendations

The objective is to gather comprehensive review data, analyze sentiment and themes, store it efficiently, and provide actionable insights for improving mobile banking applications.

---

## Business Objective

Ethiopian banks seek to enhance their mobile banking applications' user experience and customer satisfaction. This project provides:

- **Customer Sentiment Analysis**: Understand overall customer satisfaction and sentiment trends
- **Pain Point Identification**: Identify recurring issues affecting user experience
- **Competitive Benchmarking**: Compare performance across different banking apps
- **Actionable Recommendations**: Data-driven suggestions for app improvements
- **Trend Monitoring**: Track sentiment and rating changes over time

The analysis helps banks prioritize development efforts, improve customer retention, and enhance their competitive position in the digital banking space.

---

## Dataset Overview

The dataset contains Google Play Store reviews collected from three Ethiopian banking mobile applications.

### Data Collection Methodology

Reviews were collected using a custom scraping script with:

- **Multi-language Support**: Collects reviews in both Amharic (Ethiopia) and English (US)
- **Batch Processing**: Processes reviews in batches of 100 per API request
- **Retry Logic**: Automatic retry mechanism with up to 5 attempts for failed requests
- **Continuation Token Handling**: Efficiently handles pagination through review pages
- **Error Handling**: Robust error handling with graceful degradation

### Bank Applications

| Bank | App ID | Reviews Collected |
|------|--------|-------------------|
| Commercial Bank of Ethiopia | `com.combanketh.mobilebanking` | 8,174 |
| Bank of Abyssinia | `com.boa.boaMobileBanking` | 1,200 |
| Dashen Bank | `com.cr2.amolelight` | 507 |

**Total Reviews Collected**: 9,881 reviews

### Dataset Columns

| Column | Description |
|--------|-------------|
| `review_text` | The actual review content |
| `rating` | Star rating (1-5) |
| `review_date` | Date of the review |
| `bank` | Bank name (CBE, BOA, Dashen) |
| `user_name` | Reviewer username |
| `sentiment_label` | Sentiment classification (Positive, Negative, Neutral) |
| `sentiment_score` | Sentiment confidence score (0-1) |
| `themes` | Identified themes/keywords |

### Data Quality Metrics

- **Error Rate**: 0.0% (meets < 5% requirement)
- **Missing Data**: 0 (all critical fields present)
- **Invalid Ratings**: 0 (all ratings within 1-5 range)
- **Data Completeness**: 100%

### Final Review Distribution

| Bank | Processed Reviews | Average Rating |
|------|------------------|----------------|
| CBE | 7,931 | 4.05 |
| BOA | 1,168 | 3.10 |
| Dashen | 495 | 4.11 |

**Total Processed Reviews**: 9,594

Cleaned datasets are saved in `/data/processed/` and `/data/interim/` (ignored in git).

---

## Folder Structure

```
fintech-app-customer-experience-analytics/
│
├── config/                          # Configuration files
│   └── config.yaml                  # Main configuration
│
├── data/                            # Data directories
│   ├── all_banks_reviews.csv       # Original collected data
│   ├── raw/                        # Raw data storage
│   │   └── raw_reviews.csv
│   ├── processed/                  # Processed data storage
│   │   └── processed_reviews.csv
│   ├── interim/                    # Intermediate analysis results
│   │   └── analyzed_reviews.csv
│   └── results/                    # Aggregated results
│       ├── visualizations/         # Generated charts and plots
│       ├── insights.json           # Structured insights
│       └── FINAL_REPORT.md         # 10-page comprehensive report
│
├── database/                        # Database schema
│   └── schema.sql                  # PostgreSQL schema definition
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
│   ├── database/                   # Database modules (Task 3)
│   │   ├── db_connection.py       # PostgreSQL connection manager
│   │   └── db_loader.py           # Data loading into database
│   ├── insights/                    # Insights modules (Task 4)
│   │   ├── insights_generator.py  # Drivers, pain points, comparisons
│   │   ├── visualization.py        # Charts and plots
│   │   └── report_generator.py    # Final report generation
│   ├── pipeline/                   # Pipeline orchestration
│   │   ├── data_collection_pipeline.py      # Task 1 pipeline
│   │   ├── sentiment_analysis_pipeline.py   # Task 2 pipeline
│   │   ├── database_pipeline.py             # Task 3 pipeline
│   │   └── insights_pipeline.py             # Task 4 pipeline
│   └── utils/                      # Utility modules
│       ├── config_loader.py        # Configuration management
│       └── logger.py               # Logging utilities
│
├── scripts/                         # Execution scripts
│   ├── task_1_data_collection.py  # Task 1 execution
│   ├── task_2_sentiment_analysis.py # Task 2 execution
│   ├── task_3_database_storage.py  # Task 3 execution
│   ├── task_4_insights.py          # Task 4 execution
│   ├── test_database_insertion.py  # Database testing
│   └── verify_database.py          # Database verification
│
├── tests/                          # Test suite
│   ├── test_preprocessor.py       # Preprocessor unit tests
│   ├── test_sentiment_analysis.py # Sentiment analysis tests
│   └── verification/              # Verification scripts
│       ├── verify_setup.py
│       └── verify_data_quality.py
│
├── logs/                           # Application logs
│
├── .env.example                    # Environment variables template
├── requirements.txt                # Python dependencies
├── .gitignore                      # Git ignore rules
└── README.md                       # This file
```

---

## Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/habeneyasu/fintech-app-customer-experience-analytics.git
cd fintech-app-customer-experience-analytics
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### 3. Install PyTorch (CPU version for resource efficiency)

```bash
pip install torch==2.2.2+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Set Up Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your database credentials
# The .env file is already in .gitignore and will NOT be committed
```

The `.env` file should contain:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=bank_reviews
DB_USER=postgres
DB_PASSWORD=your_password_here
```

### 6. Set Up PostgreSQL Database (for Task 3)

```bash
# Install PostgreSQL (if not already installed)
# Create database
createdb bank_reviews

# Or using psql
psql -U postgres
CREATE DATABASE bank_reviews;
\q

# Schema will be created automatically when running Task 3
# Or manually: psql -d bank_reviews -f database/schema.sql
```

### 7. Verify Setup

```bash
# Verify Python environment
python tests/verification/verify_setup.py

# Verify data quality (after Task 1)
python tests/verification/verify_data_quality.py
```

---

## Tasks Completed

### Task 1: Data Collection and Preprocessing

**Objective**: Collect and preprocess Google Play Store reviews for three Ethiopian banking apps.

**Activities Performed**:
- Multi-language review collection (Amharic and English)
- Duplicate removal (41 duplicates removed)
- Length filtering (246 reviews filtered)
- Date normalization (YYYY-MM-DD format)
- Data validation (ratings 1-5, no missing critical fields)
- Quality assurance (0.0% error rate)

**Results**:
- ✅ **9,594 processed reviews** (exceeds 1,200+ requirement)
- ✅ **Error rate: 0.0%** (meets < 5% requirement)
- ✅ **All banks exceed minimum**: CBE (7,931), BOA (1,168), Dashen (495)
- ✅ **Clean CSV dataset** saved in standardized format

**Output Files**:
- `data/raw/raw_reviews.csv` - 9,881 original reviews
- `data/processed/processed_reviews.csv` - 9,594 cleaned reviews

**Run Task 1**:
```bash
python scripts/task_1_data_collection.py
```

---

### Task 2: Sentiment and Thematic Analysis

**Objective**: Analyze sentiment using DistilBERT and identify recurring themes in customer reviews.

**Activities Performed**:
- **Sentiment Analysis**: DistilBERT-based sentiment classification
  - Model: `distilbert-base-uncased-finetuned-sst-2-english`
  - Sentiment labels: Positive, Negative, Neutral
  - Confidence scores (0-1) for each prediction
- **Text Preprocessing**: 
  - Tokenization, lemmatization, stop-word removal
  - POS tagging using spaCy
- **Thematic Analysis**:
  - TF-IDF keyword extraction
  - Rule-based theme clustering
  - 7 predefined themes identified:
    1. Account Access Issues
    2. Transaction Performance
    3. User Interface & Experience
    4. Customer Support
    5. Feature Requests
    6. App Reliability
    7. Network & Connectivity
- **Aggregation**: Sentiment and themes aggregated by bank and rating

**Results**:
- ✅ **Sentiment coverage: 100%** (all 9,594 reviews analyzed)
- ✅ **2+ themes per bank** identified via keyword extraction
- ✅ **Modular, reusable components** for analysis pipeline

**Output Files**:
- `data/interim/analyzed_reviews.csv` - Reviews with sentiment and themes
- `data/results/sentiment_by_bank_rating.csv` - Aggregated sentiment metrics

**Run Task 2**:
```bash
python scripts/task_2_sentiment_analysis.py
```

---

### Task 3: Store Cleaned Data in PostgreSQL

**Objective**: Design and implement a relational database in PostgreSQL to persistently store cleaned and processed review data.

**Database Schema**:

**Banks Table**:
- `bank_id` (SERIAL PRIMARY KEY) - Unique identifier
- `bank_name` (VARCHAR(255) NOT NULL) - Bank name
- `app_name` (VARCHAR(255)) - Mobile app name
- `description` (TEXT) - Optional description
- `created_at` (TIMESTAMP) - Record creation timestamp

**Reviews Table**:
- `review_id` (SERIAL PRIMARY KEY) - Unique identifier
- `bank_id` (INT FOREIGN KEY) - References banks.bank_id
- `review_text` (TEXT NOT NULL) - Review content
- `rating` (NUMERIC(2,1)) - Star rating (1-5)
- `review_date` (DATE) - Review date
- `sentiment_label` (VARCHAR(50)) - Sentiment classification
- `sentiment_score` (NUMERIC(3,2)) - Sentiment confidence (0-1)
- `source` (VARCHAR(255)) - Data source (e.g., Google Play)
- `created_at` (TIMESTAMP) - Record insertion timestamp

**Activities Performed**:
- Database connection management with context managers
- Batch insertion for efficient data loading
- Data integrity verification (counts, averages, sentiment coverage)
- Automatic schema creation if tables don't exist

**Results**:
- ✅ **Working database connection** with environment variable configuration
- ✅ **9,594+ reviews inserted** (exceeds 1,000+ requirement)
- ✅ **3 banks loaded** with proper foreign key relationships
- ✅ **100% data integrity** verified

**Test Database Connection**:
```bash
python scripts/test_database_insertion.py
```

**Run Task 3**:
```bash
python scripts/task_3_database_storage.py
```

**Verify Database**:
```bash
python scripts/verify_database.py
```

**Schema File**: `database/schema.sql` includes table definitions, indexes, and constraints.

---

### Task 4: Insights and Recommendations

**Objective**: Derive insights from sentiment and themes, visualize results, and recommend app improvements.

**Activities Performed**:

**Insights Generation**:
- **Drivers Identification**: Identify 2+ positive drivers per bank (e.g., fast navigation, easy to use)
- **Pain Points Identification**: Identify 2+ pain points per bank (e.g., crashes, slow performance)
- **Bank Comparison**: Compare banks across key metrics (ratings, sentiment, review counts)

**Visualizations** (3-5 plots):
- Sentiment distribution by bank
- Rating distribution by bank
- Sentiment trends over time
- Bank comparison charts (ratings vs. sentiment)
- Word clouds (positive and negative reviews per bank)
- Drivers and pain points charts

**Recommendations**:
- 2+ improvement suggestions per bank based on identified pain points
- Priority-based recommendations with expected impact
- Ethics considerations (review biases, selection bias, mitigation strategies)

**Results**:
- ✅ **2+ drivers and pain points per bank** with evidence
- ✅ **3-5 visualizations** (sentiment, ratings, trends, word clouds)
- ✅ **Practical recommendations** for each bank
- ✅ **10-page final report** with all insights, visualizations, and ethics considerations
- ✅ **Bank comparison analysis** completed

**Output Files**:
- `data/results/visualizations/` - All generated charts and plots
- `data/results/insights.json` - Structured insights data
- `data/results/FINAL_REPORT.md` - 10-page comprehensive report

**Run Task 4**:
```bash
python scripts/task_4_insights.py
```

---

## Technologies Used

### Core Technologies
- **Python 3.8+** - Programming language
- **PostgreSQL 15+** - Relational database management system
- **Git & GitHub** - Version control and collaboration

### Data Processing & Analysis
- **Pandas** - Data manipulation and analysis
- **NumPy** - Numerical computing
- **scikit-learn** - Machine learning utilities (TF-IDF)

### Natural Language Processing
- **Transformers (Hugging Face)** - DistilBERT sentiment analysis
- **spaCy** - Advanced NLP processing and POS tagging
- **NLTK** - Text preprocessing utilities

### Data Visualization
- **Matplotlib** - Static plotting
- **Seaborn** - Statistical visualization
- **WordCloud** - Word cloud generation
- **Pillow (PIL)** - Image processing

### Database & Infrastructure
- **psycopg2-binary** - PostgreSQL adapter for Python
- **python-dotenv** - Environment variable management

### Web Scraping
- **google-play-scraper** - Google Play Store review collection

### Utilities
- **PyYAML** - Configuration file parsing
- **tqdm** - Progress bars
- **logging** - Application logging

### Development Tools
- **unittest** - Unit testing framework
- **pytest** (optional) - Advanced testing

---

## Key Observations

### Data Collection & Quality
- **CBE dominates review volume**: 7,931 reviews (82.6% of total), indicating highest user engagement
- **High data quality**: 0.0% error rate achieved through robust preprocessing pipeline
- **Multi-language support**: Successfully collected reviews in both Amharic and English

### Sentiment Analysis
- **Overall positive sentiment**: CBE (4.05 avg rating), Dashen (4.11 avg rating) show strong customer satisfaction
- **BOA lower ratings**: 3.10 average rating suggests areas for improvement
- **100% sentiment coverage**: All 9,594 reviews successfully analyzed with DistilBERT

### Thematic Insights
- **Common pain points across banks**: Account access issues, transaction performance, network connectivity
- **Feature requests**: Users consistently request budgeting tools and enhanced security features
- **UI/UX feedback**: Mixed feedback on navigation and interface design

### Bank Comparison
- **Dashen leads in ratings**: 4.11 average rating (highest among three banks)
- **CBE has highest volume**: Most reviews indicate largest user base and active engagement
- **BOA improvement opportunity**: Lower ratings suggest need for focused improvement initiatives

### Database Performance
- **Efficient batch processing**: 9,594 reviews inserted in 10 batches (1000 per batch)
- **Data integrity maintained**: 100% foreign key relationships validated
- **Scalable architecture**: Schema supports future expansion and additional banks

### Visualization Insights
- **Sentiment trends**: Positive sentiment increasing over time for CBE and Dashen
- **Rating distribution**: Most reviews cluster around 4-5 stars, indicating generally positive experience
- **Word clouds reveal**: "easy", "fast", "good" dominate positive reviews; "slow", "crash", "error" in negative reviews

### Ethics & Biases
- **Potential negative skew**: Users more likely to review after negative experiences
- **Selection bias**: Only Google Play Store reviews (excludes iOS users)
- **Language bias**: English reviews may over-represent certain demographics
- **Mitigation**: Analysis acknowledges limitations and provides context for findings

---

## Git & GitHub Best Practices

### Branch Strategy

The project uses a professional branch-based workflow:

- **`main`**: Stable, production-ready code. Only merged via pull requests.
- **`task-*`**: Feature branches for specific tasks (e.g., `task-1`, `task-2`, `task-3`, `task-4`)
- **`feature-*`**: Feature branches for other features

### Workflow Process

1. **Create Feature Branch**: Start from `main` and create a new branch
   ```bash
   git checkout main
   git pull origin main
   git checkout -b task-X
   ```

2. **Develop & Commit**: Make changes and commit with descriptive messages
   ```bash
   git add .
   git commit -m "Descriptive commit message"
   git push origin task-X
   ```

3. **Create Pull Request**: Use the PR template to document:
   - **Scope**: What changes were made and why
   - **Testing**: What tests were run and results
   - **Impact**: Functional, data, and dependency impacts

4. **Review & Merge**: Self-review using the PR as a checkpoint, then merge to `main`

### Pull Request Requirements

All PRs must include:
- ✅ Complete PR description using the template
- ✅ Scope section describing changes
- ✅ Testing section with test results
- ✅ Impact analysis (functional, data, dependencies)
- ✅ All checklist items completed

### Benefits

Even when working solo, this workflow provides:
- ✅ Clear, auditable history
- ✅ Better change isolation
- ✅ Review habits for collaboration
- ✅ Professional development practices

### Commit Message Guidelines

- Use clear, descriptive commit messages
- Follow conventional commit format when possible (e.g., `feat:`, `fix:`, `docs:`)
- Reference task numbers in commit messages (e.g., `Task 1: Add data collection pipeline`)

### .gitignore Best Practices

- Exclude sensitive data (`.env` files)
- Ignore generated files (`__pycache__/`, `*.pyc`, `*.log`)
- Exclude data directories (`data/raw/`, `data/processed/`, `data/interim/`)
- Ignore IDE-specific files (`.vscode/`, `.idea/`)

---

## Code Best Practices

### Architecture & Design

**Object-Oriented Design**:
- Clear separation of concerns (data collection, processing, analysis, storage)
- Reusable components (scrapers, analyzers, loaders)
- Pipeline pattern for orchestration

**Modular Structure**:
- Each task has dedicated pipeline class
- Utility functions organized in `src/utils/`
- Configuration management centralized in `config/`

### Code Quality

**PEP 8 Compliance**:
- Consistent naming conventions (snake_case for functions/variables, PascalCase for classes)
- Proper docstrings for all classes and functions
- Line length limits (max 100 characters)

**Error Handling**:
- Try-except blocks for external API calls
- Graceful degradation for missing dependencies
- Comprehensive logging for debugging

**Type Hints**:
- Type annotations for function parameters and return values
- Optional types for nullable values
- Dict, List, Tuple types for collections

### Testing

**Unit Tests**:
- Test individual components in isolation
- Mock external dependencies (database, APIs)
- Test edge cases and error conditions

**Integration Tests**:
- Test complete pipeline workflows
- Verify data flow between components
- Validate output formats

**Verification Scripts**:
- Setup verification (`verify_setup.py`)
- Data quality checks (`verify_data_quality.py`)
- Database integrity checks (`verify_database.py`)

### Documentation

**Code Documentation**:
- Docstrings for all classes and functions
- Inline comments for complex logic
- README with comprehensive project overview

**Configuration Documentation**:
- YAML configuration files with clear structure
- Environment variable templates (`.env.example`)
- Schema documentation in SQL comments

### Security

**Sensitive Data Handling**:
- Environment variables for database credentials
- `.env` file excluded from Git
- `.env.example` template for reference

**Data Privacy**:
- No personally identifiable information (PII) stored
- User names anonymized in analysis
- Review text processed without exposing user details

### Performance

**Efficient Data Processing**:
- Batch processing for database insertions (1000 records per batch)
- Lazy loading for large datasets
- Progress bars for long-running operations

**Resource Management**:
- Context managers for database connections
- Proper file handling (with statements)
- Memory-efficient data processing

### Maintainability

**Configuration-Driven**:
- YAML configuration for all settings
- Easy to modify without code changes
- Environment-specific configurations

**Logging**:
- Comprehensive logging at INFO, WARNING, ERROR levels
- Log files organized by date
- Structured logging for easy debugging

**Version Control**:
- Clear commit history
- Feature branches for isolated development
- Pull requests for code review

---

## Configuration

The project uses a YAML-based configuration system located in `config/config.yaml`. Key configuration areas include:

- **Bank Configuration**: App IDs and bank codes
- **Data Source Settings**: Options for using existing data or scraping new data
- **Scraping Parameters**: Language options, batch sizes, retry settings
- **Processing Options**: Duplicate removal, length filters, date formats
- **Path Configuration**: Directory structure for data and logs

---

## Testing

### Run Unit Tests

```bash
python -m unittest discover tests -v
```

### Verify Setup

```bash
python tests/verification/verify_setup.py
```

### Verify Data Quality

```bash
python tests/verification/verify_data_quality.py
```

### Test Database Connection

```bash
python scripts/test_database_insertion.py
```

---

## License

This project is part of a training portfolio for data engineering and analytics.

---

## Contact

For questions or support, please refer to the project facilitators or the designated communication channels.

---

**Last Updated**: December 2025  
**Status**: Task 1 Complete ✅ | Task 2 Complete ✅ | Task 3 Complete ✅ | Task 4 Complete ✅
