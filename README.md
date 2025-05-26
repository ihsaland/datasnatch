# DataSnatch - Advanced Profile Data Extraction and Analysis

A comprehensive tool for extracting, analyzing, and visualizing profile data from various sources.

## Features

- Dynamic web scraping with adaptive parsing
- Profile data extraction (names, locations, phone numbers, images, etc.)
- Image analysis and face recognition
- Phone number and name verification
- Profile authenticity assessment
- Data visualization and relationship mapping
- Optional API integration for enhanced data collection

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- For macOS users: Homebrew (for installing system dependencies)

### Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/yourusername/datasnatch.git
cd datasnatch
```

2. Make the installation script executable and run it:
```bash
chmod +x install.sh
./install.sh
```

3. Activate the virtual environment:
```bash
source venv/bin/activate
```

### Troubleshooting

If you encounter any issues during installation:

1. For macOS users:
   - Make sure you have Xcode Command Line Tools installed:
     ```bash
     xcode-select --install
     ```
   - Install Homebrew if not already installed:
     ```bash
     /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
     ```

2. For Linux users:
   - Install system dependencies:
     ```bash
     sudo apt-get update
     sudo apt-get install python3-dev cmake build-essential
     ```

3. If face_recognition installation fails:
   - Try installing dlib separately first:
     ```bash
     pip install dlib
     ```
   - Then install the remaining requirements:
     ```bash
     pip install -r requirements.txt
     ```

## Usage

Basic usage:
```bash
python main.py --url "https://listrawler.eu" --states all
```

Advanced usage with API keys:
```bash
python main.py --url "https://listrawler.eu" --states all --use-apis
```

## Configuration

Create a `.env` file in the project root with the following variables (all optional):

```
# API Keys
GOOGLE_API_KEY=your_google_api_key_here
FACE_API_KEY=your_face_api_key_here
PHONE_API_KEY=your_phone_api_key_here
LOCATION_API_KEY=your_location_api_key_here

# Application Settings
DEBUG=False
LOG_LEVEL=INFO
MAX_CONCURRENT_REQUESTS=10
REQUEST_TIMEOUT=30
```

## Project Structure

- `scraper/`: Web scraping modules
  - `base_scraper.py`: Core scraping functionality
- `processor/`: Data processing and enrichment
- `analyzer/`: Profile analysis and verification
  - `profile_analyzer.py`: Profile analysis and verification logic
- `visualizer/`: Data visualization components
  - `profile_visualizer.py`: Data visualization and reporting
- `utils/`: Utility functions and helpers
- `config/`: Configuration management
  - `settings.py`: Application settings and configuration
- `data/`: Data storage and management
- `visualizations/`: Generated visualizations and reports

## Output

The application generates several types of output:

1. Raw Data:
   - JSON files containing scraped and analyzed profile data
   - Stored in the `data/` directory

2. Visualizations:
   - Authenticity score distribution
   - Location heatmap
   - Profile connection network
   - Profile statistics
   - Image quality distribution
   - Stored in the `visualizations/` directory

3. Individual Profile Reports:
   - HTML reports for each profile
   - Contains detailed analysis and verification results
   - Stored in the `visualizations/` directory

## License

MIT License 