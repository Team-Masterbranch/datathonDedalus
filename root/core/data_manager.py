# core/data_manager.py
from typing import Dict, Any, List, Optional
import pandas as pd
import os
import glob
from datetime import datetime
from utils.logger import logger
from utils.logger import setup_logger
from core.query import Query
from core.visualizer_request import VisualizerRequest, ChartType
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
        self._update_current_schema()


    def load_csv_files(self) -> bool:
        """
        Load CSV files from the data directory and combine them into a single DataFrame.
        """
        try:
            logger.info(f"Loading CSV files from {self._data_path}")
            csv_files = glob.glob(os.path.join(self._data_path, "*.csv"))
            
            if not csv_files:
                logger.error(f"No CSV files found in {self._data_path}")
                return False
                
            dataframes = {}
            for file in csv_files:
                logger.info(f"Reading {file}")
                table_name = os.path.splitext(os.path.basename(file))[0]
                df = pd.read_csv(file)
                df = self._prefix_columns(df, table_name)
                dataframes[table_name] = df
                logger.info(f"Loaded {table_name} with columns: {df.columns.tolist()}")
                
            self._full_dataset = self._merge_dataframes(dataframes)
            if self._full_dataset is None:
                logger.error("Merge resulted in None DataFrame")
                return False
                
            logger.info(f"Final merged dataset columns: {self._full_dataset.columns.tolist()}")
            self._current_cohort = self._full_dataset.copy()
            logger.info(f"Successfully loaded {len(csv_files)} files")
            return True
            
        except Exception as e:
            logger.error(f"Error loading CSV files: {str(e)}")
            return False


    def _prefix_columns(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """
        Add table name prefix to column names except common join keys.
        """
        prefixed_columns = {}
        join_keys = ['patient_id', 'id', 'paciente_id', 'PacienteID']  # Added PacienteID
        
        for col in df.columns:
            # Don't prefix join keys
            if col in join_keys:  # Removed .lower() to maintain exact matches
                continue
            prefixed_columns[col] = f"{table_name}.{col}"
        
        return df.rename(columns=prefixed_columns)

    def _merge_dataframes(self, dataframes: Dict[str, pd.DataFrame]) -> Optional[pd.DataFrame]:
        """
        Merge DataFrames using appropriate join keys.
        """
        if not dataframes:
            return None
        
        # Start with patients table if it exists
        result = None
        remaining_dfs = dataframes.copy()
        
        if 'pacientes' in remaining_dfs:
            result = remaining_dfs.pop('pacientes')
            logger.info(f"Starting merge with pacientes table, columns: {result.columns.tolist()}")
        else:
            first_table = list(remaining_dfs.keys())[0]
            result = remaining_dfs.pop(first_table)
            logger.info(f"Starting merge with {first_table} table, columns: {result.columns.tolist()}")
        
        # Merge remaining DataFrames
        for table_name, df in remaining_dfs.items():
            # Look for join keys without considering prefixes
            join_key = None
            possible_keys = ['patient_id', 'id', 'paciente_id', 'PacienteID']
            
            for key in possible_keys:
                if key in result.columns and key in df.columns:
                    join_key = key
                    break
            
            if join_key is None:
                logger.warning(f"No join key found for table {table_name}, columns: {df.columns.tolist()}")
                continue
                
            logger.info(f"Merging {table_name} using key: {join_key}")
            result = result.merge(df, how='left', on=join_key)
            logger.info(f"After merging {table_name}, columns: {result.columns.tolist()}")
        
        return result



    def apply_filter(self, query: Query) -> Optional[pd.DataFrame]:
        """
        Apply filter based on Query object to current cohort.
        
        Args:
            query: Query object containing filter criteria
            
        Returns:
            Optional[pd.DataFrame]: Filtered DataFrame or None if error
        """
        try:
            logger.info(f"Applying filter with query: {query}")
            
            if self._current_cohort is None:
                logger.error("Cannot apply filter: current cohort is None")
                return None
                
            logger.info(f"Current cohort shape: {self._current_cohort.shape}")
            
            # Get filter mask based on query
            mask = self._apply_query_filter(query)
            if mask is None:
                return None
                
            # Apply filter mask to current cohort
            self._current_cohort = self._current_cohort[mask]
            logger.info(f"Filter applied successfully. New cohort shape: {self._current_cohort.shape}")
            
            # Update schema for filtered cohort
            self._update_current_schema()
            return self._current_cohort
            
        except Exception as e:
            logger.error(f"Error applying filter: {str(e)}")
            return None

    def _apply_query_filter(self, query: Query) -> Optional[pd.Series]:
        """
        Create and apply filter mask based on Query object.
        
        Args:
            query: Query object containing filter criteria
            
        Returns:
            Optional[pd.Series]: Boolean mask for filtering or None if error
        """
        try:
            criteria = query._query
            operation = criteria.get('operation')
            
            # Handle logical operations (AND/OR)
            if operation in ['and', 'or']:
                return self._handle_logical_operation(criteria)
                
            # Handle comparison operations
            return self._handle_comparison_operation(criteria)
            
        except Exception as e:
            logger.error(f"Error creating query filter: {str(e)}")
            return None

    def _handle_logical_operation(self, criteria: Dict[str, Any]) -> Optional[pd.Series]:
        """Handle AND/OR operations."""
        if 'criteria' not in criteria:
            logger.error("Missing criteria for logical operation")
            return None
            
        operation = criteria['operation']
        masks = []
        
        for subcriteria in criteria['criteria']:
            submask = self._handle_comparison_operation(subcriteria)
            if submask is not None:
                masks.append(submask)
        
        if not masks:
            return None
            
        if operation == 'and':
            return pd.concat(masks, axis=1).all(axis=1)
        else:  # or
            return pd.concat(masks, axis=1).any(axis=1)

    def _handle_comparison_operation(self, criteria: Dict[str, Any]) -> Optional[pd.Series]:
        """Handle comparison operations (equals, greater_than, less_than, between)."""
        field = criteria.get('field')
        operation = criteria.get('operation')
        value = criteria.get('value')
        
        if not all([field, operation]):
            logger.error(f"Invalid criteria structure: {criteria}")
            return None
            
        if field not in self._current_cohort.columns:
            logger.error(f"Field {field} not found in dataset")
            return None
            
        try:
            if operation == 'equals':
                return self._current_cohort[field] == value
            elif operation == 'greater_than':
                return self._current_cohort[field] > value
            elif operation == 'less_than':
                return self._current_cohort[field] < value
            elif operation == 'between':
                values = criteria.get('values', [])
                if len(values) != 2:
                    logger.error("Between operation requires exactly 2 values")
                    return None
                return (self._current_cohort[field] >= values[0]) & (self._current_cohort[field] <= values[1])
            else:
                logger.error(f"Unsupported operation: {operation}")
                return None
                
        except Exception as e:
            logger.error(f"Error in comparison operation: {str(e)}")
            return None

    def _update_full_schema(self):
        """Update schema for the full dataset."""
        if self._full_dataset is not None:
            self._full_schema = self._create_schema(self._full_dataset)

    def _update_current_schema(self):
        """Update schema for the current cohort."""
        if self._current_cohort is not None:
            self._current_schema = self._create_schema(self._current_cohort)

    def _create_schema(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """Create schema for given DataFrame."""
        schema = {}
        for column in df.columns:
            schema[column] = {
                'dtype': str(df[column].dtype),
                'unique_values': df[column].nunique(),
                'missing_values': df[column].isnull().sum()
            }
        return schema

    def get_full_schema(self) -> Dict[str, Dict]:
        """Get schema for the full dataset."""
        return self._full_schema

    def get_current_schema(self) -> Dict[str, Dict]:
        """Get schema for the current cohort."""
        return self._current_schema

    def get_current_cohort(self) -> Optional[pd.DataFrame]:
        """Get the current filtered cohort."""
        return self._current_cohort

    def reset_to_full(self):
        """Reset the current cohort to include all data."""
        logger.info("Resetting cohort to full dataset")
        self._current_cohort = self._full_dataset.copy()
        self._update_current_schema()
        return self._current_cohort

    def save_current_cohort(self, filepath: str, index: bool = False) -> bool:
        """
        Save the current cohort to a CSV file.
        
        Args:
            filepath: Path where to save the CSV file
            index: Whether to save the DataFrame index (default False)
            
        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            if self._current_cohort is None:
                logger.error("Cannot save: current cohort is None")
                return False
                
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
            
            # Save to CSV
            self._current_cohort.to_csv(filepath, index=index)
            logger.info(f"Successfully saved cohort to {filepath}")
            logger.info(f"Saved {len(self._current_cohort)} records")
            return True
            
        except Exception as e:
            logger.error(f"Error saving cohort to CSV: {str(e)}")
            return False


    def validate_visualization_request(self, request: VisualizerRequest) -> bool:
        """
        Validate visualization request against current cohort schema.
        
        Args:
            request: VisualizerRequest object to validate
            
        Returns:
            bool: True if request is valid for current cohort
        """
        try:
            if self._current_cohort is None:
                logger.error("No current cohort available")
                return False
                
            # Get available columns from current cohort
            available_columns = list(self._current_cohort.columns)
            
            # Check if required columns are specified based on chart type
            if request.chart_type == ChartType.BAR:
                if not request.x_column:
                    logger.error("Bar chart requires x_column")
                    return False
                    
            elif request.chart_type == ChartType.PIE:
                if not request.x_column:
                    logger.error("Pie chart requires x_column")
                    return False
                    
            elif request.chart_type == ChartType.SCATTER:
                if not (request.x_column and request.y_column):
                    logger.error("Scatter plot requires both x_column and y_column")
                    return False
                    
            elif request.chart_type == ChartType.BOX:
                if not (request.x_column and request.category_column):
                    logger.error("Box plot requires both x_column and category_column")
                    return False
                    
            elif request.chart_type == ChartType.HISTOGRAM:
                if not request.x_column:
                    logger.error("Histogram requires x_column")
                    return False
                    
            elif request.chart_type == ChartType.LINE:
                if not (request.x_column and request.y_column):
                    logger.error("Line chart requires both x_column and y_column")
                    return False

            # If we have any columns specified, validate them
            if request.x_column and request.x_column not in available_columns:
                logger.error(f"Column not found: {request.x_column}")
                return False
                
            if request.y_column and request.y_column not in available_columns:
                logger.error(f"Column not found: {request.y_column}")
                return False
                
            if request.category_column and request.category_column not in available_columns:
                logger.error(f"Column not found: {request.category_column}")
                return False

            # Additional validation based on data types
            schema = self._current_schema
            
            # Validate numeric columns for applicable chart types
            if request.chart_type in [ChartType.BOX, ChartType.HISTOGRAM, ChartType.SCATTER]:
                if request.x_column and 'float' not in schema[request.x_column]['dtype'] and 'int' not in schema[request.x_column]['dtype']:
                    logger.error(f"Column {request.x_column} must be numeric for {request.chart_type.value} chart")
                    return False
                    
                if request.y_column and 'float' not in schema[request.y_column]['dtype'] and 'int' not in schema[request.y_column]['dtype']:
                    logger.error(f"Column {request.y_column} must be numeric for {request.chart_type.value} chart")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating visualization request: {e}")
            return False

