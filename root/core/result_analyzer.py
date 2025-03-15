# core/result_analyzer.py
from typing import List, Optional
from core.data_manager import DataManager
from core.visualizer_request import VisualizerRequest, ChartType
from utils.logger import logger
from utils.logger import setup_logger
import os
from utils.config import DATA_DIR

logger = setup_logger(__name__)

class ResultAnalyzer:
    """
    Analyzes query results and suggests visualizations.
    Will be enhanced with LLM capabilities in the future.
    """
    
    def __init__(self):
        logger.info("Initializing ResultAnalyzer")

    def analyze_cohort(self, data_manager: DataManager) -> tuple[str, List[VisualizerRequest]]:
        """
        Analyze current cohort and suggest visualizations.
        Currently implements stub functionality.
        
        Args:
            data_manager: DataManager instance with current cohort
            
        Returns:
            tuple: (cohort_file_path, list of visualization requests)
        """
        try:
            # 1. Save cohort to CSV
            cohort_file_path = self._save_cohort(data_manager)
            
            # 2. Generate visualization requests
            viz_requests = self._generate_visualization_requests(data_manager)
            
            return cohort_file_path, viz_requests
            
        except Exception as e:
            logger.error(f"Error analyzing cohort: {e}")
            return None, []

    def _save_cohort(self, data_manager: DataManager) -> str:
        """Save current cohort to CSV file."""
        try:
            # Ensure data directory exists
            os.makedirs(DATA_DIR, exist_ok=True)
            
            # Create file path
            file_path = os.path.join(DATA_DIR, 'cohort.csv')
            
            # Save cohort
            cohort = data_manager.get_current_cohort()
            if cohort is not None:
                cohort.to_csv(file_path, index=False)
                logger.info(f"Saved cohort to {file_path}")
                return file_path
            else:
                logger.error("No current cohort available to save")
                return None
                
        except Exception as e:
            logger.error(f"Error saving cohort: {e}")
            return None

    def _generate_visualization_requests(self, data_manager: DataManager) -> List[VisualizerRequest]:
        """
        Generate visualization requests based on cohort schema.
        Creates one example of each chart type if possible.
        """
        try:
            requests = []
            schema = data_manager.get_current_schema()
            
            # Find numeric and categorical columns
            numeric_cols = [
                col for col, info in schema.items()
                if 'float' in info['dtype'] or 'int' in info['dtype']
            ]
            
            categorical_cols = [
                col for col, info in schema.items()
                if 'object' in info['dtype'] and info['unique_values'] < 10
            ]
            
            if not numeric_cols or not categorical_cols:
                logger.warning("Not enough variety in column types for all charts")
                return []

            # 1. Bar Chart
            if numeric_cols and categorical_cols:
                requests.append(VisualizerRequest(
                    chart_type=ChartType.BAR,
                    title=f"Distribution of {numeric_cols[0]} by {categorical_cols[0]}",
                    x_column=categorical_cols[0],
                    y_column=numeric_cols[0]
                ))

            # 2. Pie Chart (using first categorical column)
            if categorical_cols:
                requests.append(VisualizerRequest(
                    chart_type=ChartType.PIE,
                    title=f"Distribution of {categorical_cols[0]}",
                    x_column=categorical_cols[0]
                ))

            # 3. Scatter Plot (using first two numeric columns)
            if len(numeric_cols) >= 2:
                requests.append(VisualizerRequest(
                    chart_type=ChartType.SCATTER,
                    title=f"{numeric_cols[0]} vs {numeric_cols[1]}",
                    x_column=numeric_cols[0],
                    y_column=numeric_cols[1],
                    category_column=categorical_cols[0] if categorical_cols else None
                ))

            # 4. Box Plot
            if numeric_cols and categorical_cols:
                requests.append(VisualizerRequest(
                    chart_type=ChartType.BOX,
                    title=f"Distribution of {numeric_cols[0]} by {categorical_cols[0]}",
                    x_column=numeric_cols[0],
                    category_column=categorical_cols[0]
                ))

            # 5. Histogram (using first numeric column)
            if numeric_cols:
                requests.append(VisualizerRequest(
                    chart_type=ChartType.HISTOGRAM,
                    title=f"Distribution of {numeric_cols[0]}",
                    x_column=numeric_cols[0],
                    category_column=categorical_cols[0] if categorical_cols else None
                ))

            # 6. Line Chart (if we have at least 2 numeric columns)
            if len(numeric_cols) >= 2:
                requests.append(VisualizerRequest(
                    chart_type=ChartType.LINE,
                    title=f"Trend of {numeric_cols[1]} vs {numeric_cols[0]}",
                    x_column=numeric_cols[0],
                    y_column=numeric_cols[1]
                ))

            return requests
            
        except Exception as e:
            logger.error(f"Error generating visualization requests: {e}")
            return []
