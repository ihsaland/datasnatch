import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
API_CONFIG = {
    'google_api_key': os.getenv('GOOGLE_API_KEY'),
    'face_api_key': os.getenv('FACE_API_KEY'),
    'phone_api_key': os.getenv('PHONE_API_KEY'),
    'location_api_key': os.getenv('LOCATION_API_KEY')
}

# Scraping Configuration
SCRAPING_CONFIG = {
    'request_timeout': 30,
    'max_retries': 3,
    'retry_delay': 5,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Analysis Configuration
ANALYSIS_CONFIG = {
    'min_image_quality': 0.3,
    'face_detection_confidence': 0.6,
    'phone_validation_threshold': 0.7,
    'location_validation_threshold': 0.7
}

# Visualization Configuration
VISUALIZATION_CONFIG = {
    'output_dir': 'visualizations',
    'image_quality': {
        'dpi': 300,
        'format': 'png'
    },
    'network_graph': {
        'node_size': 100,
        'edge_alpha': 0.4,
        'label_font_size': 8
    }
}

# Data Storage Configuration
STORAGE_CONFIG = {
    'data_dir': 'data',
    'backup_dir': 'backups',
    'max_backups': 5
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'datasnatch.log'
}

def get_api_key(service: str) -> str:
    """Get API key for a specific service."""
    return API_CONFIG.get(f'{service}_api_key')

def is_api_enabled(service: str) -> bool:
    """Check if API is enabled for a specific service."""
    return bool(get_api_key(service)) 