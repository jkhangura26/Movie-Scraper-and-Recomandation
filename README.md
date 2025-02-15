# NextFlick

A Flask-based web application for exploring movies and receiving personalized recommendations powered by a content-based recommendation system.

## Overview

This project combines web development and machine learning to create a movie recommendation platform. Users can search for movies, view detailed information, and get AI-generated recommendations. The system uses **TF-IDF vectorization** and **cosine similarity** to suggest movies based on combined features like genre, cast, and plot.

## Key Features

- **Movie Search**: Find movies by title; automatically adds new entries via scraper if not found.
- **Detailed View**: Display movie metadata (year, rating, director, cast, plot, runtime, poster).
- **Smart Recommendations**: Get 10 similar movies using ML-based content filtering.
- **Dynamic Scraping**: Integrates with `scraper.py` to fetch and add new movies on-demand.
- **CSV Backend**: Uses `movies.csv` as a lightweight database with 250+ entries.

## Technical Architecture

### Core Components
- **Backend**: Flask (Python) for routing and business logic.
- **Data Processing**: pandas for CSV handling and feature engineering.
- **ML Pipeline**: 
  - **TF-IDF Vectorization**
  - **Similarity Scoring**
- **Subprocess Management**: Executes recommendation script as separate process.

Try it out here at [movie-scraper-and-recommendation.onrender.com](https://movie-scraper-and-recommendation.onrender.com/).

Render takes a little bit to load, it's worth the wait :)

