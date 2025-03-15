# tests/test_visualizer_practical.py
import pytest
import pandas as pd
import numpy as np
from core.visualizer import Visualizer
from core.visualizer_request import VisualizerRequest, ChartType

@pytest.fixture
def sample_medical_data():
    # Create realistic medical dataset
    np.random.seed(42)
    n_samples = 100
    
    data = pd.DataFrame({
        'Edad': np.random.normal(45, 15, n_samples).astype(int),  # Age distribution
        'Genero': np.random.choice(['M', 'F'], n_samples),
        'Peso': np.random.normal(70, 12, n_samples).round(1),     # Weight in kg
        'Altura': np.random.normal(170, 10, n_samples).round(1),  # Height in cm
        'Presion_Sistolica': np.random.normal(120, 15, n_samples).astype(int),
        'Descripcion': np.random.choice(
            ['Diabetes', 'Hipertensión', 'Asma', 'Artritis', 'Migraña'],
            n_samples,
            p=[0.3, 0.25, 0.2, 0.15, 0.1]
        ),
        'Nivel_Glucosa': np.random.normal(100, 25, n_samples).round(1),
        'Visitas_Anuales': np.random.poisson(3, n_samples)
    })
    
    # Add BMI calculation
    data['IMC'] = (data['Peso'] / (data['Altura']/100)**2).round(1)
    
    return data

class TestVisualizerPractical:
    """Practical tests generating various visualization examples."""

    def test_generate_example_visualizations(self, sample_medical_data):
        """Generate a set of example visualizations for visual inspection."""
        visualizer = Visualizer()
        
        requests = [
            # Age distribution by gender (Box Plot)
            VisualizerRequest(
                chart_type=ChartType.BOX,
                title="Distribución de Edad por Género",
                x_column="Genero",
                y_column="Edad",
                category_column="Genero"
            ),
            
            # Disease distribution (Pie Chart)
            VisualizerRequest(
                chart_type=ChartType.PIE,
                title="Distribución de Condiciones Médicas",
                x_column="Descripcion"
            ),
            
            # BMI vs Age (Scatter Plot)
            VisualizerRequest(
                chart_type=ChartType.SCATTER,
                title="IMC vs Edad",
                x_column="Edad",
                y_column="IMC",
                category_column="Genero"
            ),
            
            # Age distribution (Histogram)
            VisualizerRequest(
                chart_type=ChartType.HISTOGRAM,
                title="Distribución de Edades",
                x_column="Edad",
                category_column="Genero"
            ),
            
            # Blood pressure by condition (Bar Chart)
            VisualizerRequest(
                chart_type=ChartType.BAR,
                title="Presión Sistólica Promedio por Condición",
                x_column="Descripcion",
                y_column="Presion_Sistolica",
                category_column="Genero"
            ),
            
            # Glucose levels by condition (Box Plot)
            VisualizerRequest(
                chart_type=ChartType.BOX,
                title="Niveles de Glucosa por Condición",
                x_column="Descripcion",
                y_column="Nivel_Glucosa"
            ),
            
            # Annual visits distribution (Bar Chart)
            VisualizerRequest(
                chart_type=ChartType.BAR,
                title="Distribución de Visitas Anuales",
                x_column="Visitas_Anuales"
            ),
            
            # BMI distribution by condition (Box Plot)
            VisualizerRequest(
                chart_type=ChartType.BOX,
                title="Distribución de IMC por Condición",
                x_column="Descripcion",
                y_column="IMC"
            )
        ]
        
        # Generate all visualizations
        results = visualizer.create_visualizations(
            sample_medical_data, 
            requests,
            gui_mode=False
        )
        
        # Verify all files were created
        assert len(results) == len(requests)
        assert all(isinstance(path, str) for path in results)
        print("\nGenerated visualization files:")
        for path in results:
            print(f"- {path}")

    def test_gui_mode_examples(self, sample_medical_data):
        """Test generating visualizations in GUI mode with custom sizes."""
        visualizer = Visualizer()
        
        requests = [
            # Age vs BMI scatter plot
            VisualizerRequest(
                chart_type=ChartType.SCATTER,
                title="IMC vs Edad (GUI Mode)",
                x_column="Edad",
                y_column="IMC",
                category_column="Genero"
            ),
            
            # Disease distribution pie chart
            VisualizerRequest(
                chart_type=ChartType.PIE,
                title="Distribución de Condiciones (GUI Mode)",
                x_column="Descripcion"
            )
        ]
        
        # Generate visualizations in GUI mode
        figures = visualizer.create_visualizations(
            sample_medical_data,
            requests,
            gui_mode=True,
            figure_size=(10, 6)
        )
        
        assert len(figures) == len(requests)
        print("\nGenerated GUI mode figures")
