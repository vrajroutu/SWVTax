# Roxbury Property Data Pipeline

This project collects, processes, stores, and analyzes property prices and tax rates for Roxbury Township (Landing City) from 2015 to 2025. It provides a full ETL pipeline with reporting and visualization.

## Project Structure
- **config/**: Configuration files (YAML, environment variables)
- **data_collection/**: Scripts for scraping/downloading data from official sources (HTML, CSV, PDF, JSON)
- **data_processing/**: Data cleaning, normalization, aggregation, and feature engineering
- **data_storage/**: Database models and storage utilities (CSV, Parquet, PostgreSQL)
- **reporting/**: Automated report and chart generation (CSV, Excel, PDF, PNG)
- **reporting/output/**: Generated reports and visualizations
- **logs/**: Log files
- **main.py**: Pipeline entry point
- **requirements.txt**: Python dependencies

## Features
- Multi-format data ingestion (HTML, CSV, JSON, PDF)
- Robust error handling, logging (Loguru), and retry logic (Tenacity)
- Data normalization, aggregation, and year-over-year analysis
- Scalable storage: CSV, Parquet, or PostgreSQL (configurable)
- Automated reporting: summary tables, Excel, PDF, and charts (Matplotlib/Seaborn)
- Comparison of new vs. old homes and customizable reporting

## Usage
1. Configure data sources and storage in `config/config.yaml`
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Run the pipeline:
   ```sh
   python main.py
   ```
4. View outputs in `reporting/output/`

## Configuration
- Edit `config/config.yaml` to set data source URLs, years, and storage options.
- Optionally set environment variables (e.g., `DB_URI`) for database connections.

## Dependencies
See `requirements.txt` for core dependencies.

Key packages:
- `loguru`, `tenacity`, `requests`, `beautifulsoup4`, `tabula-py`, `sqlalchemy`, `matplotlib`, `seaborn`, `fpdf`, `lxml`, `PyYAML`, `python-dotenv`, `pandas`, `numpy`

## License
MIT License