#!/usr/bin/env python3
"""
Configuration settings for Nova-ACT form automation.

This module contains configurable parameters for field detection
and other settings used across the form automation components.
"""

# Field detection settings
MAX_FIELD_DETECTION_SCROLLS = 3  # Maximum scrolls when looking for a field

# Scroll settings
SCROLL_AMOUNT_SMALL = "a small amount"  # Minimal scroll
SCROLL_AMOUNT_MEDIUM = "about half a page"  # Medium scroll
SCROLL_AMOUNT_LARGE = "to the bottom of the page"  # Large scroll

# Step limits
MAX_STEPS_PER_DETECTION = 20  # Maximum steps for field detection operations

# URLs
HARD_FORM_URL = "https://asteroid.ai/form"
EASY_FORM_URL = "https://asteroid.ai/form2"

# Form section configuration
# Ordered list of sections as they appear in the form
FORM_SECTIONS = [
    "Contact Details",
    "Business Info",
    "Premises Details",
    "Security & Safety",
    "Coverage Options"
]

# For better generalization, can later remove this and have semantic based mapping
# Dictionary mapping JSON section names to form section names (for cases where they differ)
SECTION_MAPPING = {
    "contact": "Contact Details",
    "business": "Business Info",
    "premises": "Premises Details",
    "security": "Security & Safety",
    "fireSafety": "Fire Safety",  # Fire safety is likely part of Security & Safety section
    "coverage": "Coverage Options",
    "materialDamage": "Material Damage"  # Material damage is likely part of Coverage Options
}


# Field type mapping for JSON fields
# Maps JSON field names to their corresponding field types in the form
FIELD_TYPES = {
    # Contact Details section
    "firstName": "text",
    "lastName": "text",
    "email": "text",
    "phone": "text",
    "phoneNumber": "text",
    "address": "text",
    "city": "text",
    "state": "dropdown",
    "postalCode": "text",
    "country": "dropdown",
    "dateOfBirth": "date",
    "gender": "dropdown",
    "maritalStatus": "dropdown",
    "title": "dropdown",
    "wantsNewsletter": "checkbox",
    "jointInsured": "checkbox",
    "jointInsuredPersonName": "text",
    "numberOfYearsAsLandlord": "text",
    
    # Business Info section
    "name": "text",
    "businessName": "text",
    "type": "dropdown",
    "businessType": "dropdown",
    "trade": "text",
    "industry": "dropdown",
    "addressLine1": "text",
    "addressLine2": "text",
    "addressLine3": "text",
    "city": "text",
    "postcode": "text",
    "ernTaxCode": "text",
    "websiteUrl": "text",
    "description": "text",
    "exemptFromERNCode": "checkbox",
    "yearsOfExperience": "text",
    "registrationNumber": "text",
    "establishedDate": "date",
    "annualRevenue": "text",
    "numberOfEmployees": "text",
    "vatRegistered": "checkbox",
    "vatNumber": "text",
    "descriptionOfExperience": "text",
    
    # Premises Details section
    "type": "dropdown",
    "buildingType": "dropdown",
    "listed": "dropdown",
    "addressLine1": "text",
    "addressLine2": "text",
    "addressLine3": "text",
    "city": "text",
    "postcode": "text",
    "numberOfFlatsInBlock": "text",
    "numberOfFlatsToBeInsured": "text",
    "roofType": "dropdown",
    "wallType": "dropdown",
    "floorType": "dropdown",
    "stairType": "dropdown",
    "hasFlatRoof": "checkbox",
    "haveColdStores": "checkbox",
    "rebuildingCost": "text",
    "roofLastRelaid": "date",
    "numberOfStoreys": "text",
    "anyCompositePanels": "dropdown",
    "warehouseFloorArea": "text",
    "yearOfConstruction": "date",
    "constructionYear": "text",
    "constructionDetails": "text",
    "percentageOfFlatRoof": "text",
    "flatRoofLastInspected": "date",
    "isBuildingPurposeBuilt": "checkbox",
    "isUndergoingBuildingWorks": "checkbox",
    "propertyAge": "dropdown",
    "roofMaterial": "dropdown",
    "numberOfFloors": "text",
    "totalArea": "text",
    "heatingType": "dropdown",
    "hasAlarm": "checkbox",
    "hasSprinklers": "checkbox",
    "lastInspectionDate": "date",
    "hasFireProtection": "checkbox",
    
    # Security & Safety section
    "cctv": "checkbox",
    "cctvType": "dropdown",
    "cctvCoverage": "dropdown",
    "selfContained": "checkbox",
    "doorSecurityType": "dropdown",
    "fittedWithSmokeAlarms": "checkbox",
    "intruderAlarm": "checkbox",
    "intruderAlarmType": "dropdown",
    "requireTerrorismCover": "checkbox",
    
    # Fire Safety section
    "heating": "dropdown",
    "fireAlarm": "checkbox",
    "smokingPolicy": "dropdown",
    "sprinklerSystem": "checkbox",
    "fireExtinguishers": "checkbox",
    "fireDetectorsCoverage": "dropdown",
    "flammableLiquidStored": "checkbox",
    "flammableLiquids": "text",
    
    # Coverage Options section
    "terrorism": "checkbox",
    "subsidence": "checkbox",
    "accidentalDamage": "checkbox",
    "sumInsuredLossOfRent": "text",
    "periodOfIndemnityInMonths": "dropdown",
    "propertyOwnersLiabilityAmount": "text"
}

# Field dependencies configuration
# Format: dependent_field_name: {prerequisite_field, prerequisite_value, section}
FIELD_DEPENDENCIES = {
    "jointInsuredPersonName": {
        "prerequisite_field": "jointInsured", 
        "prerequisite_value": True,
        "section": "Contact Details"
    },
    "flatRoofLastInspected": {
        "prerequisite_field": "hasFlatRoof",
        "prerequisite_value": True,
        "section": "Premises Details"
    },
    "percentageOfFlatRoof": {
        "prerequisite_field": "hasFlatRoof",
        "prerequisite_value": True,
        "section": "Premises Details"
    },
    "cctvType": {
        "prerequisite_field": "cctv",
        "prerequisite_value": True,
        "section": "Security & Safety"
    },
    "cctvCoverage": {
        "prerequisite_field": "cctv",
        "prerequisite_value": True,
        "section": "Security & Safety"
    },
    "ernTaxCode": {
        "prerequisite_field": "exemptFromERNCode",
        "prerequisite_value": False,
        "section": "Business Info"
    },
}


# ─── 1. Known date format patterns ────────────────────────────────────────────
ORDER_PATTERNS = [
    "dd/mm/yyyy", "mm/dd/yyyy", "yyyy/mm/dd"
]

KNOWN_INPUT_FORMATS = [
    "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y",        # DMY with various separators
    "%m/%d/%Y", "%m-%d-%Y", "%m.%d.%Y",        # MDY with various separators
    "%Y/%m/%d", "%Y-%m-%d", "%Y.%m.%d",        # YMD with various separators
]