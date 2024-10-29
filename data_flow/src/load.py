import logging
import pandas as pd
from sqlalchemy import create_engine, inspect

from .config import DataPipelineConfig
from .models import Base, User, Track, ListenHistory, Test

logger = logging.getLogger(__name__)


class DataLoader:
    """Handles data loading into the database"""
    
    def __init__(self, config: DataPipelineConfig):
        self.config = config
        self.tables = [User.__table__, Track.__table__, ListenHistory.__table__]
        self.tables_test = [Test.__table__]

        self._engine = None
    
    @property
    def engine(self):
        if self._engine is None:
            self._engine = create_engine(self.config.database_url, echo=False)
        return self._engine
        
    def load_data(self, data: pd.DataFrame, table_name: str) -> None:
        """Load data into the database"""
        with self.engine.begin() as connection: # transaction management
            try:
                # insert data into the SQL Table
                data.to_sql(
                    table_name,
                    connection,
                    if_exists='append',
                    index=False
                )
                logger.info(f"Successfully loaded {len(data)} rows into {table_name}")
            except Exception as e:
                logger.error(f"Error loading data into {table_name}: {str(e)}", exc_info=True)

    def setup(self, test: bool = False):
        # NOTE: for prototyping purposes, we initally drop all tables and then 
        Base.metadata.drop_all(self.engine)
        
        inspector = inspect(self.engine)
        tables = self.tables if not test else self.tables_test
        with self.engine.connect() as connection:
            for table in tables:
                if not inspector.has_table(table.name):
                    table.create(connection)
                    logger.info(f"Table {table.name} created successfully!")
                else:
                    logger.warning(f"Table {table.name} already exists.")
