import pandas as pd
import logging
import os
from typing import Dict, Optional, List  
from datetime import datetime

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataLoader:
    """
    A class to handle loading and cleaning of patient data from CSV files.
    Data is kept in separate DataFrames to avoid duplication and maintain one-to-many relationships.

    Attributes:
        data_path (str): Path to the directory containing the CSV files.
        data (Dict[str, pd.DataFrame]): Dictionary of DataFrames for each data type.
    """

    def __init__(self, data_path: str):
        """
        Initialize the DataLoader with the path to the data directory.

        Args:
            data_path (str): Path to the directory containing the CSV files.
        """
        self.data_path = data_path
        self.data: Dict[str, pd.DataFrame] = {}

    def load_csv_files(self) -> Dict[str, pd.DataFrame]:
        """
        Load all CSV files from the data directory into separate DataFrames.
        Uses the filename (without extension) as the key in the dictionary.

        Returns:
            Dict[str, pd.DataFrame]: A dictionary mapping table names to DataFrames.
        """
        try:
            logger.info("Loading CSV files from data directory.")
            
            # Get a list of all .csv files in the data directory
            csv_files = [f for f in os.listdir(self.data_path) if f.endswith('.csv')]
            
            if not csv_files:
                logger.warning("No CSV files found in the data directory.")
                return self.data

            # Load each CSV file into a DataFrame
            for csv_file in csv_files:
                # Use the filename (without extension) as the key
                table_name = os.path.splitext(csv_file)[0]
                file_path = os.path.join(self.data_path, csv_file)
                
                logger.info(f"Loading {csv_file} as '{table_name}'.")
                self.data[table_name] = pd.read_csv(file_path)

            logger.info("CSV files loaded successfully.")
            return self.data
        except FileNotFoundError as e:
            logger.error(f"Error loading CSV files: {e}")
            raise ValueError("The specified data directory does not exist.")
        except Exception as e:
            logger.error(f"Unexpected error loading CSV files: {e}")
            raise RuntimeError("Failed to load CSV files.")

    def clean_data(self) -> Dict[str, pd.DataFrame]:
        """
        Clean the loaded data by handling missing values and standardizing formats.

        Returns:
            Dict[str, pd.DataFrame]: Dictionary of cleaned DataFrames.
        """
        logger.info("Starting data cleaning process.")

        # Handle missing values in conditions data
        self.data["conditions"]["Fecha_fin"].fillna(datetime(2025, 12, 31), inplace=True)

        # Standardize date formats across all DataFrames
        for df_name, df in self.data.items():
            if "Fecha_inicio" in df.columns:
                df["Fecha_inicio"] = pd.to_datetime(df["Fecha_inicio"])
            if "Fecha_fin" in df.columns:
                df["Fecha_fin"] = pd.to_datetime(df["Fecha_fin"])

        logger.info("Data cleaning completed.")
        return self.data

    def get_patient_data(self) -> pd.DataFrame:
        """
        Return the patient DataFrame.

        Returns:
            pd.DataFrame: The patient DataFrame.
        """
        return self.data["patients"]

    def get_related_data(self, table_name: str, patient_ids: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Get data from a related table (e.g., conditions, allergies) optionally filtered by patient IDs.

        Args:
            table_name (str): Name of the table to retrieve (e.g., "conditions", "allergies").
            patient_ids (Optional[List[str]]): List of patient IDs to filter by. If None, return all data.

        Returns:
            pd.DataFrame: DataFrame containing the related data.
        """
        if table_name not in self.data:
            raise ValueError(f"Table '{table_name}' does not exist in the data.")

        if patient_ids:
            return self.data[table_name][self.data[table_name]["PacienteID"].isin(patient_ids)]
        else:
            return self.data[table_name]

    def load_and_preprocess_data(self) -> Dict[str, pd.DataFrame]:
        """
        Load and clean all patient data, keeping it in separate DataFrames.

        Returns:
            Dict[str, pd.DataFrame]: Dictionary of preprocessed DataFrames.
        """
        try:
            # Load CSV files
            self.load_csv_files()

            # Clean the data
            self.clean_data()

            logger.info("Data loading and preprocessing completed successfully.")
            return self.data
        except Exception as e:
            logger.error(f"Error during data loading and preprocessing: {e}")
            raise RuntimeError("Failed to load and preprocess data.")