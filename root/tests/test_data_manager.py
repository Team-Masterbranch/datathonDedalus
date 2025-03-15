# tests/test_data_manager.py
import pytest
import pandas as pd
import os
from datetime import datetime
from core.data_manager import DataManager
from core.visualizer_request import VisualizerRequest, ChartType
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
        'Fecha_inicio': pd.date_range(start='2023-01-01', periods=10),
        'Genero': ['M', 'F', 'M', 'F', 'M', 'F', 'M', 'F', 'M', 'F'],
        'Peso': [70.5, 65.2, 80.1, 55.8, 90.3, 60.7, 75.4, 68.9, 82.1, 58.6]
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
    """Test cases for DataManager initialization and basic functionality."""
    
    def test_successful_initialization(self, data_manager, sample_data):
        """Test successful initialization with valid data."""
        assert data_manager._full_dataset is not None
        assert data_manager._current_cohort is not None
        assert len(data_manager._full_schema) > 0
        assert len(data_manager._current_schema) > 0
        assert data_manager._current_cohort.shape == sample_data.shape
        assert set(data_manager._current_cohort.columns) == set(sample_data.columns)

    def test_invalid_data_path(self):
        """Test initialization with invalid data path."""
        with pytest.raises(ValueError, match="Failed to load data files"):
            DataManager("invalid/path/to/nowhere")

    def test_empty_directory(self, tmp_path):
        """Test initialization with empty directory."""
        with pytest.raises(ValueError, match="Failed to load data files"):
            DataManager(str(tmp_path))

    def test_schema_creation(self, data_manager):
        """Test schema creation and structure."""
        schema = data_manager.get_full_schema()
        
        # Check schema structure
        expected_columns = {'PacienteID', 'Edad', 'Descripcion', 'Fecha_inicio', 'Genero', 'Peso'}
        assert set(schema.keys()) == expected_columns
        
        # Check schema content for each column type
        assert schema['PacienteID']['dtype'] == 'int64'
        assert schema['Edad']['dtype'] == 'int64'
        assert schema['Descripcion']['dtype'] == 'object'
        # Allow either datetime or object for date field
        assert schema['Fecha_inicio']['dtype'] in ['object', 'datetime64[ns]']
        assert schema['Genero']['dtype'] == 'object'
        assert schema['Peso']['dtype'] == 'float64'


class TestQueryFiltering:
    """Test cases for query filtering functionality."""

    def test_numeric_equals_filter(self, data_manager):
        """Test numeric equality filter."""
        query = Query({
            "field": "Edad",
            "operation": "equals",
            "value": 25
        })
        result = data_manager.apply_filter(query)
        assert len(result) == 1
        assert result.iloc[0]['Edad'] == 25

    def test_numeric_range_filter(self, data_manager):
        """Test numeric range filter."""
        query = Query({
            "field": "Edad",
            "operation": "between",
            "values": [30, 50]
        })
        result = data_manager.apply_filter(query)
        assert len(result) == 5
        assert all(30 <= age <= 50 for age in result['Edad'])

    def test_string_equals_filter(self, data_manager):
        """Test string equality filter."""
        query = Query({
            "field": "Descripcion",
            "operation": "equals",
            "value": "Diabetes tipo 2"
        })
        result = data_manager.apply_filter(query)
        assert len(result) == 4
        assert all(desc == "Diabetes tipo 2" for desc in result['Descripcion'])

    def test_complex_and_filter(self, data_manager):
        """Test complex AND filter."""
        query = Query({
            "operation": "and",
            "criteria": [
                {
                    "field": "Edad",
                    "operation": "greater_than",
                    "value": 40
                },
                {
                    "field": "Genero",
                    "operation": "equals",
                    "value": "F"
                }
            ]
        })
        result = data_manager.apply_filter(query)
        assert all(age > 40 for age in result['Edad'])
        assert all(gender == "F" for gender in result['Genero'])

    def test_complex_or_filter(self, data_manager):
        """Test complex OR filter."""
        query = Query({
            "operation": "or",
            "criteria": [
                {
                    "field": "Descripcion",
                    "operation": "equals",
                    "value": "Asma"
                },
                {
                    "field": "Descripcion",
                    "operation": "equals",
                    "value": "Hipertensión"
                }
            ]
        })
        result = data_manager.apply_filter(query)
        assert all(desc in ["Asma", "Hipertensión"] for desc in result['Descripcion'])

