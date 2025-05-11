"""Config loading and management module"""

import os
from pydantic import BaseModel, Field
from typing import Literal, Dict
import yaml
import logging.config


class DataSourceConfig(BaseModel):
    type: Literal['csv', 'sqlite']
    path: str


class AppConfig(BaseModel):
    mode: Literal['A', 'B']
    output_dir: str
    data_sources: Dict[str, DataSourceConfig]


def load_config(path: str = "config/default.yaml") -> AppConfig:
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return AppConfig(**data)


def setup_logging(log_cfg_path="config/logger.yaml"):
    with open(log_cfg_path, 'r') as f:
        config = yaml.safe_load(f)

    # Ensure log directory exists (if file handler is used)
    for handler in config.get("handlers", {}).values():
        if handler.get("class") == "logging.FileHandler":
            log_path = handler.get("filename")
            if log_path:
                os.makedirs(os.path.dirname(log_path), exist_ok=True)

    logging.config.dictConfig(config)