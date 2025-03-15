# tests/test_visualizer.py
import pytest
import pandas as pd
import matplotlib.pyplot as plt
from core.visualizer import Visualizer
from core.visualizer_request import VisualizerRequest, ChartType
import os
import tempfile

@pytest.fixture
def sample_data():
    return pd.DataFrame({
        'Edad': [25, 30, 35, 40, 45],
        'Genero': ['M', 'F', 'M', 'F', 'M'],
        'Descripcion': ['Diabetes', 'Hipertensión', 'Diabetes', 
                       'Asma', 'Hipertensión'],
        'Peso': [70, 65, 80, 60, 75]
    })

@pytest.fixture
def visualizer():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Visualizer(tmpdir)

class TestVisualizer:
    def test_cli_mode(self, visualizer, sample_data):
        requests = [
            VisualizerRequest(
                chart_type=ChartType.BAR,
                title="Test Bar",
                x_column="Edad",
                category_column="Genero"
            )
        ]
        
        results = visualizer.create_visualizations(sample_data, requests)
        assert len(results) == 1
        assert os.path.exists(results[0])
        assert results[0].endswith('.png')

    def test_gui_mode(self, visualizer, sample_data):
        requests = [
            VisualizerRequest(
                chart_type=ChartType.BAR,
                title="Test Bar",
                x_column="Edad",
                category_column="Genero"
            )
        ]
        
        results = visualizer.create_visualizations(
            sample_data, 
            requests, 
            gui_mode=True,
            figure_size=(6, 4)
        )
        assert len(results) == 1
        assert isinstance(results[0], plt.Figure)

    def test_multiple_charts(self, visualizer, sample_data):
        requests = [
            VisualizerRequest(
                chart_type=ChartType.BAR,
                title="Test Bar",
                x_column="Edad",
                category_column="Genero"
            ),
            VisualizerRequest(
                chart_type=ChartType.PIE,
                title="Test Pie",
                x_column="Descripcion"
            )
        ]
        
        results = visualizer.create_visualizations(sample_data, requests)
        assert len(results) == 2
        assert all(os.path.exists(f) for f in results)
