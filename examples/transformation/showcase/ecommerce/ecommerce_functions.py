"""
E-Commerce Transformation Functions

Comprehensive custom functions for transforming legacy e-commerce data
to modern API formats. These functions demonstrate multi-argument
processing, business logic, and data enrichment.

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha - ajsinha@gmail.com
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date, timedelta
import re
import hashlib
import math


# =============================================================================
# DATE/TIME FUNCTIONS
# =============================================================================

def parse_legacy_date(date_str: str, time_str: str = None) -> str:
    """
    Parse legacy date (MM/DD/YYYY) and optional time to ISO 8601 format.
    
    Args:
        date_str: Date in MM/DD/YYYY format
        time_str: Optional time in HH:MM:SS format
        
    Returns:
        ISO 8601 datetime string
        
    Usage in SchemaMap:
        @compute(parse_legacy_date(order_header.order_date, order_header.order_time)) : orderDate
    """
    if not date_str:
        return None
    
    try:
        # Parse date
        dt = datetime.strptime(date_str, "%m/%d/%Y")
        
        # Add time if provided
        if time_str:
            time_parts = time_str.split(":")
            dt = dt.replace(
                hour=int(time_parts[0]) if len(time_parts) > 0 else 0,
                minute=int(time_parts[1]) if len(time_parts) > 1 else 0,
                second=int(time_parts[2]) if len(time_parts) > 2 else 0
            )
        
        return dt.isoformat() + "Z"
    except (ValueError, AttributeError):
        return None


def parse_date_to_iso(date_str: str) -> str:
    """
    Parse various date formats to ISO date (YYYY-MM-DD).
    
    Supports: MM/DD/YYYY, YYYY-MM-DD, DD-MM-YYYY
    """
    if not date_str:
        return None
    
    formats = ["%m/%d/%Y", "%Y-%m-%d", "%d-%m-%Y", "%m/%d/%y"]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    
    return None


def calculate_age(birth_date: str) -> int:
    """
    Calculate age from birth date string.
    
    Args:
        birth_date: Birth date in MM/DD/YYYY format
        
    Returns:
        Age in years
    """
    if not birth_date:
        return None
    
    try:
        bd = datetime.strptime(birth_date, "%m/%d/%Y").date()
        today = date.today()
        age = today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
        return age
    except (ValueError, AttributeError):
        return None


def calculate_estimated_delivery(ship_date: str, days: int, exclude_weekends: bool = True) -> str:
    """
    Calculate estimated delivery date.
    
    Args:
        ship_date: Ship date in MM/DD/YYYY format
        days: Number of days to add
        exclude_weekends: If True, only count business days
    """
    if not ship_date:
        return None
    
    try:
        dt = datetime.strptime(ship_date, "%m/%d/%Y")
        
        if exclude_weekends:
            added = 0
            while added < days:
                dt += timedelta(days=1)
                if dt.weekday() < 5:  # Monday = 0, Friday = 4
                    added += 1
        else:
            dt += timedelta(days=days)
        
        return dt.strftime("%Y-%m-%d")
    except (ValueError, AttributeError):
        return None


# =============================================================================
# NAME FORMATTING FUNCTIONS
# =============================================================================

def format_full_name(first: str, middle: str, last: str, suffix: str = None) -> str:
    """
    Build full name from components with proper formatting.
    
    Args:
        first: First name
        middle: Middle name
        last: Last name
        suffix: Name suffix (Jr., III, etc.)
        
    Returns:
        Properly formatted full name
        
    Usage in SchemaMap:
        @compute(format_full_name(customer_info.first_nm, customer_info.middle_nm, customer_info.last_nm, customer_info.suffix)) : customer.profile.fullName
    """
    parts = []
    
    if first:
        parts.append(str(first).strip().title())
    
    if middle:
        parts.append(str(middle).strip().title())
    
    if last:
        parts.append(str(last).strip().title())
    
    name = " ".join(parts)
    
    if suffix:
        suffix = str(suffix).strip()
        if suffix.upper() in ["JR", "SR", "II", "III", "IV", "V"]:
            name += f" {suffix.upper()}"
        else:
            name += f", {suffix.title()}"
    
    return name if name else None


def format_card_holder_name(full_name: str) -> str:
    """
    Format card holder name (uppercase, limited chars).
    """
    if not full_name:
        return None
    
    # Remove special characters except spaces and hyphens
    cleaned = re.sub(r'[^A-Za-z\s\-]', '', str(full_name))
    return cleaned.upper()[:26]  # Card holder names max 26 chars


# =============================================================================
# PHONE FORMATTING FUNCTIONS
# =============================================================================

def format_phone(phone: str, country: str = "US") -> str:
    """
    Format phone number for display.
    
    Args:
        phone: Raw phone number
        country: Country code for formatting
    """
    if not phone:
        return None
    
    # Extract digits only
    digits = re.sub(r'\D', '', str(phone))
    
    if country == "US":
        if len(digits) == 10:
            return f"+1 ({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == "1":
            return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    
    return phone


def format_phone_international(phone: str, country_code: str) -> str:
    """
    Format phone as international number.
    """
    if not phone:
        return None
    
    digits = re.sub(r'\D', '', str(phone))
    
    country_codes = {
        "US": "1", "CA": "1", "UK": "44", "DE": "49", "FR": "33"
    }
    
    code = country_codes.get(country_code, "1")
    
    # Remove leading country code if present
    if digits.startswith(code):
        digits = digits[len(code):]
    
    return f"+{code}{digits}"


# =============================================================================
# ADDRESS FORMATTING FUNCTIONS
# =============================================================================

def format_address_single_line(line1: str, line2: str, line3: str, 
                               city: str, state: str, postal: str, country: str) -> str:
    """
    Format address as single line for display.
    
    Args:
        line1, line2, line3: Address lines
        city: City name
        state: State/province code
        postal: Postal/ZIP code
        country: Country code
        
    Returns:
        Formatted single-line address
    """
    parts = []
    
    for line in [line1, line2, line3]:
        if line:
            parts.append(str(line).strip().title())
    
    if city:
        parts.append(str(city).strip().title())
    
    if state and postal:
        parts.append(f"{state.upper()} {postal}")
    elif state:
        parts.append(state.upper())
    elif postal:
        parts.append(str(postal))
    
    if country and country != "US":
        parts.append(country.upper())
    
    return ", ".join(parts)


def get_country_name(country_code: str) -> str:
    """
    Get full country name from code.
    """
    countries = {
        "US": "United States",
        "CA": "Canada",
        "MX": "Mexico",
        "UK": "United Kingdom",
        "GB": "United Kingdom",
        "DE": "Germany",
        "FR": "France",
        "ES": "Spain",
        "IT": "Italy",
        "JP": "Japan",
        "CN": "China",
        "AU": "Australia"
    }
    return countries.get(str(country_code).upper(), country_code)


# =============================================================================
# FINANCIAL CALCULATION FUNCTIONS
# =============================================================================

def calculate_profit_margin(unit_price: float, unit_cost: float) -> float:
    """
    Calculate profit margin percentage.
    
    Args:
        unit_price: Selling price
        unit_cost: Cost price
        
    Returns:
        Profit margin as percentage (0-100)
    """
    try:
        price = float(unit_price)
        cost = float(unit_cost)
        
        if price <= 0:
            return 0.0
        
        margin = ((price - cost) / price) * 100
        return round(margin, 2)
    except (TypeError, ValueError, ZeroDivisionError):
        return 0.0


def calculate_effective_tax_rate(tax_total: float, subtotal: float) -> float:
    """
    Calculate effective tax rate.
    
    Args:
        tax_total: Total tax amount
        subtotal: Pre-tax subtotal
        
    Returns:
        Effective tax rate as percentage
    """
    try:
        tax = float(tax_total)
        sub = float(subtotal)
        
        if sub <= 0:
            return 0.0
        
        return round((tax / sub) * 100, 3)
    except (TypeError, ValueError, ZeroDivisionError):
        return 0.0


def calculate_total_savings(discount_total: float, shipping_discount: float, 
                           promo_savings: float = 0) -> float:
    """
    Calculate total customer savings.
    """
    try:
        savings = float(discount_total or 0) + float(shipping_discount or 0) + float(promo_savings or 0)
        return round(savings, 2)
    except (TypeError, ValueError):
        return 0.0


def calculate_order_profit(merchandise_total: float, total_cost: float, 
                          discount_total: float) -> float:
    """
    Calculate order profit.
    """
    try:
        revenue = float(merchandise_total or 0)
        cost = float(total_cost or 0)
        discounts = float(discount_total or 0)
        
        return round(revenue - cost - discounts, 2)
    except (TypeError, ValueError):
        return 0.0


def sum_item_costs(items: List[Dict]) -> float:
    """
    Sum the total cost from all line items.
    """
    if not items or not isinstance(items, list):
        return 0.0
    
    total = 0.0
    for item in items:
        if isinstance(item, dict):
            qty = float(item.get("qty_ordered", 0) or 0)
            cost = float(item.get("unit_cost", 0) or 0)
            total += qty * cost
    
    return round(total, 2)


def sum_item_weights(items: List[Dict]) -> float:
    """
    Sum weights from all items considering quantities.
    """
    if not items or not isinstance(items, list):
        return 0.0
    
    total = 0.0
    for item in items:
        if isinstance(item, dict):
            qty = float(item.get("qty_ordered", 0) or 0)
            weight = float(item.get("weight_lbs", 0) or 0)
            total += qty * weight
    
    return round(total, 2)


def count_total_quantity(items: List[Dict]) -> int:
    """
    Count total quantity of all items.
    """
    if not items or not isinstance(items, list):
        return 0
    
    total = 0
    for item in items:
        if isinstance(item, dict):
            total += int(item.get("qty_ordered", 0) or 0)
    
    return total


# =============================================================================
# LOYALTY & CUSTOMER FUNCTIONS  
# =============================================================================

def calculate_loyalty_tier_expiration(current_tier: str, loyalty_points: int) -> str:
    """
    Calculate loyalty tier expiration date based on tier and points.
    
    Higher tiers and more points = longer expiration.
    """
    tier_months = {"B": 6, "S": 9, "G": 12, "P": 18, "D": 24}
    
    base_months = tier_months.get(str(current_tier).upper()[:1], 6)
    
    # Bonus months for high point balances
    points = int(loyalty_points or 0)
    bonus = min(points // 10000, 6)  # Max 6 bonus months
    
    exp_date = date.today() + timedelta(days=(base_months + bonus) * 30)
    return exp_date.strftime("%Y-%m-%d")


def calculate_credit_available(credit_limit: float, account_balance: float) -> float:
    """
    Calculate available credit.
    
    Args:
        credit_limit: Maximum credit allowed
        account_balance: Current balance (negative = credit used)
    """
    try:
        limit = float(credit_limit or 0)
        balance = float(account_balance or 0)
        
        # If balance is negative, they owe money, reducing available credit
        available = limit + balance if balance < 0 else limit
        
        return round(max(0, available), 2)
    except (TypeError, ValueError):
        return 0.0


def determine_customer_segment(lifetime_value: float, loyalty_tier: str, 
                               total_orders: int = None) -> str:
    """
    Determine customer segment for marketing.
    """
    try:
        ltv = float(lifetime_value or 0)
        tier = str(loyalty_tier or "").upper()[:1]
        
        if tier == "D" or ltv >= 50000:
            return "VIP"
        elif tier in ["P", "G"] or ltv >= 20000:
            return "PREMIUM"
        elif tier == "S" or ltv >= 5000:
            return "STANDARD"
        else:
            return "NEW"
    except (TypeError, ValueError):
        return "NEW"


# =============================================================================
# DATA MASKING FUNCTIONS
# =============================================================================

def mask_ssn(ssn: str) -> str:
    """
    Mask SSN showing only last 4 digits.
    
    Args:
        ssn: Social Security Number
        
    Returns:
        Masked SSN (XXX-XX-1234)
    """
    if not ssn:
        return None
    
    # Extract digits
    digits = re.sub(r'\D', '', str(ssn))
    
    if len(digits) == 9:
        return f"XXX-XX-{digits[5:]}"
    
    return "XXX-XX-XXXX"


def mask_card_number(card_last4: str) -> str:
    """
    Format masked card number.
    """
    if not card_last4:
        return None
    
    digits = re.sub(r'\D', '', str(card_last4))[-4:]
    return f"****-****-****-{digits}"


# =============================================================================
# IDENTIFIER GENERATION FUNCTIONS
# =============================================================================

def generate_order_id(order_num: str, channel: str, timestamp: str = None) -> str:
    """
    Generate a unique order ID from order components.
    
    Args:
        order_num: Original order number
        channel: Order channel (WEB, STORE, etc.)
        timestamp: Optional timestamp for uniqueness
    """
    if not order_num:
        return None
    
    # Create hash for uniqueness
    components = f"{order_num}:{channel}:{timestamp or ''}"
    hash_suffix = hashlib.md5(components.encode()).hexdigest()[:8].upper()
    
    return f"ORD-{hash_suffix}"


def generate_transaction_reference(payment_method: str, transaction_id: str, 
                                   amount: float) -> str:
    """
    Generate transaction reference number.
    """
    method_codes = {"CC": "C", "DEBIT": "D", "PAYPAL": "P", "LOYALTY": "L", "GIFT": "G"}
    prefix = method_codes.get(str(payment_method).upper(), "X")
    
    return f"{prefix}-{transaction_id or 'UNKNOWN'}"


# =============================================================================
# STATUS MAPPING FUNCTIONS
# =============================================================================

def map_order_status(legacy_status: str) -> str:
    """
    Map legacy order status to modern API status.
    """
    status_map = {
        "NEW": "PENDING",
        "PND": "PENDING",
        "PENDING": "PENDING",
        "CNF": "CONFIRMED",
        "CONFIRMED": "CONFIRMED",
        "PROC": "PROCESSING",
        "PROCESSING": "PROCESSING",
        "PICK": "PROCESSING",
        "PACK": "PROCESSING",
        "SHIP": "SHIPPED",
        "SHIPPED": "SHIPPED",
        "INTRANS": "SHIPPED",
        "DLVR": "DELIVERED",
        "DELIVERED": "DELIVERED",
        "CXL": "CANCELLED",
        "CANCELLED": "CANCELLED",
        "VOID": "CANCELLED",
        "RFD": "REFUNDED",
        "REFUND": "REFUNDED",
        "REFUNDED": "REFUNDED"
    }
    
    return status_map.get(str(legacy_status).upper(), "PENDING")


def map_payment_method(legacy_method: str) -> str:
    """
    Map legacy payment method to modern format.
    """
    method_map = {
        "CC": "CREDIT_CARD",
        "CREDIT": "CREDIT_CARD",
        "VISA": "CREDIT_CARD",
        "MC": "CREDIT_CARD",
        "AMEX": "CREDIT_CARD",
        "DISC": "CREDIT_CARD",
        "DEBIT": "DEBIT_CARD",
        "DB": "DEBIT_CARD",
        "PP": "PAYPAL",
        "PAYPAL": "PAYPAL",
        "AP": "APPLE_PAY",
        "APPLE": "APPLE_PAY",
        "GP": "GOOGLE_PAY",
        "GOOGLE": "GOOGLE_PAY",
        "LYL": "LOYALTY_POINTS",
        "LOYALTY": "LOYALTY_POINTS",
        "POINTS": "LOYALTY_POINTS",
        "GC": "GIFT_CARD",
        "GIFT": "GIFT_CARD",
        "SC": "STORE_CREDIT",
        "CREDIT": "STORE_CREDIT"
    }
    
    return method_map.get(str(legacy_method).upper(), "CREDIT_CARD")


def map_fulfillment_status(legacy_status: str) -> str:
    """
    Map fulfillment status.
    """
    status_map = {
        "PENDING": "PENDING",
        "ALLOCATED": "PROCESSING",
        "PICKED": "PROCESSING",
        "PACKED": "READY",
        "SHIPPED": "SHIPPED",
        "INTRANSIT": "IN_TRANSIT",
        "DELIVERED": "DELIVERED",
        "RETURNED": "RETURNED"
    }
    return status_map.get(str(legacy_status).upper(), "PENDING")


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def validate_and_clean_email(email: str) -> str:
    """
    Validate and clean email address.
    """
    if not email:
        return None
    
    email = str(email).strip().lower()
    
    # Basic validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return email
    
    return None


def is_valid_tracking_number(tracking: str, carrier: str) -> bool:
    """
    Validate tracking number format for carrier.
    """
    if not tracking:
        return False
    
    tracking = str(tracking).upper()
    carrier = str(carrier).upper()
    
    patterns = {
        "UPS": r"^1Z[A-Z0-9]{16}$",
        "FEDEX": r"^[0-9]{12,22}$",
        "USPS": r"^[0-9]{20,22}$"
    }
    
    pattern = patterns.get(carrier)
    if pattern:
        return bool(re.match(pattern, tracking))
    
    return True  # Unknown carriers pass


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def coalesce(*values) -> Any:
    """
    Return first non-null, non-empty value.
    """
    for v in values:
        if v is not None and v != "" and v != []:
            return v
    return None


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safe division with default for divide-by-zero.
    """
    try:
        num = float(numerator or 0)
        den = float(denominator)
        if den == 0:
            return default
        return round(num / den, 4)
    except (TypeError, ValueError):
        return default


def flag_to_bool(flag: str) -> bool:
    """
    Convert Y/N flag to boolean.
    """
    return str(flag).upper() in ("Y", "YES", "TRUE", "1", "T")


def clean_text(text: str) -> str:
    """
    Clean and normalize text (trim, collapse spaces).
    """
    if not text:
        return None
    
    # Strip, collapse spaces, normalize
    cleaned = re.sub(r'\s+', ' ', str(text)).strip()
    return cleaned if cleaned else None
