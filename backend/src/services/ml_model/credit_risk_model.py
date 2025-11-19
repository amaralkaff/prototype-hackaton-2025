import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
import joblib
from pathlib import Path
from typing import Dict, List, Tuple
import json

from utils.logger import logger


class CreditRiskModel:
    """ML model for baseline credit risk assessment"""

    def __init__(self, model_path: str = None):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_names = []
        self.model_version = "1.0.0"

        if model_path and Path(model_path).exists():
            self.load_model(model_path)

    def prepare_features(self, borrower_data: Dict) -> np.ndarray:
        """
        Prepare features from borrower data for prediction

        Input features:
        - Repayment history (avg days overdue, on-time rate, default rate)
        - Loan history (num loans, avg loan size, total borrowed)
        - Demographics (age, years_in_business, num_dependents)
        - Financial literacy score
        - Business type (encoded)
        - Has bank account, keeps records (binary)
        """

        features = {}

        # Demographics
        features['age'] = borrower_data.get('age', 35)
        features['years_in_business'] = borrower_data.get('years_in_business', 2.0)
        features['num_dependents'] = borrower_data.get('num_dependents', 2)
        features['monthly_income'] = borrower_data.get('claimed_monthly_income', 3000000)

        # Financial literacy & behavior
        features['financial_literacy_score'] = borrower_data.get('financial_literacy_score', 50)
        features['has_bank_account'] = 1 if borrower_data.get('has_bank_account') else 0
        features['keeps_financial_records'] = 1 if borrower_data.get('keeps_financial_records') else 0

        # Loan history features
        loan_history = borrower_data.get('loan_history', {})
        features['num_previous_loans'] = loan_history.get('num_loans', 0)
        features['avg_loan_amount'] = loan_history.get('avg_loan_amount', 0)
        features['total_borrowed'] = loan_history.get('total_borrowed', 0)

        # Repayment history features
        repayment_history = borrower_data.get('repayment_history', {})
        features['on_time_rate'] = repayment_history.get('on_time_rate', 0.5)  # 0-1
        features['avg_days_overdue'] = repayment_history.get('avg_days_overdue', 5.0)
        features['default_rate'] = repayment_history.get('default_rate', 0.0)  # 0-1
        features['total_repayments'] = repayment_history.get('total_repayments', 0)

        # Business type encoding
        business_type = borrower_data.get('business_type', 'Unknown')
        features['business_type_encoded'] = self._encode_business_type(business_type)

        # Convert to DataFrame for consistency
        df = pd.DataFrame([features])
        self.feature_names = list(features.keys())

        return df.values

    def _encode_business_type(self, business_type: str) -> int:
        """Encode business type to numeric value"""
        business_mapping = {
            'Warung Kelontong': 1,
            'Warung Gorengan': 2,
            'Jahit Pakaian': 3,
            'Jualan Sayur': 4,
            'Catering': 5,
            'Salon': 6,
            'Toko Pulsa': 7,
            'Warung Nasi': 8,
            'Industri Kerupuk': 9,
        }

        for key in business_mapping:
            if key in business_type:
                return business_mapping[key]

        return 0  # Unknown

    def predict(self, borrower_data: Dict) -> Dict:
        """
        Predict credit risk score for a borrower

        Returns:
        {
            "baseline_score": float (0-100),
            "risk_category": str,
            "confidence": float (0-1),
            "feature_importance": dict,
            "model_version": str
        }
        """

        try:
            # Prepare features
            features = self.prepare_features(borrower_data)

            # If no model is loaded, use rule-based scoring
            if self.model is None:
                logger.warning("ML model not loaded, using rule-based scoring")
                return self._rule_based_scoring(borrower_data)

            # Scale features
            features_scaled = self.scaler.transform(features)

            # Predict probability
            prob = self.model.predict_proba(features_scaled)[0]
            # Assuming class 1 is "good credit", convert to 0-100 score
            baseline_score = float(prob[1] * 100)

            # Determine risk category
            risk_category = self._categorize_risk(baseline_score)

            # Calculate confidence
            confidence = float(max(prob))

            # Feature importance
            feature_importance = {}
            if hasattr(self.model, 'feature_importances_'):
                importances = self.model.feature_importances_
                for name, importance in zip(self.feature_names, importances):
                    feature_importance[name] = float(importance)

            return {
                "baseline_score": round(baseline_score, 2),
                "risk_category": risk_category,
                "confidence": round(confidence, 2),
                "feature_importance": feature_importance,
                "model_version": self.model_version
            }

        except Exception as e:
            logger.error(f"Error in ML prediction: {e}")
            # Fallback to rule-based scoring
            return self._rule_based_scoring(borrower_data)

    def _rule_based_scoring(self, borrower_data: Dict) -> Dict:
        """
        Rule-based credit scoring fallback when ML model is unavailable

        Scoring factors:
        - Repayment history: 40%
        - Financial behavior: 25%
        - Business stability: 20%
        - Demographics: 15%
        """

        score = 50.0  # Start at neutral

        # Repayment history (40 points)
        repayment_history = borrower_data.get('repayment_history', {})
        on_time_rate = repayment_history.get('on_time_rate', 0.5)
        avg_days_overdue = repayment_history.get('avg_days_overdue', 5.0)

        score += on_time_rate * 30  # 0-30 points
        score += max(0, 10 - avg_days_overdue)  # 0-10 points

        # Financial behavior (25 points)
        if borrower_data.get('has_bank_account'):
            score += 8
        if borrower_data.get('keeps_financial_records'):
            score += 10
        financial_literacy = borrower_data.get('financial_literacy_score', 50)
        score += (financial_literacy / 100) * 7  # 0-7 points

        # Business stability (20 points)
        years_in_business = borrower_data.get('years_in_business', 2.0)
        score += min(years_in_business * 2, 15)  # Up to 15 points
        loan_history = borrower_data.get('loan_history', {})
        num_loans = loan_history.get('num_loans', 0)
        if num_loans > 0:
            score += 5  # 5 points for loan history

        # Demographics (15 points)
        age = borrower_data.get('age', 35)
        if 25 <= age <= 50:
            score += 8  # Prime working age
        elif 18 <= age <= 60:
            score += 5

        num_dependents = borrower_data.get('num_dependents', 2)
        if num_dependents <= 3:
            score += 7  # Manageable family size
        else:
            score += 3

        # Cap score at 100
        score = min(score, 100)

        risk_category = self._categorize_risk(score)

        return {
            "baseline_score": round(score, 2),
            "risk_category": risk_category,
            "confidence": 0.70,  # Rule-based has moderate confidence
            "feature_importance": {},
            "model_version": f"{self.model_version}-rule-based"
        }

    def _categorize_risk(self, score: float) -> str:
        """Categorize risk based on credit score"""
        if score >= 75:
            return "low"
        elif score >= 55:
            return "medium"
        elif score >= 35:
            return "high"
        else:
            return "very_high"

    def train(self, training_data: List[Dict], labels: List[int]):
        """
        Train the credit risk model

        Args:
            training_data: List of borrower data dictionaries
            labels: List of binary labels (1 = good credit, 0 = bad credit)
        """

        logger.info(f"Training credit risk model with {len(training_data)} samples")

        # Prepare feature matrix
        X = np.array([self.prepare_features(data) for data in training_data])
        X = X.reshape(len(training_data), -1)
        y = np.array(labels)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train model (using RandomForest for interpretability)
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=10,
            random_state=42,
            class_weight='balanced'
        )

        self.model.fit(X_train_scaled, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        y_prob = self.model.predict_proba(X_test_scaled)[:, 1]

        logger.info("Model Training Complete")
        logger.info(f"Accuracy: {self.model.score(X_test_scaled, y_test):.3f}")
        logger.info(f"ROC-AUC: {roc_auc_score(y_test, y_prob):.3f}")
        logger.info(f"\n{classification_report(y_test, y_pred)}")

        return self.model

    def save_model(self, filepath: str):
        """Save trained model to disk"""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'model_version': self.model_version
        }

        joblib.dump(model_data, filepath)
        logger.info(f"Model saved to {filepath}")

    def load_model(self, filepath: str):
        """Load trained model from disk"""
        try:
            model_data = joblib.load(filepath)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_names = model_data['feature_names']
            self.model_version = model_data.get('model_version', '1.0.0')

            logger.info(f"Model loaded from {filepath}")
            logger.info(f"Model version: {self.model_version}")

        except Exception as e:
            logger.error(f"Error loading model: {e}")
            logger.warning("Model will use rule-based scoring fallback")
