import google.generativeai as genai
from typing import Dict, Optional
import json
import re

from utils.config import get_settings
from utils.logger import logger

settings = get_settings()


class GeminiNLPExtractor:
    """Gemini NLP service for extracting insights from field agent notes"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GOOGLE_API_KEY
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)

    async def analyze_field_note(self, note_text: str, borrower_context: Dict) -> Dict:
        """
        Extract insights from field agent notes using Gemini NLP

        Args:
            note_text: Field agent's narrative report
            borrower_context: Borrower information for context

        Returns:
            {
                "extracted_income_estimate": float,
                "sentiment_score": float (0-1),
                "risk_flags": [{"flag": str, "severity": str}],
                "behavioral_insights": {...},
                "key_entities": {...},
                "confidence_score": float (0-1)
            }
        """

        try:
            prompt = self._build_nlp_analysis_prompt(note_text, borrower_context)

            response = self.model.generate_content(prompt)

            analysis = self._parse_nlp_response(response.text)

            logger.info("Gemini NLP analysis completed for field note")

            return analysis

        except Exception as e:
            logger.error(f"Error in Gemini NLP analysis: {e}")
            return self._fallback_nlp_analysis(note_text, borrower_context)

    def _build_nlp_analysis_prompt(self, note_text: str, borrower_context: Dict) -> str:
        """Build comprehensive prompt for field note analysis"""

        prompt = f"""
You are analyzing a field agent's narrative report about a micro-entrepreneur borrower in rural Indonesia for credit assessment.

**Borrower Context:**
- Name: {borrower_context.get('full_name', 'Unknown')}
- Business Type: {borrower_context.get('business_type', 'Unknown')}
- Claimed Monthly Income: Rp {borrower_context.get('claimed_monthly_income', 0):,.0f}
- Years in Business: {borrower_context.get('years_in_business', 'Unknown')} years
- Location: {borrower_context.get('village', '')}, {borrower_context.get('district', '')}

**Field Agent Note:**
{note_text}

Please analyze this note and extract the following information in JSON format:

1. **extracted_income_estimate** (number):
   - Estimate monthly income based on the narrative (in Indonesian Rupiah)
   - Look for mentions of daily income, weekly sales, customer numbers, etc.
   - Calculate realistic estimate considering business type and activity level
   - If unclear, provide a range midpoint

2. **sentiment_score** (0.0 to 1.0):
   - Overall sentiment of the narrative
   - 0.0-0.3: Negative (concerns, problems, reluctance)
   - 0.4-0.6: Neutral (factual, mixed)
   - 0.7-1.0: Positive (optimistic, cooperative, stable)

3. **risk_flags** (array of objects):
   - Identify concerning indicators: [{"flag": "description", "severity": "low|medium|high"}]
   - Examples: irregular_income, no_financial_records, family_financial_pressure, business_challenges, debt_concerns, health_issues, unstable_secondary_income

4. **behavioral_insights** (object):
   - cooperation_level: "low|medium|high" (how cooperative is the borrower)
   - transparency: "low|medium|high" (how open about business details)
   - business_knowledge: "weak|basic|good|strong" (understanding of their business)
   - financial_planning: "weak|basic|good|strong" (financial management capability)
   - trustworthiness: "low|medium|high" (overall trustworthiness impression)

5. **key_entities** (object):
   Extract and structure:
   - daily_income_mentions: [amounts mentioned]
   - weekly_income_mentions: [amounts mentioned]
   - production_volumes: [specific quantities]
   - customer_base_indicators: [customer numbers, frequency]
   - asset_requests: [what they want to buy/improve]
   - family_situation: [relevant family info]
   - business_challenges: [problems mentioned]
   - business_strengths: [positive indicators]

6. **income_consistency_indicators** (object):
   - has_regular_customers: true/false
   - income_pattern: "stable|seasonal|irregular"
   - cash_flow_description: brief assessment

7. **confidence_score** (0.0 to 1.0):
   - Your confidence in this analysis
   - Based on clarity and detail of the note

