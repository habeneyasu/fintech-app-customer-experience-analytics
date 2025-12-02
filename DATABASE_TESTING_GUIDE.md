# Database Testing Guide

## Quick Start: Testing Data Insertion

### Prerequisites

1. **PostgreSQL installed and running**
2. **Database created**: `CREATE DATABASE bank_reviews;`
3. **Schema created**: Run `database/schema.sql` or it will be created automatically
4. **Environment variables set**: Create `.env` file (see below)

### Step 1: Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your database password
nano .env  # or use your preferred editor
```

The `.env` file should contain:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=bank_reviews
DB_USER=postgres
DB_PASSWORD=your_password_here
```

**Important**: The `.env` file is already in `.gitignore` and will NOT be committed to git.

### Step 2: Test Database Connection

Run the test script to verify everything works:

```bash
python scripts/test_database_insertion.py
```

This script will:
1. ✅ Test database connection
2. ✅ Load banks from configuration
3. ✅ Insert a test batch of 100 reviews
4. ✅ Verify data integrity

### Step 3: Insert All Data

Once tests pass, insert all reviews:

```bash
python scripts/task_3_database_storage.py
```

This will:
- Load all banks from `config/config.yaml`
- Insert all reviews from CSV files (prefers `analyzed_reviews.csv` if available)
- Verify data integrity
- Display summary statistics

### Step 4: Verify Data

Run the verification script:

```bash
python scripts/verify_database.py
```

This displays:
- Total review count
- Reviews per bank
- Average ratings
- Sentiment distribution
- Data quality metrics

## Manual Testing with psql

You can also test directly in PostgreSQL:

```bash
psql -U postgres -d bank_reviews
```

### Useful Queries

```sql
-- Count total reviews
SELECT COUNT(*) FROM reviews;

-- Count reviews per bank
SELECT b.bank_name, COUNT(r.review_id) as count
FROM banks b
LEFT JOIN reviews r ON b.bank_id = r.bank_id
GROUP BY b.bank_id, b.bank_name;

-- Check average rating
SELECT b.bank_name, AVG(r.rating) as avg_rating
FROM banks b
JOIN reviews r ON b.bank_id = r.bank_id
GROUP BY b.bank_name;

-- Check sentiment distribution
SELECT sentiment_label, COUNT(*) as count
FROM reviews
WHERE sentiment_label IS NOT NULL
GROUP BY sentiment_label;

-- Sample reviews
SELECT review_text, rating, sentiment_label
FROM reviews
LIMIT 10;
```

## Troubleshooting

### Connection Errors

**Error**: `could not connect to server`
- **Solution**: Ensure PostgreSQL is running: `sudo systemctl status postgresql`

**Error**: `database "bank_reviews" does not exist`
- **Solution**: Create database: `psql -U postgres -c "CREATE DATABASE bank_reviews;"`

**Error**: `password authentication failed`
- **Solution**: Check `.env` file has correct password

### Data Insertion Errors

**Error**: `relation "banks" does not exist`
- **Solution**: Run schema: `psql -U postgres -d bank_reviews -f database/schema.sql`

**Error**: `duplicate key value violates unique constraint`
- **Solution**: This is normal if running multiple times. The script handles duplicates.

### Environment Variable Issues

**Error**: `DB_PASSWORD not found`
- **Solution**: Ensure `.env` file exists in project root
- **Solution**: Check `.env` file has `DB_PASSWORD=your_password` line

## Security Best Practices

1. ✅ **Never commit `.env` file** - Already in `.gitignore`
2. ✅ **Use `.env.example`** as template for team members
3. ✅ **Use environment variables** in production (not `.env` file)
4. ✅ **Rotate passwords** regularly
5. ✅ **Limit database user permissions** to minimum required

## Expected Results

After successful insertion, you should see:

- **Banks**: 3 banks (CBE, BOA, Dashen)
- **Reviews**: 9,594+ reviews inserted
- **Sentiment Coverage**: 90%+ if using analyzed_reviews.csv
- **Data Quality**: 0% error rate, 100% completeness

## Next Steps

After successful testing and insertion:

1. Run verification: `python scripts/verify_database.py`
2. Explore data with SQL queries
3. Proceed to Task 4: Visualization and Insights

