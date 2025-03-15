# core/data_manager.py
from typing import Dict, Any, Tuple, Optional
import pandas as pd
import os
import glob
from datetime import datetime
from utils.logger import logger
from utils.logger import setup_logger
logger = setup_logger(__name__)

class DataManager:
    """
    Centralized data management component for clinical datasets.
    Handles data loading, cleaning, filtering and schema management.
    """
    
    def __init__(self, data_path: str):
        """
        Initialize DataManager with path to data directory and load data.
        
        Args:
            data_path: Directory containing CSV files
            
        Raises:
            ValueError: If data loading fails
        """
        self._data_path = data_path
        self._full_dataset: Optional[pd.DataFrame] = None
        self._current_cohort: Optional[pd.DataFrame] = None
        self._full_schema: Dict[str, Dict] = {}  # Schema for full dataset
        self._current_schema: Dict[str, Dict] = {}  # Schema for current cohort
        
        # Automatically load data on initialization
        if not self.load_csv_files():
            raise ValueError("Failed to load data files")
            
        # Initialize full dataset schema
        self._update_full_schema()
        
    def load_csv_files(self) -> bool:
        """
        Load CSV files from the data directory and combine them into a single DataFrame.
        
        Returns:
            bool: True if loading was successful, False otherwise
        """
        try:
            logger.info(f"Loading CSV files from {self._data_path}")
            csv_files = glob.glob(os.path.join(self._data_path, "*.csv"))
            
            if not csv_files:
                logger.error(f"No CSV files found in {self._data_path}")
                return False
                
            dataframes = []
            for file in csv_files:
                logger.info(f"Reading {file}")
                df = pd.read_csv(file)
                dataframes.append(df)
                
            self._full_dataset = pd.concat(dataframes, axis=0, ignore_index=True)
            self._current_cohort = self._full_dataset.copy()
            logger.info(f"Successfully loaded {len(csv_files)} files")
            return True
            
        except Exception as e:
            logger.error(f"Error loading CSV files: {str(e)}")
            return False


    def _update_full_schema(self):
        """Update schema for the full dataset."""
        if self._full_dataset is not None:
            self._full_schema = self._create_schema(self._full_dataset)

    def _update_current_schema(self):
        """Update schema for the current cohort."""
        if self._current_cohort is not None:
            self._current_schema = self._create_schema(self._current_cohort)

    def _create_schema(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """
        Create schema for given DataFrame.
        
        Args:
            df: DataFrame to create schema for
            
        Returns:
            Dict containing schema information
        """
        schema = {}
        for column in df.columns:
            schema[column] = {
                'dtype': str(df[column].dtype),
                'unique_values': df[column].nunique(),
                'missing_values': df[column].isnull().sum()
            }
        return schema
    
    def get_full_schema(self) -> Dict[str, Dict]:
        """
        Get schema for the full dataset.
        
        Returns:
            Dictionary containing schema information for the full dataset
        """
        return self._full_schema

    def get_current_schema(self) -> Dict[str, Dict]:
        """
        Get schema for the current cohort.
        
        Returns:
            Dictionary containing schema information for the current filtered cohort
        """
        return self._current_schema

    def get_current_cohort(self) -> Optional[pd.DataFrame]:
        """
        Get the current filtered cohort.
        
        Returns:
            Optional[pd.DataFrame]: The current filtered dataset or None if not available
        """
        return self._current_cohort


    def reset_to_full(self):
        """Reset the current cohort to include all data."""
        logger.info("Resetting cohort to full dataset")
        self._current_cohort = self._full_dataset.copy()
        self._update_current_schema()  # Update schema for new cohort
        return self._current_cohort

    def apply_filter(self, criteria: Dict[str, Any]) -> Optional[pd.DataFrame]:
        try:
            logger.info(f"Applying filter with criteria: {criteria}")
            
            if self._current_cohort is None:
                logger.error("Cannot apply filter: current cohort is None")
                return None
                
            logger.info(f"Current cohort shape: {self._current_cohort.shape}")
                
            field = criteria.get('field')
            operation = criteria.get('operation')
            value = criteria.get('value')
            
            logger.info(f"Extracted field: {field}, operation: {operation}, value: {value}")
            
            if not all([field, operation, value]):
                logger.error(f"Invalid filter criteria: {criteria}")
                return None
                
            if field not in self._current_cohort.columns:
                logger.error(f"Field {field} not found in dataset. Available columns: {list(self._current_cohort.columns)}")
                return None
                
            # Apply the filter based on operation
            logger.info(f"Applying {operation} operation on field {field} with value {value}")
            
            if operation == 'greater_than':
                self._current_cohort = self._current_cohort[self._current_cohort[field] > value]
            elif operation == 'less_than':
                self._current_cohort = self._current_cohort[self._current_cohort[field] < value]
            elif operation == 'equals':
                self._current_cohort = self._current_cohort[self._current_cohort[field] == value]
            else:
                logger.error(f"Unsupported operation: {operation}")
                return None
                
            logger.info(f"Filter applied successfully. New cohort shape: {self._current_cohort.shape}")
            self._update_current_schema()
            return self._current_cohort
            
        except Exception as e:
            logger.error(f"Error applying filter: {str(e)}")
            return None

