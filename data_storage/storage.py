from sqlalchemy import create_engine, Column, Integer, String, Float, Date, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
import os

Base = declarative_base()

class PropertyRecord(Base):
    __tablename__ = 'property_records'
    id = Column(Integer, primary_key=True)
    address = Column(String)
    year = Column(Integer)
    property_type = Column(String)
    price = Column(Float)
    tax = Column(Float)
    year_built = Column(Integer)
    subdivision = Column(String)
    new_home = Column(Integer)  # 1 for new, 0 for old
    assessment_value = Column(Float)
    assessment_formula = Column(String)
    notes = Column(String)

class DataStorage:
    def __init__(self, config):
        self.config = config
        self.db_type = config.get('DB_TYPE', 'csv')
        if self.db_type == 'postgresql':
            self.engine = create_engine(config['DB_URI'])
            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine)
        else:
            os.makedirs(config['DATA_DIR'], exist_ok=True)

    def save_to_db(self, df):
        if self.db_type == 'postgresql':
            df.to_sql('property_records', self.engine, if_exists='append', index=False)

    def save_to_csv(self, df, filename='property_records.csv'):
        path = os.path.join(self.config['DATA_DIR'], filename)
        df.to_csv(path, index=False)

    def save_to_parquet(self, df, filename='property_records.parquet'):
        path = os.path.join(self.config['DATA_DIR'], filename)
        df.to_parquet(path, index=False)

    def save(self, df):
        if self.db_type == 'postgresql':
            self.save_to_db(df)
        elif self.db_type == 'parquet':
            self.save_to_parquet(df)
        else:
            self.save_to_csv(df)
