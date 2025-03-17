# root/tests/test_query.py
import os
import sys
import pytest  # Add this import
from pathlib import Path

# Add parent directory to Python path
current_dir = Path(__file__).parent
root_dir = current_dir.parent
sys.path.insert(0, str(root_dir))

from core.query import Query

def test_simple_query_creation():
    """Test creating a simple query using create_simple"""
    query = Query.create_simple("pacientes.Edad", "greater_than", 40)
    
    assert query.is_complex == False
    assert query.query_dict == {
        "field": "pacientes.Edad",
        "operation": "greater_than",
        "value": 40
    }

def test_complex_query_creation():
    """Test creating a complex query using create_complex"""
    query1_dict = {"field": "pacientes.Genero", "operation": "equals", "value": "Femenino"}
    query2_dict = {"field": "pacientes.Edad", "operation": "greater_than", "value": 60}
    
    query = Query.create_complex("and", query1_dict, query2_dict)
    
    assert query.is_complex == True
    assert query.query_dict == {
        "operation": "and",
        "criteria": [
            {"field": "pacientes.Genero", "operation": "equals", "value": "Femenino"},
            {"field": "pacientes.Edad", "operation": "greater_than", "value": 60}
        ]
    }

def test_query_from_llm_response():
    """Test creating query from LLM response string"""
    llm_response = '''{
        "query": {
            "operation": "and",
            "criteria": [
                {"field": "pacientes.Genero", "operation": "equals", "value": "Femenino"},
                {"field": "pacientes.Edad", "operation": "greater_than", "value": 60}
            ]
        }
    }'''
    
    query = Query.from_llm_response(llm_response)
    
    assert query.is_complex == True
    assert len(query.query_dict["criteria"]) == 2
    assert query.query_dict["operation"] == "and"

def test_invalid_llm_response():
    """Test handling invalid JSON in LLM response"""
    invalid_response = "{ invalid json }"
    
    with pytest.raises(ValueError) as exc_info:
        Query.from_llm_response(invalid_response)
    assert "Invalid JSON in LLM response" in str(exc_info.value)

def test_human_readable_simple():
    """Test human readable output for simple query"""
    query = Query.create_simple("pacientes.Edad", "greater_than", 40)
    readable = query.to_human_readable()
    assert readable == "pacientes.Edad greater_than 40"

def test_human_readable_complex():
    """Test human readable output for complex query"""
    query1_dict = {"field": "pacientes.Genero", "operation": "equals", "value": "Femenino"}
    query2_dict = {"field": "pacientes.Edad", "operation": "greater_than", "value": 60}
    query = Query.create_complex("and", query1_dict, query2_dict)
    
    readable = query.to_human_readable()
    assert readable == "(pacientes.Genero equals Femenino AND pacientes.Edad greater_than 60)"

def test_direct_constructor():
    """Test direct constructor usage"""
    query_dict = {"field": "pacientes.Edad", "operation": "greater_than", "value": 40}
    query = Query(query_dict, is_complex=False)
    
    assert query.is_complex == False
    assert query.query_dict == query_dict

def test_empty_query_dict():
    """Test creating query with empty dictionary"""
    query = Query({}, False)
    readable = query.to_human_readable()
    assert readable == "Empty query"  # Changed expectation

def test_missing_query_in_llm_response():
    """Test handling LLM response without query field"""
    llm_response = '{"something_else": {}}'
    
    query = Query.from_llm_response(llm_response)
    assert query.query_dict == {}

if __name__ == '__main__':
    pytest.main([__file__])
