# Task 4: Code Evidence for Requirements

This document demonstrates how the code directly addresses the challenge requirements.

## Requirement 1: Compute Per-Bank Drivers and Pain Points

### Code Location: `src/insights/insights_generator.py`

**Drivers Computation** (Lines 45-108):
- Method: `identify_drivers(df, bank_name)`
- **Explicitly computes drivers per bank** by:
  1. Filtering positive reviews (rating >= 4 OR sentiment = 'positive')
  2. Matching keywords in review text
  3. Calculating strength scores: `(rating/5.0 * 0.5) + (sentiment_score * 0.5)`
  4. Counting mentions and collecting evidence examples
  5. Returning list of drivers with type, description, strength, mentions, examples

**Pain Points Computation** (Lines 110-173):
- Method: `identify_pain_points(df, bank_name)`
- **Explicitly computes pain points per bank** by:
  1. Filtering negative reviews (rating <= 2 OR sentiment = 'negative')
  2. Matching keywords in review text
  3. Calculating severity scores: `(1 - rating/5.0) * 0.5 + (1 - sentiment_score) * 0.5`
  4. Counting mentions and collecting evidence examples
  5. Returning list of pain points with type, description, severity, mentions, examples

**Evidence**: Each driver/pain point includes:
- Mention count (number of reviews mentioning the issue)
- Strength/severity score (calculated metric)
- Example reviews (up to 3 examples with ratings and sentiment)

## Requirement 2: Generate 3-5 Labeled Plots

### Code Location: `src/insights/visualization.py`

**All plots are properly labeled with:**
- Titles (fontweight='bold')
- Axis labels (xlabel, ylabel with fontweight='bold')
- Legends with titles
- Value annotations on bars/charts
- Grid lines for readability

**Generated Visualizations:**

1. **Sentiment Distribution by Bank** (`plot_sentiment_distribution`)
   - Labeled bars showing positive/negative/neutral counts per bank
   - Value labels on each bar
   - Clear legend

2. **Rating Distribution by Bank** (`plot_rating_distribution`)
   - Labeled bars showing 1-5 star ratings per bank
   - Color-coded by rating
   - Value labels on each bar

3. **Sentiment Trends Over Time** (`plot_sentiment_trends`)
   - Labeled line chart showing sentiment changes over months
   - Separate subplot for each bank
   - Grid lines and markers

4. **Bank Comparison Chart** (`plot_bank_comparison`)
   - Two-panel chart comparing average ratings and positive sentiment %
   - Value labels on each bar
   - Clear titles and axis labels

5. **Drivers and Pain Points Charts** (`plot_drivers_pain_points`)
   - Per-bank charts showing top 5 drivers and top 5 pain points
   - Horizontal bar charts with percentage labels
   - Clear titles indicating which bank

## Requirement 3: At Least Two Actionable Recommendations Per Bank Tied to Findings

### Code Location: `src/insights/insights_generator.py`

**Recommendations Generation** (Lines 175-230):
- Method: `generate_recommendations(drivers, pain_points, bank_name)`
- **Explicitly ties recommendations to findings** by:
  1. Using identified pain points as basis for recommendations
  2. Setting priority based on severity score and mention count
  3. Including evidence count in each recommendation
  4. Linking recommendation to specific pain point type
  5. Ensuring at least 2 recommendations per bank

**Each Recommendation Includes:**
- Priority (High/Medium) - based on pain point severity
- Title - specific to pain point type
- Description - actionable steps to address the issue
- Expected Impact - what improvement to expect
- Evidence - "X mentions in negative reviews" (directly from analysis)
- Pain Point Tied To - which specific pain point this addresses

**Example Recommendation Structure:**
```python
{
    'priority': 'High',
    'title': 'Optimize Performance',
    'description': 'Improve app speed and reduce loading times...',
    'expected_impact': 'Enhances user experience and satisfaction',
    'evidence': '71 mentions in negative reviews',  # Directly from pain point analysis
    'pain_point_tied_to': 'slow'  # Links to identified pain point
}
```

## Execution Flow

### Main Script: `scripts/task_4_insights.py`

1. Loads data (from database or CSV)
2. For each bank:
   - Calls `identify_drivers()` - computes drivers
   - Calls `identify_pain_points()` - computes pain points
   - Calls `generate_recommendations()` - creates recommendations tied to findings
   - Calls `plot_drivers_pain_points()` - creates labeled visualization
3. Generates all labeled plots (sentiment, ratings, trends, comparison)
4. Creates final report with all insights and recommendations

## Output Files

All outputs are saved to `data/results/`:
- `insights.json` - Structured data with drivers, pain points, recommendations
- `visualizations/` - All labeled plots (PNG files with 300 DPI)
- `FINAL_REPORT.md` - 10-page report with all findings

## Verification

To verify the code addresses requirements:

1. **Run Task 4**: `python scripts/task_4_insights.py`
2. **Check outputs**:
   - `data/results/insights.json` - Contains per-bank drivers and pain points
   - `data/results/visualizations/` - Contains 5+ labeled plots
   - `data/results/FINAL_REPORT.md` - Contains recommendations with evidence

3. **Review code**:
   - `src/insights/insights_generator.py` - Lines 45-230 show computation logic
   - `src/insights/visualization.py` - All methods add labels and annotations
   - `src/insights/report_generator.py` - Ties recommendations to findings in report

