"""
Custom Transformation Functions for SchemaMap

This file demonstrates how to create external Python functions
that can be called from SchemaMap DSL via @compute or @call.

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
"""

from typing import Any, List, Optional
from datetime import datetime, date
import re
import math


# ============================================================================
# Financial Functions
# ============================================================================

def calculate_tax(amount: float, rate: float = 0.08) -> float:
    """
    Calculate tax amount.
    
    Usage in SchemaMap:
        @compute(calculate_tax(order.subtotal, 0.08)) : order.tax
    """
    return round(float(amount) * float(rate), 2)


def calculate_total(subtotal: float, tax: float, shipping: float = 0) -> float:
    """
    Calculate order total.
    
    Usage in SchemaMap:
        @compute(calculate_total(order.subtotal, order.tax, order.shipping)) : order.total
    """
    return round(float(subtotal) + float(tax) + float(shipping), 2)


def format_currency(amount: float, currency: str = "USD", locale: str = "en_US") -> str:
    """
    Format a number as currency.
    
    Usage in SchemaMap:
        @compute(format_currency(order.total, "USD")) : order.displayTotal
    """
    symbols = {"USD": "$", "EUR": "€", "GBP": "£", "JPY": "¥"}
    symbol = symbols.get(currency, currency + " ")
    return f"{symbol}{float(amount):,.2f}"


def calculate_discount(amount: float, discount_pct: float) -> float:
    """
    Calculate discounted price.
    
    Usage in SchemaMap:
        @compute(calculate_discount(item.price, item.discountPercent)) : item.salePrice
    """
    discount = float(amount) * (float(discount_pct) / 100)
    return round(float(amount) - discount, 2)


def calculate_compound_interest(principal: float, rate: float, years: int, 
                                 compounds_per_year: int = 12) -> float:
    """
    Calculate compound interest.
    
    A = P(1 + r/n)^(nt)
    """
    r = float(rate) / 100
    n = int(compounds_per_year)
    t = int(years)
    return round(float(principal) * math.pow(1 + r/n, n*t), 2)


# ============================================================================
# String Functions
# ============================================================================

def format_full_name(first_name: str, last_name: str, 
                     middle_name: str = None, suffix: str = None) -> str:
    """
    Format a full name from components.
    
    Usage in SchemaMap:
        @compute(format_full_name(person.firstName, person.lastName, person.middleName, person.suffix)) : person.fullName
    """
    parts = [first_name]
    if middle_name:
        parts.append(middle_name)
    parts.append(last_name)
    if suffix:
        parts.append(suffix)
    return " ".join(str(p).strip() for p in parts if p).title()


def format_phone(phone: str, country: str = "US") -> str:
    """
    Format a phone number.
    
    Usage in SchemaMap:
        @compute(format_phone(contact.phone, "US")) : contact.formattedPhone
    """
    if not phone:
        return ""
    
    # Remove non-digits
    digits = re.sub(r'\D', '', str(phone))
    
    if country == "US" and len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif country == "US" and len(digits) == 11 and digits[0] == "1":
        return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    
    return phone


def format_ssn(ssn: str, mask: bool = True) -> str:
    """
    Format SSN with optional masking.
    
    Usage in SchemaMap:
        @compute(format_ssn(person.ssn, true)) : person.maskedSsn
    """
    if not ssn:
        return ""
    
    digits = re.sub(r'\D', '', str(ssn))
    
    if len(digits) != 9:
        return ssn
    
    if mask:
        return f"XXX-XX-{digits[5:]}"
    return f"{digits[:3]}-{digits[3:5]}-{digits[5:]}"


def slugify(text: str) -> str:
    """
    Convert text to URL-safe slug.
    
    Usage in SchemaMap:
        @compute(slugify(article.title)) : article.slug
    """
    if not text:
        return ""
    
    # Lowercase and replace spaces
    slug = str(text).lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '-', slug)
    slug = slug.strip('-')
    return slug


