# tests/test_query_preprocessor.py
import pytest
from core.query_preprocessor import QueryPreprocessor
from core.query import Query

@pytest.fixture
def preprocessor():
    """Create QueryPreprocessor instance for testing."""
    return QueryPreprocessor()

def test_initialization():
    """Test preprocessor initialization."""
    preprocessor = QueryPreprocessor()
    assert isinstance(preprocessor, QueryPreprocessor)
    assert preprocessor.get_cache_size() == 0
    assert hasattr(preprocessor, 'patterns')

def test_regex_patterns_compilation(preprocessor):
    """Test that regex patterns are properly compiled."""
    required_patterns = ['age_greater', 'age_less', 'condition_equals']
    for pattern in required_patterns:
        assert pattern in preprocessor.patterns
        assert hasattr(preprocessor.patterns[pattern], 'search')

class TestAgeQueries:
    """Test cases for age-related queries."""
    
    @pytest.mark.parametrize("query", [
        "pacientes con edad mayor que 40",
        "edad más que 40",
        "edad superior a 40",
        "años mayor que 40",
        "edad > 40"
    ])
    def test_age_greater_variations(self, preprocessor, query):
        """Test different variations of age greater than queries."""
        result, needs_llm = preprocessor.process_query(query)
        assert not needs_llm
        assert isinstance(result, Query)
        assert result.raw["field"] == "Edad"
        assert result.raw["operation"] == "greater_than"
        assert result.raw["value"] == 40

    @pytest.mark.parametrize("query", [
        "pacientes con edad menor que 40",
        "edad menos que 40",
        "edad inferior a 40",
        "años menor que 40",
        "edad < 40"
    ])
    def test_age_less_variations(self, preprocessor, query):
        """Test different variations of age less than queries."""
        result, needs_llm = preprocessor.process_query(query)
        assert not needs_llm
        assert isinstance(result, Query)
        assert result.raw["field"] == "Edad"
        assert result.raw["operation"] == "less_than"
        assert result.raw["value"] == 40

class TestConditionQueries:
    """Test cases for condition-related queries."""
    
    @pytest.mark.parametrize("query,condition", [
        ("condicion es Diabetes tipo 2", "Diabetes tipo 2"),
        ("enfermedad igual a Hipertensión", "Hipertensión"),
        ('condición "Diabetes tipo 2"', "Diabetes tipo 2"),
        ("condicion 'Hipertensión'", "Hipertensión")
    ])
    def test_condition_variations(self, preprocessor, query, condition):
        """Test different variations of condition queries."""
        result, needs_llm = preprocessor.process_query(query)
        assert not needs_llm
        assert isinstance(result, Query)
        assert result.raw["field"] == "Descripcion"
        assert result.raw["operation"] == "equals"
        assert result.raw["value"] == condition

def test_cache_functionality(preprocessor):
    """Test query caching functionality."""
    # First query - should process
    query = "edad mayor que 40"
    result1, needs_llm1 = preprocessor.process_query(query)
    assert not needs_llm1
    assert isinstance(result1, Query)
    
    # Same query again - should use cache
    result2, needs_llm2 = preprocessor.process_query(query)
    assert not needs_llm2
    assert result2 is result1  # Should be the exact same object from cache
    
    # Check cache size
    assert preprocessor.get_cache_size() == 1

def test_cache_clear(preprocessor):
    """Test cache clearing functionality."""
    # Add some queries to cache
    queries = ["edad mayor que 40", "edad menor que 30"]
    for query in queries:
        preprocessor.process_query(query)
    
    assert preprocessor.get_cache_size() == 2
    
    # Clear cache
    preprocessor.clear_cache()
    assert preprocessor.get_cache_size() == 0

def test_update_cache(preprocessor):
    """Test manual cache update."""
    query_str = "test query"
    query_obj = Query({"field": "Edad", "operation": "equals", "value": 40})
    
    preprocessor.update_cache(query_str, query_obj)
    assert preprocessor.get_cache_size() == 1
    
    # Verify cache retrieval
    cached_result = preprocessor._check_cache(query_str)
    assert cached_result is query_obj

def test_non_matching_query(preprocessor):
    """Test handling of queries that don't match any patterns."""
    query = "some complex query that doesn't match patterns"
    result, needs_llm = preprocessor.process_query(query)
    
    assert needs_llm
    assert isinstance(result, str)
    assert result == query

def test_invalid_age_format(preprocessor):
    """Test handling of invalid age format."""
    query = "edad mayor que cuarenta"  # Text instead of number
    result, needs_llm = preprocessor.process_query(query)
    
    assert needs_llm
    assert isinstance(result, str)

@pytest.mark.parametrize("invalid_input", [
    None,
    "",
    "   ",
    123,  # Non-string input
])
def test_invalid_inputs(preprocessor, invalid_input):
    """Test handling of invalid inputs."""
    try:
        result, needs_llm = preprocessor.process_query(invalid_input)
        assert needs_llm
        assert isinstance(result, str)
    except (AttributeError, TypeError):
        # Either outcome is acceptable - error or handling as unprocessable
        pass

def test_cache_consistency(preprocessor):
    """Test that cache maintains consistency across queries."""
    query1 = "edad mayor que 40"
    query2 = "edad mayor que 50"
    
    # Process first query
    result1, _ = preprocessor.process_query(query1)
    
    # Process second query
    result2, _ = preprocessor.process_query(query2)
    
    # Verify first query still returns original result
    cached_result, needs_llm = preprocessor.process_query(query1)
    assert not needs_llm
    assert cached_result is result1
    assert cached_result is not result2

def test_regex_match_edge_cases(preprocessor):
    """Test edge cases in regex matching."""
    edge_cases = [
        "edad    mayor    que    40",  # Multiple spaces
        "EDAD MAYOR QUE 40",  # All caps
        "edad mayor que40",  # No space before number
        "edadmayorque40"  # No spaces
    ]
    
    for query in edge_cases:
        result, needs_llm = preprocessor.process_query(query)
        if not needs_llm:
            assert isinstance(result, Query)
            assert result.raw["field"] == "Edad"

if __name__ == '__main__':
    pytest.main([__file__])
