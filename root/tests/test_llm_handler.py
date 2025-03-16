# tests/test_llm_handler.py

import sys
import os
from pathlib import Path

# Add root directory to Python path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from core.llm_handler import LLMHandler
from core.intention import Intention
from core.data_manager import DataManager
from utils.config import DATA_DIR
import json

def print_response(title: str, response: str):
    """Helper function to print formatted response"""
    print("\n" + "="*80)
    print(f"{title}:")
    print("-"*80)
    try:
        # Try to parse and pretty print JSON
        parsed = json.loads(response)
        print("JSON conversion successful, actual response below:")
        print("-"*80)
        print(json.dumps(parsed, indent=2))
        return parsed
    except:
        print("JSON conversion failed, actual response below:")
        print("-"*80)
        print(response)
        return None

def test_execute_intention(intention_dict: dict, data_manager: DataManager):
    """Test creating and executing an intention from LLM response"""
    print("\n" + "="*80)
    print("Testing Intention Execution:")
    print("-"*80)
    
    try:
        # Create intention from LLM response
        intention = Intention.from_llm_response(intention_dict)
        print("Intention created successfully")
        
        # Validate intention
        if intention.validate(data_manager):
            print("Intention validation successful")
            
            # Execute intention
            result = intention.execute(data_manager)
            print("\nExecution result:")
            print("-"*80)
            if result is not None:
                if hasattr(result, 'shape'):  # If result is a DataFrame
                    print(f"Result shape: {result.shape}")
                    print("\nFirst few rows:")
                    print(result.head())
                else:
                    print(result)
            else:
                print("No result returned")
        else:
            print("Intention validation failed:")
            print("\n".join(intention.validation_errors))
            
    except Exception as e:
        print(f"Error executing intention: {str(e)}")

def main():
    # Initialize LLM handler and DataManager
    llm = LLMHandler()
    data_manager = DataManager(DATA_DIR)
    
    # Test cases
    test_cases = [
        {
            "title": "Cohort Filter Test",
            "request": "Dame pacientes mayores que 65"
        }#,
        # Add more test cases here when needed
    ]

    # Run tests
    for test_case in test_cases:
        try:
            # Get LLM response
            response = llm.single_input_request(test_case["request"])
            
            # Parse and print response
            parsed_response = print_response(test_case["title"], response)
            
            # If parsing successful, test intention execution
            if parsed_response:
                test_execute_intention(parsed_response, data_manager)
                
        except Exception as e:
            print(f"\nError in {test_case['title']}: {str(e)}")

if __name__ == "__main__":
    main()
