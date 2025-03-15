# tests/test_data_manager.py
import pytest
import pandas as pd
import os
from core.data_manager import DataManager
from core.query import Query
import tempfile

@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    return pd.DataFrame({
        'PacienteID': range(1, 11),
        'Edad': [25, 30, 35, 40, 45, 50, 55, 60, 65, 70],
        'Descripcion': ['Diabetes tipo 2', 'Hipertensión', 'Diabetes tipo 2', 
                       'Asma', 'Hipertensión', 'Diabetes tipo 2', 'Asma', 
                       'Hipertensión', 'Diabetes tipo 2', 'Asma'],
        'Fecha_inicio': pd.date_range(start='2023-01-01', periods=10)
    })

@pytest.fixture
def temp_data_dir(sample_data):
    """Create temporary directory with sample CSV data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        sample_data.to_csv(os.path.join(tmpdir, 'test_data.csv'), index=False)
        yield tmpdir

@pytest.fixture
def data_manager(temp_data_dir):
    """Create DataManager instance with sample data."""
    return DataManager(temp_data_dir)

class TestDataManagerInitialization:
    def test_initialization(self, data_manager, sample_data):
        """Test basic initialization of DataManager."""
        assert data_manager._full_dataset is not None
        assert data_manager._current_cohort is not None
        assert len(data_manager._full_schema) > 0
        assert len(data_manager._current_schema) > 0
        assert data_manager._current_cohort.shape == sample_data.shape

    def test_invalid_data_path(self):
        """Test initialization with invalid data path."""
        with pytest.raises(ValueError, match="Failed to load data files"):
            DataManager("invalid/path")

    def test_schema_creation(self, data_manager):
        """Test schema creation."""
        schema = data_manager.get_full_schema()
        expected_columns = {'PacienteID', 'Edad', 'Descripcion', 'Fecha_inicio'}
        assert set(schema.keys()) == expected_columns
        assert all(key in schema['Edad'] for key in ['dtype', 'unique_values', 'missing_values'])

class TestQueryFiltering:
    def test_simple_age_query(self, data_manager):
        """Test simple age filter query."""
        query = Query({
            "field": "Edad",
            "operation": "greater_than",
            "value": 50
        })
        result = data_manager.apply_filter(query)
        
        assert result is not None
        assert len(result) == 4  # Ages 55, 60, 65, 70
        assert all(age > 50 for age in result['Edad'])

    def test_condition_equals_query(self, data_manager):
        """Test condition equals filter query."""
        query = Query({
            "field": "Descripcion",
            "operation": "equals",
            "value": "Diabetes tipo 2"
        })
        result = data_manager.apply_filter(query)
        
        assert result is not None
        assert len(result) == 4  # Count of 'Diabetes tipo 2' records
        assert all(desc == "Diabetes tipo 2" for desc in result['Descripcion'])

    def test_complex_and_query(self, data_manager):
        """Test complex AND query."""
        query = Query({
            "operation": "and",
            "criteria": [
                {
                    "field": "Edad",
                    "operation": "greater_than",
                    "value": 40
                },
                {
                    "field": "Descripcion",
                    "operation": "equals",
                    "value": "Diabetes tipo 2"
                }
            ]
        })
        result = data_manager.apply_filter(query)
        
        assert result is not None
        assert all(age > 40 for age in result['Edad'])
        assert all(desc == "Diabetes tipo 2" for desc in result['Descripcion'])

    def test_complex_or_query(self, data_manager):
        """Test complex OR query."""
        query = Query({
            "operation": "or",
            "criteria": [
                {
                    "field": "Descripcion",
                    "operation": "equals",
                    "value": "Diabetes tipo 2"
                },
                {
                    "field": "Descripcion",
                    "operation": "equals",
                    "value": "Hipertensión"
                }
            ]
        })
        result = data_manager.apply_filter(query)
        
        assert result is not None
        assert len(result) == 7  # Count of Diabetes OR Hipertensión
        assert all(desc in ["Diabetes tipo 2", "Hipertensión"] for desc in result['Descripcion'])

    def test_between_query(self, data_manager):
        """Test between operation query."""
        query = Query({
            "field": "Edad",
            "operation": "between",
            "values": [30, 50]
        })
        result = data_manager.apply_filter(query)
        
        assert result is not None
        assert len(result) == 5  # Ages 30, 35, 40, 45, 50
        assert all(30 <= age <= 50 for age in result['Edad'])

    def test_invalid_field_query(self, data_manager):
        """Test query with invalid field."""
        query = Query({
            "field": "NonExistentField",
            "operation": "equals",
            "value": "test"
        })
        result = data_manager.apply_filter(query)
        assert result is None

    def test_invalid_operation_query(self, data_manager):
        """Test query with invalid operation."""
        query = Query({
            "field": "Edad",
            "operation": "invalid_op",
            "value": 40
        })
        result = data_manager.apply_filter(query)
        assert result is None

class TestCohortManagement:
    def test_reset_to_full(self, data_manager):
        """Test resetting cohort to full dataset."""
        initial_size = len(data_manager.get_current_cohort())
        
        # Apply a filter
        query = Query({
            "field": "Edad",
            "operation": "greater_than",
            "value": 50
        })
        data_manager.apply_filter(query)
        
        # Reset and verify
        result = data_manager.reset_to_full()
        assert result is not None
        assert len(result) == initial_size

    def test_sequential_filters(self, data_manager):
        """Test applying multiple filters sequentially."""
        # First filter: age > 40
        query1 = Query({
            "field": "Edad",
            "operation": "greater_than",
            "value": 40
        })
        result1 = data_manager.apply_filter(query1)
        assert result1 is not None
        size_after_first = len(result1)
        
        # Second filter: Diabetes tipo 2
        query2 = Query({
            "field": "Descripcion",
            "operation": "equals",
            "value": "Diabetes tipo 2"
        })
        result2 = data_manager.apply_filter(query2)
        assert result2 is not None
        assert len(result2) <= size_after_first

class TestSchemaManagement:
    def test_schema_updates_after_filter(self, data_manager):
        """Test schema updates after applying filters."""
        initial_schema = data_manager.get_current_schema()
        
        query = Query({
            "field": "Edad",
            "operation": "greater_than",
            "value": 50
        })
        data_manager.apply_filter(query)
        
        filtered_schema = data_manager.get_current_schema()
        assert filtered_schema['Edad']['unique_values'] < initial_schema['Edad']['unique_values']

    def test_schema_reset(self, data_manager):
        """Test schema reset when resetting to full dataset."""
        initial_schema = data_manager.get_current_schema()
        
        # Apply filter
        query = Query({
            "field": "Edad",
            "operation": "greater_than",
            "value": 50
        })
        data_manager.apply_filter(query)
        
        # Reset and verify schema
        data_manager.reset_to_full()
        reset_schema = data_manager.get_current_schema()
        assert reset_schema == initial_schema

if __name__ == '__main__':
    pytest.main([__file__])
