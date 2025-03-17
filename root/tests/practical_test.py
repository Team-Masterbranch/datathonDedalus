import os
import sys
import json
import pandas as pd

# Add the root directory to the path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from core.intention import Intention
from core.query import Query
from core.data_manager import DataManager

def run_test():
    print("Starting practical test...")
    
    # Setup - our fixed LLM response
    llm_response = '''{
            "intention_type": "COHORT_FILTER",
            "description": "Filtrar mujeres mayores de 60 años",
            "query": {
                "operation": "and",
                "criteria": [
                    {
                        "field": "pacientes.Genero",
                        "operation": "equals",
                        "value": "Femenino"
                    },
                    {
                        "field": "pacientes.Edad",
                        "operation": "greater_than",
                        "value": 60
                    }
                ]
            },
            "filter_target": "FULL_DATASET"
        }'''

    try:
        
        # Initialize DataManager with real data
        data_path = os.path.join(root_dir, 'data')
        data_manager = DataManager(data_path)
        
        # First test: Create and verify Query object
        print("\nTesting Query creation...")
        intention_dict = json.loads(llm_response)
        query_dict = intention_dict['query']
        
        print("Query dict structure:")
        print(json.dumps(query_dict, indent=2))
        
        query = Query.from_llm_response(llm_response)
        print("\nQuery created successfully!")
        print(f"Query complex: {query.is_complex}")
        print(f"Query dictionary: {query.query_dict}")
        print(f"Human readable query: {query.to_human_readable()}")
        
        # Test query structure
        print("\nTesting query structure:")
        print(f"Is complex query: {query.is_complex}")
        print(f"Operation: {query.get_operation()}")
        
        # Test first simple query
        print("\nTesting first query (Gender):")
        query1 = query.get_query1()
        print(f"Is simple query: {not query1.is_complex}")
        print(f"Field: {query1.get_field()}")
        print(f"Operation: {query1.get_operation()}")
        print(f"Value: {query1.get_value()}")
        
        # Test second simple query
        print("\nTesting second query (Age):")
        query2 = query.get_query1()
        print(f"Is simple query: {not query1.is_complex}")
        print(f"Field: {query2.get_field()}")
        print(f"Operation: {query2.get_operation()}")
        print(f"Value: {query2.get_value()}")
        
        # Test human readable output
        print("\nTesting human readable output:")
        print(query.to_human_readable())

        # Test query application on real data
        print("\nTesting query application on full dataset...")
        
        # Show initial dataset info
        initial_cohort = data_manager.get_current_cohort()
        print("\nInitial dataset shape:", initial_cohort.shape)
        print("\nFirst few rows of initial dataset:")
        print(initial_cohort.head())
        
        # Apply query
        print("\nApplying query filter...")
        data_manager.apply_query_on_current_cohort(query)
        filtered_df = data_manager.get_current_cohort()
        
        if filtered_df is not None:
            print("\nFilter applied successfully!")
            print("Filtered dataset shape:", filtered_df.shape)
            print("\nFirst few rows of filtered dataset:")
            print(filtered_df.head())
            
            # Print some statistics
            print("\nFilter statistics:")
            print(f"Initial number of records: {len(initial_cohort)}")
            print(f"Records after filtering: {len(filtered_df)}")
            print(f"Percentage retained: {(len(filtered_df) / len(initial_cohort)) * 100:.2f}%")
        else:
            print("Query application failed!")

        # If Query creation successful, proceed with Intention
        print("\nCreating intention from LLM response...")
        intention = Intention.from_llm_response(llm_response)
        print(f"Intention created: {intention}")

        # Test intention attributes
        print("\nTesting intention attributes:")
        print(f"Type: {intention.intention_type}")
        print(f"Description: {intention.description}")
        print(f"Target: {intention.filter_target}")
        
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"\nError during test: {str(e)}")
        raise

if __name__ == "__main__":
    run_test()
