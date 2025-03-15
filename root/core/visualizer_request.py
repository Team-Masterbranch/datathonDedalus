# core/visualizer_request.py
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from utils.logger import logger
from utils.logger import setup_logger
logger = setup_logger(__name__)

class ChartType(Enum):
    """Supported chart types."""
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    HISTOGRAM = "histogram"
    SCATTER = "scatter"
    BOX = "box"

@dataclass
class VisualizerRequest:
    """
    Container for visualization request data.
    Handles parsing of LLM output into structured format.
    """
    chart_type: ChartType
    title: str
    x_column: Optional[str] = None
    y_column: Optional[str] = None
    category_column: Optional[str] = None  # For grouping/categorizing
    aggregation: Optional[str] = None  # e.g., "mean", "sum", "count"
    
    @classmethod
    def from_llm_output(cls, llm_output: str) -> Optional['VisualizerRequest']:
        """
        Create VisualizerRequest from LLM output string.
        
        Example LLM outputs:
        "Create a bar chart showing average age by gender"
        "Make a pie chart of disease distribution"
        "Show age distribution using histogram"
        
        Args:
            llm_output: String from LLM suggesting visualization
            
        Returns:
            VisualizerRequest object or None if parsing fails
        """
        try:
            # Basic parsing logic - can be enhanced based on actual LLM output format
            llm_output = llm_output.lower()
            
            # Determine chart type
            chart_type = None
            for type_enum in ChartType:
                if type_enum.value in llm_output:
                    chart_type = type_enum
                    break
            
            if not chart_type:
                logger.error(f"Could not determine chart type from: {llm_output}")
                return None
                
            # Extract title - basic implementation
            title = llm_output.capitalize()
            
            # Extract columns and aggregation based on common patterns
            x_column = None
            y_column = None
            category_column = None
            aggregation = None
            
            # Look for common patterns
            if "by" in llm_output:
                category_column = llm_output.split("by")[-1].strip()
            
            if "average" in llm_output or "mean" in llm_output:
                aggregation = "mean"
            elif "total" in llm_output or "sum" in llm_output:
                aggregation = "sum"
            elif "count" in llm_output:
                aggregation = "count"
                
            # Extract column names based on known columns
            # This would need to be enhanced based on your actual data columns
            if "age" in llm_output:
                if not x_column:
                    x_column = "Edad"
                else:
                    y_column = "Edad"
            if "gender" in llm_output:
                category_column = "Genero"
            if "disease" in llm_output or "condition" in llm_output:
                if not x_column:
                    x_column = "Descripcion"
                else:
                    y_column = "Descripcion"
            
            return cls(
                chart_type=chart_type,
                title=title,
                x_column=x_column,
                y_column=y_column,
                category_column=category_column,
                aggregation=aggregation
            )
            
        except Exception as e:
            logger.error(f"Error parsing LLM output: {e}")
            return None
    
    def validate(self, available_columns: List[str]) -> bool:
        """
        Validate request against available columns.
        
        Args:
            available_columns: List of column names in the dataset
            
        Returns:
            bool: True if request is valid
        """
        try:
            # Check if specified columns exist
            if self.x_column and self.x_column not in available_columns:
                logger.error(f"Column not found: {self.x_column}")
                return False
                
            if self.y_column and self.y_column not in available_columns:
                logger.error(f"Column not found: {self.y_column}")
                return False
                
            if self.category_column and self.category_column not in available_columns:
                logger.error(f"Column not found: {self.category_column}")
                return False
                
            # Validate required columns for each chart type
            if self.chart_type == ChartType.SCATTER and not (self.x_column and self.y_column):
                logger.error("Scatter plot requires both x and y columns")
                return False
                
            if self.chart_type == ChartType.PIE and not self.x_column:
                logger.error("Pie chart requires a category column")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error validating request: {e}")
            return False
    
    def __str__(self) -> str:
        """String representation of the request."""
        parts = [f"Chart type: {self.chart_type.value}"]
        if self.x_column:
            parts.append(f"X column: {self.x_column}")
        if self.y_column:
            parts.append(f"Y column: {self.y_column}")
        if self.category_column:
            parts.append(f"Category: {self.category_column}")
        if self.aggregation:
            parts.append(f"Aggregation: {self.aggregation}")
        return " | ".join(parts)
