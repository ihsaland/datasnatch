import asyncio
import argparse
import logging
import os
from typing import List, Dict
from dotenv import load_dotenv

from scraper.profile_scraper import ProfileScraper
from analyzer.profile_analyzer import ProfileAnalyzer
from visualizer.profile_visualizer import ProfileVisualizer

class DataSnatch:
    def __init__(self, base_url: str, use_apis: bool = False):
        self.base_url = base_url
        self.use_apis = use_apis
        self.setup_logging()
        self.setup_directories()
        
        # Initialize components
        self.scraper = ProfileScraper(base_url)
        self.analyzer = ProfileAnalyzer(use_apis=use_apis)
        self.visualizer = ProfileVisualizer()
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_directories(self):
        """Create necessary directories for data storage."""
        directories = ['data', 'visualizations']
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    async def process_profiles(self, states: List[str] = None):
        """Main processing pipeline."""
        try:
            # Step 1: Scrape profiles
            self.logger.info("Starting profile scraping...")
            profiles = await self.scraper.scrape_profiles(states)
            self.logger.info(f"Scraped {len(profiles)} profiles")
            
            # Step 2: Analyze profiles
            self.logger.info("Starting profile analysis...")
            analyzed_profiles = []
            for profile in profiles:
                analyzed_profile = await self.analyzer.analyze_profile(profile)
                analyzed_profiles.append(analyzed_profile)
            self.logger.info("Profile analysis completed")
            
            # Step 3: Save raw data
            self.scraper.save_profiles(analyzed_profiles)
            
            # Step 4: Generate visualizations
            self.logger.info("Generating visualizations...")
            self.visualizer.visualize_profiles(analyzed_profiles)
            
            # Step 5: Generate individual profile reports
            for profile in analyzed_profiles:
                self.visualizer.create_profile_report(profile)
            
            self.logger.info("Processing completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error during processing: {str(e)}")
            raise

def main():
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='DataSnatch - Profile Data Extraction and Analysis')
    parser.add_argument('--url', type=str, default='https://listrawler.eu',
                      help='Base URL to scrape (default: https://listrawler.eu)')
    parser.add_argument('--states', type=str, nargs='+', default=['all'],
                      help='States to scrape (default: all)')
    parser.add_argument('--use-apis', action='store_true',
                      help='Use external APIs for enhanced data collection')
    parser.add_argument('--depth', type=int, default=2, help='Maximum depth for crawling (default: 2).')
    
    args = parser.parse_args()
    
    # Initialize and run the application
    app = DataSnatch(args.url, use_apis=args.use_apis)
    
    # Run the async main function
    asyncio.run(app.process_profiles(args.states))

if __name__ == '__main__':
    main() 