#!/usr/bin/env python3
"""
Generate sample images for Amarta AI credit scoring demo
Creates realistic placeholder images for business, house, and field documentation
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Colors
COLORS = {
    'business_bg': '#E8F5E9',  # Light green
    'house_bg': '#E3F2FD',     # Light blue
    'field_bg': '#FFF3E0',     # Light orange
    'text': '#37474F',          # Dark gray
    'accent': '#1976D2'         # Blue
}

def create_placeholder_image(width, height, bg_color, title, subtitle, filename):
    """Create a placeholder image with text"""
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Try to use a nice font, fallback to default
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
        subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        label_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        label_font = ImageFont.load_default()

    # Draw title
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_x = (width - (title_bbox[2] - title_bbox[0])) // 2
    title_y = height // 2 - 60
    draw.text((title_x, title_y), title, fill=COLORS['text'], font=title_font)

    # Draw subtitle
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_x = (width - (subtitle_bbox[2] - subtitle_bbox[0])) // 2
    subtitle_y = title_y + 70
    draw.text((subtitle_x, subtitle_y), subtitle, fill=COLORS['accent'], font=subtitle_font)

    # Draw label at bottom
    label = f"Sample Image: {os.path.basename(filename)}"
    label_bbox = draw.textbbox((0, 0), label, font=label_font)
    label_x = (width - (label_bbox[2] - label_bbox[0])) // 2
    label_y = height - 40
    draw.text((label_x, label_y), label, fill=COLORS['text'], font=label_font)

    # Save image
    img.save(filename, 'JPEG', quality=85)
    print(f"✓ Created: {filename}")


def main():
    base_path = "/Users/amangly/Documents/prototype-amarta-ai/data/sample_images"

    # Business photos (warung kelontong, toko, kios)
    business_images = [
        ("Warung Kelontong", "Small grocery store front", "business/warung_01.jpg"),
        ("Warung Kelontong", "Store interior with inventory", "business/warung_02.jpg"),
        ("Warung Kelontong", "Display shelves and products", "business/warung_03.jpg"),
        ("Toko Sembako", "Rice and staples store", "business/toko_01.jpg"),
        ("Toko Sembako", "Store front with signage", "business/toko_02.jpg"),
        ("Kios Makanan", "Food stall setup", "business/kios_01.jpg"),
        ("Kios Makanan", "Cooking area and equipment", "business/kios_02.jpg"),
        ("Warung Nasi", "Rice stall with display", "business/nasi_01.jpg"),
        ("Pedagang Sayur", "Vegetable vendor stall", "business/sayur_01.jpg"),
        ("Pedagang Buah", "Fruit vendor display", "business/buah_01.jpg"),
    ]

    # House photos (rumah peminjam)
    house_images = [
        ("Rumah Peminjam", "House exterior front view", "house/rumah_01.jpg"),
        ("Rumah Peminjam", "House side view", "house/rumah_02.jpg"),
        ("Rumah Peminjam", "Living room interior", "house/interior_01.jpg"),
        ("Rumah Peminjam", "Kitchen area", "house/interior_02.jpg"),
        ("Rumah Peminjam", "House with motorcycle", "house/rumah_03.jpg"),
        ("Rumah Peminjam", "House entrance", "house/rumah_04.jpg"),
        ("Rumah Peminjam", "Neighborhood context", "house/rumah_05.jpg"),
        ("Rumah Peminjam", "House with small garden", "house/rumah_06.jpg"),
    ]

    # Field documentation (dokumentasi lapangan)
    field_images = [
        ("Dokumentasi", "Field officer with borrower", "field_documentation/field_visit_01.jpg"),
        ("Dokumentasi", "Business verification photo", "field_documentation/field_visit_02.jpg"),
        ("Dokumentasi", "Group meeting documentation", "field_documentation/group_meeting_01.jpg"),
        ("Dokumentasi", "Loan disbursement photo", "field_documentation/disbursement_01.jpg"),
        ("Dokumentasi", "Repayment collection", "field_documentation/repayment_01.jpg"),
        ("Dokumentasi", "Business training session", "field_documentation/training_01.jpg"),
        ("Dokumentasi", "Community gathering", "field_documentation/community_01.jpg"),
    ]

    print("\n" + "="*60)
    print("  Creating Sample Images for Amarta AI")
    print("="*60 + "\n")

    # Generate business images
    print("📸 Business Photos:")
    for title, subtitle, path in business_images:
        full_path = os.path.join(base_path, path)
        create_placeholder_image(1200, 900, COLORS['business_bg'], title, subtitle, full_path)

    # Generate house images
    print("\n🏠 House Photos:")
    for title, subtitle, path in house_images:
        full_path = os.path.join(base_path, path)
        create_placeholder_image(1200, 900, COLORS['house_bg'], title, subtitle, full_path)

    # Generate field documentation images
    print("\n📋 Field Documentation:")
    for title, subtitle, path in field_images:
        full_path = os.path.join(base_path, path)
        create_placeholder_image(1200, 900, COLORS['field_bg'], title, subtitle, full_path)

    print("\n" + "="*60)
    print(f"✅ Successfully created {len(business_images) + len(house_images) + len(field_images)} sample images")
    print("="*60)
    print(f"\nImages saved to: {base_path}")
    print("\nDirectory structure:")
    print(f"  • {base_path}/business/         - {len(business_images)} business photos")
    print(f"  • {base_path}/house/            - {len(house_images)} house photos")
    print(f"  • {base_path}/field_documentation/ - {len(field_images)} field photos")
    print("\n")


if __name__ == "__main__":
    main()
