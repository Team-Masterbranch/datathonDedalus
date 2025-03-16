# tests/practical_test_intention_executor.py
import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

import asyncio
import pandas as pd
from core.data_manager import DataManager
from core.intention_executor import IntentionExecutor
from core.query_manager import QueryManager
from core.visualizer import Visualizer
from core.llm_handler import LLMHandler
from utils.config import DATA_DIR
from core.intention import Intention

async def main():
    try:
        # Initialize components
        data_manager = DataManager(DATA_DIR)
        query_manager = QueryManager(data_manager)
        visualizer = Visualizer()
        llm_handler = LLMHandler()
        
        # Initialize intention executor
        executor = IntentionExecutor(query_manager, visualizer, data_manager)
        
        # Get LLM response as string
        user_input = "Dame mujeres mayores que 60"
        llm_response = llm_handler.single_input_request(user_input)
        
        print("\nLLM Response:")
        print(llm_response)
        
        # Create intention from LLM response string
        intention = Intention.from_llm_response(llm_response)
        
        print("\nCreated intention:")
        print(f"Type: {intention.intention_type}")
        print(f"Query: {intention.query}")
        print(f"Filter target: {intention.filter_target}")
        
        # Execute intention
        print("\nExecuting intention...")
        result = await executor.execute(intention)
        
        print("\nExecution result:")
        print(f"Success: {result['success']}")
        if result['success']:
            print(f"Type: {result['type']}")
            if 'result' in result:
                print(f"Result: {result['result']}")
        
        # Print current cohort
        current_cohort = data_manager.get_current_cohort()
        print("\nCurrent cohort (first 10 rows):")
        print(current_cohort.head(10))
        print(f"\nTotal rows in current cohort: {len(current_cohort)}")

    except Exception as e:
        print(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
