from typing import Dict, List, Optional
from decimal import Decimal
import google.generativeai as genai

from services.ml_model.credit_risk_model import CreditRiskModel
from services.gemini.vision_analyzer import GeminiVisionAnalyzer
from services.gemini.nlp_extractor import GeminiNLPExtractor
from utils.config import get_settings
from utils.logger import logger

settings = get_settings()


class AdaptiveScoringEngine:
    """
    Main orchestration engine for multimodal credit scoring

    Combines:
    1. ML baseline prediction
    2. Gemini Vision analysis
    3. Gemini NLP extraction
    4. Adaptive score fusion
    """

    def __init__(self):
        self.ml_model = CreditRiskModel(settings.ML_MODEL_PATH)
        self.vision_analyzer = GeminiVisionAnalyzer()
        self.nlp_extractor = GeminiNLPExtractor()

        # Configure Gemini for explanation generation
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.explanation_model = genai.GenerativeModel(settings.GEMINI_MODEL)

    async def assess_borrower(
        self,
        borrower_data: Dict,
        photos: List[Dict] = None,
        field_notes: List[Dict] = None,
        options: Dict = None
    ) -> Dict:
        """
        Perform comprehensive multimodal credit assessment

        Args:
            borrower_data: Borrower information and history
            photos: List of photo records with paths
            field_notes: List of field agent notes
            options: Assessment options (include_vision, include_nlp)

        Returns:
            Complete credit assessment with all scores and explanations
        """

        options = options or {}
        include_vision = options.get('include_vision', True)
        include_nlp = options.get('include_nlp', True)

        logger.info(f"Starting assessment for borrower {borrower_data.get('id', 'unknown')}")

        # Step 1: ML Baseline Prediction
        ml_result = self.ml_model.predict(borrower_data)
        logger.info(f"ML baseline score: {ml_result['baseline_score']}")

        # Step 2: Vision Analysis (if photos available)
        vision_result = None
        vision_adjustment = 0.0
        vision_confidence = 0.0

        if include_vision and photos:
            vision_result = await self._analyze_photos(photos, borrower_data)
            vision_adjustment = vision_result.get('score_adjustment', 0.0)
            vision_confidence = vision_result.get('confidence', 0.7)
            logger.info(f"Vision adjustment: {vision_adjustment:+.2f} points")

        # Step 3: NLP Analysis (if field notes available)
        nlp_result = None
        nlp_adjustment = 0.0
        nlp_confidence = 0.0

        if include_nlp and field_notes:
            nlp_result = await self._analyze_field_notes(field_notes, borrower_data)
            nlp_adjustment = nlp_result.get('score_adjustment', 0.0)
            nlp_confidence = nlp_result.get('confidence', 0.7)
            logger.info(f"NLP adjustment: {nlp_adjustment:+.2f} points")

        # Step 4: Fuse Scores
        final_score = self._fuse_scores(
            ml_result['baseline_score'],
            vision_adjustment,
            nlp_adjustment
        )

        risk_category = self._categorize_risk(final_score)

        # Step 5: Income Validation
        income_validation = self._validate_income(
            claimed_income=borrower_data.get('claimed_monthly_income', 0),
            nlp_result=nlp_result,
            vision_result=vision_result,
            borrower_data=borrower_data
        )

        # Step 6: Loan Recommendation
        loan_recommendation = self._recommend_loan(
            final_score=final_score,
            risk_category=risk_category,
            income_validation=income_validation,
            borrower_data=borrower_data
        )

        # Step 7: Generate Risk Explanation
        risk_explanation = await self._generate_risk_explanation(
            borrower_data=borrower_data,
            ml_result=ml_result,
            vision_result=vision_result,
            nlp_result=nlp_result,
            final_score=final_score,
            risk_category=risk_category
        )

        # Step 8: Extract Risk Factors
        risk_factors, positive_factors = self._extract_factors(
            borrower_data, ml_result, vision_result, nlp_result
        )

        # Compile complete assessment
        assessment = {
            "borrower_id": borrower_data.get('id'),
            "ml_baseline_score": round(ml_result['baseline_score'], 2),
            "ml_model_version": ml_result['model_version'],
            "ml_features_used": borrower_data,
            "vision_score_adjustment": round(vision_adjustment, 2),
            "vision_confidence": round(vision_confidence, 2),
            "vision_insights": vision_result.get('insights') if vision_result else None,
            "nlp_score_adjustment": round(nlp_adjustment, 2),
            "nlp_confidence": round(nlp_confidence, 2),
            "nlp_insights": nlp_result.get('insights') if nlp_result else None,
            "final_credit_score": round(final_score, 2),
            "risk_category": risk_category,
            "income_validation": income_validation,
            "loan_recommendation": loan_recommendation,
            "risk_explanation": risk_explanation,
            "risk_factors": risk_factors,
            "positive_factors": positive_factors,
            "model_version": "1.0.0"
        }

        logger.info(f"Assessment complete. Final score: {final_score:.2f}, Risk: {risk_category}")

        return assessment

    async def _analyze_photos(self, photos: List[Dict], borrower_data: Dict) -> Dict:
        """Analyze all photos and aggregate insights"""

        all_analyses = []
        total_adjustment = 0.0

        for photo in photos:
            photo_path = photo.get('storage_path') or photo.get('photo_url')
            photo_type = photo.get('photo_type')

            if 'house' in photo_type:
                analysis = await self.vision_analyzer.analyze_house_photo(
                    photo_path, photo_type, borrower_data
                )
            else:
                analysis = await self.vision_analyzer.analyze_business_photo(
                    photo_path, photo_type, borrower_data
                )

            adjustment = self.vision_analyzer.calculate_vision_score_adjustment(
                analysis, photo_type
            )

            total_adjustment += adjustment
            all_analyses.append(analysis)

        # Average adjustment across all photos
        avg_adjustment = total_adjustment / len(photos) if photos else 0.0

        # Aggregate insights
        insights = {
            "num_photos_analyzed": len(photos),
            "analyses": all_analyses,
            "summary": self._summarize_vision_insights(all_analyses)
        }

        return {
            "score_adjustment": avg_adjustment,
            "confidence": sum(a.get('confidence_score', 0.7) for a in all_analyses) / len(all_analyses),
            "insights": insights
        }

    async def _analyze_field_notes(self, field_notes: List[Dict], borrower_data: Dict) -> Dict:
        """Analyze all field notes and aggregate insights"""

        all_analyses = []
        total_adjustment = 0.0

        for note in field_notes:
            note_text = note.get('note_text', '')

            analysis = await self.nlp_extractor.analyze_field_note(
                note_text, borrower_data
            )

            adjustment = self.nlp_extractor.calculate_nlp_score_adjustment(analysis)

            total_adjustment += adjustment
            all_analyses.append(analysis)

        # Average adjustment
        avg_adjustment = total_adjustment / len(field_notes) if field_notes else 0.0

        # Aggregate insights
        insights = {
            "num_notes_analyzed": len(field_notes),
            "analyses": all_analyses,
            "summary": self._summarize_nlp_insights(all_analyses)
        }

        return {
            "score_adjustment": avg_adjustment,
            "confidence": sum(a.get('confidence_score', 0.7) for a in all_analyses) / len(all_analyses),
            "insights": insights
        }

    def _fuse_scores(self, baseline: float, vision_adj: float, nlp_adj: float) -> float:
        """
        Fuse ML baseline with Vision and NLP adjustments

        Formula: Final = Baseline + (Vision_Adj * 0.5) + (NLP_Adj * 0.5)
        """

        final = baseline + (vision_adj * 0.5) + (nlp_adj * 0.5)

        # Cap between 0-100
        final = max(0, min(100, final))

        return final

    def _categorize_risk(self, score: float) -> str:
        """Categorize risk based on final credit score"""
        if score >= 75:
            return "low"
        elif score >= 55:
            return "medium"
        elif score >= 35:
            return "high"
        else:
            return "very_high"

    def _validate_income(
        self,
        claimed_income: float,
        nlp_result: Optional[Dict],
        vision_result: Optional[Dict],
        borrower_data: Dict
    ) -> Dict:
        """Compare claimed income with AI-estimated income"""

        # Estimate from NLP
        nlp_estimate = 0
        if nlp_result:
            analyses = nlp_result.get('insights', {}).get('analyses', [])
            if analyses:
                estimates = [a.get('extracted_income_estimate', 0) for a in analyses]
                nlp_estimate = sum(e for e in estimates if e > 0) / len([e for e in estimates if e > 0]) if any(e > 0 for e in estimates) else 0

        # Estimate from vision (business scale based)
        vision_estimate = claimed_income * 0.85  # Default conservative estimate
        if vision_result:
            analyses = vision_result.get('insights', {}).get('analyses', [])
            for analysis in analyses:
                scale = analysis.get('business_scale', 'small')
                if scale == 'large':
                    vision_estimate = claimed_income * 1.1
                elif scale == 'medium':
                    vision_estimate = claimed_income * 0.95

        # Estimate from business type benchmarks
        business_type = borrower_data.get('business_type', '')
        benchmark_estimate = self._get_benchmark_income(business_type)

        # Weighted average
        weights = []
        estimates = []

        if nlp_estimate > 0:
            estimates.append(nlp_estimate)
            weights.append(0.40)

        if vision_estimate > 0:
            estimates.append(vision_estimate)
            weights.append(0.35)

        if benchmark_estimate > 0:
            estimates.append(benchmark_estimate)
            weights.append(0.25)

        if estimates:
            ai_estimate = sum(e * w for e, w in zip(estimates, weights)) / sum(weights)
        else:
            ai_estimate = claimed_income * 0.85

        # Calculate variance
        variance = ((claimed_income - ai_estimate) / ai_estimate) * 100 if ai_estimate > 0 else 0

        # Consistency score
        consistency_score = max(0, 100 - abs(variance))

        assessment = "Income claim appears consistent with AI estimate"
        if variance > 30:
            assessment = "Claimed income significantly higher than AI estimate - verify carefully"
        elif variance > 15:
            assessment = "Claimed income moderately higher than AI estimate"
        elif variance < -15:
            assessment = "Claimed income lower than AI estimate - borrower may be conservative"

        return {
            "claimed_income": round(claimed_income, 2),
            "ai_estimated_income": round(ai_estimate, 2),
            "income_consistency_score": round(consistency_score, 2),
            "variance_percentage": round(variance, 2),
            "assessment": assessment
        }

    def _get_benchmark_income(self, business_type: str) -> float:
        """Get typical income range for business type"""

        benchmarks = {
            "Warung Kelontong": 3500000,
            "Warung Gorengan": 2500000,
            "Jahit Pakaian": 3000000,
            "Jualan Sayur": 2000000,
            "Catering": 4500000,
            "Salon": 3000000,
            "Toko Pulsa": 3200000,
            "Warung Nasi": 3800000,
            "Industri Kerupuk": 2800000,
        }

        for key, value in benchmarks.items():
            if key in business_type:
                return value

        return 3000000  # Default

    def _recommend_loan(
        self,
        final_score: float,
        risk_category: str,
        income_validation: Dict,
        borrower_data: Dict
    ) -> Dict:
        """Recommend optimal loan amount and terms"""

        monthly_income = income_validation['ai_estimated_income']

        # Safe repayment rate based on risk
        safe_rates = {
            "low": 0.30,      # 30% of monthly income
            "medium": 0.25,   # 25%
            "high": 0.20,     # 20%
            "very_high": 0.15 # 15%
        }

        safe_rate = safe_rates.get(risk_category, 0.20)

        # Loan sizing based on risk
        if risk_category == "low":
            max_loan = monthly_income * 3.0
            term_weeks = 24
        elif risk_category == "medium":
            max_loan = monthly_income * 2.0
            term_weeks = 20
        elif risk_category == "high":
            max_loan = monthly_income * 1.0
            term_weeks = 16
        else:
            max_loan = monthly_income * 0.5
            term_weeks = 12

        # Conservative recommendation (80% of max)
        recommended_loan = max_loan * 0.8

        # Weekly repayment
        weekly_repayment = recommended_loan / term_weeks

        # Repayment to income ratio
        monthly_repayment = weekly_repayment * 4.3
        repayment_ratio = (monthly_repayment / monthly_income) * 100

        # Confidence based on consistency
        consistency = income_validation['income_consistency_score']
        confidence = (consistency / 100) * 0.7 + 0.3  # 0.3 to 1.0

        # Justification
        justification = f"Based on {risk_category} risk profile and estimated monthly income of Rp {monthly_income:,.0f}, " \
                       f"safe repayment capacity is approximately {safe_rate*100:.0f}% of income (Rp {monthly_income * safe_rate:,.0f}/month). " \
                       f"Recommended loan of Rp {recommended_loan:,.0f} over {term_weeks} weeks results in weekly payments of Rp {weekly_repayment:,.0f}, " \
                       f"which is {repayment_ratio:.1f}% of monthly income - within safe lending parameters."

        return {
            "recommended_loan_amount": round(recommended_loan, 2),
            "max_safe_loan_amount": round(max_loan, 2),
            "recommended_term_weeks": term_weeks,
            "weekly_repayment": round(weekly_repayment, 2),
            "repayment_to_income_ratio": round(repayment_ratio, 2),
            "recommendation_confidence": round(confidence, 2),
            "justification": justification
        }

    async def _generate_risk_explanation(
        self,
        borrower_data: Dict,
        ml_result: Dict,
        vision_result: Optional[Dict],
        nlp_result: Optional[Dict],
        final_score: float,
        risk_category: str
    ) -> str:
        """Generate human-readable risk explanation using Gemini"""

        try:
            prompt = f"""
You are a credit analyst explaining credit assessment results to field agents at Amartha, a microfinance institution in Indonesia.

**Borrower Profile:**
- Name: {borrower_data.get('full_name')}
- Business: {borrower_data.get('business_type')}
- Claimed Income: Rp {borrower_data.get('claimed_monthly_income', 0):,.0f}/month
- Years in Business: {borrower_data.get('years_in_business')} years

**Credit Assessment Results:**
- ML Baseline Score: {ml_result.get('baseline_score')}/100
- Vision Analysis Adjustment: {vision_result.get('score_adjustment', 0) if vision_result else 'N/A'}
- NLP Analysis Adjustment: {nlp_result.get('score_adjustment', 0) if nlp_result else 'N/A'}
- Final Credit Score: {final_score}/100
- Risk Category: {risk_category.upper()}

**Additional Context:**
- Financial Literacy Score: {borrower_data.get('financial_literacy_score', 'N/A')}/100
- Has Bank Account: {borrower_data.get('has_bank_account', False)}
- Keeps Records: {borrower_data.get('keeps_financial_records', False)}

Please write a clear, 2-3 paragraph explanation in Indonesian (Bahasa Indonesia) that:
1. Summarizes the borrower's creditworthiness
2. Highlights key positive factors
3. Points out any risk factors to monitor
4. Provides a balanced recommendation

Keep it professional but accessible to field agents. Focus on practical insights.
"""

            response = self.explanation_model.generate_content(prompt)
            explanation = response.text.strip()

            return explanation

        except Exception as e:
            logger.error(f"Error generating risk explanation: {e}")
            return self._fallback_explanation(borrower_data, final_score, risk_category)

    def _fallback_explanation(self, borrower_data: Dict, final_score: float, risk_category: str) -> str:
        """Fallback explanation when Gemini is unavailable"""

        name = borrower_data.get('full_name', 'Peminjam')
        business = borrower_data.get('business_type', 'usaha')
        score = final_score

        if risk_category == "low":
            return f"{name} menunjukkan profil kredit yang baik dengan skor {score:.1f}/100. " \
                   f"Riwayat pembayaran stabil, usaha {business} sudah berjalan dengan baik, dan menunjukkan perilaku keuangan yang bertanggung jawab. " \
                   f"Rekomendasi: Approve dengan jumlah pinjaman sesuai kapasitas."

        elif risk_category == "medium":
            return f"{name} memiliki profil risiko menengah dengan skor {score:.1f}/100. " \
                   f"Usaha {business} cukup stabil namun ada beberapa area yang perlu diperhatikan seperti pencatatan keuangan atau riwayat pembayaran. " \
                   f"Rekomendasi: Approve dengan monitoring ketat dan pinjaman konservatif."

        else:
            return f"{name} menunjukkan risiko tinggi dengan skor {score:.1f}/100. " \
                   f"Terdapat beberapa indikator risiko pada usaha {business} yang perlu evaluasi lebih lanjut. " \
                   f"Rekomendasi: Pertimbangkan dengan hati-hati, pinjaman minimal dengan pendampingan intensif."

    def _extract_factors(self, borrower_data: Dict, ml_result: Dict, vision_result: Optional[Dict], nlp_result: Optional[Dict]) -> tuple:
        """Extract risk and positive factors from all analyses"""

        risk_factors = []
        positive_factors = []

        # From borrower data
        if not borrower_data.get('has_bank_account'):
            risk_factors.append({"factor": "No bank account", "weight": 0.10, "impact": "negative"})
        else:
            positive_factors.append({"factor": "Has bank account", "weight": 0.08, "impact": "positive"})

        if not borrower_data.get('keeps_financial_records'):
            risk_factors.append({"factor": "No financial records", "weight": 0.12, "impact": "negative"})

        years = borrower_data.get('years_in_business', 0)
        if years >= 5:
            positive_factors.append({"factor": f"{years} years business continuity", "weight": 0.15, "impact": "positive"})
        elif years < 1:
            risk_factors.append({"factor": "New business (< 1 year)", "weight": 0.10, "impact": "negative"})

        # From NLP
        if nlp_result:
            insights = nlp_result.get('insights', {})
            summary = insights.get('summary', {})

            if summary.get('high_cooperation'):
                positive_factors.append({"factor": "Cooperative and transparent", "weight": 0.12, "impact": "positive"})

            risk_flags = summary.get('aggregated_risk_flags', [])
            for flag in risk_flags[:3]:  # Top 3 risk flags
                risk_factors.append({"factor": flag, "weight": 0.08, "impact": "negative"})

        # From Vision
        if vision_result:
            insights = vision_result.get('insights', {})
            summary = insights.get('summary', {})

            if summary.get('good_asset_quality'):
                positive_factors.append({"factor": "Good business asset quality", "weight": 0.10, "impact": "positive"})

            if summary.get('high_inventory'):
                positive_factors.append({"factor": "High inventory density", "weight": 0.08, "impact": "positive"})

        return risk_factors, positive_factors

    def _summarize_vision_insights(self, analyses: List[Dict]) -> Dict:
        """Summarize aggregated vision insights"""

        if not analyses:
            return {}

        # Aggregate business scale
        scales = [a.get('business_scale') for a in analyses if a.get('business_scale')]
        most_common_scale = max(set(scales), key=scales.count) if scales else "small"

        # Aggregate asset quality
        qualities = [a.get('asset_quality') for a in analyses if a.get('asset_quality')]
        avg_quality = max(set(qualities), key=qualities.count) if qualities else "fair"

        return {
            "most_common_business_scale": most_common_scale,
            "average_asset_quality": avg_quality,
            "good_asset_quality": avg_quality in ["good", "excellent"],
            "high_inventory": any(a.get('inventory_density') == 'high' for a in analyses)
        }

    def _summarize_nlp_insights(self, analyses: List[Dict]) -> Dict:
        """Summarize aggregated NLP insights"""

        if not analyses:
            return {}

        # Average sentiment
        sentiments = [a.get('sentiment_score', 0.6) for a in analyses]
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.6

        # Aggregate risk flags
        all_flags = []
        for analysis in analyses:
            flags = analysis.get('risk_flags', [])
            all_flags.extend([f['flag'] for f in flags])

        # Aggregate behavioral insights
        cooperations = [a.get('behavioral_insights', {}).get('cooperation_level') for a in analyses]
        high_cooperation = cooperations.count('high') > len(cooperations) / 2

        return {
            "average_sentiment": round(avg_sentiment, 2),
            "aggregated_risk_flags": list(set(all_flags)),
            "high_cooperation": high_cooperation
        }
