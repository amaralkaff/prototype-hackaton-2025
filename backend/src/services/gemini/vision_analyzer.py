import google.generativeai as genai
from typing import Dict, Optional
import json
from pathlib import Path

from utils.config import get_settings
from utils.logger import logger

settings = get_settings()


class GeminiVisionAnalyzer:
    """Gemini Vision API service for analyzing business/house photos"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GOOGLE_API_KEY
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(settings.GEMINI_VISION_MODEL)

    async def analyze_business_photo(self, image_path: str, photo_type: str, borrower_context: Dict = None) -> Dict:
        """
        Analyze business photo using Gemini Vision

        Args:
            image_path: Path to the image file
            photo_type: Type of photo (business_exterior, business_interior, inventory, etc.)
            borrower_context: Additional context about the borrower

        Returns:
            {
                "business_scale": "small|medium|large",
                "inventory_density": "low|moderate|high",
                "asset_quality": "poor|fair|good|excellent",
                "socioeconomic_indicators": {...},
                "estimated_value_range": "Rp X - Y",
                "confidence_score": float (0-1),
                "raw_analysis": str
            }
        """

        try:
            prompt = self._build_business_photo_prompt(photo_type, borrower_context)

            # Load image
            image_data = Path(image_path).read_bytes()

            # Generate analysis
            response = self.model.generate_content([
                {"mime_type": "image/jpeg", "data": image_data},
                prompt
            ])

            # Parse response
            analysis = self._parse_vision_response(response.text, "business")

            logger.info(f"Gemini Vision analysis completed for {photo_type}")

            return analysis

        except Exception as e:
            logger.error(f"Error in Gemini Vision analysis: {e}")
            return self._fallback_business_analysis(photo_type)

    async def analyze_house_photo(self, image_path: str, photo_type: str, borrower_context: Dict = None) -> Dict:
        """
        Analyze house photo using Gemini Vision

        Returns:
            {
                "housing_condition": "poor|basic|adequate|good",
                "visible_assets": [...],
                "living_standard": "lower|lower-middle|middle",
                "socioeconomic_indicators": {...},
                "confidence_score": float (0-1)
            }
        """

        try:
            prompt = self._build_house_photo_prompt(photo_type, borrower_context)

            # Load image
            image_data = Path(image_path).read_bytes()

            # Generate analysis
            response = self.model.generate_content([
                {"mime_type": "image/jpeg", "data": image_data},
                prompt
            ])

            # Parse response
            analysis = self._parse_vision_response(response.text, "house")

            logger.info(f"Gemini Vision analysis completed for house photo")

            return analysis

        except Exception as e:
            logger.error(f"Error in Gemini Vision house analysis: {e}")
            return self._fallback_house_analysis(photo_type)

    def _build_business_photo_prompt(self, photo_type: str, borrower_context: Dict = None) -> str:
        """Build comprehensive prompt for business photo analysis"""

        context_str = ""
        if borrower_context:
            context_str = f"""
Borrower Context:
- Business Type: {borrower_context.get('business_type', 'Unknown')}
- Claimed Monthly Income: Rp {borrower_context.get('claimed_monthly_income', 0):,.0f}
- Location: {borrower_context.get('village', '')}, {borrower_context.get('district', '')}
"""

        prompt = f"""
You are analyzing a photo of a micro-business in rural Indonesia for credit assessment purposes.

Photo Type: {photo_type}
{context_str}

Please analyze this image and provide a structured JSON assessment with the following information:

1. **business_scale**: Estimate the size (small/medium/large for micro-businesses)
   - small: Very small operation, minimal visible assets, home-based
   - medium: Established small business, visible inventory, dedicated space
   - large: Larger micro-enterprise, substantial inventory, good infrastructure

2. **inventory_density**: Assess visible stock levels
   - low: Minimal stock visible, sparse shelves
   - moderate: Decent stock, organized display
   - high: Well-stocked, abundant inventory

3. **asset_quality**: Evaluate equipment and space condition
   - poor: Deteriorating, makeshift equipment
   - fair: Basic but functional equipment
   - good: Well-maintained, quality equipment
   - excellent: Modern, premium equipment

4. **socioeconomic_indicators**: Detailed observations including:
   - building_condition: State of the physical structure
   - equipment_modernity: Age and quality of tools/equipment
   - organization_level: How well-organized the space is
   - cleanliness: Hygiene and maintenance standards
   - signage_quality: Professional vs handwritten signs
   - visible_inventory_items: List specific items you can identify

5. **estimated_value_range**: Rough estimate of total business asset value in Indonesian Rupiah (e.g., "Rp 5M - 10M")

6. **credit_relevant_observations**: Any factors that might indicate:
   - Business robustness and sustainability
   - Cash flow indicators
   - Growth potential
   - Risk factors

7. **confidence_score**: Your confidence in this analysis (0.0 to 1.0)

Please respond ONLY with valid JSON format. Be objective and specific in your observations.
"""

        return prompt

    def _build_house_photo_prompt(self, photo_type: str, borrower_context: Dict = None) -> str:
        """Build prompt for house photo analysis"""

        prompt = f"""
