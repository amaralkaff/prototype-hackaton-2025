import re
from typing import Optional


def validate_phone_number(phone: str) -> bool:
    """Validate Indonesian phone number format"""
    pattern = r"^(\+62|62|0)[0-9]{9,12}$"
    return bool(re.match(pattern, phone))


def validate_income(income: float) -> bool:
    """Validate monthly income is within reasonable range"""
    MIN_INCOME = 500000  # Rp 500K
    MAX_INCOME = 20000000  # Rp 20M
    return MIN_INCOME <= income <= MAX_INCOME


def validate_loan_amount(loan_amount: float, monthly_income: float) -> bool:
    """Validate loan amount is reasonable relative to income"""
    MAX_LOAN_RATIO = 5.0  # Max 5x monthly income
    return loan_amount <= monthly_income * MAX_LOAN_RATIO


def validate_age(age: int) -> bool:
    """Validate borrower age"""
    MIN_AGE = 18
    MAX_AGE = 80
    return MIN_AGE <= age <= MAX_AGE


def sanitize_text(text: str) -> str:
    """Sanitize text input to prevent injection"""
    # Remove potentially harmful characters
    sanitized = re.sub(r'[<>\"\'\\]', '', text)
    return sanitized.strip()


def validate_credit_score(score: float) -> bool:
    """Validate credit score is within valid range"""
    return 0 <= score <= 100


def validate_risk_category(category: str) -> bool:
    """Validate risk category"""
    valid_categories = ['low', 'medium', 'high', 'very_high']
    return category in valid_categories
