from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)

class ActionType(Enum):
    PRINT_MESSAGE = "print_message"
    NAME_COHORT = "name_cohort"
    SAVE_COHORT = "save_cohort"
    CREATE_VISUALIZATION = "create_visualization"
    SHOW_STATISTICS = "show_statistics"
    SUGGESTION = "suggestion"

@dataclass
class Action:
    type: ActionType
    parameters: Dict[str, Any]

class ActionManager:
    def __init__(self):
        self.actions: List[Action] = []
        logger.debug("ActionManager initialized")
        
    def decode_llm_response(self, json_str: str) -> bool:
        """
        Decode LLM JSON response and create corresponding actions
        """
        logger.debug(f"Starting to decode LLM response: {json_str[:100]}...")
        try:
            actions_data = json.loads(json_str)
            logger.debug(f"JSON successfully parsed, got {type(actions_data)}")
            
            if not isinstance(actions_data, list):
                logger.error(f"LLM response must be a list, got {type(actions_data)}")
                return False
                
            logger.debug(f"Found {len(actions_data)} actions to process")
            
            # Clear existing actions before adding new ones
            self.actions.clear()
            logger.debug("Cleared existing actions")
            
            # Validate and create each action
            for i, action_data in enumerate(actions_data):
                logger.debug(f"Processing action {i+1}/{len(actions_data)}: {action_data.get('type', 'unknown')}")
                if not self._validate_and_add_action(action_data):
                    logger.error(f"Validation failed for action {i+1}")
                    self.actions.clear()
                    return False
                    
            logger.debug(f"Successfully processed all {len(self.actions)} actions")
            return True
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            logger.debug(f"Problematic JSON string: {json_str}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during decoding: {e}")
            return False
            
    def _validate_and_add_action(self, action_data: Dict) -> bool:
        """Validate single action and add if valid"""
        try:
            logger.debug(f"Validating action data: {action_data}")
            
            # Validate basic structure
            if not isinstance(action_data, dict):
                logger.error(f"Action must be a dictionary, got {type(action_data)}")
                return False
                
            action_type = action_data.get("type")
            parameters = action_data.get("parameters", {})
            
            logger.debug(f"Action type: {action_type}, Parameters: {parameters}")
            
            if not action_type:
                logger.error("Missing action type")
                return False
                
            if not isinstance(parameters, dict):
                logger.error(f"Parameters must be a dictionary, got {type(parameters)}")
                return False
                
            # Validate specific action types
            logger.debug(f"Validating parameters for action type: {action_type}")
            if not self._validate_action_parameters(action_type, parameters):
                logger.error(f"Parameter validation failed for action type: {action_type}")
                return False
                
            # Create and add action
            try:
                action = Action(
                    type=ActionType(action_type),
                    parameters=parameters
                )
                logger.debug(f"Created action object: {action}")
                self.actions.append(action)
                return True
            except ValueError as e:
                logger.error(f"Invalid action type: {action_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error in action validation: {e}")
            return False
            
    def _validate_action_parameters(self, action_type: str, parameters: Dict) -> bool:
        """Validate parameters for specific action type"""
        logger.debug(f"Validating parameters for {action_type}: {parameters}")
        try:
            if action_type == "print_message":
                valid = isinstance(parameters.get("message"), str)
                logger.debug(f"print_message validation: {valid}")
                return valid
                
            elif action_type == "name_cohort":
                valid = isinstance(parameters.get("name"), str)
                logger.debug(f"name_cohort validation: {valid}")
                return valid
                
            elif action_type == "save_cohort":
                valid = isinstance(parameters.get("name"), str)
                logger.debug(f"save_cohort validation: {valid}")
                return valid
                
            elif action_type == "create_visualization":
                request = parameters.get("request")
                valid = isinstance(request, dict)
                logger.debug(f"create_visualization validation: {valid}")
                return valid
                
            elif action_type == "suggestion":
                valid = (isinstance(parameters.get("message"), str) and
                        isinstance(parameters.get("prompt"), str))
                logger.debug(f"suggestion validation: {valid}")
                return valid
                
            logger.error(f"Unknown action type: {action_type}")
            return False
            
        except Exception as e:
            logger.error(f"Error in parameter validation: {e}")
            return False

    def get_pending_actions_count(self) -> int:
        """Get number of pending actions"""
        logger.debug(f"Getting count of pending actions: {len(self.actions)}")
        return len(self.actions)
