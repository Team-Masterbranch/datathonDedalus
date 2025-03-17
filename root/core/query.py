from typing import Dict, List, Any, TYPE_CHECKING
from datetime import datetime
from utils.logger import logger
from utils.logger import setup_logger
logger = setup_logger(__name__)

if TYPE_CHECKING:
    from core.data_manager import DataManager

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
        self._query_dict = query_dict
        self.timestamp = datetime.now()
        logger.info(f"Created query: {self._query_dict}")
        
    def get_query_dict(self) -> Dict[str, Any]:
        """Return the query dictionary."""
        return self._query_dict

    def get_operation(self) -> str:
        """Return the operation of the query."""
        logger.debug(f"Getting operation for query: {self._query_dict}")
        return self._query_dict.get('operation', '')

    def to_dict(self) -> Dict:
        if self._query_dict.get('operation') in ['and', 'or']:
            return {
                'operation': self._query_dict['operation'],
                'criteria': [q.to_dict() if isinstance(q, Query) else q 
                        for q in self._query_dict['criteria']]
            }
        return self._query_dict

    def to_human_readable(self) -> str:
        if self._query_dict.get('operation') in ['and', 'or']:
            sub_queries = [q.to_human_readable() if isinstance(q, Query) else str(q) 
                        for q in self._query_dict['criteria']]
            join_word = ' AND ' if self._query_dict['operation'] == 'and' else ' OR '
            return f"({join_word.join(sub_queries)})"
        
        field = self._query_dict.get('field', '')
        operation = self._query_dict.get('operation', '')
        value = self._query_dict.get('value', '')
        
        operation_map = {
            'equals': 'equals',
            'greater_than': 'is greater than',
            'less_than': 'is less than',
            'contains': 'contains'
            # Add more operations as needed
        }
        
        readable_operation = operation_map.get(operation, operation)
        return f"{field} {readable_operation} {value}"



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
            "query_structure": self._query_dict,
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
        collect_ops(self._query_dict)
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
        collect_fields(self._query_dict)
        return list(fields)

    def validate(self, schema) -> bool:
        """
        Validate the query against the data manager's schema
        """
        logger.debug(f"Entered a query.validate method")
        logger.debug(f"Query: {self._query_dict}")
        logger.debug(f"Schema: {schema}")
        try:
            query_dict = self.get_query_dict()
            
            # For compound queries (AND/OR)
            if query_dict.get('operation') in ['and', 'or']:
                # Validate each sub-query in criteria
                logger.debug(f"Validating compound query: {query_dict}")
                criterion = query_dict.get('criteria', [])
                logger.debug(f"criterion: {criterion}")
                return all(
                    criterion.validate(schema) 
                    for criterion in query_dict.get('criteria', [])
                )
                
            # For simple queries
            field = query_dict.get('field')
            operation = query_dict.get('operation')
            logger.debug(f"Validating simple query: {query_dict}")
            
            if not field or not operation:
                logger.error(f"Missing field or operation in query: {query_dict}")
                return False
            
            # Validate field exists in schema
            logger.debug(f"Schema: {schema}")
            if field not in schema:
                logger.error(f"Field {field} not found in schema")
                return False
            
            # Validate operation is valid for field type
            field_type = schema[field]['dtype']
            valid_ops = self.TYPE_OPERATIONS.get(field_type, [])
            
            if operation not in valid_ops:
                logger.error(f"Operation {operation} not valid for field type {field_type}")
                return False
            
            logger.debug(f"Exited a query.validate method (success)")
            return True
            
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
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
        return self._query_dict == other._query_dict

    @property
    def raw(self) -> Dict[str, Any]:
        """Access the underlying query dictionary."""
        return self._query_dict