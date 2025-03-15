# tests/test_query.py
import pytest
from datetime import datetime
from core.query import Query

@pytest.fixture
def sample_schema():
    """Provide test schema that matches our test data structure."""
    return {
        'PacienteID': {'dtype': 'int64', 'unique_values': 100, 'missing_values': 0},
        'Edad': {'dtype': 'int64', 'unique_values': 50, 'missing_values': 0},
        'Descripcion': {'dtype': 'object', 'unique_values': 10, 'missing_values': 0},
        'Fecha_inicio': {'dtype': 'datetime64[ns]', 'unique_values': 30, 'missing_values': 0}
    }

@pytest.fixture
def simple_query():
    """Provide a simple query for testing."""
    return Query({
        "field": "Edad",
        "operation": "greater_than",
        "value": 40
    })

@pytest.fixture
def complex_query():
    """Provide a complex query with nested conditions."""
    return Query({
        "operation": "and",
        "criteria": [
            {
                "field": "Edad",
                "operation": "greater_than",
                "value": 40
            },
            {
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
            }
        ]
    })

def test_query_initialization():
    """Test basic query initialization."""
    query_dict = {"field": "Edad", "operation": "equals", "value": 40}
    query = Query(query_dict)
    assert query.raw == query_dict
    assert isinstance(query.timestamp, datetime)

def test_simple_human_readable(simple_query):
    """Test human readable output for simple query."""
    readable = simple_query.to_human_readable()
    assert readable == "Edad es mayor que 40"

def test_complex_human_readable(complex_query):
    """Test human readable output for complex query."""
    readable = complex_query.to_human_readable()
    assert readable == "(Edad es mayor que 40 Y (Descripcion es igual a Diabetes tipo 2 O Descripcion es igual a Hipertensión))"

def test_query_validation_simple(simple_query, sample_schema):
    """Test validation of simple query against schema."""
    assert simple_query.validate(sample_schema) is True

def test_query_validation_complex(complex_query, sample_schema):
    """Test validation of complex query against schema."""
    assert complex_query.validate(sample_schema) is True

def test_query_validation_invalid_field(sample_schema):
    """Test validation with non-existent field."""
    query = Query({
        "field": "NonExistentField",
        "operation": "equals",
        "value": 40
    })
    assert query.validate(sample_schema) is False

def test_query_validation_invalid_operation(sample_schema):
    """Test validation with invalid operation for field type."""
    query = Query({
        "field": "Edad",
        "operation": "like",  # 'like' operation not supported for int64
        "value": 40
    })
    assert query.validate(sample_schema) is False

def test_query_validation_invalid_structure(sample_schema):
    """Test validation with invalid query structure."""
    query = Query({
        "operation": "and",
        "criteria": []  # Empty criteria list is invalid
    })
    assert query.validate(sample_schema) is False

def test_llm_format(complex_query):
    """Test LLM format output structure."""
    llm_format = complex_query.to_llm_format()
    
    assert "query_structure" in llm_format
    assert "human_readable" in llm_format
    assert "timestamp" in llm_format
    assert "metadata" in llm_format
    
    metadata = llm_format["metadata"]
    assert "operations_used" in metadata
    assert "fields_referenced" in metadata
    
    assert set(metadata["operations_used"]) == {"and", "or", "greater_than", "equals"}
    assert set(metadata["fields_referenced"]) == {"Edad", "Descripcion"}

def test_query_equality():
    """Test query equality comparison."""
    query1 = Query({"field": "Edad", "operation": "equals", "value": 40})
    query2 = Query({"field": "Edad", "operation": "equals", "value": 40})
    query3 = Query({"field": "Edad", "operation": "equals", "value": 41})
    
    assert query1 == query2
    assert query1 != query3
    assert query1 != "not a query"

def test_get_operations_used(complex_query):
    """Test extraction of used operations."""
    operations = complex_query._get_operations_used()
    assert set(operations) == {"and", "or", "greater_than", "equals"}

def test_get_fields_referenced(complex_query):
    """Test extraction of referenced fields."""
    fields = complex_query._get_fields_referenced()
    assert set(fields) == {"Edad", "Descripcion"}

def test_invalid_node_structure():
    """Test handling of invalid node structure."""
    query = Query({"invalid": "structure"})
    readable = query.to_human_readable()
    assert isinstance(readable, str)  # Should not raise exception
    assert not query.validate(sample_schema)

def test_string_representation(complex_query):
    """Test string representation of query."""
    assert str(complex_query) == complex_query.to_human_readable()

if __name__ == '__main__':
    pytest.main([__file__])
