"""
Generated Transformer - examples/transformation/showcase/ecommerce/order_transformation.smap
Generated: 2026-01-30T02:39:30.479138
JsonTools SchemaMap Compiler v1.4.0
"""

from __future__ import annotations
import re
import uuid
from datetime import datetime
from typing import Any, Dict, List, Callable


class ECommerceTransformer:
    """Compiled SchemaMap Transformer."""

    def __init__(self):
        self._lookups = {
            "status_codes": {
                "NEW": "PENDING",
                "PND": "PENDING",
                "CNF": "CONFIRMED",
                "PROC": "PROCESSING",
                "PICK": "PROCESSING",
                "PACK": "PROCESSING",
                "SHIP": "SHIPPED",
                "INTRANS": "SHIPPED",
                "DLVR": "DELIVERED",
                "CXL": "CANCELLED",
                "VOID": "CANCELLED",
                "RFD": "REFUNDED",
            },
            "customer_types": {
                "P": "INDIVIDUAL",
                "B": "BUSINESS",
                "G": "GOVERNMENT",
                "I": "INDIVIDUAL",
            },
            "gender_codes": {
                "M": "MALE",
                "F": "FEMALE",
                "O": "OTHER",
                "U": "UNSPECIFIED",
            },
            "loyalty_tiers": {
                "B": "BRONZE",
                "S": "SILVER",
                "G": "GOLD",
                "P": "PLATINUM",
                "D": "DIAMOND",
            },
            "phone_types": {
                "M": "MOBILE",
                "H": "HOME",
                "W": "WORK",
                "C": "MOBILE",
            },
            "contact_prefs": {
                "E": "EMAIL",
                "P": "PHONE",
                "S": "SMS",
                "M": "EMAIL",
            },
            "payment_methods": {
                "CC": "CREDIT_CARD",
                "DEBIT": "DEBIT_CARD",
                "PAYPAL": "PAYPAL",
                "LOYALTY": "LOYALTY_POINTS",
                "GC": "GIFT_CARD",
            },
            "channels": {
                "WEB": "WEB",
                "MOB": "MOBILE",
                "STORE": "STORE",
                "POS": "STORE",
                "PHONE": "PHONE",
                "API": "API",
            },
            "priorities": {
                "Y": "PRIORITY",
                "E": "EXPRESS",
                "N": "STANDARD",
            },
            "address_types": {
                "B": "BILLING",
                "S": "SHIPPING",
            },
            "country_names": {
                "US": "United States",
                "CA": "Canada",
                "MX": "Mexico",
                "UK": "United Kingdom",
                "GB": "United Kingdom",
            },
        }
        self._external_functions: Dict[str, Callable] = {}
        self._null_handling = "omit"

    def register_function(self, name: str, func: Callable) -> "ECommerceTransformer":
        self._external_functions[name] = func
        return self

    def transform(self, source: Dict[str, Any]) -> Dict[str, Any]:
        target: Dict[str, Any] = {}
        
        _v = self._evaluate_expr("generate_order_id(order_header.order_num,order_header.channel,order_header.order_date)", source)
        self._set_value(target, "orderId", _v)

        _v = self._get_value(source, "order_header.order_num")
        _v = (lambda _v: re.sub(r'\\s+', ' ', str(_v)).strip() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "orderNumber", _v)

        _v = self._evaluate_expr("parse_legacy_date(order_header.order_date,order_header.order_time)", source)
        self._set_value(target, "orderDate", _v)

        _v = self._get_value(source, "order_header.order_status")
        _v = (lambda _v: str(_v).upper() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        _v = self._lookup("status_codes", _v)
        self._set_value(target, "status", _v)

        _v = self._get_value(source, "order_header.priority_flag")
        _v = self._lookup("priorities", _v)
        self._set_value(target, "priority", _v)

        _v = self._get_value(source, "order_header.notes")
        _v = (lambda _v: re.sub(r'\\s+', ' ', str(_v)).strip() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "notes", _v)

        _v = self._get_value(source, "order_header.channel")
        _v = self._lookup("channels", _v)
        self._set_value(target, "channel.type", _v)

        _v = self._get_value(source, "order_header.store_id")
        self._set_value(target, "channel.storeId", _v)

        _v = self._get_value(source, "order_header.terminal_id")
        self._set_value(target, "channel.terminalId", _v)

        _v = self._get_value(source, "order_header.cashier_id")
        self._set_value(target, "channel.associateId", _v)

        _v = self._get_value(source, "order_header.gift_flag")
        _v = str(_v).upper() in ('Y','YES','TRUE','1','T') if _v is not None else False
        self._set_value(target, "flags.isGift", _v)

        _v = self._get_value(source, "order_header.priority_flag")
        _v = str(_v).upper() in ('Y','YES','TRUE','1','T') if _v is not None else False
        self._set_value(target, "flags.isPriority", _v)

        _v = self._get_value(source, "customer_info.tax_exempt")
        _v = str(_v).upper() in ('Y','YES','TRUE','1','T') if _v is not None else False
        self._set_value(target, "flags.isTaxExempt", _v)

        _v = self._get_value(source, "shipping_info.signature_required")
        _v = str(_v).upper() in ('Y','YES','TRUE','1','T') if _v is not None else False
        self._set_value(target, "flags.requiresSignature", _v)

        _v = self._get_value(source, "customer_info.cust_id")
        _v = (lambda _v: re.sub(r'\\s+', ' ', str(_v)).strip() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "customer.customerId", _v)

        _v = self._get_value(source, "customer_info.cust_type")
        _v = self._lookup("customer_types", _v)
        self._set_value(target, "customer.customerType", _v)

        _v = self._evaluate_expr("format_full_name(customer_info.first_nm,customer_info.middle_nm,customer_info.last_nm,customer_info.suffix)", source)
        self._set_value(target, "customer.profile.fullName", _v)

        _v = self._get_value(source, "customer_info.first_nm")
        _v = (lambda _v: str(_v).title() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "customer.profile.firstName", _v)

        _v = self._get_value(source, "customer_info.middle_nm")
        _v = (lambda _v: str(_v).title() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "customer.profile.middleName", _v)

        _v = self._get_value(source, "customer_info.last_nm")
        _v = (lambda _v: str(_v).title() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "customer.profile.lastName", _v)

        _v = self._get_value(source, "customer_info.suffix")
        _v = (lambda _v: str(_v).upper() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "customer.profile.suffix", _v)

        _v = self._get_value(source, "customer_info.email_addr")
        _v = (lambda _v: str(_v).lower() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "customer.profile.email", _v)

        _v = self._evaluate_expr("parse_date_to_iso(customer_info.birth_dt)", source)
        self._set_value(target, "customer.profile.dateOfBirth", _v)

        _v = self._evaluate_expr("calculate_age(customer_info.birth_dt)", source)
        self._set_value(target, "customer.profile.age", _v)

        _v = self._get_value(source, "customer_info.gender_cd")
        _v = self._lookup("gender_codes", _v)
        self._set_value(target, "customer.profile.gender", _v)

        _v = self._evaluate_expr("mask_ssn(customer_info.ssn)", source)
        self._set_value(target, "customer.profile.taxId", _v)

        _v = self._evaluate_expr("format_phone(customer_info.phone_primary,\"US\")", source)
        self._set_value(target, "customer.contact.primaryPhone", _v)

        _v = self._evaluate_expr("format_phone(customer_info.phone_secondary,\"US\")", source)
        self._set_value(target, "customer.contact.secondaryPhone", _v)

        _v = self._get_value(source, "customer_info.phone_type")
        _v = self._lookup("phone_types", _v)
        self._set_value(target, "customer.contact.phoneType", _v)

        _v = self._get_value(source, "customer_info.preferred_contact")
        _v = self._lookup("contact_prefs", _v)
        self._set_value(target, "customer.contact.preferredMethod", _v)

        _v = self._get_value(source, "customer_info.language_pref")
        _v = (lambda _v: str(_v).upper() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "customer.preferences.language", _v)

        _v = self._get_value(source, "customer_info.currency_pref")
        _v = (lambda _v: str(_v).upper() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "customer.preferences.currency", _v)

        _v = self._get_value(source, "customer_info.marketing_opt_in")
        _v = str(_v).upper() in ('Y','YES','TRUE','1','T') if _v is not None else False
        self._set_value(target, "customer.preferences.marketingOptIn", _v)

        _v = self._get_value(source, "customer_info.sms_opt_in")
        _v = str(_v).upper() in ('Y','YES','TRUE','1','T') if _v is not None else False
        self._set_value(target, "customer.preferences.smsOptIn", _v)

        _v = self._get_value(source, "customer_info.loyalty_num")
        self._set_value(target, "customer.loyalty.memberId", _v)

        _v = self._get_value(source, "customer_info.loyalty_tier")
        _v = self._lookup("loyalty_tiers", _v)
        self._set_value(target, "customer.loyalty.tier", _v)

        _v = self._get_value(source, "customer_info.loyalty_points")
        _v = int(float(_v)) if _v is not None else None
        self._set_value(target, "customer.loyalty.points", _v)

        _v = self._get_value(source, "customer_info.lifetime_value")
        _v = (lambda _v: round(float(_v), 2) if _v is not None else None)((lambda _v: float(_v) if _v is not None else None)(_v))
        self._set_value(target, "customer.loyalty.lifetimeValue", _v)

        _v = self._evaluate_expr("calculate_loyalty_tier_expiration(customer_info.loyalty_tier,customer_info.loyalty_points)", source)
        self._set_value(target, "customer.loyalty.tierExpirationDate", _v)

        _v = self._get_value(source, "customer_info.account_balance")
        _v = (lambda _v: round(float(_v), 2) if _v is not None else None)((lambda _v: float(_v) if _v is not None else None)(_v))
        self._set_value(target, "customer.account.balance", _v)

        _v = self._get_value(source, "customer_info.credit_limit")
        _v = (lambda _v: round(float(_v), 2) if _v is not None else None)((lambda _v: float(_v) if _v is not None else None)(_v))
        self._set_value(target, "customer.account.creditLimit", _v)

        _v = self._evaluate_expr("calculate_credit_available(customer_info.credit_limit,customer_info.account_balance)", source)
        self._set_value(target, "customer.account.creditAvailable", _v)

        _v = self._get_value(source, "billing_address.addr_type")
        _v = self._lookup("address_types", _v)
        self._set_value(target, "addresses.billing.type", _v)

        _v = self._get_value(source, "billing_address.addr_line1")
        _v = (lambda _v: str(_v).title() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "addresses.billing.line1", _v)

        _v = self._get_value(source, "billing_address.addr_line2")
        _v = (lambda _v: str(_v).title() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "addresses.billing.line2", _v)

        _v = self._get_value(source, "billing_address.addr_line3")
        _v = (lambda _v: str(_v).title() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "addresses.billing.line3", _v)

        _v = self._get_value(source, "billing_address.city")
        _v = (lambda _v: str(_v).title() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "addresses.billing.city", _v)

        _v = self._get_value(source, "billing_address.state_prov")
        _v = (lambda _v: str(_v).upper() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "addresses.billing.state", _v)

        _v = self._get_value(source, "billing_address.postal_cd")
        _v = (lambda _v: re.sub(r'\\s+', ' ', str(_v)).strip() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "addresses.billing.postalCode", _v)

        _v = self._get_value(source, "billing_address.country_cd")
        _v = (lambda _v: str(_v).upper() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "addresses.billing.country", _v)

        _v = self._get_value(source, "billing_address.country_cd")
        _v = self._lookup("country_names", _v)
        self._set_value(target, "addresses.billing.countryName", _v)

        _v = self._evaluate_expr("format_address_single_line(billing_address.addr_line1,billing_address.addr_line2,billing_address.addr_line3,billing_address.city,billing_address.state_prov,billing_address.postal_cd,billing_address.country_cd)", source)
        self._set_value(target, "addresses.billing.formatted", _v)

        _v = self._get_value(source, "billing_address.validated")
        _v = str(_v).upper() in ('Y','YES','TRUE','1','T') if _v is not None else False
        self._set_value(target, "addresses.billing.isValidated", _v)

        _v = self._get_value(source, "billing_address.residential")
        _v = str(_v).upper() in ('Y','YES','TRUE','1','T') if _v is not None else False
        self._set_value(target, "addresses.billing.isResidential", _v)

        _v = self._get_value(source, "shipping_address.addr_type")
        _v = self._lookup("address_types", _v)
        self._set_value(target, "addresses.shipping.type", _v)

        _v = self._get_value(source, "shipping_address.addr_line1")
        _v = (lambda _v: str(_v).title() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "addresses.shipping.line1", _v)

        _v = self._get_value(source, "shipping_address.addr_line2")
        _v = (lambda _v: str(_v).title() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "addresses.shipping.line2", _v)

        _v = self._get_value(source, "shipping_address.addr_line3")
        _v = (lambda _v: str(_v).title() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "addresses.shipping.line3", _v)

        _v = self._get_value(source, "shipping_address.city")
        _v = (lambda _v: str(_v).title() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "addresses.shipping.city", _v)

        _v = self._get_value(source, "shipping_address.state_prov")
        _v = (lambda _v: str(_v).upper() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "addresses.shipping.state", _v)

        _v = self._get_value(source, "shipping_address.postal_cd")
        _v = (lambda _v: re.sub(r'\\s+', ' ', str(_v)).strip() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "addresses.shipping.postalCode", _v)

        _v = self._get_value(source, "shipping_address.country_cd")
        _v = (lambda _v: str(_v).upper() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "addresses.shipping.country", _v)

        _v = self._get_value(source, "shipping_address.country_cd")
        _v = self._lookup("country_names", _v)
        self._set_value(target, "addresses.shipping.countryName", _v)

        _v = self._evaluate_expr("format_address_single_line(shipping_address.addr_line1,shipping_address.addr_line2,shipping_address.addr_line3,shipping_address.city,shipping_address.state_prov,shipping_address.postal_cd,shipping_address.country_cd)", source)
        self._set_value(target, "addresses.shipping.formatted", _v)

        _v = self._get_value(source, "shipping_address.validated")
        _v = str(_v).upper() in ('Y','YES','TRUE','1','T') if _v is not None else False
        self._set_value(target, "addresses.shipping.isValidated", _v)

        _v = self._get_value(source, "shipping_address.residential")
        _v = str(_v).upper() in ('Y','YES','TRUE','1','T') if _v is not None else False
        self._set_value(target, "addresses.shipping.isResidential", _v)

        _v = self._get_value(source, "shipping_address.special_instructions")
        _v = (lambda _v: re.sub(r'\\s+', ' ', str(_v)).strip() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "addresses.shipping.specialInstructions", _v)

        _v = self._get_value(source, "line_items[*].line_num")
        _v = self._apply_transform(_v, lambda x: int(float(x)) if x is not None else None)
        self._set_value(target, "items[*].lineNumber", _v)

        _v = self._get_value(source, "line_items[*].item_sku")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: str(x).strip() if x is not None else None), lambda x: str(x).upper() if x is not None else None)
        self._set_value(target, "items[*].sku", _v)

        _v = self._get_value(source, "line_items[*].item_upc")
        self._set_value(target, "items[*].upc", _v)

        _v = self._get_value(source, "line_items[*].item_desc")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: str(x).strip() if x is not None else None), lambda x: str(x).title() if x is not None else None)
        self._set_value(target, "items[*].name", _v)

        _v = self._get_value(source, "line_items[*].item_desc")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: str(x).strip() if x is not None else None), lambda x: re.sub(r'\\s+', ' ', str(x)).strip() if x is not None else None)
        self._set_value(target, "items[*].description", _v)

        _v = self._get_value(source, "line_items[*].category_cd")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: str(x).strip() if x is not None else None), lambda x: str(x).upper() if x is not None else None)
        self._set_value(target, "items[*].category", _v)

        _v = self._get_value(source, "line_items[*].subcategory_cd")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: str(x).strip() if x is not None else None), lambda x: str(x).upper() if x is not None else None)
        self._set_value(target, "items[*].subcategory", _v)

        _v = self._get_value(source, "line_items[*].brand")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: str(x).strip() if x is not None else None), lambda x: str(x).title() if x is not None else None)
        self._set_value(target, "items[*].brand", _v)

        _v = self._get_value(source, "line_items[*].model_num")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: str(x).strip() if x is not None else None), lambda x: str(x).upper() if x is not None else None)
        self._set_value(target, "items[*].model", _v)

        _v = self._get_value(source, "line_items[*].color")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: str(x).strip() if x is not None else None), lambda x: str(x).title() if x is not None else None)
        self._set_value(target, "items[*].variant.color", _v)

        _v = self._get_value(source, "line_items[*].size")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: str(x).strip() if x is not None else None), lambda x: str(x).upper() if x is not None else None)
        self._set_value(target, "items[*].variant.size", _v)

        _v = self._get_value(source, "line_items[*].qty_ordered")
        _v = self._apply_transform(_v, lambda x: int(float(x)) if x is not None else None)
        self._set_value(target, "items[*].quantity.ordered", _v)

        _v = self._get_value(source, "line_items[*].qty_shipped")
        _v = self._apply_transform(_v, lambda x: int(float(x)) if x is not None else None)
        self._set_value(target, "items[*].quantity.shipped", _v)

        _v = self._get_value(source, "line_items[*].qty_backordered")
        _v = self._apply_transform(_v, lambda x: int(float(x)) if x is not None else None)
        self._set_value(target, "items[*].quantity.backordered", _v)

        _v = self._get_value(source, "line_items[*].unit_price")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: float(x) if x is not None else None), lambda x: round(float(x), 2) if x is not None else None)
        self._set_value(target, "items[*].pricing.unitPrice", _v)

        _v = self._get_value(source, "line_items[*].unit_cost")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: float(x) if x is not None else None), lambda x: round(float(x), 2) if x is not None else None)
        self._set_value(target, "items[*].pricing.unitCost", _v)

        _v = self._get_value(source, "line_items[*].discount_pct")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: float(x) if x is not None else None), lambda x: round(float(x), 3) if x is not None else None)
        self._set_value(target, "items[*].pricing.discountPercent", _v)

        _v = self._get_value(source, "line_items[*].discount_amt")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: float(x) if x is not None else None), lambda x: round(float(x), 2) if x is not None else None)
        self._set_value(target, "items[*].pricing.discountAmount", _v)

        _v = self._get_value(source, "line_items[*].extended_price")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: float(x) if x is not None else None), lambda x: round(float(x), 2) if x is not None else None)
        self._set_value(target, "items[*].pricing.extendedPrice", _v)

        _v = self._get_value(source, "line_items[*].tax_rate")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: float(x) if x is not None else None), lambda x: round(float(x), 3) if x is not None else None)
        self._set_value(target, "items[*].pricing.taxRate", _v)

        _v = self._get_value(source, "line_items[*].tax_amt")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: float(x) if x is not None else None), lambda x: round(float(x), 2) if x is not None else None)
        self._set_value(target, "items[*].pricing.taxAmount", _v)

        _v = self._get_value(source, "line_items[*].fulfillment_status")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: str(x).strip() if x is not None else None), lambda x: str(x).upper() if x is not None else None)
        self._set_value(target, "items[*].fulfillment.status", _v)

        _v = self._get_value(source, "line_items[*].tracking_num")
        self._set_value(target, "items[*].fulfillment.trackingNumber", _v)

        _v = self._get_value(source, "line_items[*].carrier_cd")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: str(x).strip() if x is not None else None), lambda x: str(x).upper() if x is not None else None)
        self._set_value(target, "items[*].fulfillment.carrier", _v)

        _v = self._get_value(source, "line_items[*].weight_lbs")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: float(x) if x is not None else None), lambda x: round(float(x), 2) if x is not None else None)
        self._set_value(target, "items[*].attributes.weight", _v)

        _v = self._get_value(source, "line_items[*].hazmat_flag")
        _v = self._apply_transform(_v, lambda x: str(x).upper() in ('Y','YES','TRUE','1','T') if x is not None else False)
        self._set_value(target, "items[*].attributes.isHazmat", _v)

        _v = self._get_value(source, "line_items[*].serial_num")
        self._set_value(target, "items[*].attributes.serialNumber", _v)

        _v = self._get_value(source, "line_items[*].lot_num")
        self._set_value(target, "items[*].attributes.lotNumber", _v)

        _v = self._get_value(source, "line_items[*].gift_wrap")
        _v = self._apply_transform(_v, lambda x: str(x).upper() in ('Y','YES','TRUE','1','T') if x is not None else False)
        self._set_value(target, "items[*].gift.isGiftWrapped", _v)

        _v = self._get_value(source, "line_items[*].gift_message")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: str(x).strip() if x is not None else None), lambda x: re.sub(r'\\s+', ' ', str(x)).strip() if x is not None else None)
        self._set_value(target, "items[*].gift.message", _v)

        _v = self._get_value(source, "line_items[*].warranty_sku")
        self._set_value(target, "items[*].warranty.sku", _v)

        _v = self._get_value(source, "line_items[*].warranty_price")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: float(x) if x is not None else None), lambda x: round(float(x), 2) if x is not None else None)
        self._set_value(target, "items[*].warranty.price", _v)

        _v = self._get_value(source, "payment_info[*].payment_seq")
        _v = self._apply_transform(_v, lambda x: int(float(x)) if x is not None else None)
        self._set_value(target, "payments[*].sequence", _v)

        _v = self._get_value(source, "payment_info[*].payment_method")
        _v = self._apply_transform(_v, lambda x: self._lookup("payment_methods", x))
        self._set_value(target, "payments[*].method", _v)

        _v = self._get_value(source, "payment_info[*].payment_amt")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: float(x) if x is not None else None), lambda x: round(float(x), 2) if x is not None else None)
        self._set_value(target, "payments[*].amount", _v)

        _v = self._get_value(source, "payment_info[*].card_type")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: str(x).strip() if x is not None else None), lambda x: str(x).upper() if x is not None else None)
        self._set_value(target, "payments[*].card.type", _v)

        _v = self._get_value(source, "payment_info[*].card_last4")
        self._set_value(target, "payments[*].card.lastFour", _v)

        _v = self._get_value(source, "payment_info[*].card_exp")
        self._set_value(target, "payments[*].card.expiration", _v)

        _v = self._get_value(source, "payment_info[*].card_holder")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: str(x).strip() if x is not None else None), lambda x: str(x).upper() if x is not None else None)
        self._set_value(target, "payments[*].card.holderName", _v)

        _v = self._get_value(source, "payment_info[*].transaction_id")
        self._set_value(target, "payments[*].transaction.id", _v)

        _v = self._get_value(source, "payment_info[*].auth_code")
        self._set_value(target, "payments[*].transaction.authCode", _v)

        _v = self._get_value(source, "payment_info[*].avs_result")
        self._set_value(target, "payments[*].verification.avsResult", _v)

        _v = self._get_value(source, "payment_info[*].cvv_result")
        self._set_value(target, "payments[*].verification.cvvResult", _v)

        _v = self._get_value(source, "payment_info[*].billing_addr_match")
        _v = self._apply_transform(_v, lambda x: str(x).upper() in ('Y','YES','TRUE','1','T') if x is not None else False)
        self._set_value(target, "payments[*].verification.addressMatch", _v)

        _v = self._get_value(source, "order_totals.subtotal")
        _v = (lambda _v: round(float(_v), 2) if _v is not None else None)((lambda _v: float(_v) if _v is not None else None)(_v))
        self._set_value(target, "totals.subtotal", _v)

        _v = self._get_value(source, "order_totals.discount_total")
        _v = (lambda _v: round(float(_v), 2) if _v is not None else None)((lambda _v: float(_v) if _v is not None else None)(_v))
        self._set_value(target, "totals.discount", _v)

        _v = self._get_value(source, "order_totals.tax_total")
        _v = (lambda _v: round(float(_v), 2) if _v is not None else None)((lambda _v: float(_v) if _v is not None else None)(_v))
        self._set_value(target, "totals.tax", _v)

        _v = self._get_value(source, "order_totals.shipping_cost")
        _v = (lambda _v: round(float(_v), 2) if _v is not None else None)((lambda _v: float(_v) if _v is not None else None)(_v))
        self._set_value(target, "totals.shipping", _v)

        _v = self._get_value(source, "order_totals.handling_fee")
        _v = (lambda _v: round(float(_v), 2) if _v is not None else None)((lambda _v: float(_v) if _v is not None else None)(_v))
        self._set_value(target, "totals.handling", _v)

        _v = self._get_value(source, "order_totals.gift_wrap_total")
        _v = (lambda _v: round(float(_v), 2) if _v is not None else None)((lambda _v: float(_v) if _v is not None else None)(_v))
        self._set_value(target, "totals.giftWrap", _v)

        _v = self._get_value(source, "order_totals.warranty_total")
        _v = (lambda _v: round(float(_v), 2) if _v is not None else None)((lambda _v: float(_v) if _v is not None else None)(_v))
        self._set_value(target, "totals.warranty", _v)

        _v = self._get_value(source, "order_totals.order_total")
        _v = (lambda _v: round(float(_v), 2) if _v is not None else None)((lambda _v: float(_v) if _v is not None else None)(_v))
        self._set_value(target, "totals.grandTotal", _v)

        _v = self._get_value(source, "order_totals.amount_paid")
        _v = (lambda _v: round(float(_v), 2) if _v is not None else None)((lambda _v: float(_v) if _v is not None else None)(_v))
        self._set_value(target, "totals.paid", _v)

        _v = self._get_value(source, "order_totals.balance_due")
        _v = (lambda _v: round(float(_v), 2) if _v is not None else None)((lambda _v: float(_v) if _v is not None else None)(_v))
        self._set_value(target, "totals.due", _v)

        _v = self._get_value(source, "order_totals.currency_cd")
        _v = (lambda _v: str(_v).upper() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "totals.currency", _v)

        _v = self._evaluate_expr("count_total_quantity(line_items)", source)
        self._set_value(target, "totals.totalQuantity", _v)

        _v = self._evaluate_expr("sum_item_weights(line_items)", source)
        self._set_value(target, "totals.totalWeight", _v)

        _v = self._evaluate_expr("calculate_effective_tax_rate(order_totals.tax_total,order_totals.subtotal)", source)
        self._set_value(target, "totals.effectiveTaxRate", _v)

        _v = self._evaluate_expr("calculate_total_savings(order_totals.discount_total,order_totals.shipping_discount,0)", source)
        self._set_value(target, "totals.totalSavings", _v)

        _v = self._evaluate_expr("count(line_items)", source)
        self._set_value(target, "totals.itemCount", _v)

        _v = self._get_value(source, "shipping_info.ship_method")
        _v = (lambda _v: str(_v).upper() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "shipping.method", _v)

        _v = self._get_value(source, "shipping_info.ship_carrier")
        _v = (lambda _v: str(_v).upper() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "shipping.carrier", _v)

        _v = self._get_value(source, "shipping_info.ship_speed")
        _v = (lambda _v: re.sub(r'\\s+', ' ', str(_v)).strip() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "shipping.speed", _v)

        _v = self._get_value(source, "shipping_info.package_count")
        _v = int(float(_v)) if _v is not None else None
        self._set_value(target, "shipping.packageCount", _v)

        _v = self._get_value(source, "shipping_info.ship_weight_total")
        _v = (lambda _v: round(float(_v), 2) if _v is not None else None)((lambda _v: float(_v) if _v is not None else None)(_v))
        self._set_value(target, "shipping.totalWeight", _v)

        _v = self._get_value(source, "shipping_info.insurance_amt")
        _v = (lambda _v: round(float(_v), 2) if _v is not None else None)((lambda _v: float(_v) if _v is not None else None)(_v))
        self._set_value(target, "shipping.insuranceAmount", _v)

        _v = self._get_value(source, "shipping_info.tracking_numbers")
        self._set_value(target, "shipping.trackingNumbers", _v)

        _v = self._get_value(source, "promotions_applied[*].promo_cd")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: str(x).strip() if x is not None else None), lambda x: str(x).upper() if x is not None else None)
        self._set_value(target, "promotions[*].code", _v)

        _v = self._get_value(source, "promotions_applied[*].promo_desc")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: str(x).strip() if x is not None else None), lambda x: re.sub(r'\\s+', ' ', str(x)).strip() if x is not None else None)
        self._set_value(target, "promotions[*].description", _v)

        _v = self._get_value(source, "promotions_applied[*].promo_type")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: str(x).strip() if x is not None else None), lambda x: str(x).upper() if x is not None else None)
        self._set_value(target, "promotions[*].type", _v)

        _v = self._get_value(source, "promotions_applied[*].promo_savings")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: float(x) if x is not None else None), lambda x: round(float(x), 2) if x is not None else None)
        self._set_value(target, "promotions[*].savings", _v)

        _v = '2.0'
        _v = _v
        self._set_value(target, "metadata.version", _v)

        _v = 'v2'
        _v = _v
        self._set_value(target, "metadata.apiVersion", _v)

        _v = self._get_value(source, "audit_info.source_system")
        _v = (lambda _v: str(_v).upper() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "metadata.sourceSystem", _v)

        _v = datetime.now().isoformat() + "Z"
        self._set_value(target, "metadata.transformedAt", _v)

        _v = str(uuid.uuid4())
        self._set_value(target, "metadata.transformationId", _v)

        
        if self._null_handling == "omit":
            target = self._remove_nulls(target)
        return target

    def transform_batch(self, items: List[Dict]) -> List[Dict]:
        return [self.transform(item) for item in items]

    def _get_value(self, data: Any, path: str) -> Any:
        if not path or data is None:
            return data
        if "[*]" in path:
            return self._get_array_values(data, path)
        current = data
        for seg in path.split("."):
            if current is None:
                return None
            if "[" in seg:
                key = seg[:seg.index("[")]
                idx = seg[seg.index("[")+1:seg.index("]")]
                if key:
                    current = current.get(key) if isinstance(current, dict) else None
                if current and isinstance(current, list) and idx != "*":
                    current = current[int(idx)] if -len(current) <= int(idx) < len(current) else None
            else:
                current = current.get(seg) if isinstance(current, dict) else None
        return current

    def _get_array_values(self, data: Any, path: str) -> List[Any]:
        parts = path.split("[*]")
        before = parts[0]
        after = parts[1].lstrip(".") if len(parts) > 1 else ""
        arr = self._get_value(data, before) if before else data
        if not isinstance(arr, list):
            return []
        if not after:
            return arr
        return [self._get_value(item, after) for item in arr]

    def _set_value(self, data: Dict, path: str, value: Any) -> None:
        if "[*]" in path:
            self._set_array_value(data, path, value)
            return
        segments = path.split(".")
        current = data
        for seg in segments[:-1]:
            if seg not in current:
                current[seg] = {}
            current = current[seg]
        current[segments[-1]] = value

    def _set_array_value(self, data: Dict, path: str, value: Any) -> None:
        parts = path.split("[*]")
        before = parts[0]
        after = parts[1].lstrip(".") if len(parts) > 1 else ""
        if before not in data:
            data[before] = []
        arr = data[before]
        if isinstance(value, list):
            while len(arr) < len(value):
                arr.append({})
            for i, v in enumerate(value):
                if after:
                    self._set_nested(arr[i], after, v)
                else:
                    arr[i] = v

    def _set_nested(self, data: Dict, path: str, value: Any) -> None:
        segments = path.split(".")
        current = data
        for seg in segments[:-1]:
            if seg not in current:
                current[seg] = {}
            current = current[seg]
        current[segments[-1]] = value

    def _remove_nulls(self, data: Any) -> Any:
        if isinstance(data, dict):
            return {k: self._remove_nulls(v) for k, v in data.items() if v is not None}
        elif isinstance(data, list):
            return [self._remove_nulls(v) for v in data if v is not None]
        return data

    def _lookup(self, table: str, value: Any) -> Any:
        return self._lookups.get(table, {}).get(value, value)

    def _apply_transform(self, value: Any, func) -> Any:
        """Apply a transform function, handling lists element-wise."""
        if isinstance(value, list):
            return [func(v) for v in value]
        return func(value)

    def _evaluate_expr(self, expr: str, source: Dict) -> Any:
        import re as _re
        m = _re.match(r"(\w+)\((.*)\)", expr)
        if m:
            fn, args = m.group(1), m.group(2)
            if fn in self._external_functions:
                parsed = self._parse_args(args, source)
                return self._external_functions[fn](*parsed)
            if fn == "sum":
                vals = self._get_value(source, args)
                return sum(float(v or 0) for v in vals) if isinstance(vals, list) else 0
            if fn == "count":
                vals = self._get_value(source, args)
                return len(vals) if isinstance(vals, list) else 0
        return self._get_value(source, expr)

    def _parse_args(self, args_str: str, source: Dict) -> List[Any]:
        args = []
        for arg in args_str.split(","):
            arg = arg.strip()
            if not arg:
                continue
            try:
                args.append(float(arg) if "." in arg else int(arg))
                continue
            except ValueError:
                pass
            if (arg.startswith('"') and arg.endswith('"')) or (arg.startswith("'") and arg.endswith("'")):
                args.append(arg[1:-1])
                continue
            args.append(self._get_value(source, arg))
        return args


if __name__ == "__main__":
    import json, sys
    t = ECommerceTransformer()
    data = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else {}
    print(json.dumps(t.transform(data), indent=2, default=str))
