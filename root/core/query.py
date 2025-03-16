from typing import Dict, Any, Optional, List
from datetime import datetime
from utils.logger import logger
from utils.logger import setup_logger
logger = setup_logger(__name__)

class Query:
    """
    A wrapper class for query dictionaries that provides additional functionality
    for validation, human readable output and LLM interaction.
    """
    # Supported operations and their human-readable translations
    OPERATIONS = {
        "equals": "es igual a",
        "not_equals": "no es igual a",
        "greater_than": "es mayor que",
        "less_than": "es menor que",
        "and": "Y",
        "or": "O"
    }
    
    # Valid operations for different data types
    TYPE_OPERATIONS = {
        'int64': ['equals', 'not_equals', 'greater_than', 'less_than'],
        'float64': ['equals', 'not_equals', 'greater_than', 'less_than'],
        'object': ['equals', 'not_equals'],  # string type in pandas
        'datetime64[ns]': ['equals', 'not_equals', 'greater_than', 'less_than']
    }

    def __init__(self, query_dict: Dict[str, Any]):
        """Initialize Query with a dictionary representation."""
        self._query = query_dict
        self.timestamp = datetime.now()
        logger.info(f"Created query: {self._query}")

    def to_human_readable(self) -> str:
        """Convert query to human readable format."""
        try:
            return self._process_node_human_readable(self._query)
        except Exception as e:
            logger.error(f"Error converting query to human readable: {e}")
            return str(self._query)

    def _process_node_human_readable(self, node: Dict[str, Any]) -> str:
        """Recursively process query nodes for human readable output."""
        if "operation" in node and "criteria" in node:
            # Process logical operation (AND/OR)
            op = self.OPERATIONS.get(node["operation"], node["operation"]).upper()
            criteria = [self._process_node_human_readable(c) for c in node["criteria"]]
            if len(criteria) == 1:
                return criteria[0]
            return f"({f' {op} '.join(criteria)})"
        
        elif "field" in node and "operation" in node and "value" in node:
            # Process comparison operation
            field = node["field"]
            op = self.OPERATIONS.get(node["operation"], node["operation"])
            value = str(node["value"])
            return f"{field} {op} {value}"
        
        else:
            logger.warning(f"Unknown node structure: {node}")
            return str(node)

    def to_llm_format(self) -> Dict[str, Any]:
        """Format query for LLM consumption."""
        return {
            "query_structure": self._query,
            "human_readable": self.to_human_readable(),
            "timestamp": self.timestamp.isoformat(),
            "metadata": {
                "operations_used": self._get_operations_used(),
                "fields_referenced": self._get_fields_referenced()
            }
        }

    def _get_operations_used(self) -> List[str]:
        """Get list of all operations used in query."""
        ops = set()
        def collect_ops(node):
            if "operation" in node:
                ops.add(node["operation"])
            if "criteria" in node:
                for c in node["criteria"]:
                    collect_ops(c)
        collect_ops(self._query)
        return list(ops)

    def _get_fields_referenced(self) -> List[str]:
        """Get list of all fields referenced in query."""
        fields = set()
        def collect_fields(node):
            if "field" in node:
                fields.add(node["field"])
            if "criteria" in node:
                for c in node["criteria"]:
                    collect_fields(c)
        collect_fields(self._query)
        return list(fields)

    def validate(self, schema: Dict[str, Dict]) -> bool:
        """Validate query against provided schema."""
        try:
            return self._validate_node(self._query, schema)  # Use self._query instead of self
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False

    def _validate_node(self, node: Dict[str, Any], schema: Dict[str, Dict]) -> bool:
        """Recursively validate query nodes against schema."""
        # Validate logical operation node
        if "operation" in node and "criteria" in node:
            if node["operation"] not in ["and", "or"]:
                logger.error(f"Invalid logical operation: {node['operation']}")
                return False
            if not isinstance(node["criteria"], list) or not node["criteria"]:
                logger.error(f"Invalid criteria for logical operation: {node['criteria']}")
                return False
            return all(self._validate_node(c, schema) for c in node["criteria"])

        # Validate comparison operation node
        elif "field" in node and "operation" in node and "value" in node:
            # Check if field exists in schema
            if node["field"] not in schema:
                logger.error(f"Field not found in schema: {node['field']}")
                return False

            field_type = schema[node["field"]]["dtype"]
            
            # Check if operation is valid for field type
            if field_type not in self.TYPE_OPERATIONS:
                logger.error(f"Unsupported field type: {field_type}")
                return False
            
            if node["operation"] not in self.TYPE_OPERATIONS[field_type]:
                logger.error(
                    f"Operation {node['operation']} not supported for type {field_type}"
                )
                return False

            return True

        else:
            logger.error(f"Invalid node structure: {node}")
            return False
    
    
    def __str__(self) -> str:
        """Returns human readable representation."""
        return self.to_human_readable()

    def __eq__(self, other: 'Query') -> bool:
        """Compare queries based on their dictionary representation."""
        if not isinstance(other, Query):
            return False
        return self._query == other._query

    @property
    def raw(self) -> Dict[str, Any]:
        """Access the underlying query dictionary."""
        return self._query