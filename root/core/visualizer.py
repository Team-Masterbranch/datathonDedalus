# core/visualizer.py
# core/visualizer.py
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
from datetime import datetime
from utils.logger import logger
from utils.logger import setup_logger
from core.visualizer_request import VisualizerRequest, ChartType
from utils.config import (
    CLI_CHART_WIDTH,
    CLI_CHART_HEIGHT,
    IMG_DPI,
    IMG_FORMAT
)

logger = setup_logger(__name__)

class Visualizer:
    """
    Creates visual representations of cohort data based on structured requests.
    Supports both CLI and GUI interactions with different output handling.
    """
    
    def __init__(self, output_dir: str = 'data/img'):
        """
        Initialize Visualizer.
        
        Args:
            output_dir: Directory for saving images when in CLI mode
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Set default style - using seaborn's default style
        sns.set_style("whitegrid")  # Changed from plt.style.use('seaborn')
        sns.set_palette("husl")

    def clear_output_directory(self) -> None:
        """
        Clear all images from the output directory.
        """
        try:
            if not os.path.exists(self.output_dir):
                logger.info(f"Output directory does not exist: {self.output_dir}")
                return

            file_count = 0
            for filename in os.listdir(self.output_dir):
                file_path = os.path.join(self.output_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    file_count += 1

            logger.info(f"Cleared {file_count} files from output directory: {self.output_dir}")

        except Exception as e:
            logger.error(f"Error clearing output directory: {e}")


    def create_visualizations(self, 
                            data: pd.DataFrame, 
                            requests: List[VisualizerRequest],
                            gui_mode: bool = False,
                            figure_size: Optional[Tuple[int, int]] = None) -> List[Any]:
        """
        Create multiple visualizations based on requests.
        
        Args:
            data: DataFrame containing cohort data
            requests: List of VisualizerRequest objects
            gui_mode: If True, returns figure objects instead of saving files
            figure_size: Optional tuple of (width, height) for GUI mode
            
        Returns:
            List of either:
            - File paths (CLI mode)
            - Figure objects (GUI mode)
        """
        results = []
        
        try:
            for request in requests:
                if gui_mode:
                    fig = self._create_visualization(
                        data, 
                        request, 
                        figure_size=figure_size,
                        return_figure=True
                    )
                    results.append(fig)
                else:
                    filepath = self._create_visualization(
                        data, 
                        request, 
                        figure_size=(CLI_CHART_WIDTH, CLI_CHART_HEIGHT),
                        return_figure=False
                    )
                    results.append(filepath)
                    
            return results
            
        except Exception as e:
            logger.error(f"Error creating visualizations: {e}")
            return results

    # Outdated
    def _create_visualization(self,
                            data: pd.DataFrame,
                            request: VisualizerRequest,
                            figure_size: Optional[Tuple[int, int]] = None,
                            return_figure: bool = False) -> Any:
        """
        Create single visualization based on request.
        
        Args:
            data: DataFrame containing cohort data
            request: VisualizerRequest object
            figure_size: Optional tuple of (width, height)
            return_figure: If True, returns figure object instead of saving
            
        Returns:
            Either:
            - File path (if return_figure=False)
            - Figure object (if return_figure=True)
        """
        try:
            # Create figure with specified size
            fig = plt.figure(figsize=figure_size)
            
            if request.chart_type == ChartType.BAR:
                self._create_bar_chart(data, request)
            elif request.chart_type == ChartType.PIE:
                self._create_pie_chart(data, request)
            elif request.chart_type == ChartType.LINE:
                self._create_line_chart(data, request)
            elif request.chart_type == ChartType.HISTOGRAM:
                self._create_histogram(data, request)
            elif request.chart_type == ChartType.SCATTER:
                self._create_scatter_plot(data, request)
            elif request.chart_type == ChartType.BOX:
                self._create_box_plot(data, request)
            
            plt.title(request.title)
            plt.tight_layout()
            
            if return_figure:
                return fig
            else:
                return self._save_plot(request.title)
                
        except Exception as e:
            logger.error(f"Error creating visualization: {e}")
            if return_figure:
                plt.close(fig)
                return None
            return None

    def _create_bar_chart(self, data: pd.DataFrame, request: VisualizerRequest):
        """Create bar chart."""
        if request.aggregation:
            plot_data = data.groupby(request.category_column)[request.x_column].agg(request.aggregation)
            sns.barplot(x=plot_data.index, y=plot_data.values)
        else:
            sns.barplot(data=data, x=request.x_column, y=request.y_column, hue=request.category_column)

    def _create_pie_chart(self, data: pd.DataFrame, request: VisualizerRequest):
        """Create pie chart."""
        counts = data[request.x_column].value_counts()
        plt.pie(counts.values, labels=counts.index, autopct='%1.1f%%')

    def _create_line_chart(self, data: pd.DataFrame, request: VisualizerRequest):
        """Create line chart."""
        if request.category_column:
            for category in data[request.category_column].unique():
                category_data = data[data[request.category_column] == category]
                plt.plot(category_data[request.x_column], 
                        category_data[request.y_column], 
                        label=str(category))
            plt.legend()
        else:
            plt.plot(data[request.x_column], data[request.y_column])

    def _create_histogram(self, data: pd.DataFrame, request: VisualizerRequest):
        """Create histogram."""
        sns.histplot(data=data, x=request.x_column, hue=request.category_column)

    def _create_scatter_plot(self, data: pd.DataFrame, request: VisualizerRequest):
        """Create scatter plot."""
        sns.scatterplot(data=data, x=request.x_column, y=request.y_column, 
                       hue=request.category_column)

    def _create_box_plot(self, data: pd.DataFrame, request: VisualizerRequest):
        """Create box plot."""
        sns.boxplot(data=data, x=request.category_column, y=request.x_column, 
                   hue=request.y_column)

    def _save_plot(self, title: str) -> str:
        """Save the current plot to a file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{title.lower().replace(' ', '_')}_{timestamp}.{IMG_FORMAT}"
        filepath = os.path.join(self.output_dir, filename)
        
        plt.savefig(filepath, dpi=IMG_DPI, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved plot to {filepath}")
        return filepath

    def create_visualization_old(self,
                        data: pd.DataFrame,
                        request: VisualizerRequest,
                        gui_mode: bool = False,
                        figure_size: Optional[Tuple[int, int]] = None) -> Any:
        """
        Create single visualization based on request.
        
        Args:
            data: DataFrame containing cohort data
            request: VisualizerRequest object
            gui_mode: If True, returns figure object instead of saving
            figure_size: Optional tuple of (width, height)
            
        Returns:
            Either:
            - File path (if gui_mode=False)
            - Figure object (if gui_mode=True)
        """
        try:
            # Create figure with specified size
            fig = plt.figure(figsize=figure_size)
            
            if request.chart_type == ChartType.BAR:
                self._create_bar_chart(data, request)
            elif request.chart_type == ChartType.PIE:
                self._create_pie_chart(data, request)
            elif request.chart_type == ChartType.LINE:
                self._create_line_chart(data, request)
            elif request.chart_type == ChartType.HISTOGRAM:
                self._create_histogram(data, request)
            elif request.chart_type == ChartType.SCATTER:
                self._create_scatter_plot(data, request)
            elif request.chart_type == ChartType.BOX:
                self._create_box_plot(data, request)
            
            plt.title(request.title)
            plt.tight_layout()
            
            if gui_mode:
                return fig
            else:
                return self._save_plot(request.title)
                
        except Exception as e:
            logger.error(f"Error creating visualization: {e}")
            if gui_mode:
                plt.close(fig)
                return None
            return None

    def create_visualization(self,
                            data: pd.DataFrame,
                            request: VisualizerRequest,
                            output_path: Path) -> bool:
        """
        Create and save a single visualization.
        
        Args:
            data: DataFrame containing cohort data
            request: VisualizerRequest object
            output_path: Path where to save the visualization
            
        Returns:
            bool: True if visualization was created and saved successfully
        """
        try:
            # Calculate figure size (width: 1000px, height: automatic based on golden ratio)
            width_inches = 1000 / 100  # Convert pixels to inches (assuming 100 DPI)
            height_inches = width_inches / 1.618  # Golden ratio for aesthetically pleasing dimensions
            
            # Create figure with specified size
            fig = plt.figure(figsize=(width_inches, height_inches), dpi=100)
            
            # Add subplot with a specific background color
            ax = fig.add_subplot(111, facecolor='none')
            
            # Create the visualization based on chart type
            if request.chart_type == ChartType.BAR:
                self._create_bar_chart(data, request)
            elif request.chart_type == ChartType.PIE:
                self._create_pie_chart(data, request)
            elif request.chart_type == ChartType.LINE:
                self._create_line_chart(data, request)
            elif request.chart_type == ChartType.HISTOGRAM:
                self._create_histogram(data, request)
            elif request.chart_type == ChartType.SCATTER:
                self._create_scatter_plot(data, request)
            elif request.chart_type == ChartType.BOX:
                self._create_box_plot(data, request)
            else:
                logger.error(f"Unsupported chart type: {request.chart_type}")
                return False
            
            # Customize the plot
            plt.title(request.title, pad=20)
            plt.tight_layout()
            
            # Save the plot with transparency
            output_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(
                output_path,
                format='png',
                dpi=100,
                bbox_inches='tight',
                facecolor='none',
                edgecolor='none',
                transparent=True
            )
            
            # Close the figure to free memory
            plt.close(fig)
            
            logger.info(f"Saved visualization to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating visualization: {e}")
            plt.close()  # Ensure figure is closed even if error occurs
            return False



    def create_visualizations_list(self,
                                data: pd.DataFrame,
                                requests: List[VisualizerRequest],
                                gui_mode: bool = False,
                                figure_size: Optional[Tuple[int, int]] = None) -> List[Any]:
        """
        Create multiple visualizations based on requests.
        
        Args:
            data: DataFrame containing cohort data
            requests: List of VisualizerRequest objects
            gui_mode: If True, returns figure objects instead of saving files
            figure_size: Optional tuple of (width, height)
            
        Returns:
            List of either:
            - File paths (if gui_mode=False)
            - Figure objects (if gui_mode=True)
        """
        results = []
        
        try:
            for request in requests:
                result = self.create_visualization(
                    data=data,
                    request=request,
                    gui_mode=gui_mode,
                    figure_size=figure_size
                )
                if result is not None:
                    results.append(result)
                    logger.debug(f"Created visualization for request: {request.title}")
                else:
                    logger.warning(f"Failed to create visualization for request: {request.title}")
                    
            return results
            
        except Exception as e:
            logger.error(f"Error creating visualizations list: {e}")
            return results
