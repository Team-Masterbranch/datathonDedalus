from core.data_loader import DataLoader
from utils.logger import logger

def test_data_loading():
    logger.info("Starting data loader test")
    
    # Initialize DataLoader with your data path
    data_loader = DataLoader("data")
    
    try:
        # Test loading CSV files
        data = data_loader.load_csv_files()
        logger.info(f"Successfully loaded {len(data)} datasets")
        
        # You can add more specific tests here
        for table_name, df in data.items():
            logger.info(f"Table '{table_name}' has {len(df)} rows")
            
    except Exception as e:
        logger.error(f"Test failed: {e}")

if __name__ == "__main__":
    test_data_loading()
