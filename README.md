# Amazon Sales Dashboard

## Overview

This project is an interactive Streamlit dashboard that analyzes Amazon product data. It provides summary metrics, visualizations, and insights into product prices, discounts, ratings, and reviews.

## Requirements

- Python 3.11 or newer
- uv package manager

## Installation

1. Clone this repository.
2. Navigate to the project folder.
3. Install the project dependencies:

```bash
uv sync
```

## Running the Dashboard

Start the Streamlit application with:

```bash
uv run streamlit run app.py
```

Then open the local URL displayed in the terminal (usually http://localhost:8501).

## Project Structure

```
amazon-sales-dashboard/
├── app.py
├── data/
│   └── raw/
│       └── amazon.csv
├── pyproject.toml
├── README.md
└── .gitignore