def truncate(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to max length with suffix.
    
    Usage in SchemaMap:
        @compute(truncate(article.content, 200, "...")) : article.excerpt
    """
    if not text:
        return ""
    
    text = str(text)
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)].rsplit(' ', 1)[0] + suffix


# ============================================================================
# Date/Time Functions
# ============================================================================

def calculate_age(birth_date: str) -> int:
    """
    Calculate age from birth date.
    
    Usage in SchemaMap:
        @compute(calculate_age(person.birthDate)) : person.age
    """
    if not birth_date:
        return 0
    
    try:
        if isinstance(birth_date, str):
            # Try common formats
            for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S"]:
                try:
                    bd = datetime.strptime(birth_date.split("T")[0], fmt).date()
                    break
                except ValueError:
                    continue
            else:
                return 0
        elif isinstance(birth_date, (datetime, date)):
            bd = birth_date if isinstance(birth_date, date) else birth_date.date()
        else:
            return 0
        
        today = date.today()
        age = today.year - bd.year
        if (today.month, today.day) < (bd.month, bd.day):
            age -= 1
        return age
    except Exception:
        return 0


def format_date(date_str: str, output_format: str = "%B %d, %Y") -> str:
    """
    Format a date string.
    
    Usage in SchemaMap:
        @compute(format_date(order.createdAt, "%B %d, %Y")) : order.displayDate
    """
    if not date_str:
        return ""
    
    try:
        # Try common input formats
        for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ", 
                    "%m/%d/%Y", "%d/%m/%Y"]:
            try:
                dt = datetime.strptime(str(date_str).split("+")[0].replace("Z", ""), fmt)
                return dt.strftime(output_format)
            except ValueError:
                continue
        return date_str
    except Exception:
        return date_str


def days_between(date1: str, date2: str) -> int:
    """
    Calculate days between two dates.
    
    Usage in SchemaMap:
        @compute(days_between(order.startDate, order.endDate)) : order.duration
    """
    try:
        d1 = datetime.fromisoformat(str(date1).replace("Z", ""))
        d2 = datetime.fromisoformat(str(date2).replace("Z", ""))
        return abs((d2 - d1).days)
    except Exception:
        return 0


# ============================================================================
# Validation Functions
# ============================================================================

def is_valid_email(email: str) -> bool:
    """
    Validate email format.
    
    Usage in SchemaMap:
        @compute(is_valid_email(contact.email)) : contact.emailValid
    """
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, str(email)))


def is_valid_phone(phone: str, country: str = "US") -> bool:
    """
    Validate phone number format.
    """
    if not phone:
        return False
    digits = re.sub(r'\D', '', str(phone))
    if country == "US":
        return len(digits) in (10, 11)
    return len(digits) >= 7


# ============================================================================
# Array/Collection Functions
# ============================================================================

def sum_field(items: List[dict], field: str) -> float:
    """
    Sum a field across all items in a list.
    
    Usage in SchemaMap:
        @compute(sum_field(order.items, "total")) : order.subtotal
    """
    if not items or not isinstance(items, list):
        return 0.0
    
    total = 0.0
    for item in items:
        if isinstance(item, dict) and field in item:
            try:
                total += float(item[field])
            except (ValueError, TypeError):
                pass
    return round(total, 2)


def count_where(items: List[dict], field: str, value: Any) -> int:
    """
    Count items where field equals value.
    
    Usage in SchemaMap:
        @compute(count_where(order.items, "status", "shipped")) : order.shippedCount
    """
    if not items or not isinstance(items, list):
        return 0
    
    count = 0
    for item in items:
        if isinstance(item, dict) and item.get(field) == value:
            count += 1
    return count


def group_by_field(items: List[dict], field: str) -> dict:
    """
    Group items by a field value.
    
    Usage in SchemaMap:
        @compute(group_by_field(products, "category")) : productsByCategory
    """
    if not items or not isinstance(items, list):
        return {}
    
    groups = {}
    for item in items:
        if isinstance(item, dict) and field in item:
            key = str(item[field])
            if key not in groups:
                groups[key] = []
            groups[key].append(item)
    return groups


# ============================================================================
# Business Logic Functions
# ============================================================================

def calculate_shipping(subtotal: float, weight: float = 0, 
                       method: str = "standard") -> float:
    """
    Calculate shipping cost based on order details.
    
    Usage in SchemaMap:
        @compute(calculate_shipping(order.subtotal, order.totalWeight, order.shippingMethod)) : order.shipping
    """
    subtotal = float(subtotal)
    weight = float(weight) if weight else 0
    
    # Free shipping over $100
    if subtotal >= 100:
        return 0.0
    
    rates = {
        "standard": 5.99,
        "express": 12.99,
        "overnight": 24.99
    }
    
    base = rates.get(method, 5.99)
    
    # Add weight-based surcharge
    if weight > 10:
        base += (weight - 10) * 0.50
    
    return round(base, 2)


def determine_tier(total_spent: float) -> str:
    """
    Determine customer tier based on total spent.
    
    Usage in SchemaMap:
        @compute(determine_tier(customer.totalSpent)) : customer.tier
    """
    total = float(total_spent) if total_spent else 0
    
    if total >= 10000:
        return "PLATINUM"
    elif total >= 5000:
        return "GOLD"
    elif total >= 1000:
        return "SILVER"
    return "BRONZE"


def generate_order_number(prefix: str = "ORD", timestamp: str = None) -> str:
    """
    Generate a unique order number.
    
    Usage in SchemaMap:
        @compute(generate_order_number("ORD")) : order.orderNumber
    """
    import uuid
    ts = datetime.now().strftime("%Y%m%d")
    short_uuid = str(uuid.uuid4())[:8].upper()
    return f"{prefix}-{ts}-{short_uuid}"
