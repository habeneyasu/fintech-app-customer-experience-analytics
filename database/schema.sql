-- PostgreSQL Database Schema for Bank Reviews Analytics
-- Database: bank_reviews
-- Created: November 2025

-- Create database (run this manually if needed)
-- CREATE DATABASE bank_reviews;

-- Connect to database
-- \c bank_reviews

-- ============================================
-- BANKS TABLE
-- ============================================
-- Stores information about the banks
CREATE TABLE IF NOT EXISTS banks (
    bank_id SERIAL PRIMARY KEY,               -- Unique identifier for each bank
    bank_name VARCHAR(255) NOT NULL,          -- Name of the bank
    app_name VARCHAR(255),                     -- Name of the bank's app (optional)
    description TEXT,                          -- Description of the bank (optional)
    created_at TIMESTAMP DEFAULT NOW()        -- Timestamp when the record was created
);

-- Add unique constraint on bank_name (if not exists)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'banks_bank_name_unique'
    ) THEN
        ALTER TABLE banks ADD CONSTRAINT banks_bank_name_unique UNIQUE (bank_name);
    END IF;
END $$;

-- Create index on bank_name for faster lookups
CREATE INDEX IF NOT EXISTS idx_banks_bank_name ON banks(bank_name);

-- ============================================
-- REVIEWS TABLE
-- ============================================
-- Stores the scraped and processed review data
CREATE TABLE IF NOT EXISTS reviews (
    review_id SERIAL PRIMARY KEY,               -- Unique identifier for each review
    bank_id INT NOT NULL REFERENCES banks(bank_id) ON DELETE CASCADE,  -- Link to banks table
    review_text TEXT NOT NULL,                  -- The actual review text
    rating NUMERIC(2,1),                        -- Rating (e.g., 4.5, range 1-5)
    review_date DATE,                            -- Date of the review
    sentiment_label VARCHAR(50),                -- e.g., Positive, Negative, Neutral
    sentiment_score NUMERIC(3,2),               -- e.g., 0.85 (confidence score, range 0-1)
    source VARCHAR(255),                         -- Source of the review (e.g., Google Play)
    created_at TIMESTAMP DEFAULT NOW()          -- Timestamp when the record was inserted
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_reviews_bank_id ON reviews(bank_id);
CREATE INDEX IF NOT EXISTS idx_reviews_rating ON reviews(rating);
CREATE INDEX IF NOT EXISTS idx_reviews_review_date ON reviews(review_date);
CREATE INDEX IF NOT EXISTS idx_reviews_sentiment_label ON reviews(sentiment_label);
CREATE INDEX IF NOT EXISTS idx_reviews_source ON reviews(source);

-- Add check constraint for rating range (if not exists)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'reviews_rating_range'
    ) THEN
        ALTER TABLE reviews ADD CONSTRAINT reviews_rating_range CHECK (rating >= 1 AND rating <= 5);
    END IF;
END $$;

-- Add check constraint for sentiment_score range (if not exists)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'reviews_sentiment_score_range'
    ) THEN
        ALTER TABLE reviews ADD CONSTRAINT reviews_sentiment_score_range CHECK (sentiment_score >= 0 AND sentiment_score <= 1);
    END IF;
END $$;

-- ============================================
-- VERIFICATION QUERIES
-- ============================================

-- Count total reviews
-- SELECT COUNT(*) as total_reviews FROM reviews;

-- Count reviews per bank
-- SELECT 
--     b.bank_name, 
--     COUNT(r.review_id) as review_count
-- FROM banks b
-- LEFT JOIN reviews r ON b.bank_id = r.bank_id
-- GROUP BY b.bank_id, b.bank_name
-- ORDER BY review_count DESC;

-- Average rating per bank
-- SELECT 
--     b.bank_name, 
--     AVG(r.rating) as avg_rating,
--     COUNT(r.review_id) as review_count
-- FROM banks b
-- LEFT JOIN reviews r ON b.bank_id = r.bank_id
-- WHERE r.rating IS NOT NULL
-- GROUP BY b.bank_id, b.bank_name
-- ORDER BY avg_rating DESC;

-- Sentiment distribution
-- SELECT 
--     sentiment_label, 
--     COUNT(*) as count,
--     ROUND(COUNT(*)::numeric / (SELECT COUNT(*) FROM reviews WHERE sentiment_label IS NOT NULL) * 100, 2) as percentage
-- FROM reviews
-- WHERE sentiment_label IS NOT NULL
-- GROUP BY sentiment_label
-- ORDER BY count DESC;

-- Sentiment coverage
-- SELECT 
--     COUNT(*) as total_reviews,
--     COUNT(sentiment_label) as reviews_with_sentiment,
--     ROUND(COUNT(sentiment_label)::numeric / COUNT(*) * 100, 2) as coverage_percentage
-- FROM reviews;

-- Reviews by rating distribution
-- SELECT 
--     rating,
--     COUNT(*) as count,
--     ROUND(COUNT(*)::numeric / (SELECT COUNT(*) FROM reviews WHERE rating IS NOT NULL) * 100, 2) as percentage
-- FROM reviews
-- WHERE rating IS NOT NULL
-- GROUP BY rating
-- ORDER BY rating DESC;

-- Top banks by review count
-- SELECT 
--     b.bank_name,
--     COUNT(r.review_id) as review_count,
--     AVG(r.rating) as avg_rating
-- FROM banks b
-- JOIN reviews r ON b.bank_id = r.bank_id
-- GROUP BY b.bank_id, b.bank_name
-- ORDER BY review_count DESC
-- LIMIT 10;

