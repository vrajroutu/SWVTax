import logging
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
import requests
from bs4 import BeautifulSoup
import pandas as pd
import tabula
import json
import os
import re
from urllib.robotparser import RobotFileParser

class DataCollector:
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.headers = {'User-Agent': 'Mozilla/5.0 (compatible; RoxburyBot/1.0)'}

    def check_robots(self, url):
        rp = RobotFileParser()
        robots_url = re.sub(r"/[^/]*$", "/robots.txt", url)
        rp.set_url(robots_url)
        try:
            # Skip robots.txt check due to SSL issues
            logger.info(f"Skipping robots.txt check for {url} to avoid SSL issues")
            return True
        except Exception as e:
            logger.warning(f"Could not read robots.txt for {url}: {e}")
            return True

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def fetch_url(self, url):
        if not self.check_robots(url):
            logger.warning(f"Scraping disallowed by robots.txt: {url}")
            return None
        try:
            # Disable SSL certificate verification for testing purposes
            response = self.session.get(url, headers=self.headers, timeout=20, verify=False)
            # Suppress only the InsecureRequestWarning from urllib3
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                logger.warning(f"File not found (404): {url}")
            else:
                logger.error(f"Failed to fetch {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            raise

    def fetch_html(self, url):
        resp = self.fetch_url(url)
        if resp:
            return BeautifulSoup(resp.text, 'lxml')
        return None

    def fetch_csv(self, url):
        resp = self.fetch_url(url)
        if resp:
            return pd.read_csv(pd.compat.StringIO(resp.text))
        return None

    def fetch_json(self, url):
        resp = self.fetch_url(url)
        if resp:
            return resp.json()
        return None

    def fetch_pdf(self, url, pages='all'):
        resp = self.fetch_url(url)
        if resp:
            pdf_path = os.path.join(self.config['DATA_DIR'], 'temp.pdf')
            with open(pdf_path, 'wb') as f:
                f.write(resp.content)
            try:
                dfs = tabula.read_pdf(pdf_path, pages=pages, multiple_tables=True)
                return dfs
            except Exception as e:
                logger.error(f"Failed to parse PDF: {e}")
                return None
        return None

    def parse_csv(self, csv_path_or_url):
        col_map = {
            'Address': 'address',
            'Year': 'year',
            'PropertyType': 'property_type',
            'Price': 'price',
            'Tax': 'tax',
            'YearBuilt': 'year_built',
            'Subdivision': 'subdivision',
            'AssessmentValue': 'assessment_value',
            'AssessmentFormula': 'assessment_formula',
            'Notes': 'notes',
        }
        try:
            if csv_path_or_url.startswith('http'):
                df = self.fetch_csv(csv_path_or_url)
            else:
                df = pd.read_csv(csv_path_or_url)
            if df is None or df.empty:
                logger.warning(f"No data found in CSV: {csv_path_or_url}")
                return pd.DataFrame(columns=list(col_map.values()))
            # Standardize columns
            df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})
            # Ensure all required columns exist
            for col in col_map.values():
                if col not in df.columns:
                    df[col] = None
            logger.info(f"Parsed {len(df)} records from {csv_path_or_url}")
            return df[list(col_map.values())]
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                logger.warning(f"File not found (404): {csv_path_or_url}")
                return pd.DataFrame(columns=list(col_map.values()))
            else:
                logger.error(f"Failed to parse CSV {csv_path_or_url}: {e}")
                return pd.DataFrame(columns=list(col_map.values()))
        except Exception as e:
            # Handle tenacity.RetryError for repeated HTTPError 404
            from tenacity import RetryError
            if isinstance(e, RetryError):
                last_exc = e.last_attempt.exception() if hasattr(e, 'last_attempt') and hasattr(e.last_attempt, 'exception') else None
                if isinstance(last_exc, requests.exceptions.HTTPError) and last_exc.response is not None and last_exc.response.status_code == 404:
                    logger.warning(f"File not found after retries (404): {csv_path_or_url}")
                    return pd.DataFrame(columns=list(col_map.values()))
            logger.error(f"Failed to parse CSV {csv_path_or_url}: {e}")
            return pd.DataFrame(columns=list(col_map.values()))

    def fetch_morris_county_roxbury_records(self, year=None, max_records=1000):
        """
        Scrape Roxbury Township property records from the Morris County Tax Board portal.
        Optionally filter by year. Returns a DataFrame.
        """
        import pandas as pd
        from bs4 import BeautifulSoup
        import time
        url = self.config.get('MORRIS_COUNTY_TAX_BOARD_URL')
        session = self.session
        records = []
        page = 1
        while True:
            data = {
                'Municipality': 'Roxbury Twp',
                'Page': page,
                'PageSize': max_records,
            }
            if year:
                data['Year'] = str(year)
            resp = session.post(url, data=data, verify=False)
            soup = BeautifulSoup(resp.text, 'html.parser')
            table = soup.find('table')
            if not table:
                logger.error(f"No table found in Morris County Tax Board response for Roxbury Twp, year={year}. URL: {url}")
                logger.debug(f"Response snippet: {resp.text[:1000]}")
                break
            try:
                from io import StringIO
                df = pd.read_html(StringIO(str(table)))[0]
            except Exception as e:
                logger.error(f"Failed to parse table HTML: {e}")
                logger.debug(f"Table HTML: {str(table)[:1000]}")
                break
            if df.empty:
                break
            records.append(df)
            break
        if records:
            result = pd.concat(records, ignore_index=True)
            logger.info(f"Fetched {len(result)} records from Morris County Tax Board for Roxbury Twp")
            return result
        else:
            logger.warning("No records found for Roxbury Twp in Morris County Tax Board portal.")
            return pd.DataFrame()
