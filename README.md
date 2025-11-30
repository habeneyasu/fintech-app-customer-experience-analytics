# Customer Experience Analytics - Task 1: Data Collection and Preprocessing

A professional data engineering project for collecting and preprocessing Google Play Store reviews of Ethiopian banking mobile applications.

## Project Overview

This project focuses on collecting and preprocessing user reviews from Google Play Store for three Ethiopian banking mobile applications:
- **Commercial Bank of Ethiopia (CBE)**
- **Bank of Abyssinia (BOA)**
- **Dashen Bank**

The objective is to gather comprehensive review data, clean and preprocess it, and prepare it for downstream analysis tasks.

## Project Setup

### Prerequisites

- Python 3.8 or higher
- Virtual environment support
- Git

### Installation Steps

1. **Create Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install PyTorch (CPU version for resource efficiency)**
   ```bash
   pip install torch==2.2.2+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Dependencies

The project uses the following key dependencies:
- `google-play-scraper` - Web scraping library
- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `tqdm` - Progress bars
- `python-dotenv` - Environment variable management
- `pyyaml` - Configuration file parsing

## Data Collection Methodology

### Data Source

Reviews were collected from Google Play Store using a custom scraping script that implements:

- **Multi-language Support**: Collects reviews in both Amharic (Ethiopia) and English (US)
- **Batch Processing**: Processes reviews in batches of 100 per API request
- **Retry Logic**: Implements automatic retry mechanism with up to 5 attempts for failed requests
- **Continuation Token Handling**: Efficiently handles pagination through review pages
- **Error Handling**: Robust error handling with graceful degradation

### Bank Applications

The following mobile banking applications were analyzed:

| Bank | App ID | Reviews Collected |
|------|--------|-------------------|
| Commercial Bank of Ethiopia | `com.combanketh.mobilebanking` | 8,174 |
| Bank of Abyssinia | `com.boa.boaMobileBanking` | 1,200 |
| Dashen Bank | `com.cr2.amolelight` | 507 |

**Total Reviews Collected**: 9,881 reviews

## Data Preprocessing

### Preprocessing Steps

1. **Duplicate Removal**: Removed 41 duplicate reviews based on review text, bank, and user name
2. **Length Filtering**: Filtered out 246 reviews that were too short (< 3 characters) or too long (> 1000 characters)
3. **Date Normalization**: Standardized all dates to YYYY-MM-DD format
4. **Data Validation**: Ensured all ratings are within valid range (1-5 stars)
5. **Missing Data Handling**: Removed rows with missing critical fields

### Preprocessing Results

- **Initial Reviews**: 9,881
- **Duplicates Removed**: 41
- **Filtered by Length**: 246
- **Final Processed Reviews**: 9,594

## Data Quality Metrics

### Quality Assurance Results

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

## Project Structure

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
│   └── processed/                  # Processed data storage
│       └── processed_reviews.csv
│
├── src/                             # Source code
│   ├── data_collection/            # Data collection modules
│   │   ├── scraper.py             # Google Play Store scraper
│   │   └── data_loader.py          # Data loading utilities
│   ├── data_processing/           # Data processing modules
│   │   └── preprocessor.py        # Data preprocessing pipeline
│   ├── pipeline/                   # Pipeline orchestration
│   │   └── data_collection_pipeline.py
│   └── utils/                      # Utility modules
│       ├── config_loader.py        # Configuration management
│       └── logger.py               # Logging utilities
│
├── scripts/                         # Execution scripts
│   └── task_1_data_collection.py  # Main task execution script
│
├── tests/                          # Test suite
│   ├── test_preprocessor.py       # Preprocessor unit tests
│   └── verification/              # Verification scripts
│       ├── verify_setup.py
│       └── verify_data_quality.py
│
├── logs/                           # Application logs
│
├── requirements.txt                # Python dependencies
├── .gitignore                      # Git ignore rules
└── README.md                       # This file
```

## Usage

### Running the Pipeline

Execute the complete data collection and preprocessing pipeline:

```bash
python scripts/task_1_data_collection.py
```

### Output Files

The pipeline generates the following output files:

- **Raw Data**: `data/raw/raw_reviews.csv` - Contains 9,881 original reviews
- **Processed Data**: `data/processed/processed_reviews.csv` - Contains 9,594 cleaned reviews
- **Logs**: `logs/YYYYMMDD.log` - Execution logs with detailed information

## Success Criteria

All Task 1 requirements have been successfully met:

- ✅ **1,200+ reviews collected**: 9,594 total processed reviews
- ✅ **Error rate < 5%**: Achieved 0.0% error rate
- ✅ **Clean CSV dataset**: Processed data saved in standardized format
- ✅ **All banks exceed minimum**: 
  - CBE: 7,931 reviews (exceeds 400 minimum)
  - BOA: 1,168 reviews (exceeds 400 minimum)
  - Dashen: 495 reviews (exceeds 400 minimum)
- ✅ **Organized Git repository**: Proper version control with clear commit history
- ✅ **Documentation**: Comprehensive project documentation

## Configuration

The project uses a YAML-based configuration system located in `config/config.yaml`. Key configuration areas include:

- **Bank Configuration**: App IDs and bank codes
- **Data Source Settings**: Options for using existing data or scraping new data
- **Scraping Parameters**: Language options, batch sizes, retry settings
- **Processing Options**: Duplicate removal, length filters, date formats
- **Path Configuration**: Directory structure for data and logs

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

## Architecture

The project follows an object-oriented design pattern with clear separation of concerns:

- **DataCollectionPipeline**: Main orchestrator for the complete workflow
- **PlayStoreScraper**: Handles web scraping with multi-language support
- **DataLoader**: Manages loading and preparation of existing data files
- **DataPreprocessor**: Implements data cleaning and validation logic

This architecture ensures:
- **Reusability**: Components can be used independently
- **Testability**: Easy to unit test individual components
- **Maintainability**: Clear separation of concerns
- **Extensibility**: Easy to add new features or modify behavior

## Data Collection Features

The data collection process includes:

- **Multi-language Support**: Collects reviews in Amharic and English
- **Robust Error Handling**: Automatic retry with configurable attempts
- **Rate Limiting**: Respects API rate limits with appropriate delays
- **Duplicate Detection**: Identifies and handles duplicate reviews
- **Progress Tracking**: Real-time progress updates during collection

## Next Steps

After completing Task 1, the processed data is ready for:

- **Task 2**: Sentiment and thematic analysis
- **Task 3**: Database storage in PostgreSQL
- **Task 4**: Insights generation and visualization

## Version Control & Git Workflow

The project uses Git for version control with a professional branch-based workflow and pull request (PR) process.

### Branch Strategy

- **`main`**: Stable, production-ready code. Only merged via pull requests.
- **`task-*`**: Feature branches for specific tasks (e.g., `task-1`, `task-2`)
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
- ✅ Complete PR description using the template (`.github/pull_request_template.md`)
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

For detailed workflow instructions, see [`.github/workflow-guide.md`](.github/workflow-guide.md).

## License

This project is part of a training portfolio for data engineering and analytics.

## Contact

For questions or support, please refer to the project facilitators or the designated communication channels.

---

**Last Updated**: November 2025  
**Status**: Task 1 Complete ✅

