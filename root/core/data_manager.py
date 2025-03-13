import pandas as pd
import os
from typing import Optional
from datetime import datetime
from utils.logger import logger

class DataManager:
    """
    Centralized data management class that maintains patient data in a single DataFrame.
    All related information (conditions, medications, etc.) will be merged with patient data.

    Attributes:
        data_path (str): Path to the directory containing the CSV files.
        data (pd.DataFrame): Single DataFrame containing all patient data and related information.
    """

    def __init__(self, data_path: str):
        """
        Initialize the DataManager with the path to the data directory.

        Args:
            data_path (str): Path to the directory containing the CSV files.
        """
        self.data_path = data_path
        self.data: Optional[pd.DataFrame] = None
        self.current_cohort: Optional[pd.DataFrame] = None

    def load_csv_files(self) -> bool:
        """
        Load and merge all CSV files into a single DataFrame.
        Returns:
            bool: True if loading successful, False otherwise.
        """
        try:
            logger.info("Loading CSV files from data directory.")
            
            # Load patients as base DataFrame
            patients_path = os.path.join(self.data_path, 'pacientes.csv')  # Changed from 'patients.csv'
            self.data = pd.read_csv(patients_path)
            
            # Get list of other CSV files
            related_files = [f for f in os.listdir(self.data_path) 
                        if f.endswith('.csv') and f != 'pacientes.csv']  # Changed from 'patients.csv'
            
            # Merge each related table with patient data
            for file in related_files:
                table_name = os.path.splitext(file)[0]
                file_path = os.path.join(self.data_path, file)
                
                logger.info(f"Merging {table_name} data.")
                related_data = pd.read_csv(file_path)
                
                # Merge with patient data
                self.data = pd.merge(
                    self.data,
                    related_data,
                    on='PacienteID',
                    how='left',
                    suffixes=('', f'_{table_name}')
                )

            # Initialize current cohort as all patients
            self.current_cohort = self.data.copy()
            
            logger.info("Data loading and merging completed successfully.")
            return True

        except FileNotFoundError as e:
            logger.error(f"Error loading CSV files: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during data loading: {e}")
            return False

    def clean_data(self) -> bool:
        """
        Clean the loaded data by handling missing values and standardizing formats.
        
        Returns:
            bool: True if cleaning successful, False otherwise.
        """
        try:
            logger.info("Starting data cleaning process.")

            if self.data is None:
                logger.error("No data loaded to clean")
                return False

            # Create a copy of the data for cleaning
            cleaned_data = self.data.copy()

            # Convert date columns to datetime
            date_columns = [col for col in cleaned_data.columns 
                        if 'Fecha' in col]
            
            for col in date_columns:
                cleaned_data[col] = pd.to_datetime(cleaned_data[col])
                
            # Fill missing end dates with future date
            end_date_columns = [col for col in date_columns 
                            if 'Fecha_fin' in col]
            for col in end_date_columns:
                # Replace inplace operation with assignment
                cleaned_data[col] = cleaned_data[col].fillna(datetime(2025, 12, 31))

            # Assign cleaned data back to main data and current cohort
            self.data = cleaned_data
            self.current_cohort = cleaned_data.copy()
            
            logger.info("Data cleaning completed.")
            return True

        except Exception as e:
            logger.error(f"Error during data cleaning: {e}")
            return False

    def get_data(self) -> pd.DataFrame:
        """
        Return the complete DataFrame.

        Returns:
            pd.DataFrame: The complete dataset.
        """
        return self.data if self.data is not None else pd.DataFrame()

    def get_current_cohort(self) -> pd.DataFrame:
        """
        Return the current filtered cohort.

        Returns:
            pd.DataFrame: The current cohort.
        """
        return self.current_cohort if self.current_cohort is not None else pd.DataFrame()

    def reset_cohort(self) -> None:
        """Reset the current cohort to include all patients."""
        if self.data is not None:
            self.current_cohort = self.data.copy()
            logger.info("Reset cohort to include all patients.")
