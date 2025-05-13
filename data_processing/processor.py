import pandas as pd
import numpy as np
import re
from loguru import logger

class DataProcessor:
    def __init__(self):
        pass

    def clean_address(self, address):
        # Standardize address format (simple example)
        if pd.isnull(address):
            return None
        address = address.strip().upper()
        address = re.sub(r'\s+', ' ', address)
        return address

    def normalize_currency(self, value):
        # Remove currency symbols, commas, and convert to float
        if pd.isnull(value):
            return np.nan
        try:
            return float(re.sub(r'[^0-9.]', '', str(value)))
        except Exception as e:
            logger.warning(f"Could not normalize currency: {value} ({e})")
            return np.nan

    def tag_new_homes(self, df, new_home_year=2015):
        if 'year_built' in df.columns:
            df['new_home'] = df['year_built'].apply(lambda y: 1 if pd.notnull(y) and int(y) >= new_home_year else 0)
        else:
            df['new_home'] = np.nan
        return df

    def process(self, df):
        # Example: Clean and normalize columns
        if 'address' in df.columns:
            df['address'] = df['address'].apply(self.clean_address)
        if 'price' in df.columns:
            df['price'] = df['price'].apply(self.normalize_currency)
        if 'tax' in df.columns:
            df['tax'] = df['tax'].apply(self.normalize_currency)
        if 'year_built' in df.columns:
            df['year_built'] = pd.to_numeric(df['year_built'], errors='coerce')
        if 'subdivision' in df.columns:
            df['subdivision'] = df['subdivision'].astype(str).str.upper().str.strip()
        if 'assessment_value' in df.columns:
            df['assessment_value'] = df['assessment_value'].apply(self.normalize_currency)
        if 'assessment_formula' in df.columns:
            df['assessment_formula'] = df['assessment_formula'].astype(str).str.strip()
        if 'notes' in df.columns:
            df['notes'] = df['notes'].astype(str).str.strip()
        df = self.tag_new_homes(df)
        # Handle missing values
        df = df.dropna(subset=['address', 'price', 'tax'], how='any')
        # Add more cleaning as needed
        return df

    def aggregate(self, df, by=['year', 'property_type']):
        # Aggregate by year and property type
        agg = df.groupby(by).agg({
            'price': 'mean',
            'tax': ['mean', 'sum'],
            'address': 'count'
        }).reset_index()
        agg.columns = ['_'.join(col).strip('_') for col in agg.columns.values]
        return agg

    def aggregate_by_age(self, df, by=['year', 'new_home']):
        agg = df.groupby(by).agg({
            'price': 'mean',
            'tax': ['mean', 'sum'],
            'address': 'count'
        }).reset_index()
        agg.columns = ['_'.join(col).strip('_') for col in agg.columns.values]
        return agg

    def compare_new_vs_old(self, df):
        # Compare average tax rates for new vs. old homes by year
        comp = df.groupby(['year', 'new_home']).agg({
            'tax': 'mean',
            'price': 'mean',
            'address': 'count'
        }).reset_index()
        comp['home_type'] = comp['new_home'].map({1: 'New', 0: 'Old'})
        return comp

    def calculate_yoy(self, df, value_col='tax', group_col='address'):
        # Calculate year-over-year changes for each property
        df = df.sort_values([group_col, 'year'])
        df['tax_yoy_change'] = df.groupby(group_col)[value_col].pct_change()
        return df
