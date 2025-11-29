"""Configuration loader utility"""
import yaml
from pathlib import Path
from typing import Dict, Any


def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to the configuration YAML file
        
    Returns:
        Dictionary containing configuration values
    """
    # Get project root directory
    project_root = Path(__file__).parent.parent.parent
    
    # Load YAML config
    config_file = project_root / config_path
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    return config


def get_project_root() -> Path:
    """Get the project root directory"""
    return Path(__file__).parent.parent.parent

