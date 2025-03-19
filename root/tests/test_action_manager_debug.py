import os
import sys
import json
from pathlib import Path
import logging
from typing import Dict, Any

# Add root directory to Python path
root_dir = str(Path(__file__).parent.parent)
sys.path.append(root_dir)

from core.action_manager import ActionManager
from core.session_manager import SessionManager
from core.llm_handler import LLMHandler
from core.data_manager import DataManager
from core.visualizer import Visualizer
from utils.config import DATA_DIR

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def load_llm_response(filename: str) -> str:
    """Load LLM response from test file"""
    test_dir = Path(__file__).parent
    file_path = test_dir / "test_data" / filename
    
    logger.info(f"Loading LLM response from {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            logger.debug(f"Loaded content: {content}")
            return content
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Error loading file: {e}")
        raise

def setup_components() -> Dict[str, Any]:
    """Initialize all required components with real data"""
    logger.info("Setting up components...")
    
    # Setup paths
    output_dir = Path(__file__).parent / "test_output"
    output_dir.mkdir(exist_ok=True)
    logger.info(f"Output directory: {output_dir}")

    # Initialize components with real configurations
    try:
        data_manager = DataManager(DATA_DIR)
        logger.info("DataManager initialized successfully")
        
        session_manager = SessionManager()
        # Set the interaction path directly for testing
        session_manager._current_interaction_path = str(output_dir)
        logger.info(f"SessionManager initialized with interaction path: {session_manager._current_interaction_path}")
        
        visualizer = Visualizer(output_dir=str(output_dir))
        logger.info("Visualizer initialized successfully")
        
        llm_handler = LLMHandler()
        logger.info("LLMHandler initialized successfully")
        
        return {
            "llm_handler": llm_handler,
            "session_manager": session_manager,
            "data_manager": data_manager,
            "visualizer": visualizer
        }
    except Exception as e:
        logger.error(f"Error during component setup: {e}")
        raise

def test_process_problematic_llm_response():
    """
    Test processing a problematic LLM response from file with full debugging
    """
    logger.info("Starting test_process_problematic_llm_response")
    
    try:
        # Setup components
        components = setup_components()
        
        # Initialize ActionManager with real components
        action_manager = ActionManager(
            llm_handler=components["llm_handler"],
            session_manager=components["session_manager"],
            data_manager=components["data_manager"],
            visualizer=components["visualizer"]
        )
        logger.info("ActionManager initialized successfully")
        
        # Load test response from file
        llm_response = load_llm_response("problematic_response.txt")
        
        # Process the response
        logger.info("Attempting to decode LLM response")
        success = action_manager.decode_llm_response(llm_response)
        
        if not success:
            logger.error("Failed to decode LLM response")
            return
            
        # Log number of actions
        action_count = action_manager.get_pending_actions_count()
        logger.info(f"Number of actions to execute: {action_count}")
        
        # Log each action before execution
        for i, action in enumerate(action_manager.actions, 1):
            logger.info(f"\nAction {i}/{action_count}:")
            logger.info(f"Type: {action.type.value}")
            logger.info(f"Parameters: {json.dumps(action.parameters, indent=2)}")
            
        # Execute all actions
        try:
            logger.info("Executing actions...")
            action_manager.execute_actions()
            logger.info("Actions executed successfully")
        except Exception as e:
            logger.error(f"Error executing actions: {e}")
            import traceback
            logger.error(traceback.format_exc())
                
        logger.info("Test completed!")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise

if __name__ == "__main__":
    # Create test_data directory if it doesn't exist
    test_data_dir = Path(__file__).parent / "test_data"
    test_data_dir.mkdir(exist_ok=True)
    
    # Create test_output directory if it doesn't exist
    test_output_dir = Path(__file__).parent / "test_output"
    test_output_dir.mkdir(exist_ok=True)
    
    # Example of how to create a problematic_response.txt if it doesn't exist
    if not (test_data_dir / "problematic_response.txt").exists():
        example_response = '''[
  {
    "type": "print_message",
    "parameters": {
      "message": "Analyzing patient data..."
    }
  },
  {
    "type": "create_visualization",
    "parameters": {
      "request": {
        "chart_type": "pie",
        "title": "Patient Distribution",
        "labels": ["Group A", "Group B"],
        "values": [30, 70]
      }
    }
  }
]'''
        with open(test_data_dir / "problematic_response.txt", 'w', encoding='utf-8') as f:
            f.write(example_response)
    
    # Run the test
    test_process_problematic_llm_response()
