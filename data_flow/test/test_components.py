import pytest
import pandas as pd
from unittest.mock import patch

from src.config import DataPipelineConfig
from src.load import DataLoader
from src.extract import DataExtractor
from src.transform import DataTransformer
from src.pipeline import DataPipeline


@pytest.fixture
def config():
    return DataPipelineConfig(
        # NOTE: can be loaded from env vars for security
        api_base_url="http://127.0.0.1:8000",
        database_url="mysql+pymysql://avnadmin:AVNS_gKvSFEto1ZIBhma42zG@mysql-1d845ed5-youness-7db7.f.aivencloud.com:13542/defaultdb",
        batch_size=10
    )

@pytest.fixture
def sample_track_data():
    return [
        {
            "id": 1,
            "name": "Test Song",
            "artist": "Test Artist",
            "songwriters": "Test Writer",
            "duration": "03:45",
            "genres": "rock",
            "album": "Test Album",
            "created_at": "2024-01-01T00:00:00.000Z",
            "updated_at": "2024-01-02T00:00:00.000Z"
        }
    ]

@pytest.fixture
def sample_listen_history():
    return [
        {
            "user_id": 1,
            "items": [1, 2, 3],
            "created_at": "2024-01-01T00:00:00.000Z",
            "updated_at": "2024-01-02T00:00:00.000Z"
        }
    ]

class TestDataExtractor:
    @pytest.mark.asyncio
    async def test_pagination_handling(self, config):
        """Test if the extractor correctly handles pagination"""
        mock_responses = [
            {'items': [{'id': i} for i in range(10)], 'total': 15},
            {'items': [{'id': i} for i in range(10, 15)], 'total': 15}
        ]

        async def mock_fetch_page(self, endpoint: str, page: int):
            return mock_responses[page - 1]

        with patch.object(DataExtractor, 'fetch_page', mock_fetch_page):
            async with DataExtractor(config) as extractor:
                data = await extractor.fetch_all_data('tracks')
                assert len(data) == 15
                assert data[-1]['id'] == 14

class TestDataTransformer:
    def test_track_transformation(self, sample_track_data):
        """Test if track data is correctly transformed"""
        transformer = DataTransformer()
        df = transformer.transform_tracks(sample_track_data)
        
        # Check data types
        assert isinstance(df['duration'].iloc[0], pd.Timestamp)
        assert isinstance(df['created_at'].iloc[0], pd.Timestamp)
        assert isinstance(df['updated_at'].iloc[0], pd.Timestamp)
        
        # Check if all required columns are present
        required_columns = {
            'id', 'name', 'artist', 'songwriters', 'duration',
            'genres', 'album', 'created_at', 'updated_at'
        }
        assert all(col in df.columns for col in required_columns)

    def test_listen_history_transformation(self, sample_listen_history):
        """Test if listen history is correctly transformed"""
        transformer = DataTransformer()
        df = transformer.transform_listen_history(sample_listen_history)
        
        # Check if track_id is properly flattened
        assert isinstance(df['track_id'].iloc[0], int)
        assert df['track_id'].tolist() == [1, 2, 3]
        
        # Check datetime conversion
        assert isinstance(df['created_at'].iloc[0], pd.Timestamp)
        assert isinstance(df['updated_at'].iloc[0], pd.Timestamp)

class TestDataLoader:
    def test_data_loading(self, config):
        """Test if data is correctly loaded into the database"""
        loader = DataLoader(config)
        loader.setup(test=True)
        
        # Create test data
        test_data = pd.DataFrame({
            'id': [1, 2],
            'name': ['Test1', 'Test2'],
            'created_at': ['2024-01-01', '2024-01-02']
        })
        
        # Load data
        loader.load_data(test_data, 'test_table')
        
        # Query data
        with loader.engine.connect() as conn:
            result = pd.read_sql_table('test_table', conn)
            assert len(result) == 2
            assert list(result['name']) == ['Test1', 'Test2']

class TestEndToEnd:
    @pytest.mark.asyncio
    async def test_pipeline_execution(self, config, sample_track_data):
        """Test if the pipeline can execute end-to-end"""
        async def mock_fetch_all_data(self, endpoint):
            data_map = {
                'tracks': sample_track_data,
                'listen_history': sample_listen_history
            }
            return data_map.get(endpoint, [])

        with patch.object(DataExtractor, 'fetch_all_data', mock_fetch_all_data):
            pipeline = DataPipeline(config)
            await pipeline.process_endpoint(
                'tracks',
                pipeline.transformer.transform_tracks
            )

if __name__ == '__main__':
    pytest.main([__file__])