import logging
from src import schedule_pipeline, DataPipelineConfig


def main(config: DataPipelineConfig):
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('data_pipeline.log'),
            logging.StreamHandler()
        ]
    )
    # Launch the pipeline
    schedule_pipeline(config)


if __name__ == "__main__":
    main(DataPipelineConfig.from_args())
    