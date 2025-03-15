# tests/test_parser.py
import pytest
from core.parser import Parser
from core.query import Query

@pytest.fixture
def parser():
    """Create Parser instance for testing."""
    return Parser()

@pytest.fixture
def sample_schema():
    """Provide test schema that matches our test data."""
    return {
        'PacienteID': {'dtype': 'int64', 'unique_values': 100, 'missing_values': 0},
        'Edad': {'dtype': 'int64', 'unique_values': 50, 'missing_values': 0},
        'Descripcion': {'dtype': 'object', 'unique_values': 10, 'missing_values': 0},
        'Fecha_inicio': {'dtype': 'datetime64[ns]', 'unique_values': 30, 'missing_values': 0}
    }

def test_parser_initialization():
    """Test basic parser initialization."""
    parser = Parser()
    assert isinstance(parser, Parser)

def test_process_age_query(parser):
    """Test processing of age-related query."""
    query = "pacientes con edad mayor que 40"
    result = parser.process_with_llm(query)
    
    assert isinstance(result, Query)
    assert result.raw["field"] == "Edad"
    assert result.raw["operation"] == "greater_than"
    assert result.raw["value"] == 40

def test_process_condition_query(parser):
    """Test processing of condition-related query."""
    query = "pacientes con condicion diabetes o hipertension"
    result = parser.process_with_llm(query)
    
    assert isinstance(result, Query)
    assert result.raw["operation"] == "or"
    assert len(result.raw["criteria"]) == 2
    assert all(c["field"] == "Descripcion" for c in result.raw["criteria"])
    assert "Diabetes tipo 2" in [c["value"] for c in result.raw["criteria"]]
    assert "Hipertensión" in [c["value"] for c in result.raw["criteria"]]

def test_process_complex_query(parser):
    """Test processing of complex query with AND condition."""
    query = "pacientes mayores de 40 and con diabetes"
    result = parser.process_with_llm(query)
    
    assert isinstance(result, Query)
    assert result.raw["operation"] == "and"
    assert len(result.raw["criteria"]) == 2
    
    # Check first condition (age)
    age_condition = [c for c in result.raw["criteria"] 
                    if c["field"] == "Edad"][0]
    assert age_condition["operation"] == "greater_than"
    assert age_condition["value"] == 40
    
    # Check second condition (diabetes)
    disease_condition = [c for c in result.raw["criteria"] 
                        if c["field"] == "Descripcion"][0]
    assert disease_condition["operation"] == "equals"
    assert disease_condition["value"] == "Diabetes tipo 2"

def test_process_default_query(parser):
    """Test processing of query that doesn't match any patterns."""
    query = "query without specific keywords"
    result = parser.process_with_llm(query)
    
    assert isinstance(result, Query)
    assert result.raw["field"] == "Edad"
    assert result.raw["operation"] == "greater_than"
    assert result.raw["value"] == 70

def test_validate_criteria_simple(parser):
    """Test validation of simple criteria."""
    criteria = {
        "field": "Edad",
        "operation": "greater_than",
        "value": 40
    }
    assert parser.validate_criteria(criteria) is True

def test_validate_criteria_complex(parser):
    """Test validation of complex criteria."""
    criteria = {
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
    }
    assert parser.validate_criteria(criteria) is True

def test_validate_criteria_invalid_operation(parser):
    """Test validation with invalid operation."""
    criteria = {
        "field": "Edad",
        "operation": "invalid_op",
        "value": 40
    }
    assert parser.validate_criteria(criteria) is False

def test_validate_criteria_missing_field(parser):
    """Test validation with missing field."""
    criteria = {
        "operation": "equals",
        "value": 40
    }
    assert parser.validate_criteria(criteria) is False

def test_validate_criteria_invalid_structure(parser):
    """Test validation with invalid structure."""
    criteria = {
        "operation": "and",
        "criteria": "not a list"
    }
    assert parser.validate_criteria(criteria) is False

def test_validate_criteria_between_operation(parser):
    """Test validation of between operation."""
    criteria = {
        "field": "Edad",
        "operation": "between",
        "values": [20, 30]
    }
    assert parser.validate_criteria(criteria) is True

def test_validate_criteria_invalid_between(parser):
    """Test validation of invalid between operation."""
    criteria = {
        "field": "Edad",
        "operation": "between",
        "values": [20]  # Should have two values
    }
    assert parser.validate_criteria(criteria) is False

def test_format_criteria_valid(parser):
    """Test formatting of valid criteria."""
    criteria = {
        "field": "Edad",
        "operation": "greater_than",
        "value": 40
    }
    formatted = parser._format_criteria(criteria)
    assert formatted == criteria

def test_format_criteria_invalid(parser):
    """Test formatting of invalid criteria."""
    criteria = {
        "invalid": "structure"
    }
    with pytest.raises(ValueError):
        parser._format_criteria(criteria)

def test_process_with_llm_invalid_response(parser, monkeypatch):
    """Test handling of invalid LLM response."""
    def mock_llm_response(_):
        return {"invalid": "structure"}
    
    monkeypatch.setattr(parser, '_get_llm_response', mock_llm_response)
    
    with pytest.raises(ValueError):
        parser.process_with_llm("any query")

def test_error_handling_in_validation(parser):
    """Test error handling during validation."""
    # Test with None
    assert parser.validate_criteria(None) is False
    
    # Test with invalid type
    assert parser.validate_criteria("not a dict") is False
    
    # Test with empty dict
    assert parser.validate_criteria({}) is False

if __name__ == '__main__':
    pytest.main([__file__])
