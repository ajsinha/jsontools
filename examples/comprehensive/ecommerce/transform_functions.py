"""
E-Commerce Transformation Functions

Comprehensive custom functions demonstrating multi-argument processing,
business calculations, data formatting, and validation.

Usage in SchemaMap:
    @compute(function_name(arg1, arg2, arg3)) : target.path

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha - ajsinha@gmail.com
"""

from datetime import datetime, date, timedelta
from typing import Any, Dict, List, Optional, Union
import re
import hashlib


# =============================================================================
# DATE/TIME FUNCTIONS (Multi-argument)
# =============================================================================

def parse_datetime(date_str: str, time_str: str = None) -> str:
    """
    Parse legacy date and time to ISO 8601 format.
    
    Args:
        date_str: Date in MM/DD/YYYY format
        time_str: Optional time in HH:MM:SS format
        
    Returns:
        ISO 8601 datetime string (2024-12-15T14:35:22Z)
        
    Example:
        @compute(parse_datetime(header.orderDate, header.orderTime)) : orderTimestamp
    """
    if not date_str:
        return None
    try:
        dt = datetime.strptime(date_str.strip(), "%m/%d/%Y")
        if time_str:
            parts = time_str.strip().split(":")
            dt = dt.replace(
                hour=int(parts[0]) if len(parts) > 0 else 0,
                minute=int(parts[1]) if len(parts) > 1 else 0,
                second=int(parts[2]) if len(parts) > 2 else 0
            )
        return dt.isoformat() + "Z"
    except (ValueError, AttributeError):
        return None


def format_date(date_str: str, input_fmt: str = "%m/%d/%Y", output_fmt: str = "%Y-%m-%d") -> str:
    """
    Convert date between formats.
    
    Args:
        date_str: Input date string
        input_fmt: Input format (default: MM/DD/YYYY)
        output_fmt: Output format (default: YYYY-MM-DD)
    """
    if not date_str:
        return None
    try:
        dt = datetime.strptime(date_str.strip(), input_fmt)
        return dt.strftime(output_fmt)
    except (ValueError, AttributeError):
        return None


def calculate_age(birth_date: str) -> int:
    """Calculate age in years from birth date (MM/DD/YYYY)."""
    if not birth_date:
        return None
    try:
        bd = datetime.strptime(birth_date.strip(), "%m/%d/%Y").date()
        today = date.today()
        return today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
    except (ValueError, AttributeError):
        return None


def add_business_days(date_str: str, days: int) -> str:
    """
    Add business days to a date.
    
    Args:
        date_str: Start date (MM/DD/YYYY)
        days: Number of business days to add
    """
    if not date_str:
        return None
    try:
        dt = datetime.strptime(date_str.strip(), "%m/%d/%Y")
        added = 0
        while added < days:
            dt += timedelta(days=1)
            if dt.weekday() < 5:  # Mon-Fri
                added += 1
        return dt.strftime("%Y-%m-%d")
    except (ValueError, AttributeError):
        return None


# =============================================================================
# NAME FORMATTING FUNCTIONS (Multi-argument)
# =============================================================================

def format_full_name(first: str, middle: str, last: str, suffix: str = None) -> str:
    """
    Build properly formatted full name.
    
    Args:
        first: First name
        middle: Middle name (can be None)
        last: Last name
        suffix: Optional suffix (Jr., III, etc.)
        
    Returns:
        Formatted name: "Jennifer Marie Smith-Johnson III"
        
    Example:
        @compute(format_full_name(customer.firstName, customer.middleName, customer.lastName, customer.suffix)) : profile.fullName
    """
    parts = []
    for name in [first, middle, last]:
        if name:
            parts.append(str(name).strip().title())
    
    result = " ".join(parts)
    
    if suffix:
        s = str(suffix).strip().upper()
        if s in ["JR", "SR", "II", "III", "IV", "V"]:
            result += f" {s}"
        elif s:
            result += f", {s}"
    
    return result if result else None


def format_display_name(first: str, last: str) -> str:
    """Format as 'Last, First' for display."""
    parts = []
    if last:
        parts.append(str(last).strip().title())
    if first:
        parts.append(str(first).strip().title())
    return ", ".join(parts) if parts else None


# =============================================================================
# PHONE FORMATTING FUNCTIONS
# =============================================================================

def format_phone(phone: str, country: str = "US") -> str:
    """
    Format phone number for display.
    
    Args:
        phone: Raw phone digits
        country: Country code (US, UK, etc.)
        
    Returns:
        Formatted phone: "+1 (212) 555-1234"
    """
    if not phone:
        return None
    digits = re.sub(r'\D', '', str(phone))
    
    if country == "US" and len(digits) == 10:
        return f"+1 ({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif country == "US" and len(digits) == 11 and digits[0] == "1":
        return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    return phone


