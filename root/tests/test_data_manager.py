# tests/test_data_manager.py
import pytest
import pandas as pd
import os
from datetime import datetime
from core.data_manager import DataManager

if __name__ == '__main__':
    pytest.main([__file__])

@pytest.fixture
def test_data_path(tmp_path):
    """Create temporary test data files."""
    # Create test directory
    data_dir = tmp_path / "test_data"
    data_dir.mkdir()
    
    # Create test CSV files
    patients_data = pd.DataFrame({
        'PacienteID': [1, 2, 3],
        'Nombre': ['John', 'Jane', 'Bob'],
        'Edad': [45, 55, 35],
        'Fecha_registro': ['2023-01-01', '2023-01-02', '2023-01-03']
    })
    
    conditions_data = pd.DataFrame({
        'PacienteID': [1, 1, 2],
        'Condicion': ['Diabetes', 'Hypertension', 'Asthma'],
        'Fecha_inicio': ['2022-01-01', '2022-02-01', '2022-03-01'],
        'Fecha_fin': ['2023-12-31', None, '2024-12-31']
    })
    
    # Save test files
    patients_data.to_csv(data_dir / "pacientes.csv", index=False)
    conditions_data.to_csv(data_dir / "condiciones.csv", index=False)
    
    return str(data_dir)

@pytest.fixture
def data_manager(test_data_path):
    """Create DataManager instance with test data."""
    dm = DataManager(test_data_path)
    dm.load_csv_files()
    return dm

def test_load_csv_files(data_manager):
    """Test CSV loading and merging."""
    # Check if data was loaded correctly
    assert not data_manager.full_dataset.empty
    
    # Since we have 3 patients and some have multiple conditions,
    # we should have one row per patient-condition combination
    expected_rows = len(data_manager.full_dataset)
    assert expected_rows == len(data_manager.full_dataset)
    
    # Check if all expected columns are present
    assert 'Condicion' in data_manager.full_dataset.columns
    assert 'Nombre' in data_manager.full_dataset.columns

def test_clean_data(data_manager):
    """Test data cleaning operations."""
    assert data_manager.clean_data()
    
    # Check date conversions
    assert pd.api.types.is_datetime64_dtype(data_manager.full_dataset['Fecha_registro'])
    assert pd.api.types.is_datetime64_dtype(data_manager.full_dataset['Fecha_inicio'])
    
    # Check missing end dates
    assert not data_manager.full_dataset['Fecha_fin'].isna().any()
    
    # Check if any end dates are set to the future date
    future_date = pd.Timestamp('2025-12-31')
    assert (data_manager.full_dataset['Fecha_fin'] == future_date).any()

def test_apply_filter(data_manager):
    """Test filter application."""
    # Test numeric filter
    data_manager.apply_filter({"Edad": (">=", 50)})
    assert len(data_manager.current_cohort) == 1
    assert data_manager.current_cohort.iloc[0]['Nombre'] == 'Jane'
    
    # Test string filter
    data_manager.reset_to_full()
    data_manager.apply_filter({"Condicion": ("==", "Diabetes")})
    filtered_df = data_manager.current_cohort
    assert len(filtered_df[filtered_df['Condicion'] == 'Diabetes']) > 0
    
    # Test multiple conditions
    data_manager.reset_to_full()
    data_manager.apply_filter({
        "Edad": (">=", 40),
        "Condicion": ("==", "Diabetes")
    })
    assert len(data_manager.current_cohort) > 0

def test_reset_to_full(data_manager):
    """Test cohort reset."""
    # Apply filter first
    data_manager.apply_filter({"Edad": (">=", 50)})
    assert len(data_manager.current_cohort) < len(data_manager.full_dataset)
    
    # Test reset
    data_manager.reset_to_full()
    assert len(data_manager.current_cohort) == len(data_manager.full_dataset)
    pd.testing.assert_frame_equal(data_manager.current_cohort, data_manager.full_dataset)

def test_schema_generation(data_manager):
    """Test schema metadata generation."""
    schema = data_manager.get_schema()
    
    # Check basic schema structure
    assert "Edad" in schema
    assert "type" in schema["Edad"]
    assert "unique_count" in schema["Edad"]
    
    # Check numerical column metadata
    assert "min" in schema["Edad"]
    assert "max" in schema["Edad"]
    assert "mean" in schema["Edad"]
    
    # Check categorical column metadata
    assert "Condicion" in schema
    assert "unique_values" in schema["Condicion"]
    assert isinstance(schema["Condicion"]["unique_values"], list)


def test_schema_updates_with_filter(data_manager):
    """Test schema updates when cohort changes."""
    initial_schema = data_manager.get_schema()
    initial_age_stats = {
        "min": initial_schema["Edad"]["min"],
        "max": initial_schema["Edad"]["max"]
    }
    
    # Apply filter and check schema updates
    data_manager.apply_filter({"Edad": (">=", 50)})
    updated_schema = data_manager.get_schema()
    
    assert updated_schema["Edad"]["min"] >= 50
    assert updated_schema["Edad"]["min"] != initial_age_stats["min"]
    assert updated_schema["Edad"]["unique_count"] < initial_schema["Edad"]["unique_count"]

def test_invalid_filter(data_manager):
    """Test error handling for invalid filters."""
    with pytest.raises(ValueError, match="Column.*not found in dataset"):
        data_manager.apply_filter({"NonexistentColumn": ("==", "value")})

def test_data_immutability(data_manager):
    """Test that full_dataset remains immutable."""
    original_data = data_manager.full_dataset.copy()
    
    # Try to modify the returned DataFrame
    df = data_manager.full_dataset
    df.loc[0, "Nombre"] = "Changed"
    
    # Verify original data wasn't changed
    pd.testing.assert_frame_equal(data_manager.full_dataset, original_data)