You are analyzing a photo of a borrower's house in rural Indonesia for credit assessment purposes.

Photo Type: {photo_type}

Please analyze this image and provide a structured JSON assessment:

1. **housing_condition**: Overall state of the residence
   - poor: Significant deterioration, basic materials
   - basic: Simple structure, minimal amenities
   - adequate: Decent condition, standard materials
   - good: Well-maintained, quality construction

2. **visible_assets**: List any valuable items or infrastructure you can identify:
   - Appliances (TV, refrigerator, etc.)
   - Furniture quality
   - Vehicles or motorcycles
   - Building materials (brick, concrete, etc.)

3. **living_standard**: Estimated socioeconomic level
   - lower: Very basic living conditions
   - lower-middle: Simple but adequate conditions
   - middle: Comfortable living conditions

4. **socioeconomic_indicators**:
   - building_materials: What the house is made of
   - roof_condition: Quality and state of the roof
   - windows_doors_quality: Condition of openings
   - visible_amenities: What facilities are visible
   - surrounding_environment: Neighborhood condition

5. **area_size_estimate**: Rough estimate of house size in square meters

6. **confidence_score**: Your confidence in this analysis (0.0 to 1.0)

Respond ONLY with valid JSON format.
"""

        return prompt

    def _parse_vision_response(self, response_text: str, analysis_type: str) -> Dict:
        """Parse Gemini Vision API response"""

        try:
            # Try to extract JSON from response
            # Sometimes the model wraps JSON in markdown code blocks
            if "```json" in response_text:
                json_start = response_text.index("```json") + 7
                json_end = response_text.index("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.index("```") + 3
                json_end = response_text.index("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            else:
                json_str = response_text

            parsed = json.loads(json_str)
            parsed['raw_analysis'] = response_text

            return parsed

        except Exception as e:
            logger.error(f"Error parsing Gemini Vision response: {e}")
            logger.debug(f"Response text: {response_text}")

            # Return structured fallback
            if analysis_type == "business":
                return self._fallback_business_analysis("unknown")
            else:
                return self._fallback_house_analysis("unknown")

    def _fallback_business_analysis(self, photo_type: str) -> Dict:
        """Fallback business analysis when Vision API fails"""
        return {
            "business_scale": "small",
            "inventory_density": "moderate",
            "asset_quality": "fair",
            "socioeconomic_indicators": {
                "building_condition": "basic",
                "equipment_modernity": "standard",
                "organization_level": "moderate",
                "cleanliness": "adequate",
                "signage_quality": "basic"
            },
            "estimated_value_range": "Rp 3M - 8M",
            "confidence_score": 0.50,
            "raw_analysis": "Fallback analysis - Vision API unavailable",
            "fallback": True
        }

    def _fallback_house_analysis(self, photo_type: str) -> Dict:
        """Fallback house analysis when Vision API fails"""
        return {
            "housing_condition": "basic",
            "visible_assets": ["basic furniture", "standard walls"],
            "living_standard": "lower-middle",
            "socioeconomic_indicators": {
                "building_materials": "mixed brick and wood",
                "roof_condition": "adequate",
                "windows_doors_quality": "standard",
                "visible_amenities": "basic",
                "surrounding_environment": "rural residential"
            },
            "area_size_estimate": "40-60 sqm",
            "confidence_score": 0.50,
            "fallback": True
        }

    def calculate_vision_score_adjustment(self, vision_results: Dict, photo_type: str) -> float:
        """
        Calculate credit score adjustment based on vision analysis

        Returns: Score adjustment (-15 to +15 points)
        """

        adjustment = 0.0

        # Business scale impact (+/- 5 points)
        business_scale = vision_results.get('business_scale', 'small')
        if business_scale == 'large':
            adjustment += 5
        elif business_scale == 'medium':
            adjustment += 2
        elif business_scale == 'small':
            adjustment += 0

        # Inventory density (+/- 3 points)
        inventory = vision_results.get('inventory_density', 'moderate')
        if inventory == 'high':
            adjustment += 3
        elif inventory == 'moderate':
            adjustment += 1

        # Asset quality (+/- 5 points)
        asset_quality = vision_results.get('asset_quality', 'fair')
        if asset_quality == 'excellent':
            adjustment += 5
        elif asset_quality == 'good':
            adjustment += 3
        elif asset_quality == 'fair':
            adjustment += 1
        elif asset_quality == 'poor':
            adjustment -= 2

        # Housing condition (for house photos) (+/- 4 points)
        housing = vision_results.get('housing_condition')
        if housing:
            if housing == 'good':
                adjustment += 4
            elif housing == 'adequate':
                adjustment += 2
            elif housing == 'basic':
                adjustment += 0
            elif housing == 'poor':
                adjustment -= 3

        # Confidence factor
        confidence = vision_results.get('confidence_score', 0.7)
        adjustment = adjustment * confidence

        return round(adjustment, 2)
