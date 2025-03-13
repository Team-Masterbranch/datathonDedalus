from core.data_manager import DataManager
from utils.logger import logger

def test_data_loading():
    logger.info("Starting data manager test")
    
    # Initialize DataManager with correct data path
    data_path = "data" 
    data_manager = DataManager(data_path)
    
    try:
        # Test loading and merging CSV files
        assert data_manager.load_csv_files(), "Data loading should succeed"
        
        # Check if data was loaded
        data = data_manager.get_data()
        assert not data.empty, "Data should not be empty"
        logger.info(f"Successfully loaded dataset with {len(data)} rows")
        
        # Check if current cohort matches full dataset initially
        cohort = data_manager.get_current_cohort()
        assert len(cohort) == len(data), "Initial cohort should contain all patients"
        logger.info("Current cohort matches full dataset")
        
        # Test data cleaning
        assert data_manager.clean_data(), "Data cleaning should succeed"
        logger.info("Data cleaning completed successfully")
            
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise

if __name__ == "__main__":
    test_data_loading()
