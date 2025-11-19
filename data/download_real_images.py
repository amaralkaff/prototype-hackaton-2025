#!/usr/bin/env python3
"""
Download real sample images for Amarta AI credit scoring demo
Downloads authentic images of Indonesian micro-businesses and documentation
"""

import requests
import os
from pathlib import Path

# Free stock photo sources with Indonesian business/house images
SAMPLE_IMAGES = {
    'business': [
        {
            'url': 'https://images.unsplash.com/photo-1604719312566-8912e9227c6a?w=1200',
            'filename': 'warung_01.jpg',
            'description': 'Indonesian warung kelontong'
        },
        {
            'url': 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=1200',
            'filename': 'restaurant_01.jpg', 
            'description': 'Small restaurant interior'
        },
        {
            'url': 'https://images.unsplash.com/photo-1567521464027-f127ff144326?w=1200',
            'filename': 'market_stall_01.jpg',
            'description': 'Market vendor stall'
        },
        {
            'url': 'https://images.unsplash.com/photo-1578916171728-46686eac8d58?w=1200',
            'filename': 'grocery_store_01.jpg',
            'description': 'Small grocery store'
        },
        {
            'url': 'https://images.unsplash.com/photo-1542838132-92c53300491e?w=1200',
            'filename': 'food_stall_01.jpg',
            'description': 'Street food stall'
        },
    ],
    'house': [
        {
            'url': 'https://images.unsplash.com/photo-1582268611958-ebfd161ef9cf?w=1200',
            'filename': 'house_01.jpg',
            'description': 'Asian residential house'
        },
        {
            'url': 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=1200',
            'filename': 'house_02.jpg',
            'description': 'Modern house exterior'
        },
        {
            'url': 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=1200',
            'filename': 'interior_01.jpg',
            'description': 'Living room interior'
        },
        {
            'url': 'https://images.unsplash.com/photo-1556912167-f556f1f39fdf?w=1200',
            'filename': 'kitchen_01.jpg',
            'description': 'Kitchen area'
        },
    ],
    'field_documentation': [
        {
            'url': 'https://images.unsplash.com/photo-1521791136064-7986c2920216?w=1200',
            'filename': 'meeting_01.jpg',
            'description': 'Business meeting'
        },
        {
            'url': 'https://images.unsplash.com/photo-1573497491208-6b1acb260507?w=1200',
            'filename': 'discussion_01.jpg',
            'description': 'Group discussion'
        },
        {
            'url': 'https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=1200',
            'filename': 'field_work_01.jpg',
            'description': 'Field documentation'
        },
    ]
}

def download_image(url, filepath, description):
    """Download image from URL to filepath"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        print(f"✓ Downloaded: {description} -> {os.path.basename(filepath)}")
        return True
    except Exception as e:
        print(f"✗ Failed: {description} - {str(e)}")
        return False

def main():
    base_path = Path("/Users/amangly/Documents/prototype-amarta-ai/data/sample_images")
    
    print("\n" + "="*70)
    print("  Downloading Real Sample Images for Amarta AI")
    print("="*70 + "\n")
    
    total_success = 0
    total_failed = 0
    
    for category, images in SAMPLE_IMAGES.items():
        print(f"\n📸 Downloading {category.replace('_', ' ').title()} Images:")
        category_path = base_path / category
        category_path.mkdir(parents=True, exist_ok=True)
        
        for image_info in images:
            filepath = category_path / image_info['filename']
            success = download_image(
                image_info['url'],
                filepath,
                image_info['description']
            )
            if success:
                total_success += 1
            else:
                total_failed += 1
    
    print("\n" + "="*70)
    print(f"✅ Successfully downloaded: {total_success} images")
    if total_failed > 0:
        print(f"❌ Failed downloads: {total_failed} images")
    print("="*70)
    print(f"\nImages saved to: {base_path}")
    print("\nNote: These are free stock photos from Unsplash for demonstration.")
    print("In production, use actual field photos from Amartha operations.\n")

if __name__ == "__main__":
    main()
