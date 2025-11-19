# Sample Images for Amarta AI Credit Scoring

This directory contains sample images for demonstrating the multimodal credit scoring system.

## Directory Structure

```
sample_images/
├── business/                # Business photos (warung, toko, kios)
├── house/                   # Borrower house photos
└── field_documentation/     # Field officer documentation
```

## Image Categories

### 📸 Business Photos (14 images)

Photos of micro-businesses for Gemini Vision analysis:

**Real Photos from Unsplash:**
- `warung_01.jpg` - Indonesian warung kelontong storefront
- `restaurant_01.jpg` - Small restaurant interior with seating
- `market_stall_01.jpg` - Traditional market vendor stall
- `grocery_store_01.jpg` - Small neighborhood grocery store
- `food_stall_01.jpg` - Street food vendor stall

**Generated Placeholders:**
- `warung_02.jpg`, `warung_03.jpg` - Additional warung samples
- `toko_01.jpg`, `toko_02.jpg` - Rice and staples stores
- `kios_01.jpg`, `kios_02.jpg` - Food kiosk setups
- `nasi_01.jpg` - Rice stall display
- `sayur_01.jpg` - Vegetable vendor stall
- `buah_01.jpg` - Fruit vendor display

**Vision Analysis Indicators:**
- Business scale (small/medium/large inventory)
- Inventory density and variety
- Asset quality (equipment, displays)
- Store condition and organization
- Customer flow and accessibility

### 🏠 House Photos (14 images)

Photos of borrower residences for socioeconomic analysis:

**Real Photos from Unsplash:**
- `house_01.jpg` - Asian residential house exterior
- `house_02.jpg` - Modern house with good construction
- `interior_01.jpg` - Living room with furniture
- `kitchen_01.jpg` - Kitchen area setup

**Generated Placeholders:**
- `rumah_01.jpg` through `rumah_06.jpg` - Various house exteriors
- `interior_02.jpg` - Additional interior view

**Vision Analysis Indicators:**
- Housing condition and construction quality
- Visible assets (furniture, appliances, vehicles)
- Living standards and maintenance
- Neighborhood context
- Property size and features

### 📋 Field Documentation (10 images)

Photos from field officer visits and activities:

**Real Photos from Unsplash:**
- `meeting_01.jpg` - Business consultation meeting
- `discussion_01.jpg` - Group discussion setting
- `field_work_01.jpg` - Field officer documentation

**Generated Placeholders:**
- `field_visit_01.jpg`, `field_visit_02.jpg` - Field officer with borrower
- `group_meeting_01.jpg` - Community group meeting
- `disbursement_01.jpg` - Loan disbursement documentation
- `repayment_01.jpg` - Repayment collection
- `training_01.jpg` - Business training session
- `community_01.jpg` - Community gathering

**Documentation Types:**
- Borrower verification photos
- Business validation evidence
- Group meeting attendance
- Loan disbursement records
- Repayment collection proof

## Usage in Credit Scoring

### Gemini Vision Analysis

The `GeminiVisionAnalyzer` service processes these images to extract:

**From Business Photos:**
```python
{
    "business_scale": "small|medium|large",
    "inventory_density": 0-10 scale,
    "asset_quality": 0-10 scale,
    "estimated_monthly_revenue": Rp amount,
    "visible_customers": boolean,
    "store_condition": "poor|fair|good|excellent"
}
```

**From House Photos:**
```python
{
    "housing_condition": "poor|fair|good|excellent",
    "visible_assets": ["tv", "fridge", "motorcycle", ...],
    "living_standard": 0-10 scale,
    "estimated_household_income": Rp amount
}
```

### Score Adjustment

Vision analysis provides **±15 points** adjustment to baseline credit score:
- **Positive indicators**: Good business scale, quality assets, maintained property → +15 points
- **Neutral**: Average conditions → 0 points
- **Negative indicators**: Poor conditions, minimal inventory → -15 points

### API Integration

To enable photo analysis in credit assessment:

```python
# Backend API call
POST /api/v1/credit-scoring/assess
{
    "borrower_id": "uuid",
    "include_photos": true,  # Enable vision analysis
    "include_field_notes": false,
    "save_to_database": true
}
```

## Image Sources

**Real Photos:**
- Source: [Unsplash](https://unsplash.com) - Free stock photos
- License: Unsplash License (Free to use)
- Purpose: Demonstration and testing only

**Generated Placeholders:**
- Created with: Python PIL/Pillow
- Purpose: Fill gaps in demonstration dataset

## Production Notes

⚠️ **Important for Production:**

1. **Replace with Actual Photos**: Use real field photos from Amartha operations
2. **Privacy Compliance**: Ensure borrower consent for photo usage
3. **Data Security**: Store photos securely with proper encryption
4. **Quality Standards**:
   - Minimum resolution: 800x600 pixels
   - Format: JPEG (for smaller file sizes)
   - Clear, well-lit photos for better AI analysis
5. **Photo Guidelines**:
   - Business: Show storefront, inventory, interior
   - House: Exterior, living room, assets (with permission)
   - Field: Clear documentation of activities

## Regenerating Sample Images

To regenerate placeholder images:

```bash
cd /Users/amangly/Documents/prototype-amarta-ai/data
python3 generate_sample_images.py
```

To download fresh stock photos:

```bash
cd /Users/amangly/Documents/prototype-amarta-ai
python3 download_real_images.py
```

## Testing Vision Analysis

Test the Gemini Vision analyzer with sample images:

```python
from services.gemini.vision_analyzer import GeminiVisionAnalyzer

analyzer = GeminiVisionAnalyzer()

# Analyze business photo
business_result = await analyzer.analyze_business_photo(
    photo_url="file:///path/to/sample_images/business/warung_01.jpg"
)

# Analyze house photo
house_result = await analyzer.analyze_house_photo(
    photo_url="file:///path/to/sample_images/house/house_01.jpg"
)
```

## File Statistics

- **Total Images**: 36 photos
- **Business Photos**: 14 images
- **House Photos**: 14 images
- **Field Documentation**: 10 images
- **Total Size**: ~3.5 MB (compressed JPEGs)

---

**Note**: These sample images are for MVP demonstration purposes. In production, use actual field photographs from Amartha's microfinance operations with proper consent and security measures.
