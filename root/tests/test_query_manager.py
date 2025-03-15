# tests/test_query_manager.py
import pytest
from unittest.mock import Mock, patch
from core.query_manager import QueryManager, QueryExecutionError
from core.data_manager import DataManager
from core.query import Query
import pandas as pd

@pytest.fixture
def mock_data_manager():
    manager = Mock(spec=DataManager)
    # Create a real DataFrame for the mock to return
    df = pd.DataFrame({
        'Edad': range(10),
        'Descripcion': ['test'] * 10
    })
    manager.get_current_cohort.return_value = df
    return manager

@pytest.fixture
def query_manager(mock_data_manager):
    return QueryManager(mock_data_manager)

@pytest.mark.asyncio
async def test_execute_simple_query(query_manager, mock_data_manager):
    """Test execution of a simple query."""
    # Setup
    query = Query({
        "field": "Edad",
        "operation": "greater_than",
        "value": 50
    })
    
    # Create real DataFrame for mock returns
    filtered_df = pd.DataFrame({
        'Edad': [55, 60, 65, 70, 75],
        'Descripcion': ['test'] * 5
    })
    full_df = pd.DataFrame({
        'Edad': range(50, 80, 5),
        'Descripcion': ['test'] * 6
    })
    
    mock_data_manager.get_current_schema.return_value = {
        "Edad": {"dtype": "int64"}
    }
    mock_data_manager.apply_filter.return_value = filtered_df
    mock_data_manager.get_current_cohort.return_value = full_df

    # Execute
    result = await query_manager.execute_query(query)

    # Assert
    assert result["row_count"] == 5
    assert result["filtered_from"] == 6
    mock_data_manager.reset_to_full.assert_called_once()

@pytest.mark.asyncio
async def test_execute_complex_query(query_manager, mock_data_manager):
    """Test execution of a complex query with multiple conditions."""
    # Setup
    query = Query({
        "operation": "and",
        "criteria": [
            {
                "field": "Edad",
                "operation": "greater_than",
                "value": 50
            },
            {
                "field": "Descripcion",
                "operation": "equals",
                "value": "Diabetes"
            }
        ]
    })
    
    # Create real DataFrames for mock returns
    filtered_df = pd.DataFrame({
        'Edad': [55, 60, 65],
        'Descripcion': ['Diabetes'] * 3
    })
    full_df = pd.DataFrame({
        'Edad': range(50, 80, 5),
        'Descripcion': ['Diabetes'] * 6
    })
    
    mock_data_manager.get_current_schema.return_value = {
        "Edad": {"dtype": "int64"},
        "Descripcion": {"dtype": "object"}
    }
    mock_data_manager.apply_filter.return_value = filtered_df
    mock_data_manager.get_current_cohort.return_value = full_df

    # Execute
    result = await query_manager.execute_query(query)

    # Assert
    assert result["row_count"] == 3
    assert result["filtered_from"] == 6

@pytest.mark.asyncio
async def test_execute_query_with_cohort_filter(query_manager, mock_data_manager):
    """Test query execution with cohort filtering enabled."""
    # Setup
    query = Query({
        "field": "Edad",
        "operation": "greater_than",
        "value": 50
    })
    
    # Create real DataFrames for mock returns
    filtered_df = pd.DataFrame({
        'Edad': [55, 60],
        'Descripcion': ['test'] * 2
    })
    cohort_df = pd.DataFrame({
        'Edad': range(45, 65, 5),
        'Descripcion': ['test'] * 4
    })
    
    mock_data_manager.get_current_schema.return_value = {
        "Edad": {"dtype": "int64"}
    }
    mock_data_manager.apply_filter.return_value = filtered_df
    mock_data_manager.get_current_cohort.return_value = cohort_df

    # Execute
    result = await query_manager.execute_query(query, filter_current_cohort=True)

    # Assert
    assert result["row_count"] == 2
    assert result["filtered_from"] == 4
    assert result["filter_type"] == "current_cohort"
    mock_data_manager.reset_to_full.assert_not_called()

def test_get_current_cohort_size(query_manager, mock_data_manager):
    """Test getting the current cohort size."""
    # Create real DataFrame for mock return
    df = pd.DataFrame({
        'Edad': range(5),
        'Descripcion': ['test'] * 5
    })
    mock_data_manager.get_current_cohort.return_value = df
    
    size = query_manager.get_current_cohort_size()
    assert size == 5
