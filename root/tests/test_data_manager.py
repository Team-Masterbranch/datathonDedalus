# tests/test_data_manager.py
import pytest
import pandas as pd
import numpy as np
import os
from datetime import datetime
from core.data_manager import DataManager
from core.query import Query
import tempfile

from root.utils.config import UNIQUE_VALUES_THRESHOLD

@pytest.fixture
def sample_csv_files():
    """Create temporary CSV files for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create pacientes.csv
        pacientes_df = pd.DataFrame({
            'PacienteID': [1, 2, 3, 4, 5],
            'Edad': [25, 35, 45, 55, 65],
            'Genero': ['M', 'F', 'M', 'F', 'M'],
            'Provincia': ['Madrid', 'Barcelona', 'Madrid', 'Valencia', 'Barcelona']
        })
        pacientes_df.to_csv(os.path.join(tmpdir, 'pacientes.csv'), index=False)

        # Create conditions.csv
        conditions_df = pd.DataFrame({
            'PacienteID': [1, 2, 3, 4, 5],
            'Descripcion': ['Diabetes', 'Asma', 'Hipertension', 'Diabetes', 'Asma'],
            'Fecha': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05']
        })
        conditions_df.to_csv(os.path.join(tmpdir, 'conditions.csv'), index=False)

        yield tmpdir

@pytest.fixture
def data_manager(sample_csv_files):
    """Create DataManager instance with sample data."""
    return DataManager(sample_csv_files)

def test_data_manager_initialization(data_manager):
    """Test if DataManager initializes correctly."""
    assert data_manager._full_dataset is not None
    assert data_manager._current_cohort is not None
    assert len(data_manager._full_dataset) > 0
    assert len(data_manager._current_cohort) > 0

def test_column_prefixing(data_manager):
    """Test if columns are correctly prefixed."""
    df = data_manager._full_dataset
    expected_columns = {
        'PacienteID',  # Join key should not be prefixed
        'pacientes.Edad',
        'pacientes.Genero',
        'pacientes.Provincia',
        'conditions.Descripcion',
        'conditions.Fecha'
    }
    assert set(df.columns) == expected_columns

def test_schema_creation(data_manager):
    """Test if schema is created correctly."""
    schema = data_manager.get_current_schema()
    
    # Check if all expected columns are in schema
    assert 'pacientes.Edad' in schema
    assert 'pacientes.Genero' in schema
    assert 'conditions.Descripcion' in schema
    
    # Check schema structure for a numeric column
    edad_schema = schema['pacientes.Edad']
    assert 'dtype' in edad_schema
    assert 'unique_values' in edad_schema
    assert 'missing_values' in edad_schema

def test_equals_filter(data_manager):
    """Test equals filter operation."""
    query = Query({
        "field": "pacientes.Genero",
        "operation": "equals",
        "value": "M"
    })
    
    filtered_df = data_manager.apply_filter(query)
    assert filtered_df is not None
    assert all(row == 'M' for row in filtered_df['pacientes.Genero'])

def test_greater_than_filter(data_manager):
    """Test greater than filter operation."""
    query = Query({
        "field": "pacientes.Edad",
        "operation": "greater_than",
        "value": 40
    })
    
    filtered_df = data_manager.apply_filter(query)
    assert filtered_df is not None
    assert all(age > 40 for age in filtered_df['pacientes.Edad'])

def test_not_equals_filter(data_manager):
    """Test not equals filter operation."""
    query = Query({
        "field": "pacientes.Provincia",
        "operation": "not_equals",
        "value": "Madrid"
    })
    
    filtered_df = data_manager.apply_filter(query)
    assert filtered_df is not None
    assert all(provincia != "Madrid" for provincia in filtered_df['pacientes.Provincia'])

def test_complex_filter(data_manager):
    """Test complex filter with multiple conditions."""
    query = Query({
        "operation": "and",
        "criteria": [
            {
                "field": "pacientes.Edad",
                "operation": "greater_than",
                "value": 30
            },
            {
                "field": "pacientes.Genero",
                "operation": "equals",
                "value": "M"
            }
        ]
    })
    
    filtered_df = data_manager.apply_filter(query)
    assert filtered_df is not None
    assert all(age > 30 for age in filtered_df['pacientes.Edad'])
    assert all(gender == 'M' for gender in filtered_df['pacientes.Genero'])

def test_reset_cohort(data_manager):
    """Test resetting cohort to full dataset."""
    # First apply a filter
    query = Query({
        "field": "pacientes.Genero",
        "operation": "equals",
        "value": "M"
    })
    data_manager.apply_filter(query)
    
    # Then reset
    original_size = len(data_manager._full_dataset)
    data_manager.reset_to_full()
    assert len(data_manager._current_cohort) == original_size

def test_save_cohort(data_manager, tmp_path):
    """Test saving cohort to CSV."""
    # Apply a filter
    query = Query({
        "field": "pacientes.Edad",
        "operation": "greater_than",
        "value": 40
    })
    data_manager.apply_filter(query)
    
    # Save filtered cohort
    output_path = os.path.join(tmp_path, 'filtered_cohort.csv')
    success = data_manager.save_current_cohort(output_path)
    
    assert success
    assert os.path.exists(output_path)
    saved_df = pd.read_csv(output_path)
    assert all(age > 40 for age in saved_df['pacientes.Edad'])


def test_unique_values_threshold(data_manager):
    """Test unique values threshold in schema."""
    schema = data_manager.get_current_schema()
    
    # Debug output
    print("\nSchema for Genero:", schema['pacientes.Genero'])
    print("Schema for Edad:", schema['pacientes.Edad'])
    
    # Test categorical field (Genero - should have possible_values)
    genero_schema = schema['pacientes.Genero']
    assert 'unique_values' in genero_schema
    assert genero_schema['unique_values'] <= 5  # We know there are only 2 values: M, F
    assert 'possible_values' in genero_schema
    assert set(genero_schema['possible_values']) == {'M', 'F'}
    
    # Test numeric field (Edad - should have numeric stats instead of possible_values)
    edad_schema = schema['pacientes.Edad']
    assert 'unique_values' in edad_schema
    assert 'min' in edad_schema
    assert 'max' in edad_schema
    assert 'mean' in edad_schema
    assert 'possible_values' not in edad_schema  # Numeric field should not list all values
    
    # Test text field with many values (Provincia)
    provincia_schema = schema['pacientes.Provincia']
    assert 'unique_values' in provincia_schema
    if provincia_schema['unique_values'] <= 5:
        assert 'possible_values' in provincia_schema
    else:
        assert 'possible_values' not in provincia_schema


def test_schema_handling(data_manager):
    """Test schema creation for different types of fields."""
    schema = data_manager.get_current_schema()
    
    # Test numeric field (Edad)
    edad_schema = schema['pacientes.Edad']
    assert edad_schema['dtype'] == 'int64'
    assert 'unique_values' in edad_schema
    assert 'min' in edad_schema
    assert 'max' in edad_schema
    assert 'mean' in edad_schema
    assert 'possible_values' not in edad_schema
    
    # Test categorical field (Genero)
    genero_schema = schema['pacientes.Genero']
    assert 'unique_values' in genero_schema
    assert genero_schema['unique_values'] == 2
    assert 'possible_values' in genero_schema
    assert set(genero_schema['possible_values']) == {'M', 'F'}
    
    # Test date field (Fecha)
    fecha_schema = schema['conditions.Fecha']
    assert 'unique_values' in fecha_schema
        
    # Test text field (Provincia)
    provincia_schema = schema['pacientes.Provincia']
    assert 'unique_values' in provincia_schema
    if provincia_schema['unique_values'] <= UNIQUE_VALUES_THRESHOLD:
        assert 'possible_values' in provincia_schema
        assert len(provincia_schema['possible_values']) == provincia_schema['unique_values']




def test_schema_numeric_stats(data_manager):
    """Test numeric statistics in schema."""
    schema = data_manager.get_current_schema()
    edad_schema = schema['pacientes.Edad']
    
    assert edad_schema['min'] == 25
    assert edad_schema['max'] == 65
    assert 'mean' in edad_schema
    assert isinstance(edad_schema['mean'], (int, float))

def test_schema_categorical_stats(data_manager):
    """Test categorical field statistics in schema."""
    schema = data_manager.get_current_schema()
    genero_schema = schema['pacientes.Genero']
    
    assert genero_schema['unique_values'] == 2
    assert 'missing_values' in genero_schema
    assert 'possible_values' in genero_schema
    assert set(genero_schema['possible_values']) == {'M', 'F'}

if __name__ == '__main__':
    pytest.main([__file__])