def format_phone_e164(phone: str, country_code: str = "1") -> str:
    """Format phone in E.164 international format (+12125551234)."""
    if not phone:
        return None
    digits = re.sub(r'\D', '', str(phone))
    if digits.startswith(country_code):
        return f"+{digits}"
    return f"+{country_code}{digits}"


# =============================================================================
# ADDRESS FORMATTING FUNCTIONS (Multi-argument)
# =============================================================================

def format_address(line1: str, line2: str, line3: str, 
                   city: str, state: str, zip_code: str, country: str = "US") -> str:
    """
    Format complete address as single line.
    
    Args:
        line1, line2, line3: Address lines
        city: City name
        state: State/province code
        zip_code: Postal code
        country: Country code
        
    Returns:
        "123 Main St, Apt 4B, New York, NY 10001"
    """
    parts = []
    for line in [line1, line2, line3]:
        if line:
            parts.append(str(line).strip().title())
    
    if city:
        parts.append(str(city).strip().title())
    
    state_zip = []
    if state:
        state_zip.append(str(state).strip().upper())
    if zip_code:
        state_zip.append(str(zip_code).strip())
    if state_zip:
        parts.append(" ".join(state_zip))
    
    if country and country.upper() != "US":
        parts.append(country.upper())
    
    return ", ".join(parts)


def get_country_name(code: str) -> str:
    """Convert country code to full name."""
    countries = {
        "US": "United States", "CA": "Canada", "MX": "Mexico",
        "UK": "United Kingdom", "GB": "United Kingdom",
        "DE": "Germany", "FR": "France", "ES": "Spain",
        "IT": "Italy", "JP": "Japan", "CN": "China", "AU": "Australia"
    }
    return countries.get(str(code).upper(), code)


# =============================================================================
# FINANCIAL CALCULATION FUNCTIONS (Multi-argument)
# =============================================================================

def calculate_line_total(unit_price: float, quantity: int, discount_pct: float = 0) -> float:
    """
    Calculate line item total with discount.
    
    Args:
        unit_price: Price per unit
        quantity: Number of units
        discount_pct: Discount percentage (0-100)
    """
    try:
        price = float(unit_price or 0)
        qty = int(quantity or 0)
        disc = float(discount_pct or 0) / 100
        return round(price * qty * (1 - disc), 2)
    except (TypeError, ValueError):
        return 0.0


def calculate_tax(amount: float, rate: float) -> float:
    """
    Calculate tax amount.
    
    Args:
        amount: Taxable amount
        rate: Tax rate as percentage (e.g., 8.875)
    """
    try:
        return round(float(amount or 0) * float(rate or 0) / 100, 2)
    except (TypeError, ValueError):
        return 0.0


def calculate_profit_margin(price: float, cost: float) -> float:
    """
    Calculate profit margin percentage.
    
    Args:
        price: Selling price
        cost: Cost price
        
    Returns:
        Margin as percentage (0-100)
    """
    try:
        p = float(price or 0)
        c = float(cost or 0)
        if p <= 0:
            return 0.0
        return round((p - c) / p * 100, 2)
    except (TypeError, ValueError, ZeroDivisionError):
        return 0.0


def calculate_effective_rate(total_tax: float, subtotal: float) -> float:
    """Calculate effective tax rate from totals."""
    try:
        tax = float(total_tax or 0)
        sub = float(subtotal or 0)
        if sub <= 0:
            return 0.0
        return round(tax / sub * 100, 3)
    except (TypeError, ValueError, ZeroDivisionError):
        return 0.0


def calculate_savings(discount: float, shipping_discount: float, promo_savings: float = 0) -> float:
    """Calculate total customer savings."""
    try:
        return round(
            float(discount or 0) + 
            float(shipping_discount or 0) + 
            float(promo_savings or 0), 2
        )
    except (TypeError, ValueError):
        return 0.0


def calculate_credit_available(limit: float, balance: float) -> float:
    """
    Calculate available credit.
    
    Args:
        limit: Credit limit
        balance: Current balance (negative = owes money)
    """
    try:
        lim = float(limit or 0)
        bal = float(balance or 0)
        # If balance is negative, they owe that much
        available = lim + bal if bal < 0 else lim
        return round(max(0, available), 2)
    except (TypeError, ValueError):
        return 0.0


# =============================================================================
# ARRAY AGGREGATION FUNCTIONS
# =============================================================================