class TestCohortManagement:
    """Test cases for cohort management functionality."""

    def test_reset_to_full(self, data_manager):
        """Test resetting cohort to full dataset."""
        initial_size = len(data_manager.get_current_cohort())
        
        # Apply filter
        query = Query({
            "field": "Edad",
            "operation": "greater_than",
            "value": 50
        })
        data_manager.apply_filter(query)
        
        # Reset and verify
        result = data_manager.reset_to_full()
        assert len(result) == initial_size
        assert result.equals(data_manager._full_dataset)

    def test_sequential_filters(self, data_manager):
        """Test applying multiple filters sequentially."""
        # First filter
        query1 = Query({
            "field": "Edad",
            "operation": "greater_than",
            "value": 40
        })
        result1 = data_manager.apply_filter(query1)
        size_after_first = len(result1)
        
        # Second filter
        query2 = Query({
            "field": "Genero",
            "operation": "equals",
            "value": "F"
        })
        result2 = data_manager.apply_filter(query2)
        
        assert len(result2) <= size_after_first
        assert all(gender == "F" for gender in result2['Genero'])

class TestDataExport:
    """Test cases for data export functionality."""

    def test_save_current_cohort(self, data_manager, tmp_path):
        """Test saving current cohort to CSV."""
        output_path = os.path.join(tmp_path, 'cohort.csv')
        
        # Save cohort
        success = data_manager.save_current_cohort(output_path)
        assert success
        assert os.path.exists(output_path)
        
        # Verify saved data
        saved_df = pd.read_csv(output_path)
        assert len(saved_df) == len(data_manager.get_current_cohort())
        assert list(saved_df.columns) == list(data_manager.get_current_cohort().columns)

    def test_save_filtered_cohort(self, data_manager, tmp_path):
        """Test saving filtered cohort to CSV."""
        # Apply filter
        query = Query({
            "field": "Edad",
            "operation": "greater_than",
            "value": 50
        })
        data_manager.apply_filter(query)
        
        # Save filtered cohort
        output_path = os.path.join(tmp_path, 'filtered_cohort.csv')
        success = data_manager.save_current_cohort(output_path)
        
        assert success
        saved_df = pd.read_csv(output_path)
        assert all(age > 50 for age in saved_df['Edad'])

    def test_save_with_invalid_path(self, data_manager):
        """Test saving to invalid path."""
        success = data_manager.save_current_cohort('')
        assert not success

