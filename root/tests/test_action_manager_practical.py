import os
import sys
import json
from pathlib import Path

# Add root directory to Python path
root_dir = str(Path(__file__).parent.parent)
sys.path.append(root_dir)

from core.action_manager import ActionManager
from core.data_manager import DataManager
from core.visualizer import Visualizer
from core.visualizer_request import VisualizerRequest, ChartType

# Setup paths
DATA_PATH = os.path.join(root_dir, "data")
OUTPUT_DIR = os.path.join(root_dir, "tests", "img")
os.makedirs(OUTPUT_DIR, exist_ok=True)


# At the start of test_action_manager_practical.py, add:
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


# Mock LLM response
mock_llm_response = '''
[
    {
        "type": "print_message",
        "parameters": {
            "message": "Analizando los datos de pacientes en la base de datos"
        }
    },
    {
        "type": "create_visualization",
        "parameters": {
            "request": {
                "chart_type": "pie",
                "title": "Distribución por Género",
                "x_column": "pacientes.Genero"
            }
        }
    },
    {
        "type": "create_visualization",
        "parameters": {
            "request": {
                "chart_type": "histogram",
                "title": "Distribución de Edad",
                "x_column": "pacientes.Edad"
            }
        }
    },
    {
        "type": "suggestion",
        "parameters": {
            "message": "¿Le gustaría ver la distribución de las condiciones médicas más comunes?",
            "prompt": "mostrar gráfico de las condiciones médicas más frecuentes"
        }
    },
    {
        "type": "name_cohort",
        "parameters": {
            "name": "pacientes_completos"
        }
    },
    {
        "type": "save_cohort",
        "parameters": {
            "name": "pacientes_completos"
        }
    }
]
'''


def main():
    # Initialize components
    print("Initializing components...")
    
    # Initialize DataManager with data path
    data_manager = DataManager(DATA_PATH)
    
    # Set custom output directory for Visualizer
    visualizer = Visualizer(output_dir=OUTPUT_DIR)
    
    # Create ActionManager instance
    action_manager = ActionManager()
    
    print("\nDecoding mock LLM response...")
    # Decode mock response
    success = action_manager.decode_llm_response(mock_llm_response)
    
    if not success:
        print("Failed to decode LLM response")
        return
        
    print(f"\nNumber of actions to execute: {action_manager.get_pending_actions_count()}")
    
    print("\nExecuting actions...")
    # Execute all actions

    try:
        for action in action_manager.actions:
            print(f"\nExecuting action: {action.type.value}")
            print("Parameters:", json.dumps(action.parameters, indent=2))
            
            if action.type.value == "create_visualization":
                # Get request parameters
                request_params = action.parameters["request"]
                
                # Convert string chart_type to ChartType enum
                chart_type_str = request_params["chart_type"]
                request_params["chart_type"] = ChartType(chart_type_str)
                
                # Create VisualizerRequest object
                viz_request = VisualizerRequest(**request_params)
                
                # Create visualization
                result = visualizer.create_visualization(
                    data=data_manager.get_current_cohort(),
                    request=viz_request,
                    gui_mode=False,
                    figure_size=(10, 6)
                )
                if result:
                    print(f"Visualization saved as: {result}")
                else:
                    print("Failed to create visualization")
            else:
                # For other actions, just print what would happen
                print(f"Action would be executed with data manager")
                
    except Exception as e:
        print(f"Error during execution: {e}")
        import traceback
        traceback.print_exc()
        
    print("\nTest completed!")

if __name__ == "__main__":
    main()