def sum_field(items: list, field: str) -> float:
    """
    Sum a field across all items in an array.
    
    Args:
        items: List of dictionaries
        field: Field name to sum
    """
    if not items or not isinstance(items, list):
        return 0.0
    total = 0.0
    for item in items:
        if isinstance(item, dict):
            val = item.get(field, 0)
            try:
                total += float(val or 0)
            except (TypeError, ValueError):
                pass
    return round(total, 2)


def sum_weighted_field(items: list, value_field: str, quantity_field: str) -> float:
    """
    Sum field * quantity across all items.
    
    Args:
        items: List of dictionaries
        value_field: Field with value (e.g., 'weight')
        quantity_field: Field with quantity (e.g., 'quantityOrdered')
    """
    if not items or not isinstance(items, list):
        return 0.0
    total = 0.0
    for item in items:
        if isinstance(item, dict):
            val = float(item.get(value_field, 0) or 0)
            qty = int(item.get(quantity_field, 0) or 0)
            total += val * qty
    return round(total, 2)


def count_items(items: list) -> int:
    """Count number of items in array."""
    return len(items) if isinstance(items, list) else 0


def sum_quantity(items: list, quantity_field: str = "quantityOrdered") -> int:
    """Sum quantities across all items."""
    if not items or not isinstance(items, list):
        return 0
    total = 0
    for item in items:
        if isinstance(item, dict):
            total += int(item.get(quantity_field, 0) or 0)
    return total


# =============================================================================
# LOYALTY FUNCTIONS
# =============================================================================

def calculate_tier_expiration(tier: str, points: int) -> str:
    """
    Calculate loyalty tier expiration date.
    
    Args:
        tier: Current tier code (B/S/G/P/D)
        points: Current point balance
    """
    tier_months = {"B": 6, "S": 9, "G": 12, "P": 18, "D": 24}
    base = tier_months.get(str(tier).upper()[:1], 6)
    
    # Bonus months for high points (max 6)
    bonus = min(int(points or 0) // 10000, 6)
    
    exp = date.today() + timedelta(days=(base + bonus) * 30)
    return exp.strftime("%Y-%m-%d")


def determine_customer_segment(lifetime_value: float, tier: str) -> str:
    """Determine marketing segment based on value and tier."""
    try:
        ltv = float(lifetime_value or 0)
        t = str(tier or "").upper()[:1]
        
        if t == "D" or ltv >= 50000:
            return "VIP"
        elif t in ["P", "G"] or ltv >= 20000:
            return "PREMIUM"
        elif t == "S" or ltv >= 5000:
            return "STANDARD"
        return "NEW"
    except (TypeError, ValueError):
        return "NEW"


# =============================================================================
# DATA MASKING FUNCTIONS
# =============================================================================

def mask_ssn(ssn: str) -> str:
    """Mask SSN showing only last 4 digits."""
    if not ssn:
        return None
    digits = re.sub(r'\D', '', str(ssn))
    if len(digits) >= 4:
        return f"XXX-XX-{digits[-4:]}"
    return "XXX-XX-XXXX"


def mask_card(last_four: str) -> str:
    """Format masked card number."""
    if not last_four:
        return None
    digits = re.sub(r'\D', '', str(last_four))[-4:]
    return f"****-****-****-{digits}"


# =============================================================================
# ID GENERATION FUNCTIONS
# =============================================================================

def generate_order_id(order_num: str, channel: str) -> str:
    """Generate unique order ID from components."""
    if not order_num:
        return None
    data = f"{order_num}:{channel or 'UNK'}"
    hash_str = hashlib.md5(data.encode()).hexdigest()[:8].upper()
    return f"ORD-{hash_str}"


def generate_line_id(order_num: str, line_num: int) -> str:
    """Generate unique line item ID."""
    return f"{order_num}-L{line_num:03d}" if order_num else None


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def clean_email(email: str) -> str:
    """Clean and validate email address."""
    if not email:
        return None
    email = str(email).strip().lower()
    if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return email
    return None


def clean_text(text: str) -> str:
    """Clean text: trim and collapse whitespace."""
    if not text:
        return None
    return re.sub(r'\s+', ' ', str(text).strip()) or None


# =============================================================================
# CONVERSION FUNCTIONS
# =============================================================================

def flag_to_bool(flag: str) -> bool:
    """Convert Y/N flag to boolean."""
    return str(flag).upper() in ("Y", "YES", "TRUE", "1", "T")


def to_float(value: Any, default: float = 0.0) -> float:
    """Safe float conversion."""
    try:
        return round(float(value), 2)
    except (TypeError, ValueError):
        return default


def to_int(value: Any, default: int = 0) -> int:
    """Safe int conversion."""
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default
