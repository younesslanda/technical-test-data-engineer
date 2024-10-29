import os
import argparse
from dataclasses import dataclass, field, fields

@dataclass
class DataPipelineConfig:
    """Configuration for the data pipeline"""
    api_base_url: str = field(default=os.environ.get("API_BASE_URL"))
    database_url: str = field(default=os.environ.get("DATABASE_URL"))

    batch_size: int = 100

    pipeline_runtime: str = "00:00"
    timezone: str = "EST"
    
    @classmethod
    def from_args(cls):
        parser = argparse.ArgumentParser()

        # Dynamically add arguments based on the dataclass fields
        for field in fields(cls):
            field_type = field.type
            parser.add_argument(f"--{field.name}", type=field_type, default=field.default)

        parsed_args = parser.parse_args()

        return cls(**vars(parsed_args))