# tests/test_data_manager.py
class TestVisualizationRequests:
    """Test cases for visualization request validation."""

    def test_valid_box_plot_request(self, data_manager):
        """Test validation of a valid box plot request."""
        request = VisualizerRequest(
            chart_type=ChartType.BOX,
            title="Age Distribution by Gender",
            x_column="Edad",
            category_column="Genero"
        )
        assert data_manager.validate_visualization_request(request)

    def test_invalid_box_plot_numeric(self, data_manager):
        """Test validation fails when using non-numeric column for box plot."""
        request = VisualizerRequest(
            chart_type=ChartType.BOX,
            title="Invalid Box Plot",
            x_column="Descripcion",  # Non-numeric column
            category_column="Genero"
        )
        assert not data_manager.validate_visualization_request(request)

    def test_valid_pie_chart_request(self, data_manager):
        """Test validation of a valid pie chart request."""
        request = VisualizerRequest(
            chart_type=ChartType.PIE,
            title="Disease Distribution",
            x_column="Descripcion"
        )
        assert data_manager.validate_visualization_request(request)

    def test_valid_scatter_plot_request(self, data_manager):
        """Test validation of a valid scatter plot request."""
        request = VisualizerRequest(
            chart_type=ChartType.SCATTER,
            title="Age vs Weight",
            x_column="Edad",
            y_column="Peso"
        )
        assert data_manager.validate_visualization_request(request)

    def test_invalid_column_name(self, data_manager):
        """Test validation fails with non-existent column."""
        request = VisualizerRequest(
            chart_type=ChartType.BAR,
            title="Invalid Column Test",
            x_column="NonExistentColumn",
            y_column="Edad"
        )
        assert not data_manager.validate_visualization_request(request)

    def test_missing_required_columns(self, data_manager):
        """Test validation fails when required columns are missing."""
        request = VisualizerRequest(
            chart_type=ChartType.SCATTER,
            title="Missing Columns Test",
            x_column="Edad"  # Missing y_column for scatter plot
        )
        assert not data_manager.validate_visualization_request(request)

    def test_validation_with_none_cohort(self, data_manager):
        """Test validation fails when current cohort is None."""
        data_manager._current_cohort = None
        request = VisualizerRequest(
            chart_type=ChartType.BAR,
            title="Test with None Cohort",
            x_column="Edad"
        )
        assert not data_manager.validate_visualization_request(request)

    def test_histogram_numeric_validation(self, data_manager):
        """Test validation of numeric column for histogram."""
        request = VisualizerRequest(
            chart_type=ChartType.HISTOGRAM,
            title="Age Distribution",
            x_column="Edad"
        )
        assert data_manager.validate_visualization_request(request)

        # Test with non-numeric column
        invalid_request = VisualizerRequest(
            chart_type=ChartType.HISTOGRAM,
            title="Invalid Histogram",
            x_column="Descripcion"
        )
        assert not data_manager.validate_visualization_request(invalid_request)

    def test_bar_chart_many_categories(self, data_manager):
        """Test validation warning for bar chart with many categories."""
        # Create many unique values matching the DataFrame length
        num_rows = len(data_manager._current_cohort)
        
        # First modify the data to have many unique values
        data_manager._current_cohort['ManyCategories'] = [f'Cat_{i}' for i in range(num_rows)]
        data_manager._update_current_schema()

        request = VisualizerRequest(
            chart_type=ChartType.BAR,
            title="Many Categories Test",
            category_column="ManyCategories",
            x_column="Edad"
        )
        # Should still validate but check logs for warning
        assert data_manager.validate_visualization_request(request)

    def test_multiple_column_validation(self, data_manager):
        """Test validation with multiple columns specified."""
        request = VisualizerRequest(
            chart_type=ChartType.BOX,
            title="Complex Box Plot",
            x_column="Edad",
            y_column="Peso",
            category_column="Genero"
        )
        assert data_manager.validate_visualization_request(request)

    def test_empty_request(self, data_manager):
        """Test validation with minimal request information."""
        request = VisualizerRequest(
            chart_type=ChartType.BAR,
            title="Empty Request"
            # No columns specified
        )
        # Should fail validation because BAR chart requires x_column
        assert not data_manager.validate_visualization_request(request)

        # Test with other chart types as well
        request_scatter = VisualizerRequest(
            chart_type=ChartType.SCATTER,
            title="Empty Scatter"
        )
        assert not data_manager.validate_visualization_request(request_scatter)

        request_box = VisualizerRequest(
            chart_type=ChartType.BOX,
            title="Empty Box"
        )
        assert not data_manager.validate_visualization_request(request_box)


    def test_validation_after_cohort_filter(self, data_manager):
        """Test validation after applying cohort filter."""
        # Apply a filter first
        query = Query({
            "field": "Genero",
            "operation": "equals",
            "value": "M"
        })
        data_manager.apply_filter(query)

        # Then validate visualization request
        request = VisualizerRequest(
            chart_type=ChartType.BOX,
            title="Filtered Cohort Plot",
            x_column="Edad",
            category_column="Descripcion"
        )
        assert data_manager.validate_visualization_request(request)


if __name__ == '__main__':
    pytest.main([__file__])
