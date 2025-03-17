# tests/test_intention.py
import pytest
from core.intention import Intention, IntentionType, FilterTarget
from core.query import Query
from core.visualizer_request import VisualizerRequest

@pytest.fixture
def mock_data_manager():
    """Mock DataManager for testing"""
    class MockDataManager:
        def get_full_schema(self):
            return {
                "age": {
                    "dtype": "int64",
                    "unique_values": 100,
                    "missing_values": 0
                },
                "name": {
                    "dtype": "object",
                    "unique_values": 1000,
                    "missing_values": 0
                },
                "gender": {
                    "dtype": "object",
                    "unique_values": 3,
                    "missing_values": 0
                }
            }
            
        def get_current_schema(self):
            return {
                "age": {
                    "dtype": "int64",
                    "unique_values": 80,
                    "missing_values": 0
                },
                "gender": {
                    "dtype": "object",
                    "unique_values": 3,
                    "missing_values": 0
                }
            }
    
    return MockDataManager()

@pytest.fixture
def sample_query():
    """Fixture for a sample Query object"""
    return Query({
        "field": "age",
        "operation": "greater_than",
        "value": 40
    })

@pytest.fixture
def sample_visualizer_request():
    """Fixture for a sample VisualizerRequest object"""
    viz_request = VisualizerRequest(
        chart_type="bar",
        x_column="age",
        y_column="count",
        title="Age Distribution"  # Added required title parameter
    )
    return viz_request

class TestIntention:
    def test_cohort_filter_intention_valid(self, sample_query, mock_data_manager):
        """Test valid COHORT_FILTER intention creation and validation"""
        intention = Intention(
            intention_type=IntentionType.COHORT_FILTER,
            description="Filter patients over 40",
            query=sample_query,
            filter_target=FilterTarget.CURRENT_COHORT
        )
        
        assert intention.validate(mock_data_manager) is True
        assert len(intention.get_validation_errors()) == 0

    def test_cohort_filter_missing_target(self, sample_query, mock_data_manager):
        """Test COHORT_FILTER intention with missing filter_target"""
        intention = Intention(
            intention_type=IntentionType.COHORT_FILTER,
            description="Filter patients over 40",
            query=sample_query,
            filter_target=None
        )
        
        assert intention.validate(mock_data_manager) is False
        assert any("Filter target is required" in error 
                  for error in intention.get_validation_errors())

    def test_cohort_filter_invalid_target_type(self, sample_query, mock_data_manager):
        """Test COHORT_FILTER intention with invalid filter_target type"""
        intention = Intention(
            intention_type=IntentionType.COHORT_FILTER,
            description="Filter patients over 40",
            query=sample_query,
            filter_target="invalid_target"  # String instead of FilterTarget enum
        )
        
        assert intention.validate(mock_data_manager) is False
        assert any("Filter target must be a valid FilterTarget enum value" in error 
                  for error in intention.get_validation_errors())

    def test_visualization_intention_valid(self, sample_visualizer_request, mock_data_manager):
        """Test valid VISUALIZATION intention"""
        intention = Intention(
            intention_type=IntentionType.VISUALIZATION,
            description="Show age distribution",
            visualizer_request=sample_visualizer_request
        )
        
        # Mock the validate method of VisualizerRequest to return True
        original_validate = sample_visualizer_request.validate
        sample_visualizer_request.validate = lambda x: True
        
        try:
            assert intention.validate(mock_data_manager) is True
            assert len(intention.get_validation_errors()) == 0
        finally:
            # Restore original validate method
            sample_visualizer_request.validate = original_validate

    def test_visualization_intention_invalid_columns(self, sample_visualizer_request, mock_data_manager):
        """Test VISUALIZATION intention with invalid columns"""
        intention = Intention(
            intention_type=IntentionType.VISUALIZATION,
            description="Show invalid column distribution",
            visualizer_request=VisualizerRequest(
                chart_type="bar",
                x_column="invalid_column",  # Column that doesn't exist
                y_column="count",
                title="Invalid Column Distribution"
            )
        )
        
        assert intention.validate(mock_data_manager) is False
        assert any("Invalid visualizer request" in error 
                  for error in intention.get_validation_errors())



    def test_from_llm_response_visualization(self):
        """Test creating VISUALIZATION intention from LLM response"""
        llm_response = {
            "intention_type": "VISUALIZATION",
            "description": "Show age distribution",
            "visualizer_request": {
                "chart_type": "bar",
                "x_column": "age",
                "y_column": "count",
                "title": "Age Distribution"
            }
        }
        
        intention = Intention.from_llm_response(llm_response)
        
        # Test intention type
        assert intention.intention_type == IntentionType.VISUALIZATION, \
            f"Expected VISUALIZATION but got {intention.intention_type}"
        
        # Test visualizer request
        assert intention.visualizer_request is not None, "VisualizerRequest should not be None"
        assert intention.visualizer_request.chart_type == "bar"
        assert intention.visualizer_request.x_column == "age"
        assert intention.visualizer_request.y_column == "count"
        assert intention.visualizer_request.title == "Age Distribution"




    def test_help_intention_valid(self, mock_data_manager):
        """Test HELP intention"""
        intention = Intention(
            intention_type=IntentionType.HELP,
            description="Show available commands"
        )
        
        assert intention.validate(mock_data_manager) is True
        assert len(intention.get_validation_errors()) == 0

    def test_unknown_intention_valid(self, mock_data_manager):
        """Test UNKNOWN intention"""
        intention = Intention(
            intention_type=IntentionType.UNKNOWN,
            description="Unrecognized command"
        )
        
        assert intention.validate(mock_data_manager) is True
        assert len(intention.get_validation_errors()) == 0

    def test_missing_description(self, mock_data_manager):
        """Test intention with missing description"""
        intention = Intention(
            intention_type=IntentionType.HELP,
            description=""
        )
        
        assert intention.validate(mock_data_manager) is False
        assert any("Description is required" in error 
                  for error in intention.get_validation_errors())

    def test_from_llm_response_cohort_filter(self):
        """Test creating COHORT_FILTER intention from LLM response"""
        llm_response = {
            "intention_type": "COHORT_FILTER",
            "description": "Filter patients over 40",
            "query": {
                "field": "age",
                "operation": "greater_than",
                "value": 40
            },
            "filter_target": "CURRENT_COHORT"
        }

        intention = Intention.from_llm_response(llm_response)

        # Test intention type
        assert intention.intention_type == IntentionType.COHORT_FILTER, \
            f"Expected COHORT_FILTER but got {intention.intention_type}"

        # Test filter target
        assert intention.filter_target == FilterTarget.CURRENT_COHORT, \
            f"Expected CURRENT_COHORT but got {intention.filter_target}"

        # Test query
        assert intention.query is not None, "Query should not be None"
        assert intention.query._query_dict["field"] == "age", \
            f"Expected field 'age' but got {intention.query._query_dict['field']}"
        assert intention.query._query_dict["operation"] == "greater_than", \
            f"Expected operation 'greater_than' but got {intention.query._query_dict['operation']}"
        assert intention.query._query_dict["value"] == 40, \
            f"Expected value 40 but got {intention.query._query_dict['value']}"
