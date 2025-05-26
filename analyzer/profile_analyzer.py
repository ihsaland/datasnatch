import face_recognition
import cv2
import numpy as np
from PIL import Image
import requests
from typing import Dict, List, Optional, Tuple
import logging
import os
from datetime import datetime
import json
import re
from urllib.parse import urlparse
import aiohttp
import asyncio

class ProfileAnalyzer:
    def __init__(self, use_apis: bool = False):
        self.use_apis = use_apis
        self.setup_logging()
        self.face_cache = {}
        self.phone_pattern = re.compile(r'\+?1?\s*\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}')
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    async def analyze_profile(self, profile: Dict) -> Dict:
        enriched_profile = profile.copy()
        
        # Analyze images
        if 'images' in profile:
            enriched_profile['image_analysis'] = await self.analyze_images(profile['images'])
        
        # Analyze phone number
        if 'phone' in profile:
            enriched_profile['phone_analysis'] = await self.analyze_phone(profile['phone'])
        
        # Analyze location
        if 'location' in profile:
            enriched_profile['location_analysis'] = await self.analyze_location(profile['location'])
        
        # Calculate authenticity score
        enriched_profile['authenticity_score'] = self.calculate_authenticity_score(enriched_profile)
        
        return enriched_profile

    async def analyze_images(self, image_urls: List[str]) -> Dict:
        analysis = {
            'face_detected': False,
            'face_encodings': [],
            'image_quality': [],
            'reverse_image_results': []
        }
        
        for url in image_urls:
            try:
                # Download and analyze image
                image_data = await self.download_image(url)
                if image_data:
                    # Face detection
                    face_encoding = self.detect_face(image_data)
                    if face_encoding is not None:
                        analysis['face_detected'] = True
                        analysis['face_encodings'].append(face_encoding.tolist())
                    
                    # Image quality assessment
                    quality_score = self.assess_image_quality(image_data)
                    analysis['image_quality'].append(quality_score)
                    
                    # Reverse image search
                    if self.use_apis:
                        reverse_results = await self.reverse_image_search(url)
                        analysis['reverse_image_results'].extend(reverse_results)
            
            except Exception as e:
                self.logger.error(f"Error analyzing image {url}: {str(e)}")
        
        return analysis

    async def analyze_phone(self, phone: str) -> Dict:
        analysis = {
            'is_valid': False,
            'carrier': None,
            'location': None,
            'associated_names': [],
            'associated_profiles': []
        }
        
        # Basic phone validation
        if self.phone_pattern.match(phone):
            analysis['is_valid'] = True
            
            if self.use_apis:
                # Enhanced phone analysis with APIs
                carrier_info = await self.get_carrier_info(phone)
                analysis['carrier'] = carrier_info
                
                # Search for associated profiles
                associated_data = await self.search_phone_online(phone)
                analysis['associated_names'] = associated_data.get('names', [])
                analysis['associated_profiles'] = associated_data.get('profiles', [])
        
        return analysis

    async def analyze_location(self, location: str) -> Dict:
        analysis = {
            'is_valid': False,
            'coordinates': None,
            'associated_profiles': []
        }
        
        if self.use_apis:
            # Geocode location
            coordinates = await self.geocode_location(location)
            if coordinates:
                analysis['is_valid'] = True
                analysis['coordinates'] = coordinates
                
                # Search for associated profiles in the area
                nearby_profiles = await self.search_nearby_profiles(coordinates)
                analysis['associated_profiles'] = nearby_profiles
        
        return analysis

    def calculate_authenticity_score(self, profile: Dict) -> float:
        score = 0.0
        weights = {
            'face_detected': 0.3,
            'phone_valid': 0.2,
            'location_valid': 0.2,
            'image_quality': 0.15,
            'profile_completeness': 0.15
        }
        
        # Face detection score
        if profile.get('image_analysis', {}).get('face_detected'):
            score += weights['face_detected']
        
        # Phone validation score
        if profile.get('phone_analysis', {}).get('is_valid'):
            score += weights['phone_valid']
        
        # Location validation score
        if profile.get('location_analysis', {}).get('is_valid'):
            score += weights['location_valid']
        
        # Image quality score
        image_qualities = profile.get('image_analysis', {}).get('image_quality', [])
        if image_qualities:
            avg_quality = sum(image_qualities) / len(image_qualities)
            score += avg_quality * weights['image_quality']
        
        # Profile completeness score
        required_fields = ['name', 'phone', 'location', 'images']
        completeness = sum(1 for field in required_fields if profile.get(field)) / len(required_fields)
        score += completeness * weights['profile_completeness']
        
        return min(1.0, score)

    async def download_image(self, url: str) -> Optional[np.ndarray]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        return cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
        except Exception as e:
            self.logger.error(f"Error downloading image {url}: {str(e)}")
        return None

    def detect_face(self, image: np.ndarray) -> Optional[np.ndarray]:
        try:
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_image)
            
            if face_locations:
                face_encoding = face_recognition.face_encodings(rgb_image, face_locations)[0]
                return face_encoding
        except Exception as e:
            self.logger.error(f"Error detecting face: {str(e)}")
        return None

    def assess_image_quality(self, image: np.ndarray) -> float:
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Calculate Laplacian variance (sharpness)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Calculate brightness
            brightness = np.mean(gray)
            
            # Normalize scores
            sharpness_score = min(1.0, laplacian_var / 500.0)
            brightness_score = min(1.0, brightness / 255.0)
            
            return (sharpness_score + brightness_score) / 2
        except Exception as e:
            self.logger.error(f"Error assessing image quality: {str(e)}")
            return 0.0

    async def reverse_image_search(self, image_url: str) -> List[Dict]:
        if not self.use_apis:
            return []
        
        # Implement reverse image search using available APIs
        # This is a placeholder for the actual implementation
        return []

    async def get_carrier_info(self, phone: str) -> Optional[Dict]:
        if not self.use_apis:
            return None
        
        # Implement carrier lookup using available APIs
        # This is a placeholder for the actual implementation
        return None

    async def search_phone_online(self, phone: str) -> Dict:
        if not self.use_apis:
            return {'names': [], 'profiles': []}
        
        # Implement phone number search using available APIs
        # This is a placeholder for the actual implementation
        return {'names': [], 'profiles': []}

    async def geocode_location(self, location: str) -> Optional[Tuple[float, float]]:
        if not self.use_apis:
            return None
        
        # Implement geocoding using available APIs
        # This is a placeholder for the actual implementation
        return None

    async def search_nearby_profiles(self, coordinates: Tuple[float, float]) -> List[Dict]:
        if not self.use_apis:
            return []
        
        # Implement nearby profile search using available APIs
        # This is a placeholder for the actual implementation
        return [] 