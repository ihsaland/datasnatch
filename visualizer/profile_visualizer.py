import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import json
import os
from datetime import datetime
import logging
from PIL import Image
import io
import base64

class ProfileVisualizer:
    def __init__(self, output_dir: str = 'visualizations'):
        self.output_dir = output_dir
        self.setup_logging()
        os.makedirs(output_dir, exist_ok=True)
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def visualize_profiles(self, profiles: List[Dict]):
        """Generate all visualizations for the profiles."""
        self.visualize_authenticity_distribution(profiles)
        self.visualize_location_heatmap(profiles)
        self.visualize_profile_network(profiles)
        self.visualize_profile_stats(profiles)
        self.visualize_image_quality_distribution(profiles)

    def visualize_authenticity_distribution(self, profiles: List[Dict]):
        """Create a histogram of authenticity scores."""
        scores = [p.get('authenticity_score', 0) for p in profiles]
        
        plt.figure(figsize=(10, 6))
        sns.histplot(scores, bins=20, kde=True)
        plt.title('Distribution of Profile Authenticity Scores')
        plt.xlabel('Authenticity Score')
        plt.ylabel('Count')
        
        output_path = os.path.join(self.output_dir, 'authenticity_distribution.png')
        plt.savefig(output_path)
        plt.close()
        
        self.logger.info(f"Saved authenticity distribution to {output_path}")

    def visualize_location_heatmap(self, profiles: List[Dict]):
        """Create a heatmap of profile locations."""
        # Extract valid coordinates
        coordinates = []
        for profile in profiles:
            location_analysis = profile.get('location_analysis', {})
            if location_analysis.get('is_valid') and location_analysis.get('coordinates'):
                coordinates.append(location_analysis['coordinates'])
        
        if not coordinates:
            return
        
        # Create heatmap
        plt.figure(figsize=(12, 8))
        lats, lons = zip(*coordinates)
        
        # Create a 2D histogram
        heatmap, xedges, yedges = np.histogram2d(lats, lons, bins=50)
        
        # Plot heatmap
        plt.imshow(heatmap.T, origin='lower', cmap='hot')
        plt.colorbar(label='Number of Profiles')
        plt.title('Profile Location Heatmap')
        plt.xlabel('Latitude')
        plt.ylabel('Longitude')
        
        output_path = os.path.join(self.output_dir, 'location_heatmap.png')
        plt.savefig(output_path)
        plt.close()
        
        self.logger.info(f"Saved location heatmap to {output_path}")

    def visualize_profile_network(self, profiles: List[Dict]):
        """Create a network graph of connected profiles."""
        G = nx.Graph()
        
        # Add nodes and edges based on shared information
        for i, profile in enumerate(profiles):
            G.add_node(i, **{k: v for k, v in profile.items() if k not in ['phone_analysis', 'location_analysis']})
            
            # Add edges based on shared phone numbers
            phone_analysis = profile.get('phone_analysis', {})
            if phone_analysis.get('associated_profiles'):
                for associated_profile in phone_analysis['associated_profiles']:
                    G.add_edge(i, associated_profile, type='phone')
            
            # Add edges based on shared locations
            location_analysis = profile.get('location_analysis', {})
            if location_analysis.get('associated_profiles'):
                for associated_profile in location_analysis['associated_profiles']:
                    G.add_edge(i, associated_profile, type='location')
        
        # Create the visualization
        plt.figure(figsize=(15, 15))
        pos = nx.spring_layout(G)
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_size=100, alpha=0.6)
        
        # Draw edges with different colors for different types
        edge_colors = ['red' if G[u][v]['type'] == 'phone' else 'blue' 
                      for u, v in G.edges()]
        nx.draw_networkx_edges(G, pos, edge_color=edge_colors, alpha=0.4)
        
        # Add labels
        labels = {i: profiles[i].get('name', f'Profile {i}') for i in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, font_size=8)
        
        plt.title('Profile Connection Network')
        
        output_path = os.path.join(self.output_dir, 'profile_network.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Saved profile network to {output_path}")

    def visualize_profile_stats(self, profiles: List[Dict]):
        """Create various statistical visualizations of profile data."""
        # Create a figure with multiple subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Age distribution
        ages = [p.get('age') for p in profiles if p.get('age')]
        if ages:
            sns.histplot(ages, bins=20, ax=axes[0, 0])
            axes[0, 0].set_title('Age Distribution')
            axes[0, 0].set_xlabel('Age')
            axes[0, 0].set_ylabel('Count')
        
        # Image count distribution
        image_counts = [len(p.get('images', [])) for p in profiles]
        sns.histplot(image_counts, bins=20, ax=axes[0, 1])
        axes[0, 1].set_title('Number of Images per Profile')
        axes[0, 1].set_xlabel('Number of Images')
        axes[0, 1].set_ylabel('Count')
        
        # Profile completeness
        required_fields = ['name', 'phone', 'location', 'images']
        completeness = [sum(1 for field in required_fields if p.get(field)) / len(required_fields) 
                       for p in profiles]
        sns.histplot(completeness, bins=20, ax=axes[1, 0])
        axes[1, 0].set_title('Profile Completeness Distribution')
        axes[1, 0].set_xlabel('Completeness Score')
        axes[1, 0].set_ylabel('Count')
        
        # Message length distribution
        message_lengths = [len(p.get('message', '')) for p in profiles]
        sns.histplot(message_lengths, bins=20, ax=axes[1, 1])
        axes[1, 1].set_title('Message Length Distribution')
        axes[1, 1].set_xlabel('Message Length')
        axes[1, 1].set_ylabel('Count')
        
        plt.tight_layout()
        
        output_path = os.path.join(self.output_dir, 'profile_stats.png')
        plt.savefig(output_path)
        plt.close()
        
        self.logger.info(f"Saved profile statistics to {output_path}")

    def visualize_image_quality_distribution(self, profiles: List[Dict]):
        """Create a visualization of image quality scores."""
        quality_scores = []
        for profile in profiles:
            image_analysis = profile.get('image_analysis', {})
            quality_scores.extend(image_analysis.get('image_quality', []))
        
        if not quality_scores:
            return
        
        plt.figure(figsize=(10, 6))
        sns.histplot(quality_scores, bins=20, kde=True)
        plt.title('Distribution of Image Quality Scores')
        plt.xlabel('Quality Score')
        plt.ylabel('Count')
        
        output_path = os.path.join(self.output_dir, 'image_quality_distribution.png')
        plt.savefig(output_path)
        plt.close()
        
        self.logger.info(f"Saved image quality distribution to {output_path}")

    def create_profile_report(self, profile: Dict) -> str:
        """Create a detailed HTML report for a single profile."""
        report = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .section {{ margin-bottom: 20px; }}
                .score {{ font-size: 24px; color: #2ecc71; }}
                .warning {{ color: #e74c3c; }}
            </style>
        </head>
        <body>
            <h1>Profile Report</h1>
            
            <div class="section">
                <h2>Basic Information</h2>
                <p>Name: {profile.get('name', 'N/A')}</p>
                <p>Age: {profile.get('age', 'N/A')}</p>
                <p>Location: {profile.get('location', 'N/A')}</p>
                <p>Phone: {profile.get('phone', 'N/A')}</p>
            </div>
            
            <div class="section">
                <h2>Authenticity Analysis</h2>
                <p>Authenticity Score: <span class="score">{profile.get('authenticity_score', 0):.2f}</span></p>
            </div>
            
            <div class="section">
                <h2>Image Analysis</h2>
                <p>Number of Images: {len(profile.get('images', []))}</p>
                <p>Face Detected: {'Yes' if profile.get('image_analysis', {}).get('face_detected') else 'No'}</p>
                <p>Average Image Quality: {np.mean(profile.get('image_analysis', {}).get('image_quality', [0])):.2f}</p>
            </div>
            
            <div class="section">
                <h2>Phone Analysis</h2>
                <p>Valid Phone: {'Yes' if profile.get('phone_analysis', {}).get('is_valid') else 'No'}</p>
                <p>Carrier: {profile.get('phone_analysis', {}).get('carrier', 'N/A')}</p>
                <p>Associated Names: {', '.join(profile.get('phone_analysis', {}).get('associated_names', []))}</p>
            </div>
            
            <div class="section">
                <h2>Location Analysis</h2>
                <p>Valid Location: {'Yes' if profile.get('location_analysis', {}).get('is_valid') else 'No'}</p>
                <p>Coordinates: {profile.get('location_analysis', {}).get('coordinates', 'N/A')}</p>
            </div>
        </body>
        </html>
        """
        
        output_path = os.path.join(self.output_dir, f'profile_report_{profile.get("name", "unknown")}.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        self.logger.info(f"Saved profile report to {output_path}")
        return output_path 