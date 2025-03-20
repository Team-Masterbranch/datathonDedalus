# core/data_manager.py
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
import os
import glob
from datetime import datetime
from utils.logger import logger
from utils.logger import setup_logger
from core.query import Query
from core.visualizer_request import VisualizerRequest, ChartType
from utils.config import PATIENT_ID_COLUMN, PATIENT_ID_ALTERNATIVES, UNIQUE_VALUES_THRESHOLD

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
                logger.debug(f"Reading {file}")
                table_name = os.path.splitext(os.path.basename(file))[0]
                df = pd.read_csv(file)
                df = self._prefix_columns(df, table_name)
                dataframes[table_name] = df
                logger.debug(f"Loaded {table_name} with columns: {df.columns.tolist()}")
                
            self._full_dataset = self._merge_dataframes(dataframes)
            if self._full_dataset is None:
                logger.error("Merge resulted in None DataFrame")
                return False
                
            logger.debug(f"Final merged dataset columns: {self._full_dataset.columns.tolist()}")
            self._current_cohort = self._full_dataset.copy()
            logger.info(f"Successfully loaded {len(csv_files)} files")
            return True
            
        except Exception as e:
            logger.error(f"Error loading CSV files: {str(e)}")
            return False

    def _prefix_columns(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """
        Add table name prefix to column names except join keys.
        """
        prefixed_columns = {}
        join_keys = [PATIENT_ID_COLUMN] + PATIENT_ID_ALTERNATIVES
        
        for col in df.columns:
            if col not in join_keys:  # If not a join key
                if not col.startswith(f"{table_name}."):  # If not already prefixed
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
            logger.debug(f"Starting merge with pacientes table, columns: {result.columns.tolist()}")
        else:
            first_table = list(remaining_dfs.keys())[0]
            result = remaining_dfs.pop(first_table)
            logger.debug(f"Starting merge with {first_table} table, columns: {result.columns.tolist()}")
        
        # Merge remaining DataFrames
        for table_name, df in remaining_dfs.items():
            # Look for join keys without considering prefixes
            join_key = None
            possible_keys = [PATIENT_ID_COLUMN] + PATIENT_ID_ALTERNATIVES
            
            for key in possible_keys:
                if key in result.columns and key in df.columns:
                    join_key = key
                    break
            
            if join_key is None:
                logger.warning(f"No join key found for table {table_name}, columns: {df.columns.tolist()}")
                continue
                
            logger.info(f"Merging {table_name} using key: {join_key}")
            result = result.merge(df, how='left', on=join_key)
            logger.debug(f"After merging {table_name}, columns: {result.columns.tolist()}")
        
        return result

    def apply_query_on_current_cohort(self, query: Query):
        """
        Apply a query to the current cohort.

        Args:
            query: Query object containing query parameters

        Returns:
            bool: True if query was applied successfully, False otherwise

        Raises:
            ValueError: If query is invalid or operation is not supported
        """
        logger.debug(f"Entered apply_query_on_current_cohort method.")
        result = self._apply_query_to_dataframe(query, self._current_cohort)
        logger.debug(f"apply_query_on_current_cohort >> Result shape after applying query: {result.shape if result is not None else 'None'}")
        self._current_cohort = result
        self._update_current_schema()
        logger.debug(f"New cohort shape: {self._current_cohort.shape if self._current_cohort is not None else 'None'}")

    def _apply_query_to_dataframe(self, query: Query, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply a query to the current cohort.

        Args:
            query: Query object containing query parameters

        Returns:
            bool: True if query was applied successfully, False otherwise

        Raises:
            ValueError: If query is invalid or operation is not supported
        """
        try:
            logger.debug(f"Entered _apply_query_to_dataframe with df shape {df.shape}")
            # Simple query
            if not query.is_complex:
                logger.debug(f"Applying simple query: {query.to_human_readable()}")
                result = self._apply_basic_query_to_dataframe(query, df)
                logger.debug(f"Result shape after simple query: {result.shape if result is not None else 'None'}")
                return result
            # Complex query
            else:
                logger.debug(f"Applying complex query: {query.to_human_readable()}")
                left_df = self._apply_query_to_dataframe(query.get_query1(), df)
                right_df = self._apply_query_to_dataframe(query.get_query2(), df)
                operation = query.get_operation().lower()
                result = self._apply_operation_to_dataframes(left_df, right_df, operation)
                logger.debug(f"Result shape after complex query: {result.shape if result is not None else 'None'}")
                return result
        
        except Exception as e:
            logger.error(f"Error applying query: {e}")
            return False

    def _apply_basic_query_to_dataframe(self, query: Query, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply a simple query to a DataFrame.
        
        Args:
            df (pd.DataFrame): Input DataFrame
            query (Query): Simple query object
                Example: Query with field="pacientes.Edad", operation="greater_than", value=40
        
        Returns:
            pd.DataFrame: Filtered DataFrame
            
        Raises:
            ValueError: If query is complex or operation is not supported
        """
        try:
            if query.is_complex:
                raise ValueError("Expected simple query, got complex query")
                
            field = query.get_field()
            operation = query.get_operation().lower()
            value = query.get_value()
            
            logger.debug(f"Applying query: {field} {operation} {value}")
            logger.debug(f"Input DataFrame shape: {df.shape}")
            
            # Verify field exists in DataFrame
            if field not in df.columns:
                raise ValueError(f"Field '{field}' not found in DataFrame")
                
            # Apply the appropriate operation
            if operation == 'equals':
                result = df[df[field] == value]
                
            elif operation == 'not_equals':
                result = df[df[field] != value]
                
            elif operation == 'greater_than':
                result = df[df[field] > value]
                
            elif operation == 'less_than':
                result = df[df[field] < value]
                
            elif operation == 'greater_equal':
                result = df[df[field] >= value]
                
            elif operation == 'less_equal':
                result = df[df[field] <= value]
                
            elif operation == 'contains':
                if not isinstance(value, str):
                    raise ValueError("'contains' operation requires string value")
                result = df[df[field].astype(str).str.contains(value, na=False)]
                
            elif operation == 'in':
                if not isinstance(value, (list, tuple)):
                    raise ValueError("'in' operation requires list or tuple value")
                result = df[df[field].isin(value)]
                
            elif operation == 'between':
                if not isinstance(value, (list, tuple)) or len(value) != 2:
                    raise ValueError("'between' operation requires list/tuple of 2 values")
                result = df[(df[field] >= value[0]) & (df[field] <= value[1])]
                
            elif operation == 'is_null':
                result = df[df[field].isna()]
                
            elif operation == 'is_not_null':
                result = df[df[field].notna()]
                
            else:
                raise ValueError(f"Unsupported operation: {operation}")
                
            logger.debug(f"Result DataFrame shape: {result.shape}")
            return result
            
        except Exception as e:
            logger.error(f"Error in _apply_basic_query_to_dataframe: {str(e)}")
            raise RuntimeError(f"Failed to apply query: {str(e)}")

    def _apply_operation_to_dataframes(self, df1: pd.DataFrame, df2: pd.DataFrame, operation: str) -> pd.DataFrame:
        """
        Apply logical operation (AND/OR) between two DataFrames.
        
        Args:
            df1 (pd.DataFrame): First DataFrame
            df2 (pd.DataFrame): Second DataFrame
            operation (str): Logical operation ('and' or 'or')
            
        Returns:
            pd.DataFrame: Result of applying the logical operation
            
        Example:
            If operation is 'and':
                Returns rows that exist in both df1 AND df2
            If operation is 'or':
                Returns rows that exist in either df1 OR df2
        """
        try:
            logger.debug(f"Applying {operation} operation between DataFrames")
            logger.debug(f"DataFrame 1 shape: {df1.shape}")
            logger.debug(f"DataFrame 2 shape: {df2.shape}")
            
            if operation.lower() == 'and':
                # For AND, we want intersection of both DataFrames
                # Keep only rows that exist in both DataFrames
                result = pd.merge(df1, df2, how='inner')
                
            elif operation.lower() == 'or':
                # For OR, we want union of both DataFrames
                # Keep rows that exist in either DataFrame
                result = pd.concat([df1, df2]).drop_duplicates()
                
            else:
                logger.error(f"Unsupported operation: {operation}")
                raise ValueError(f"Unsupported operation: {operation}. Use 'and' or 'or'.")
                
            logger.debug(f"Result DataFrame shape: {result.shape}")
            return result
            
        except Exception as e:
            logger.error(f"Error in _apply_operation: {str(e)}")
            raise RuntimeError(f"Failed to apply operation: {str(e)}")

    def _print_preview_df (self, df: pd.DataFrame, n: int = 5) -> None:
        """Print preview of DataFrame."""
        logger.debug(f"Preview of DataFrame (first {n} rows):")
        logger.debug(df.head(n))

    def _update_full_schema(self):
        """Update schema for the full dataset."""
        if self._full_dataset is not None:
            self._full_schema = self._create_schema(self._full_dataset)

    def _update_current_schema(self):
        """Update schema for the current cohort."""
        if self._current_cohort is not None:
            self._current_schema = self._create_schema(self._current_cohort)

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

    def _save_current_data(self, path: str, name: str) -> None:
        """
        Helper method to save the current cohort data to a CSV file.
        
        Args:
            path (str): Directory path where the file will be saved
            name (str): Base name for the file (without extension)
        """
        if self._current_cohort is None:
            raise ValueError("No cohort is currently loaded")
            
        file_path = os.path.join(path, f"{name}.csv")
        os.makedirs(path, exist_ok=True)
        self._current_cohort.to_csv(file_path, index=False)

    def _save_current_schema(self, path: str, name: str) -> None:
        """
        Helper method to save the current cohort schema to a text file.
        
        Args:
            path (str): Directory path where the file will be saved
            name (str): Base name for the file (without extension)
        """
        if self._current_cohort is None:
            raise ValueError("No cohort is currently loaded")
            
        schema_path = os.path.join(path, f"{name}_schema.txt")
        os.makedirs(path, exist_ok=True)
        
        # Get formatted schema using existing method
        formatted_schema = self._format_schema_to_string(self._current_schema)
               
        # Write formatted schema to file
        with open(schema_path, 'w', encoding='utf-8') as f:
            f.write(formatted_schema)
            
        logger.info(f"Saved current schema with {len(self._current_schema)} columns")


    def save_current_cohort(self, path: str = "root/data/temp/data_manager_output", 
                        name: str = "test") -> None:
        """
        Save the current cohort data and its schema to separate files.
        
        Args:
            path (str): Directory path where the files will be saved. 
                    Defaults to "root/data/temp/data_manager_output"
            name (str): Base name for the files (without extension). 
                    Defaults to "test"
        """
        # Normalize path separators for cross-platform compatibility
        path = os.path.normpath(path)
        
        # Save both data and schema
        self._save_current_data(path, name)
        self._save_current_schema(path, name)

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

    def get_readable_schema_current_cohort(self) -> str:
        """
        Get a human-readable string representation of the current cohort schema.

        Returns:
            str: Formatted string representation of the schema
        """
        if self._current_cohort is None:
            return "No current cohort available"

        return self._format_schema_to_string(self._current_schema)
    
    def get_readable_schema_full_dataset(self) -> str:
        """
        Get a human-readable string representation of the full dataset schema.

        Returns:
            str: Formatted string representation of the schema
        """
        if self._full_dataset is None:
            return "No full dataset available"

        return self._format_schema_to_string(self._full_schema)
    
    def _create_schema(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """
        Create schema for given DataFrame with enhanced value distribution information.
        """
        # Get original source tables from column prefixes
        source_tables = sorted(set(col.split('.')[0] for col in df.columns if '.' in col))
        
        # Look for patient ID column
        patient_id_col = next((col for col in [PATIENT_ID_COLUMN] + PATIENT_ID_ALTERNATIVES 
                             if col in df.columns), None)
        
        # Count unique patients if we found the ID column
        unique_patients = df[patient_id_col].nunique() if patient_id_col else None
        
        schema = {
            '_database_info': {
                'total_rows': len(df),
                'unique_patients': unique_patients,
                'total_columns': len(df.columns),
                'source_tables': source_tables,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        
        # Generate column-level information
        for column in df.columns:
            column_info = {
                'dtype': str(df[column].dtype),
                'unique_values': df[column].nunique(),
                'missing_values': df[column].isnull().sum(),
                'total_rows': len(df)
            }
            
            # Add numeric statistics for numeric columns
            if np.issubdtype(df[column].dtype, np.number):
                column_info.update({
                    'min': float(df[column].min()) if not df[column].isna().all() else None,
                    'max': float(df[column].max()) if not df[column].isna().all() else None,
                    'mean': float(df[column].mean()) if not df[column].isna().all() else None
                })
                
            # Add value distribution for columns with few unique values
            if 1 < df[column].nunique() <= UNIQUE_VALUES_THRESHOLD:
                value_counts = df[column].value_counts()
                total_non_null = value_counts.sum()
                
                distribution = []
                for value, count in value_counts.items():
                    percentage = (count / total_non_null) * 100
                    # Handle different types of values (including numpy types)
                    cleaned_value = str(value.item() if hasattr(value, 'item') else value)
                    distribution.append({
                        'value': cleaned_value,
                        'count': int(count),
                        'percentage': round(float(percentage), 2)
                    })
                
                column_info['value_distribution'] = distribution
            
            schema[column] = column_info
        
        return schema

    def _format_schema_to_string(self, schema: Dict[str, Dict]) -> str:
        """
        Format schema into a readable string representation.
        
        Args:
            schema (Dict[str, Dict]): Schema dictionary to format
            
        Returns:
            str: Formatted string representation of the schema
        """
        if not schema:
            return "Empty schema"
            
        formatted_lines = []
        
        # Database-level information
        if '_database_info' in schema:
            db_info = schema['_database_info']
            formatted_lines.extend([
                "DATABASE INFORMATION",
                "=" * 50,
                f"Total Rows: {db_info['total_rows']}",
                f"Unique Patients: {db_info['unique_patients']}",
                f"Total Columns: {db_info['total_columns']}",
                f"Original Source Tables: {', '.join(db_info['source_tables'])}",
                f"Schema Generated: {db_info['timestamp']}",
                "",
                "COLUMN DETAILS",
                "=" * 50,
                ""
            ])
        
        # Column-level information
        for column, info in sorted(schema.items()):
            if column == '_database_info':
                continue
                
            # Basic column information
            formatted_lines.append(f"Column: {column}")
            formatted_lines.append(f"- Type: {info['dtype']}")
            formatted_lines.append(f"- Unique Values: {info['unique_values']}")
            
            # Missing values information
            missing_percentage = (info['missing_values'] / info['total_rows']) * 100
            formatted_lines.append(
                f"- Missing Values: {info['missing_values']} of {info['total_rows']} "
                f"({missing_percentage:.2f}%)"
            )
            
            # Numeric statistics if available
            if all(key in info for key in ['min', 'max', 'mean']):
                if info['min'] is not None:  # Check if numeric stats exist
                    formatted_lines.extend([
                        f"- Minimum: {info['min']}",
                        f"- Maximum: {info['max']}",
                        f"- Mean: {info['mean']:.2f}"
                    ])
                
            # Value distribution if available
            if 'value_distribution' in info:
                formatted_lines.append("- Value Distribution:")
                for dist in info['value_distribution']:
                    formatted_lines.append(
                        f"  • {dist['value']}: {dist['count']} occurrences "
                        f"({dist['percentage']}%)"
                    )
            
            # Add blank line between columns
            formatted_lines.append("")
        
        return "\n".join(formatted_lines)
