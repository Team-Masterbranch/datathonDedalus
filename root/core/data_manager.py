# core/data_manager.py
from typing import Dict, Any, Tuple, Optional
import pandas as pd
import os
from datetime import datetime
from utils.logger import logger

class DataManager:
    """
    Centralized data management component for clinical datasets.
    Handles data loading, cleaning, filtering and schema management.
    """
    
    def __init__(self, data_path: str):
        """
        Initialize DataManager with path to data directory.
        
        Args:
            data_path: Directory containing CSV files
        """
        self._data_path = data_path
        self._full_dataset: Optional[pd.DataFrame] = None
        self._current_cohort: Optional[pd.DataFrame] = None
        self._schema: Dict[str, Dict] = {}
        
    @property
    def full_dataset(self) -> pd.DataFrame:
        """Original merged dataset (immutable view)."""
        if self._full_dataset is None:
            raise ValueError("Dataset not loaded. Call load_csv_files() first.")
        return self._full_dataset.copy()
    
    @property
    def current_cohort(self) -> pd.DataFrame:
        """Current filtered view of the dataset."""
        if self._current_cohort is None:
            raise ValueError("Dataset not loaded. Call load_csv_files() first.")
        return self._current_cohort
    
    @property
    def schema(self) -> Dict[str, Dict]:
        """Current schema metadata (auto-updated with cohort changes)."""
        return self._schema
    
    @property
    def data_path(self) -> str:
        """Path to CSV directory (immutable)."""
        return self._data_path

    def load_csv_files(self) -> bool:
        """
        Load and merge all CSV files into a single DataFrame.
        
        Returns:
            bool: True if loading successful, False otherwise
        """
        try:
            logger.info("Loading CSV files from data directory")
            
            # Load patients as base DataFrame
            patients_path = os.path.join(self.data_path, 'pacientes.csv')
            self._full_dataset = pd.read_csv(patients_path)
            
            # Get list of other CSV files
            related_files = [f for f in os.listdir(self.data_path) 
                           if f.endswith('.csv') and f != 'pacientes.csv']
            
            # Merge each related table
            for file in related_files:
                table_name = os.path.splitext(file)[0]
                file_path = os.path.join(self.data_path, file)
                
                logger.info(f"Merging {table_name} data")
                related_data = pd.read_csv(file_path)
                
                self._full_dataset = pd.merge(
                    self._full_dataset,
                    related_data,
                    on='PacienteID',
                    how='left',
                    suffixes=('', f'_{table_name}')
                )

            # Initialize current cohort and schema
            self._current_cohort = self._full_dataset.copy()
            self._update_schema()
            
            logger.info("Data loading completed successfully")
            return True

        except Exception as e:
            logger.error(f"Error loading CSV files: {e}")
            return False

    def clean_data(self) -> bool:
        """
        Standardize data formats and handle missing values.
        
        Returns:
            bool: True if cleaning successful, False otherwise
        """
        try:
            logger.info("Starting data cleaning process")

            if self._full_dataset is None:
                raise ValueError("No data loaded to clean")

            # Convert date columns
            date_columns = [col for col in self._full_dataset.columns 
                          if 'Fecha' in col]
            
            for col in date_columns:
                self._full_dataset[col] = pd.to_datetime(self._full_dataset[col])
                
            # Fill missing end dates
            end_date_columns = [col for col in date_columns 
                              if 'Fecha_fin' in col]
            future_date = pd.Timestamp('2025-12-31')
            
            for col in end_date_columns:
                self._full_dataset[col] = self._full_dataset[col].fillna(future_date)

            # Update current cohort and schema
            self._current_cohort = self._full_dataset.copy()
            self._update_schema()
            
            logger.info("Data cleaning completed")
            return True

        except Exception as e:
            logger.error(f"Error during data cleaning: {e}")
            return False

    def apply_filter(self, criteria: Dict[str, Tuple[str, Any]]) -> None:
        """
        Apply filter criteria to current cohort.
        
        Args:
            criteria: Dictionary of column filters with operators and values
                     e.g., {"Edad": (">=", 50)}
                     
        Raises:
            ValueError: If column name doesn't exist in dataset
        """
        try:
            # Validate all columns first
            invalid_columns = [
                column for column in criteria.keys() 
                if column not in self._current_cohort.columns
            ]
            
            if invalid_columns:
                raise ValueError(
                    f"Column(s) not found in dataset: {', '.join(invalid_columns)}"
                )

            query_parts = []
            for column, (operator, value) in criteria.items():
                # Handle string values
                if isinstance(value, str):
                    value = f"'{value}'"
                
                query_parts.append(f"{column} {operator} {value}")
            
            query_string = " and ".join(query_parts)
            self._current_cohort = self._current_cohort.query(query_string)
            self._update_schema()
            
            logger.debug(f"Applied filter: {query_string}")  # Changed to debug level
            
        except ValueError as e:
            # Re-raise ValueError without logging as it's an expected validation error
            raise
        except Exception as e:
            # Log unexpected errors
            logger.error(f"Error applying filter: {e}")
            raise


    def reset_to_full(self) -> None:
        """Reset current cohort to full dataset."""
        logger.info("Resetting cohort to full dataset")
        self._current_cohort = self._full_dataset.copy()
        self._update_schema()

    def _update_schema(self) -> None:
        """Update schema metadata for current cohort."""
        schema = {}
        
        for column in self._current_cohort.columns:
            col_data = self._current_cohort[column]
            col_info = {
                "type": str(col_data.dtype),
                "unique_count": col_data.nunique()
            }
            
            # Add numerical statistics
            if pd.api.types.is_numeric_dtype(col_data):
                col_info.update({
                    "min": float(col_data.min()),
                    "max": float(col_data.max()),
                    "mean": float(col_data.mean())
                })
            
            # Add unique values for categorical data with few unique values
            elif col_data.nunique() < 50:  # Threshold for including unique values
                col_info["unique_values"] = col_data.unique().tolist()
            
            schema[column] = col_info
        
        self._schema = schema

    def get_schema(self) -> Dict[str, Dict]:
        """Get current schema metadata."""
        return self._schema
