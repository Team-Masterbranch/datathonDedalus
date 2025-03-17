# tests/test_intention_executor.py
import pytest
from unittest.mock import Mock, AsyncMock
import warnings
import asyncio

from core.intention_executor import IntentionExecutor
from core.intention import Intention, IntentionType, FilterTarget
from core.query import Query
from core.visualizer_request import VisualizerRequest

# Configure pytest for async testing
pytest.register_assert_rewrite('pytest_asyncio')

# Filter warnings
warnings.filterwarnings(
    "ignore",
    category=RuntimeWarning,
    message="coroutine.*was never awaited"
)

class TestIntentionExecutor:
    @pytest.fixture
    def query_manager(self):
        mock = AsyncMock()
        mock.execute_query.return_value = {"filtered_count": 100}
        return mock

    @pytest.fixture
    def visualizer(self):
        mock = AsyncMock()
        mock.create_visualizations.return_value = ["path/to/viz.png"]
        return mock

    @pytest.fixture
    def data_manager(self):
        mock = AsyncMock()
        mock.get_current_cohort.return_value = {"data": "some_data"}
        return mock

    @pytest.fixture
    def executor(self, query_manager, visualizer, data_manager):
        return IntentionExecutor(query_manager, visualizer, data_manager)

    @pytest.mark.asyncio
    async def test_execute_cohort_filter(self, executor, query_manager, data_manager):
        # Arrange
        query = Mock(spec=Query)
        query.validate.return_value = True

        intention = Mock(spec=Intention)
        intention.intention_type = IntentionType.COHORT_FILTER
        intention.query = query
        intention.filter_target = FilterTarget.FULL_DATASET
        intention.validate.return_value = True

        # Act
        result = await executor.execute(intention)

        # Assert
        assert result["success"] is True
        assert result["type"] == "cohort_filter"
        assert "result" in result
        # Clean up any pending coroutines
        await asyncio.sleep(0)
        query_manager.execute_query.assert_called_once_with(
            query,
            filter_current_cohort=False
        )

    @pytest.mark.asyncio
    async def test_execute_visualization(self, executor, visualizer, data_manager):
        # Arrange
        viz_request = Mock(spec=VisualizerRequest)
        
        intention = Mock(spec=Intention)
        intention.intention_type = IntentionType.VISUALIZATION
        intention.visualizer_request = viz_request
        intention.validate.return_value = True
        
        # Act
        result = await executor.execute(intention)
        
        # Assert
        assert result["success"] is True
        assert result["type"] == "visualization"
        assert "visualization_paths" in result
        # Clean up any pending coroutines
        await asyncio.sleep(0)
        visualizer.create_visualizations.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_help(self, executor):
        # Arrange
        intention = Mock(spec=Intention)
        intention.intention_type = IntentionType.HELP
        intention.description = "Help message"
        intention.validate.return_value = True
        
        # Act
        result = await executor.execute(intention)
        
        # Assert
        assert result["success"] is True
        assert result["type"] == "help"
        assert result["message"] == "Help message"

    @pytest.mark.asyncio
    async def test_execute_cohort_filter_current_cohort(self, executor, query_manager):
        # Arrange
        query = Mock(spec=Query)
        query.validate.return_value = True
        
        intention = Mock(spec=Intention)
        intention.intention_type = IntentionType.COHORT_FILTER
        intention.query = query
        intention.filter_target = FilterTarget.CURRENT_COHORT
        intention.validate.return_value = True
        
        query_manager.execute_query.return_value = {"filtered_count": 50}
        
        # Act
        result = await executor.execute(intention)
        
        # Assert
        assert result["success"] is True
        # Clean up any pending coroutines
        await asyncio.sleep(0)
        query_manager.execute_query.assert_called_once_with(
            query,
            filter_current_cohort=True
        )
