from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional
import logging

class ProfileScraper(BaseScraper):
    def __init__(self, base_url: str, max_depth: int = 2):
        super().__init__(base_url)
        self.max_depth = max_depth
        self.logger = logging.getLogger(__name__)

    def _extract_name(self, soup: BeautifulSoup) -> Optional[str]:
        name_elem = soup.find('h1', class_='profile-name')
        return name_elem.text.strip() if name_elem else None

    def _extract_phone(self, soup: BeautifulSoup) -> Optional[str]:
        phone_elem = soup.find('div', class_='phone-number')
        if phone_elem:
            phone_text = phone_elem.text.strip()
            # Extract phone number using regex
            phone_match = re.search(r'\+?[\d\s-]+', phone_text)
            return phone_match.group(0) if phone_match else None
        return None

    def _extract_location(self, soup: BeautifulSoup) -> Optional[str]:
        location_elem = soup.find('div', class_='location')
        return location_elem.text.strip() if location_elem else None

    def _extract_age(self, soup: BeautifulSoup) -> Optional[int]:
        age_elem = soup.find('div', class_='age')
        if age_elem:
            try:
                return int(re.search(r'\d+', age_elem.text).group(0))
            except (ValueError, AttributeError):
                return None
        return None

    def _extract_date(self, soup: BeautifulSoup) -> Optional[str]:
        date_elem = soup.find('div', class_='date-posted')
        return date_elem.text.strip() if date_elem else None

    def _extract_message(self, soup: BeautifulSoup) -> Optional[str]:
        message_elem = soup.find('div', class_='message')
        return message_elem.text.strip() if message_elem else None

    def _extract_images(self, soup: BeautifulSoup) -> List[str]:
        images = []
        img_elements = soup.find_all('img', class_='profile-image')
        for img in img_elements:
            if img.get('src'):
                images.append(img['src'])
        return images

    async def _scrape_state(self, state: str) -> List[Dict]:
        self.logger.info(f"Scraping profiles for state: {state}")
        profiles = []
        visited_urls = set()  # Keep track of visited URLs to avoid duplicates

        async def crawl_page(url: str, depth: int = 0):
            if depth > self.max_depth or url in visited_urls:
                return
            visited_urls.add(url)
            self.logger.info(f"Crawling {url} at depth {depth}")
            try:
                content = await self.get_page_content(url)
                soup = BeautifulSoup(content, 'html.parser')
                # Extract profile data if this is a profile page
                if 'profile' in url.lower():
                    profile_data = self.parse_profile(content)
                    profiles.append(profile_data)
                # Find all links on the page
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    if not href.startswith('http'):
                        href = f"{self.base_url.rstrip('/')}/{href.lstrip('/')}"
                    if href.startswith(self.base_url) and href not in visited_urls:
                        await crawl_page(href, depth + 1)
            except Exception as e:
                self.logger.error(f"Error crawling {url}: {str(e)}")

        try:
            await crawl_page(self.base_url)
        except Exception as e:
            self.logger.error(f"Error during crawling: {str(e)}")
        return profiles 