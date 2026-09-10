import os
import yaml
from pathlib import Path

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"

def load_config(config_path=None):
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found at: {path}")
    
    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    # Ensure directories exist
    base_dir = path.parent
    for key in ["screenshots_dir", "videos_dir"]:
        dir_path = base_dir / config["storage"][key]
        dir_path.mkdir(parents=True, exist_ok=True)
        
    db_path = base_dir / config["database"]["path"]
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    return config