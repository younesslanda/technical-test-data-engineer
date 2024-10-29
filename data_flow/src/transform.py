import pandas as pd
from typing import Dict, List

class DataTransformer:
    """Handles data transformation and validation"""
    
    @staticmethod
    def transform_tracks(tracks: List[Dict]) -> pd.DataFrame:
        df = pd.DataFrame(tracks)
        df['duration'] = pd.to_datetime(df['duration'], format='%M:%S')
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['updated_at'] = pd.to_datetime(df['updated_at'])
        return df
    
    @staticmethod
    def transform_users(users: List[Dict]) -> pd.DataFrame:
        df = pd.DataFrame(users)
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['updated_at'] = pd.to_datetime(df['updated_at'])
        return df
    
    @staticmethod
    def transform_listen_history(history: List[Dict]) -> pd.DataFrame:
        # Flatten the elements of items into new rows
        df = pd.DataFrame(history).explode('items').reset_index(drop=True)
        df = df.rename(columns={'items': 'track_id'})
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['updated_at'] = pd.to_datetime(df['updated_at'])
        return df