Respond ONLY with valid JSON format. Be objective and base your assessment strictly on the text provided.
"""

        return prompt

    def _parse_nlp_response(self, response_text: str) -> Dict:
        """Parse Gemini NLP API response"""

        try:
            # Extract JSON from response
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
            logger.error(f"Error parsing Gemini NLP response: {e}")
            logger.debug(f"Response text: {response_text}")

            # Try regex extraction as fallback
            return self._regex_extraction_fallback(response_text)

    def _regex_extraction_fallback(self, note_text: str) -> Dict:
        """Fallback: Use regex to extract basic information"""

        # Try to find income mentions
        income_pattern = r'Rp\s?(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)'
        income_matches = re.findall(income_pattern, note_text)

        extracted_income = 0
        if income_matches:
            # Take the largest number as likely monthly income
            amounts = [float(m.replace('.', '').replace(',', '')) for m in income_matches]
            extracted_income = max(amounts)

        # Sentiment based on keywords
        positive_keywords = ['kooperatif', 'ramai', 'stabil', 'bagus', 'baik', 'tertata', 'rapi', 'loyal']
        negative_keywords = ['sepi', 'susah', 'sulit', 'rusak', 'tidak', 'belum', 'kurang']

        positive_count = sum(1 for word in positive_keywords if word in note_text.lower())
        negative_count = sum(1 for word in negative_keywords if word in note_text.lower())

        if positive_count > negative_count:
            sentiment = 0.7
        elif negative_count > positive_count:
            sentiment = 0.4
        else:
            sentiment = 0.55

        return {
            "extracted_income_estimate": extracted_income,
            "sentiment_score": sentiment,
            "risk_flags": [],
            "behavioral_insights": {
                "cooperation_level": "medium",
                "transparency": "medium",
                "business_knowledge": "basic",
                "financial_planning": "basic",
                "trustworthiness": "medium"
            },
            "key_entities": {
                "income_mentions": income_matches[:3] if income_matches else [],
                "extracted_method": "regex_fallback"
            },
            "confidence_score": 0.40,
            "fallback": True
        }

    def _fallback_nlp_analysis(self, note_text: str, borrower_context: Dict) -> Dict:
        """Fallback NLP analysis when Gemini API fails"""

        claimed_income = borrower_context.get('claimed_monthly_income', 3000000)

        return {
            "extracted_income_estimate": claimed_income * 0.9,  # Slightly lower than claimed
            "sentiment_score": 0.60,
            "risk_flags": [
                {"flag": "api_unavailable", "severity": "low"}
            ],
            "behavioral_insights": {
                "cooperation_level": "medium",
                "transparency": "medium",
                "business_knowledge": "basic",
                "financial_planning": "basic",
                "trustworthiness": "medium"
            },
            "key_entities": {},
            "income_consistency_indicators": {
                "has_regular_customers": True,
                "income_pattern": "irregular",
                "cash_flow_description": "Unable to analyze"
            },
            "confidence_score": 0.50,
            "fallback": True,
            "raw_analysis": "Fallback analysis - NLP API unavailable"
        }

    def calculate_nlp_score_adjustment(self, nlp_results: Dict) -> float:
        """
        Calculate credit score adjustment based on NLP analysis

        Returns: Score adjustment (-15 to +15 points)
        """

        adjustment = 0.0

        # Sentiment impact (+/- 5 points)
        sentiment = nlp_results.get('sentiment_score', 0.6)
        if sentiment >= 0.8:
            adjustment += 5
        elif sentiment >= 0.7:
            adjustment += 3
        elif sentiment >= 0.5:
            adjustment += 0
        else:
            adjustment -= 3

        # Behavioral insights (+/- 6 points)
        behavioral = nlp_results.get('behavioral_insights', {})

        cooperation = behavioral.get('cooperation_level', 'medium')
        if cooperation == 'high':
            adjustment += 2
        elif cooperation == 'low':
            adjustment -= 2

        transparency = behavioral.get('transparency', 'medium')
        if transparency == 'high':
            adjustment += 2
        elif transparency == 'low':
            adjustment -= 2

        financial_planning = behavioral.get('financial_planning', 'basic')
        if financial_planning in ['good', 'strong']:
            adjustment += 2
        elif financial_planning == 'weak':
            adjustment -= 2

        # Risk flags impact (- 4 points max)
        risk_flags = nlp_results.get('risk_flags', [])
        high_severity_flags = [f for f in risk_flags if f.get('severity') == 'high']
        medium_severity_flags = [f for f in risk_flags if f.get('severity') == 'medium']

        adjustment -= len(high_severity_flags) * 2
        adjustment -= len(medium_severity_flags) * 1

        # Confidence factor
        confidence = nlp_results.get('confidence_score', 0.7)
        adjustment = adjustment * confidence

        return round(adjustment, 2)
