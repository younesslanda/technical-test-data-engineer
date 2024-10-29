import asyncio
import aiohttp
import backoff

from typing import Dict, List, Optional

from .config import DataPipelineConfig


class DataExtractor:
    """Handles data extraction from the API"""
    
    def __init__(self, config: DataPipelineConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, asyncio.TimeoutError),
        max_tries=3
    )
    async def fetch_page(self, endpoint: str, page: int) -> Dict:
        """Fetch a single page of data from the API"""
        params = {
            'page': page,
            'size': self.config.batch_size
        }
        
        async with self.session.get(
            f"{self.config.api_base_url}/{endpoint}",
            params=params
        ) as response:
            response.raise_for_status()
            return await response.json()
    
    async def fetch_all_data(self, endpoint: str) -> List[Dict]:
        """Fetch all pages of data from an endpoint"""
        all_data = []
        page = 1
        
        while True:
            data = await self.fetch_page(endpoint, page)
            all_data.extend(data['items'])
            
            if len(data['items']) < self.config.batch_size:
                break
            
            page += 1
            
        return all_data
