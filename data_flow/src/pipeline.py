import time
import schedule
import logging
import asyncio

from .config import DataPipelineConfig
from .extract import DataExtractor
from .transform import DataTransformer
from .load import DataLoader

logger = logging.getLogger(__name__) 


class DataPipeline:
    """Main pipeline orchestrator"""
    
    def __init__(self, config: DataPipelineConfig):
        self.config = config
        
        self.transformer = DataTransformer()
        self.loader = DataLoader(self.config)
        self.loader.setup()
    
    async def process_endpoint(self, endpoint: str, transform_func) -> None:
        """Process a single endpoint"""
        try:
            async with DataExtractor(self.config) as extractor:
                # Extract
                raw_data = await extractor.fetch_all_data(endpoint)
                
                # Transform
                transformed_data = transform_func(raw_data)
                
                # Load
                self.loader.load_data(transformed_data, endpoint)
                
                logger.info(f"Successfully processed {endpoint}")
                
        except Exception as e:
            logger.error(f"Error processing {endpoint}: {str(e)}", exc_info=True)
            raise
    
    async def run(self) -> None:
        """Run the complete pipeline"""
        logger.info("Starting data pipeline run")
        
        tasks = [
            self.process_endpoint('tracks', self.transformer.transform_tracks),
            self.process_endpoint('users', self.transformer.transform_users),
            self.process_endpoint('listen_history', self.transformer.transform_listen_history)
        ]
        
        await asyncio.gather(*tasks)
        logger.info("Completed data pipeline run")



def run_pipeline(config: DataPipelineConfig) -> None:
    """Entry point for running the pipeline"""
    try:
        pipeline = DataPipeline(config)
        asyncio.run(pipeline.run())
    except Exception as e:
        logger.error(f"Pipeline run failed: {str(e)}", exc_info=True)
        raise

def schedule_pipeline(config: DataPipelineConfig) -> None:
    """Schedule the pipeline to run daily"""
    schedule.every().day.at(time_str=config.pipeline_runtime, tz=config.timezone).do(run_pipeline, config)
    
    while True:
        schedule.run_pending()
        time.sleep(60)
     
    # run_pipeline(config)
