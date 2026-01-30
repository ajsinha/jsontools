"""
Generated Transformer - examples/comprehensive/ecommerce/order_transform.smap
Generated: 2026-01-30T02:39:03.674937
JsonChamp SchemaMap Compiler v1.4.0
"""

from __future__ import annotations
import re
import uuid
from datetime import datetime
from typing import Any, Dict, List, Callable


class OrderTransformer:
    """Compiled SchemaMap Transformer."""

    def __init__(self):
        self._lookups = {
            "order_status": {
                "NEW": "PENDING",
                "PND": "PENDING",
                "CNF": "CONFIRMED",
                "PROC": "PROCESSING",
                "SHIP": "SHIPPED",
                "DLVR": "DELIVERED",
                "CXL": "CANCELLED",
            },
            "customer_type": {
                "P": "INDIVIDUAL",
                "B": "BUSINESS",
                "G": "GOVERNMENT",
            },
            "gender": {
                "M": "MALE",
                "F": "FEMALE",
                "O": "OTHER",
            },
            "loyalty_tier": {
                "B": "BRONZE",
                "S": "SILVER",
                "G": "GOLD",
                "P": "PLATINUM",
                "D": "DIAMOND",
            },
            "contact_pref": {
                "E": "EMAIL",
                "P": "PHONE",
                "S": "SMS",
            },
            "payment_method": {
                "CC": "CREDIT_CARD",
                "DC": "DEBIT_CARD",
                "PP": "PAYPAL",
                "LOYALTY": "LOYALTY_POINTS",
                "GC": "GIFT_CARD",
            },
            "country_name": {
                "US": "United States",
                "CA": "Canada",
                "MX": "Mexico",
                "UK": "United Kingdom",
            },
        }
        self._external_functions: Dict[str, Callable] = {}
        self._null_handling = "omit"

    def register_function(self, name: str, func: Callable) -> "OrderTransformer":
        self._external_functions[name] = func
        return self

    def transform(self, source: Dict[str, Any]) -> Dict[str, Any]:
        target: Dict[str, Any] = {}
        
        _v = self._evaluate_expr("generate_order_id(header.orderNumber,header.channel)", source)
        self._set_value(target, "orderId", _v)

        _v = self._get_value(source, "header.orderNumber")
        _v = (lambda _v: re.sub(r'\\s+', ' ', str(_v)).strip() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "orderNumber", _v)

        _v = self._evaluate_expr("parse_datetime(header.orderDate,header.orderTime)", source)
        self._set_value(target, "orderTimestamp", _v)

        _v = self._get_value(source, "header.status")
        _v = (lambda _v: str(_v).upper() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        _v = self._lookup("order_status", _v)
        self._set_value(target, "status", _v)

        _v = self._get_value(source, "header.channel")
        _v = (lambda _v: str(_v).upper() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "channel.type", _v)

        _v = self._get_value(source, "header.storeCode")
        self._set_value(target, "channel.storeId", _v)

        _v = self._get_value(source, "header.register")
        self._set_value(target, "channel.terminalId", _v)

        _v = self._get_value(source, "header.associateId")
        self._set_value(target, "channel.associateId", _v)

        _v = self._get_value(source, "header.giftOrder")
        _v = str(_v).upper() in ('Y','YES','TRUE','1','T') if _v is not None else False
        self._set_value(target, "flags.isGift", _v)

        _v = self._get_value(source, "header.priorityCode")
        _v = str(_v).upper() in ('Y','YES','TRUE','1','T') if _v is not None else False
        self._set_value(target, "flags.isPriority", _v)

        _v = self._get_value(source, "header.orderNotes")
        _v = (lambda _v: re.sub(r'\\s+', ' ', str(_v)).strip() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "notes", _v)

        _v = self._get_value(source, "customer.customerId")
        _v = (lambda _v: re.sub(r'\\s+', ' ', str(_v)).strip() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "customer.customerId", _v)

        _v = self._get_value(source, "customer.customerType")
        _v = self._lookup("customer_type", _v)
        self._set_value(target, "customer.type", _v)

        _v = self._evaluate_expr("format_full_name(customer.firstName,customer.middleName,customer.lastName,customer.suffix)", source)
        self._set_value(target, "customer.profile.fullName", _v)

        _v = self._get_value(source, "customer.firstName")
        _v = (lambda _v: str(_v).title() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "customer.profile.firstName", _v)

        _v = self._get_value(source, "customer.middleName")
        _v = (lambda _v: str(_v).title() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "customer.profile.middleName", _v)

        _v = self._get_value(source, "customer.lastName")
        _v = (lambda _v: str(_v).title() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "customer.profile.lastName", _v)

        _v = self._get_value(source, "customer.suffix")
        _v = (lambda _v: str(_v).upper() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "customer.profile.suffix", _v)

        _v = self._evaluate_expr("format_display_name(customer.firstName,customer.lastName)", source)
        self._set_value(target, "customer.profile.displayName", _v)

        _v = self._evaluate_expr("clean_email(customer.email)", source)
        self._set_value(target, "customer.profile.email", _v)

        _v = self._evaluate_expr("format_date(customer.birthDate)", source)
        self._set_value(target, "customer.profile.dateOfBirth", _v)

        _v = self._evaluate_expr("calculate_age(customer.birthDate)", source)
        self._set_value(target, "customer.profile.age", _v)

        _v = self._get_value(source, "customer.gender")
        _v = self._lookup("gender", _v)
        self._set_value(target, "customer.profile.gender", _v)

        _v = self._evaluate_expr("mask_ssn(customer.ssn)", source)
        self._set_value(target, "customer.profile.taxIdMasked", _v)

        _v = self._evaluate_expr("format_phone(customer.primaryPhone,\"US\")", source)
        self._set_value(target, "customer.contact.primaryPhone", _v)

        _v = self._evaluate_expr("format_phone(customer.secondaryPhone,\"US\")", source)
        self._set_value(target, "customer.contact.secondaryPhone", _v)

        _v = self._evaluate_expr("format_phone_e164(customer.primaryPhone,\"1\")", source)
        self._set_value(target, "customer.contact.primaryPhoneE164", _v)

        _v = self._get_value(source, "customer.preferredContact")
        _v = self._lookup("contact_pref", _v)
        self._set_value(target, "customer.contact.preferredMethod", _v)

        _v = self._get_value(source, "customer.language")
        _v = (lambda _v: str(_v).upper() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "customer.preferences.language", _v)

        _v = self._get_value(source, "customer.currency")
        _v = (lambda _v: str(_v).upper() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "customer.preferences.currency", _v)

        _v = self._get_value(source, "customer.marketingOptIn")
        _v = str(_v).upper() in ('Y','YES','TRUE','1','T') if _v is not None else False
        self._set_value(target, "customer.preferences.marketingOptIn", _v)

        _v = self._get_value(source, "customer.smsOptIn")
        _v = str(_v).upper() in ('Y','YES','TRUE','1','T') if _v is not None else False
        self._set_value(target, "customer.preferences.smsOptIn", _v)

        _v = self._get_value(source, "customer.loyaltyNumber")
        self._set_value(target, "customer.loyalty.memberId", _v)

        _v = self._get_value(source, "customer.loyaltyTier")
        _v = self._lookup("loyalty_tier", _v)
        self._set_value(target, "customer.loyalty.tier", _v)

        _v = self._get_value(source, "customer.loyaltyPoints")
        _v = int(float(_v)) if _v is not None else None
        self._set_value(target, "customer.loyalty.points", _v)

        _v = self._get_value(source, "customer.lifetimeSpend")
        _v = (lambda _v: round(float(_v), 2) if _v is not None else None)((lambda _v: float(_v) if _v is not None else None)(_v))
        self._set_value(target, "customer.loyalty.lifetimeValue", _v)

        _v = self._evaluate_expr("calculate_tier_expiration(customer.loyaltyTier,customer.loyaltyPoints)", source)
        self._set_value(target, "customer.loyalty.tierExpiration", _v)

        _v = self._evaluate_expr("determine_customer_segment(customer.lifetimeSpend,customer.loyaltyTier)", source)
        self._set_value(target, "customer.loyalty.segment", _v)

        _v = self._get_value(source, "customer.accountBalance")
        _v = (lambda _v: round(float(_v), 2) if _v is not None else None)((lambda _v: float(_v) if _v is not None else None)(_v))
        self._set_value(target, "customer.account.balance", _v)

        _v = self._get_value(source, "customer.creditLimit")
        _v = (lambda _v: round(float(_v), 2) if _v is not None else None)((lambda _v: float(_v) if _v is not None else None)(_v))
        self._set_value(target, "customer.account.creditLimit", _v)

        _v = self._evaluate_expr("calculate_credit_available(customer.creditLimit,customer.accountBalance)", source)
        self._set_value(target, "customer.account.creditAvailable", _v)

        _v = self._get_value(source, "billTo.line1")
        _v = (lambda _v: str(_v).title() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "addresses.billing.line1", _v)

        _v = self._get_value(source, "billTo.line2")
        _v = (lambda _v: str(_v).title() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "addresses.billing.line2", _v)

        _v = self._get_value(source, "billTo.line3")
        _v = (lambda _v: str(_v).title() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "addresses.billing.line3", _v)

        _v = self._get_value(source, "billTo.city")
        _v = (lambda _v: str(_v).title() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "addresses.billing.city", _v)

        _v = self._get_value(source, "billTo.state")
        _v = (lambda _v: str(_v).upper() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "addresses.billing.state", _v)

        _v = self._get_value(source, "billTo.zip")
        self._set_value(target, "addresses.billing.postalCode", _v)

        _v = self._get_value(source, "billTo.country")
        _v = (lambda _v: str(_v).upper() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "addresses.billing.country", _v)

        _v = self._get_value(source, "billTo.country")
        _v = self._lookup("country_name", _v)
        self._set_value(target, "addresses.billing.countryName", _v)

        _v = self._get_value(source, "billTo.validated")
        _v = str(_v).upper() in ('Y','YES','TRUE','1','T') if _v is not None else False
        self._set_value(target, "addresses.billing.isValidated", _v)

        _v = self._get_value(source, "billTo.residential")
        _v = str(_v).upper() in ('Y','YES','TRUE','1','T') if _v is not None else False
        self._set_value(target, "addresses.billing.isResidential", _v)

        _v = self._evaluate_expr("format_address(billTo.line1,billTo.line2,billTo.line3,billTo.city,billTo.state,billTo.zip,billTo.country)", source)
        self._set_value(target, "addresses.billing.formatted", _v)

        _v = self._get_value(source, "shipTo.line1")
        _v = (lambda _v: str(_v).title() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "addresses.shipping.line1", _v)

        _v = self._get_value(source, "shipTo.line2")
        _v = (lambda _v: str(_v).title() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "addresses.shipping.line2", _v)

        _v = self._get_value(source, "shipTo.line3")
        _v = (lambda _v: str(_v).title() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "addresses.shipping.line3", _v)

        _v = self._get_value(source, "shipTo.city")
        _v = (lambda _v: str(_v).title() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "addresses.shipping.city", _v)

        _v = self._get_value(source, "shipTo.state")
        _v = (lambda _v: str(_v).upper() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "addresses.shipping.state", _v)

        _v = self._get_value(source, "shipTo.zip")
        self._set_value(target, "addresses.shipping.postalCode", _v)

        _v = self._get_value(source, "shipTo.country")
        _v = (lambda _v: str(_v).upper() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "addresses.shipping.country", _v)

        _v = self._get_value(source, "shipTo.country")
        _v = self._lookup("country_name", _v)
        self._set_value(target, "addresses.shipping.countryName", _v)

        _v = self._get_value(source, "shipTo.validated")
        _v = str(_v).upper() in ('Y','YES','TRUE','1','T') if _v is not None else False
        self._set_value(target, "addresses.shipping.isValidated", _v)

        _v = self._get_value(source, "shipTo.residential")
        _v = str(_v).upper() in ('Y','YES','TRUE','1','T') if _v is not None else False
        self._set_value(target, "addresses.shipping.isResidential", _v)

        _v = self._get_value(source, "shipTo.instructions")
        _v = (lambda _v: re.sub(r'\\s+', ' ', str(_v)).strip() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "addresses.shipping.instructions", _v)

        _v = self._evaluate_expr("format_address(shipTo.line1,shipTo.line2,shipTo.line3,shipTo.city,shipTo.state,shipTo.zip,shipTo.country)", source)
        self._set_value(target, "addresses.shipping.formatted", _v)

        _v = self._get_value(source, "items[*].lineNum")
        _v = self._apply_transform(_v, lambda x: int(float(x)) if x is not None else None)
        self._set_value(target, "lineItems[*].lineNumber", _v)

        _v = self._get_value(source, "items[*].sku")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: str(x).strip() if x is not None else None), lambda x: str(x).upper() if x is not None else None)
        self._set_value(target, "lineItems[*].sku", _v)

        _v = self._get_value(source, "items[*].upc")
        self._set_value(target, "lineItems[*].upc", _v)

        _v = self._get_value(source, "items[*].description")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: str(x).strip() if x is not None else None), lambda x: str(x).title() if x is not None else None)
        self._set_value(target, "lineItems[*].name", _v)

        _v = self._get_value(source, "items[*].category")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: str(x).strip() if x is not None else None), lambda x: str(x).upper() if x is not None else None)
        self._set_value(target, "lineItems[*].category", _v)

        _v = self._get_value(source, "items[*].subcategory")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: str(x).strip() if x is not None else None), lambda x: str(x).upper() if x is not None else None)
        self._set_value(target, "lineItems[*].subcategory", _v)

        _v = self._get_value(source, "items[*].brand")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: str(x).strip() if x is not None else None), lambda x: str(x).title() if x is not None else None)
        self._set_value(target, "lineItems[*].brand", _v)

        _v = self._get_value(source, "items[*].modelNumber")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: str(x).strip() if x is not None else None), lambda x: str(x).upper() if x is not None else None)
        self._set_value(target, "lineItems[*].model", _v)

        _v = self._get_value(source, "items[*].color")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: str(x).strip() if x is not None else None), lambda x: str(x).title() if x is not None else None)
        self._set_value(target, "lineItems[*].variant.color", _v)

        _v = self._get_value(source, "items[*].size")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: str(x).strip() if x is not None else None), lambda x: str(x).upper() if x is not None else None)
        self._set_value(target, "lineItems[*].variant.size", _v)

        _v = self._get_value(source, "items[*].quantityOrdered")
        _v = self._apply_transform(_v, lambda x: int(float(x)) if x is not None else None)
        self._set_value(target, "lineItems[*].quantity.ordered", _v)

        _v = self._get_value(source, "items[*].quantityShipped")
        _v = self._apply_transform(_v, lambda x: int(float(x)) if x is not None else None)
        self._set_value(target, "lineItems[*].quantity.shipped", _v)

        _v = self._get_value(source, "items[*].quantityBackordered")
        _v = self._apply_transform(_v, lambda x: int(float(x)) if x is not None else None)
        self._set_value(target, "lineItems[*].quantity.backordered", _v)

        _v = self._get_value(source, "items[*].unitPrice")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: float(x) if x is not None else None), lambda x: round(float(x), 2) if x is not None else None)
        self._set_value(target, "lineItems[*].pricing.unitPrice", _v)

        _v = self._get_value(source, "items[*].unitCost")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: float(x) if x is not None else None), lambda x: round(float(x), 2) if x is not None else None)
        self._set_value(target, "lineItems[*].pricing.unitCost", _v)

        _v = self._get_value(source, "items[*].discountPercent")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: float(x) if x is not None else None), lambda x: round(float(x), 3) if x is not None else None)
        self._set_value(target, "lineItems[*].pricing.discountPercent", _v)

        _v = self._get_value(source, "items[*].discountAmount")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: float(x) if x is not None else None), lambda x: round(float(x), 2) if x is not None else None)
        self._set_value(target, "lineItems[*].pricing.discountAmount", _v)

        _v = self._get_value(source, "items[*].lineTotal")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: float(x) if x is not None else None), lambda x: round(float(x), 2) if x is not None else None)
        self._set_value(target, "lineItems[*].pricing.lineTotal", _v)

        _v = self._get_value(source, "items[*].taxRate")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: float(x) if x is not None else None), lambda x: round(float(x), 3) if x is not None else None)
        self._set_value(target, "lineItems[*].pricing.taxRate", _v)

        _v = self._get_value(source, "items[*].taxAmount")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: float(x) if x is not None else None), lambda x: round(float(x), 2) if x is not None else None)
        self._set_value(target, "lineItems[*].pricing.taxAmount", _v)

        _v = self._get_value(source, "items[*].fulfillmentStatus")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: str(x).strip() if x is not None else None), lambda x: str(x).upper() if x is not None else None)
        self._set_value(target, "lineItems[*].fulfillment.status", _v)

        _v = self._get_value(source, "items[*].shipDate")
        self._set_value(target, "lineItems[*].fulfillment.shipDate", _v)

        _v = self._get_value(source, "items[*].trackingNumber")
        self._set_value(target, "lineItems[*].fulfillment.trackingNumber", _v)

        _v = self._get_value(source, "items[*].carrier")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: str(x).strip() if x is not None else None), lambda x: str(x).upper() if x is not None else None)
        self._set_value(target, "lineItems[*].fulfillment.carrier", _v)

        _v = self._get_value(source, "items[*].weight")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: float(x) if x is not None else None), lambda x: round(float(x), 2) if x is not None else None)
        self._set_value(target, "lineItems[*].attributes.weight", _v)

        _v = self._get_value(source, "items[*].hazmat")
        _v = self._apply_transform(_v, lambda x: str(x).upper() in ('Y','YES','TRUE','1','T') if x is not None else False)
        self._set_value(target, "lineItems[*].attributes.isHazmat", _v)

        _v = self._get_value(source, "items[*].serialNumber")
        self._set_value(target, "lineItems[*].attributes.serialNumber", _v)

        _v = self._get_value(source, "items[*].giftWrap")
        _v = self._apply_transform(_v, lambda x: str(x).upper() in ('Y','YES','TRUE','1','T') if x is not None else False)
        self._set_value(target, "lineItems[*].gift.isWrapped", _v)

        _v = self._get_value(source, "items[*].giftMessage")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: str(x).strip() if x is not None else None), lambda x: re.sub(r'\\s+', ' ', str(x)).strip() if x is not None else None)
        self._set_value(target, "lineItems[*].gift.message", _v)

        _v = self._get_value(source, "items[*].warrantyCode")
        self._set_value(target, "lineItems[*].warranty.code", _v)

        _v = self._get_value(source, "items[*].warrantyPrice")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: float(x) if x is not None else None), lambda x: round(float(x), 2) if x is not None else None)
        self._set_value(target, "lineItems[*].warranty.price", _v)

        _v = self._get_value(source, "payments[*].sequence")
        _v = self._apply_transform(_v, lambda x: int(float(x)) if x is not None else None)
        self._set_value(target, "payments[*].sequence", _v)

        _v = self._get_value(source, "payments[*].method")
        _v = self._apply_transform(_v, lambda x: self._lookup("payment_method", x))
        self._set_value(target, "payments[*].method", _v)

        _v = self._get_value(source, "payments[*].amount")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: float(x) if x is not None else None), lambda x: round(float(x), 2) if x is not None else None)
        self._set_value(target, "payments[*].amount", _v)

        _v = self._get_value(source, "payments[*].cardType")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: str(x).strip() if x is not None else None), lambda x: str(x).upper() if x is not None else None)
        self._set_value(target, "payments[*].card.type", _v)

        _v = self._get_value(source, "payments[*].lastFour")
        self._set_value(target, "payments[*].card.lastFour", _v)

        _v = self._get_value(source, "payments[*].expiration")
        self._set_value(target, "payments[*].card.expiration", _v)

        _v = self._get_value(source, "payments[*].cardHolder")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: str(x).strip() if x is not None else None), lambda x: str(x).upper() if x is not None else None)
        self._set_value(target, "payments[*].card.holderName", _v)

        _v = self._get_value(source, "payments[*].authCode")
        self._set_value(target, "payments[*].transaction.authCode", _v)

        _v = self._get_value(source, "payments[*].transactionId")
        self._set_value(target, "payments[*].transaction.id", _v)

        _v = self._get_value(source, "payments[*].avsResult")
        self._set_value(target, "payments[*].verification.avs", _v)

        _v = self._get_value(source, "payments[*].cvvResult")
        self._set_value(target, "payments[*].verification.cvv", _v)

        _v = self._get_value(source, "totals.subtotal")
        _v = (lambda _v: round(float(_v), 2) if _v is not None else None)((lambda _v: float(_v) if _v is not None else None)(_v))
        self._set_value(target, "totals.subtotal", _v)

        _v = self._get_value(source, "totals.discountTotal")
        _v = (lambda _v: round(float(_v), 2) if _v is not None else None)((lambda _v: float(_v) if _v is not None else None)(_v))
        self._set_value(target, "totals.discount", _v)

        _v = self._get_value(source, "totals.taxTotal")
        _v = (lambda _v: round(float(_v), 2) if _v is not None else None)((lambda _v: float(_v) if _v is not None else None)(_v))
        self._set_value(target, "totals.tax", _v)

        _v = self._get_value(source, "totals.shippingCost")
        _v = (lambda _v: round(float(_v), 2) if _v is not None else None)((lambda _v: float(_v) if _v is not None else None)(_v))
        self._set_value(target, "totals.shipping", _v)

        _v = self._get_value(source, "totals.giftWrapTotal")
        _v = (lambda _v: round(float(_v), 2) if _v is not None else None)((lambda _v: float(_v) if _v is not None else None)(_v))
        self._set_value(target, "totals.giftWrap", _v)

        _v = self._get_value(source, "totals.warrantyTotal")
        _v = (lambda _v: round(float(_v), 2) if _v is not None else None)((lambda _v: float(_v) if _v is not None else None)(_v))
        self._set_value(target, "totals.warranty", _v)

        _v = self._get_value(source, "totals.grandTotal")
        _v = (lambda _v: round(float(_v), 2) if _v is not None else None)((lambda _v: float(_v) if _v is not None else None)(_v))
        self._set_value(target, "totals.grandTotal", _v)

        _v = self._get_value(source, "totals.amountPaid")
        _v = (lambda _v: round(float(_v), 2) if _v is not None else None)((lambda _v: float(_v) if _v is not None else None)(_v))
        self._set_value(target, "totals.paid", _v)

        _v = self._get_value(source, "totals.balanceDue")
        _v = (lambda _v: round(float(_v), 2) if _v is not None else None)((lambda _v: float(_v) if _v is not None else None)(_v))
        self._set_value(target, "totals.due", _v)

        _v = self._evaluate_expr("count_items(items)", source)
        self._set_value(target, "totals.lineItemCount", _v)

        _v = self._evaluate_expr("sum_quantity(items,\"quantityOrdered\")", source)
        self._set_value(target, "totals.totalQuantity", _v)

        _v = self._evaluate_expr("sum_weighted_field(items,\"weight\",\"quantityOrdered\")", source)
        self._set_value(target, "totals.totalWeight", _v)

        _v = self._evaluate_expr("calculate_effective_rate(totals.taxTotal,totals.subtotal)", source)
        self._set_value(target, "totals.effectiveTaxRate", _v)

        _v = self._evaluate_expr("calculate_savings(totals.discountTotal,totals.shippingDiscount,0)", source)
        self._set_value(target, "totals.totalSavings", _v)

        _v = self._get_value(source, "shipping.method")
        _v = (lambda _v: str(_v).upper() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "shipping.method", _v)

        _v = self._get_value(source, "shipping.carrier")
        _v = (lambda _v: str(_v).upper() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "shipping.carrier", _v)

        _v = self._get_value(source, "shipping.speed")
        _v = (lambda _v: re.sub(r'\\s+', ' ', str(_v)).strip() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "shipping.speed", _v)

        _v = self._get_value(source, "shipping.packageCount")
        _v = int(float(_v)) if _v is not None else None
        self._set_value(target, "shipping.packageCount", _v)

        _v = self._get_value(source, "shipping.totalWeight")
        _v = (lambda _v: round(float(_v), 2) if _v is not None else None)((lambda _v: float(_v) if _v is not None else None)(_v))
        self._set_value(target, "shipping.totalWeight", _v)

        _v = self._get_value(source, "shipping.insuranceAmount")
        _v = (lambda _v: round(float(_v), 2) if _v is not None else None)((lambda _v: float(_v) if _v is not None else None)(_v))
        self._set_value(target, "shipping.insuranceAmount", _v)

        _v = self._get_value(source, "shipping.signatureRequired")
        _v = str(_v).upper() in ('Y','YES','TRUE','1','T') if _v is not None else False
        self._set_value(target, "shipping.signatureRequired", _v)

        _v = self._get_value(source, "shipping.trackingNumbers")
        self._set_value(target, "shipping.trackingNumbers", _v)

        _v = self._evaluate_expr("format_date(shipping.estimatedDelivery)", source)
        self._set_value(target, "shipping.estimatedDelivery", _v)

        _v = self._get_value(source, "promotions[*].code")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: str(x).strip() if x is not None else None), lambda x: str(x).upper() if x is not None else None)
        self._set_value(target, "promotions[*].code", _v)

        _v = self._get_value(source, "promotions[*].description")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: str(x).strip() if x is not None else None), lambda x: re.sub(r'\\s+', ' ', str(x)).strip() if x is not None else None)
        self._set_value(target, "promotions[*].description", _v)

        _v = self._get_value(source, "promotions[*].type")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: str(x).strip() if x is not None else None), lambda x: str(x).upper() if x is not None else None)
        self._set_value(target, "promotions[*].type", _v)

        _v = self._get_value(source, "promotions[*].value")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: float(x) if x is not None else None), lambda x: round(float(x), 2) if x is not None else None)
        self._set_value(target, "promotions[*].value", _v)

        _v = self._get_value(source, "promotions[*].savings")
        _v = self._apply_transform(self._apply_transform(_v, lambda x: float(x) if x is not None else None), lambda x: round(float(x), 2) if x is not None else None)
        self._set_value(target, "promotions[*].savings", _v)

        _v = '2.0'
        _v = _v
        self._set_value(target, "metadata.schemaVersion", _v)

        _v = self._get_value(source, "audit.source")
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
    t = OrderTransformer()
    data = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else {}
    print(json.dumps(t.transform(data), indent=2, default=str))
