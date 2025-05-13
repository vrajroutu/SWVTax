import os
import yaml
from dotenv import load_dotenv

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '../config/config.yaml')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    load_dotenv()
    # Optionally override with environment variables
    config['DB_URI'] = os.getenv('DB_URI', config.get('DB_URI'))
    return config
