# tests/test_data_manager.py
import pytest
import pandas as pd
from core.data_manager import DataManager

@pytest.fixture
def test_data_path(tmp_path):
    """Create test data with realistic healthcare data structure."""
    data_dir = tmp_path / "test_data"
    data_dir.mkdir()
    
    # Create conditions test data
    conditions_data = pd.DataFrame({
        'PacienteID': [1, 1, 2, 2],
        'Fecha_inicio': ['2023-01-01', '2023-02-01', '2023-03-01', '2023-04-01'],
        'Fecha_fin': ['2024-01-01', '2024-02-01', '2024-03-01', '2024-04-01'],
        'Codigo_SNOMED': ['C0011849', 'C0020538', 'C0038356', 'C0027651'],
        'Descripcion': ['Hipertensión', 'Diabetes tipo 2', 'Asma', 'Migraña']
    })
    
    # Create allergies test data
    allergies_data = pd.DataFrame({
        'PacienteID': [1, 1, 2, 2],
        'Fecha_diagnostico': ['2023-01-01', '2023-02-01', '2023-03-01', '2023-04-01'],
        'Codigo_SNOMED': ['91936005', '91933007', '91931005', '300913006'],
        'Descripcion': ['Alergia al polen', 'Alergia a frutos secos', 
                       'Alergia a la leche', 'Alergia a la penicilina']
    })
    
    # Save test files
    conditions_data.to_csv(data_dir / "condiciones.csv", index=False)
    allergies_data.to_csv(data_dir / "alergias.csv", index=False)
    
    return str(data_dir)

@pytest.fixture
def data_manager(test_data_path):
    """Create DataManager instance with test data."""
    return DataManager(test_data_path)

def test_load_csv_files(data_manager):
    """Test initial data loading."""
    assert data_manager._full_dataset is not None
    assert data_manager._current_cohort is not None
    assert len(data_manager._full_dataset) > 0
    assert len(data_manager._current_cohort) > 0

def test_apply_equals_filter(data_manager):
    """Test applying equals filter condition."""
    filter_criteria = {
        "field": "Descripcion",
        "operation": "equals",
        "value": "Diabetes tipo 2"
    }
    
    data_manager.apply_filter(filter_criteria)
    filtered = data_manager._current_cohort
    
    assert filtered is not None
    assert len(filtered) > 0
    assert all(row['Descripcion'] == "Diabetes tipo 2" for _, row in filtered.iterrows())

def test_apply_greater_than_filter(data_manager):
    """Test applying greater than filter."""
    filter_criteria = {
        "field": "PacienteID",
        "operation": "greater_than",
        "value": 1
    }
    
    data_manager.apply_filter(filter_criteria)
    filtered = data_manager._current_cohort
    
    assert filtered is not None
    assert len(filtered) > 0
    assert all(row['PacienteID'] > 1 for _, row in filtered.iterrows())

def test_apply_less_than_filter(data_manager):
    """Test applying less than filter."""
    filter_criteria = {
        "field": "PacienteID",
        "operation": "less_than",
        "value": 2
    }
    
    data_manager.apply_filter(filter_criteria)
    filtered = data_manager._current_cohort
    
    assert filtered is not None
    assert len(filtered) > 0
    assert all(row['PacienteID'] < 2 for _, row in filtered.iterrows())

def test_apply_date_filter(data_manager):
    """Test applying date filters."""
    filter_criteria = {
        "field": "Fecha_inicio",
        "operation": "greater_than",
        "value": "2023-02-01"
    }
    
    data_manager.apply_filter(filter_criteria)
    filtered = data_manager._current_cohort
    
    assert filtered is not None
    assert len(filtered) > 0
    assert all(pd.to_datetime(row['Fecha_inicio']) > pd.to_datetime('2023-02-01') 
              for _, row in filtered.iterrows())

def test_reset_cohort(data_manager):
    """Test resetting cohort to full dataset."""
    # Apply a filter first
    filter_criteria = {
        "field": "Descripcion",
        "operation": "equals",
        "value": "Asma"
    }
    
    data_manager.apply_filter(filter_criteria)
    filtered_size = len(data_manager._current_cohort)
    assert filtered_size < len(data_manager._full_dataset)
    
    # Reset and verify
    data_manager.reset_to_full()
    assert len(data_manager._current_cohort) == len(data_manager._full_dataset)
    pd.testing.assert_frame_equal(data_manager._current_cohort, data_manager._full_dataset)

def test_filter_error_handling(data_manager):
    """Test error handling for filters."""
    original_data = data_manager._current_cohort.copy()
    
    # Test with non-existent field
    filter_criteria = {
        "field": "NonExistentField",
        "operation": "equals",
        "value": "SomeValue"
    }
    result = data_manager.apply_filter(filter_criteria)
    assert result is None
    pd.testing.assert_frame_equal(data_manager._current_cohort, original_data)
    
    # Test with invalid operation
    filter_criteria = {
        "field": "Descripcion",
        "operation": "INVALID_OP",
        "value": "Asma"
    }
    result = data_manager.apply_filter(filter_criteria)
    assert result is None
    pd.testing.assert_frame_equal(data_manager._current_cohort, original_data)

def test_data_immutability(data_manager):
    """Test that operations don't modify the original dataset."""
    original_full = data_manager._full_dataset.copy()
    
    # Apply filter
    data_manager.apply_filter({
        "field": "Descripcion",
        "operation": "equals",
        "value": "Asma"
    })
    
    # Reset and verify original data hasn't changed
    data_manager.reset_to_full()
    pd.testing.assert_frame_equal(original_full, data_manager._full_dataset)

if __name__ == '__main__':
    pytest.main([__file__])
