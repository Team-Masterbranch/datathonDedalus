# tests/test_data_manager.py
import sys
from pathlib import Path

# Add root directory to Python path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

import pytest
import pandas as pd
from core.data_manager import DataManager
from core.query import Query

@pytest.fixture
def data_manager():
    """Create a DataManager instance with real data"""
    root_dir = Path(__file__).parent.parent  # Get root directory
    data_dir = root_dir / "data"  # Path to data directory
    return DataManager(str(data_dir))

def test_simple_query_equals(data_manager):
    """Test simple equality query"""
    df = data_manager.get_current_cohort()  # Get the actual data
    query = Query.create_from_dict({
        'field': 'gender',
        'operation': 'equals',
        'value': 'F'
    })
    
    result = data_manager._apply_query_to_dataframe(query, df)
    assert len(result) > 0
    assert all(result['gender'] == 'F')


if __name__ == '__main__':
    pytest.main([__file__])
