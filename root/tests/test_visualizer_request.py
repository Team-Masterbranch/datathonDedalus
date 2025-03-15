# tests/test_visualizer_request.py
import pytest
from core.visualizer_request import VisualizerRequest, ChartType

class TestVisualizerRequest:
    def test_parse_bar_chart_request(self):
        llm_output = "Create a bar chart showing average age by gender"
        request = VisualizerRequest.from_llm_output(llm_output)
        
        assert request is not None
        assert request.chart_type == ChartType.BAR
        assert request.x_column == "Edad"
        assert request.category_column == "Genero"
        assert request.aggregation == "mean"

    def test_parse_pie_chart_request(self):
        llm_output = "Make a pie chart of disease distribution"
        request = VisualizerRequest.from_llm_output(llm_output)
        
        assert request is not None
        assert request.chart_type == ChartType.PIE
        assert request.x_column == "Descripcion"

    def test_validate_request(self):
        request = VisualizerRequest(
            chart_type=ChartType.BAR,
            title="Test Chart",
            x_column="Edad",
            category_column="Genero"
        )
        
        available_columns = ["Edad", "Genero", "Descripcion"]
        assert request.validate(available_columns)

    def test_validate_invalid_columns(self):
        request = VisualizerRequest(
            chart_type=ChartType.BAR,
            title="Test Chart",
            x_column="NonexistentColumn"
        )
        
        available_columns = ["Edad", "Genero", "Descripcion"]
        assert not request.validate(available_columns)

    def test_invalid_llm_output(self):
        llm_output = "This is not a valid visualization request"
        request = VisualizerRequest.from_llm_output(llm_output)
        assert request is None
