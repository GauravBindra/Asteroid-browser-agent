#!/usr/bin/env python3
"""
Form Schemas for Asteroid Form Challenge

This module defines the schema structures for both the easy and hard forms.
Each schema maps form fields to their properties and corresponding data paths.
"""

from typing import Dict, Any

# Easy Form Schema
# A simple single-page form with basic fields
EASY_FORM_SCHEMA = {
    "firstName": {
        "type": "text",
        "label": "First Name",
        "required": True,
        "data_path": "firstName",
        "selector": "label:has-text('First Name') + input, label:has-text('First Name') ~ input"
    },
    "lastName": {
        "type": "text",
        "label": "Last Name",
        "required": True,
        "data_path": "lastName",
        "selector": "label:has-text('Last Name') + input, label:has-text('Last Name') ~ input"
    },
    "dateOfBirth": {
        "type": "text",  # Using text instead of date for custom format
        "label": "Date of Birth (dd-mm-yyyy)",
        "placeholder": "dd-mm-yyyy",
        "required": True,
        "data_path": "dateOfBirth",
        "selector": "input[placeholder='dd-mm-yyyy']"
    },
    "email": {
        "type": "email",
        "label": "Email",
        "required": True,
        "data_path": "email",
        "selector": "label:has-text('Email') + input, label:has-text('Email') ~ input, input[type='email']"
    },
    "phoneNumber": {
        "type": "tel",
        "label": "Phone Number",
        "required": True,
        "data_path": "phoneNumber",
        "selector": "label:has-text('Phone Number') + input, label:has-text('Phone Number') ~ input, input[type='tel']"
    },
    "hasInsurance": {
        "type": "checkbox",
        "label": "Do you currently have insurance?",
        "input_id": "hasInsurance",
        "required": False,
        "data_path": "hasInsurance",
        "selector": "#hasInsurance, input[id='hasInsurance']"
    },
    "wantsNewsletter": {
        "type": "checkbox",
        "label": "Would you like to receive our newsletter?",
        "input_id": "wantsNewsletter",
        "required": False,
        "data_path": "wantsNewsletter",
        "selector": "#wantsNewsletter, input[id='wantsNewsletter']"
    },
    "agreeToTerms": {
        "type": "checkbox",
        "label": "I agree to the terms and conditions",
        "input_id": "agreeToTerms",
        "required": True,
        "data_path": "agreeToTerms",
        "selector": "#agreeToTerms, input[id='agreeToTerms']"
    },
    "submitButton": {
        "type": "button",
        "label": "Review",
        "selector": "button[type='submit'], input[type='submit'], button:has-text('Review')"
    }
}

# Hard Form Schema by Sections
# A complex multi-section form with many field types and conditional fields

# Section 1: Contact Details
CONTACT_DETAILS_SCHEMA = {
    "title": {
        "type": "select",
        "label": "Title",
        "required": True,
        "data_path": "contact.title",
        "options": ["Mr", "Mrs", "Ms", "Dr", "Prof", "Other"]
    },
    "firstName": {
        "type": "text",
        "label": "First Name",
        "required": True,
        "data_path": "contact.firstName"
    },
    "lastName": {
        "type": "text",
        "label": "Last Name",
        "required": True,
        "data_path": "contact.lastName"
    },
    "dateOfBirth": {
        "type": "date",
        "label": "Date of Birth",
        "required": True,
        "data_path": "contact.dateOfBirth"
    },
    "phoneNumber": {
        "type": "tel",
        "label": "Phone Number",
        "required": True,
        "data_path": "contact.phoneNumber"
    },
    "numberOfYearsAsLandlord": {
        "type": "number",
        "label": "Years as Landlord",
        "required": True,
        "data_path": "contact.numberOfYearsAsLandlord"
    },
    "jointInsured": {
        "type": "checkbox",
        "label": "Joint Insured",
        "input_id": "jointInsured",
        "required": False,
        "data_path": "contact.jointInsured",
        "triggers_conditional": True
    },
    "jointInsuredPersonName": {
        "type": "text",
        "label": "Joint Insured Person Name",
        "required": False,
        "data_path": "contact.jointInsuredPersonName",
        "conditional": True,
        "depends_on": "jointInsured",
        "visible_when": True
    }
}

# Section 2: Business Info
BUSINESS_INFO_SCHEMA = {
    "businessName": {
        "type": "text",
        "label": "Business Name",
        "required": True,
        "data_path": "business.name"
    },
    "businessType": {
        "type": "select",
        "label": "Business Type",
        "required": True,
        "data_path": "business.type",
        "options": [
            "Sole Trader",
            "Private Limited Company (LTD)",
            "Public Limited Company (PLC)",
            "Limited Liability Partnership (LLP)",
            "Partnership",
            "Charity",
            "Other"
        ]
    },
    "businessTrade": {
        "type": "text",
        "label": "Business Trade",
        "required": True,
        "data_path": "business.trade"
    },
    "businessAddressLine1": {
        "type": "text",
        "label": "Address Line 1",
        "required": True,
        "data_path": "business.address.addressLine1"
    },
    "businessAddressLine2": {
        "type": "text",
        "label": "Address Line 2",
        "required": False,
        "data_path": "business.address.addressLine2"
    },
    "businessAddressLine3": {
        "type": "text",
        "label": "Address Line 3",
        "required": False,
        "data_path": "business.address.addressLine3"
    },
    "businessCity": {
        "type": "text",
        "label": "City",
        "required": True,
        "data_path": "business.address.city"
    },
    "businessPostcode": {
        "type": "text",
        "label": "Postcode",
        "required": True,
        "data_path": "business.address.postcode"
    },
    "ernTaxCode": {
        "type": "text",
        "label": "ERN Tax Code",
        "required": True,
        "data_path": "business.ernTaxCode"
    },
    "exemptFromERNCode": {
        "type": "checkbox",
        "label": "Exempt from ERN Code",
        "required": False,
        "data_path": "business.exemptFromERNCode"
    },
    "websiteUrl": {
        "type": "text",
        "label": "Website URL",
        "required": False,
        "data_path": "business.websiteUrl"
    },
    "businessDescription": {
        "type": "text",
        "label": "Business Description",
        "required": True,
        "data_path": "business.description"
    },
    "yearsOfExperience": {
        "type": "number",
        "label": "Years of Experience",
        "required": True,
        "data_path": "business.yearsOfExperience"
    },
    "descriptionOfExperience": {
        "type": "textarea",
        "label": "Description of Experience",
        "required": True,
        "data_path": "business.descriptionOfExperience"
    }
}

# Section 3: Premises Details
PREMISES_DETAILS_SCHEMA = {
    # Identity Group
    "premisesType": {
        "type": "select",
        "label": "Premises Type",
        "required": True,
        "data_path": "premises.identity.type",
        "options": ["Commercial", "Residential", "Mixed Use"]
    },
    "listedStatus": {
        "type": "select",
        "label": "Listed Status",
        "required": True,
        "data_path": "premises.identity.listed",
        "options": ["Not Listed", "Grade I", "Grade II", "Grade II*"]
    },
    "premisesAddressLine1": {
        "type": "text",
        "label": "Address Line 1",
        "required": True,
        "data_path": "premises.identity.address.addressLine1"
    },
    "premisesAddressLine2": {
        "type": "text",
        "label": "Address Line 2",
        "required": False,
        "data_path": "premises.identity.address.addressLine2"
    },
    "premisesAddressLine3": {
        "type": "text",
        "label": "Address Line 3",
        "required": False,
        "data_path": "premises.identity.address.addressLine3"
    },
    "premisesCity": {
        "type": "text",
        "label": "City",
        "required": True,
        "data_path": "premises.identity.address.city"
    },
    "premisesPostcode": {
        "type": "text",
        "label": "Postcode",
        "required": True,
        "data_path": "premises.identity.address.postcode"
    },
    "numberOfFlatsInBlock": {
        "type": "number",
        "label": "Number of Flats in Block",
        "required": True,
        "data_path": "premises.identity.numberOfFlatsInBlock"
    },
    "numberOfFlatsToBeInsured": {
        "type": "number",
        "label": "Number of Flats to be Insured",
        "required": True,
        "data_path": "premises.identity.numberOfFlatsToBeInsured"
    },
    
    # Construction Group
    "roofType": {
        "type": "select",
        "label": "Roof Type",
        "required": True,
        "data_path": "premises.construction.roofType",
        "options": ["Slate", "Tile", "Concrete", "Metal", "Other"]
    },
    "wallType": {
        "type": "select",
        "label": "Wall Type",
        "required": True,
        "data_path": "premises.construction.wallType",
        "options": ["Brick Built", "Stone", "Concrete", "Metal", "Wood Frame", "Other"]
    },
    "floorType": {
        "type": "select",
        "label": "Floor Type",
        "required": True,
        "data_path": "premises.construction.floorType",
        "options": ["Concrete", "Timber", "Steel", "Other"]
    },
    "stairType": {
        "type": "select",
        "label": "Stair Type",
        "required": True,
        "data_path": "premises.construction.stairType",
        "options": ["Concrete", "Metal", "Timber", "None", "Other"]
    },
    "hasFlatRoof": {
        "type": "checkbox",
        "label": "Has Flat Roof",
        "required": False,
        "data_path": "premises.construction.hasFlatRoof",
        "triggers_conditional": True
    },
    "percentageOfFlatRoof": {
        "type": "number",
        "label": "Percentage of Flat Roof",
        "required": False,
        "data_path": "premises.construction.percentageOfFlatRoof",
        "conditional": True,
        "depends_on": "hasFlatRoof",
        "visible_when": True
    },
    "flatRoofLastInspected": {
        "type": "date",
        "label": "Flat Roof Last Inspected",
        "required": False,
        "data_path": "premises.construction.flatRoofLastInspected",
        "conditional": True,
        "depends_on": "hasFlatRoof",
        "visible_when": True
    },
    "haveColdStores": {
        "type": "checkbox",
        "label": "Have Cold Stores",
        "required": False,
        "data_path": "premises.construction.haveColdStores"
    },
    "rebuildingCost": {
        "type": "number",
        "label": "Rebuilding Cost",
        "required": True,
        "data_path": "premises.construction.rebuildingCost"
    },
    "roofLastRelaid": {
        "type": "date",
        "label": "Roof Last Relaid",
        "required": True,
        "data_path": "premises.construction.roofLastRelaid"
    },
    "numberOfStoreys": {
        "type": "number",
        "label": "Number of Storeys",
        "required": True,
        "data_path": "premises.construction.numberOfStoreys"
    },
    "anyCompositePanels": {
        "type": "select",
        "label": "Any Composite Panels",
        "required": True,
        "data_path": "premises.construction.anyCompositePanels",
        "options": ["No panels", "Yes - approved panels", "Yes - unapproved panels", "Unknown"]
    },
    "warehouseFloorArea": {
        "type": "text",
        "label": "Warehouse Floor Area",
        "required": True,
        "data_path": "premises.construction.warehouseFloorArea"
    },
    "yearOfConstruction": {
        "type": "date",
        "label": "Year of Construction",
        "required": True,
        "data_path": "premises.construction.yearOfConstruction"
    },
    "constructionDetails": {
        "type": "textarea",
        "label": "Construction Details",
        "required": False,
        "data_path": "premises.construction.constructionDetails"
    },
    "isBuildingPurposeBuilt": {
        "type": "checkbox",
        "label": "Is Building Purpose Built",
        "required": False,
        "data_path": "premises.construction.isBuildingPurposeBuilt"
    },
    "isUndergoingBuildingWorks": {
        "type": "checkbox",
        "label": "Is Undergoing Building Works",
        "required": False,
        "data_path": "premises.construction.isUndergoingBuildingWorks"
    }
}

# Section 4: Security & Safety
SECURITY_SAFETY_SCHEMA = {
    # Security Group
    "cctv": {
        "type": "checkbox",
        "label": "CCTV",
        "required": False,
        "data_path": "security.cctv",
        "triggers_conditional": True
    },
    "cctvType": {
        "type": "select",
        "label": "CCTV Type",
        "required": False,
        "data_path": "security.cctvType",
        "conditional": True,
        "depends_on": "cctv",
        "visible_when": True,
        "options": [
            "Recorded only",
            "Monitored only",
            "Recorded and monitored by staff",
            "Recorded and monitored by a professional monitoring company"
        ]
    },
    "cctvCoverage": {
        "type": "select",
        "label": "CCTV Coverage",
        "required": False,
        "data_path": "security.cctvCoverage",
        "conditional": True,
        "depends_on": "cctv",
        "visible_when": True,
        "options": ["Internal only", "External only", "Both"]
    },
    "selfContained": {
        "type": "checkbox",
        "label": "Self Contained",
        "required": False,
        "data_path": "security.selfContained"
    },
    "doorSecurityType": {
        "type": "select",
        "label": "Door Security Type",
        "required": True,
        "data_path": "security.doorSecurityType",
        "options": [
            "Standard Key Lock",
            "5 Lever Mortise",
            "Mortise Deadlock - 5 Or More Levers BS3621",
            "Multi-point Locking System",
            "Electronic Access Control",
            "Other"
        ]
    },
    "fittedWithSmokeAlarms": {
        "type": "checkbox",
        "label": "Fitted with Smoke Alarms",
        "required": False,
        "data_path": "security.fittedWithSmokeAlarms"
    },
    "intruderAlarm": {
        "type": "checkbox",
        "label": "Intruder Alarm",
        "required": False,
        "data_path": "security.intruderAlarm",
        "triggers_conditional": True
    },
    "intruderAlarmType": {
        "type": "select",
        "label": "Intruder Alarm Type",
        "required": False,
        "data_path": "security.intruderAlarmType",
        "conditional": True,
        "depends_on": "intruderAlarm",
        "visible_when": True,
        "options": [
            "Audible Only",
            "Digital Communicator",
            "Central Station",
            "Police Response",
            "Redcare",
            "Professional"
        ]
    },
    "requireTerrorismCover": {
        "type": "checkbox",
        "label": "Require Terrorism Cover",
        "required": False,
        "data_path": "security.requireTerrorismCover"
    },
    
    # Fire Safety Group
    "heating": {
        "type": "select",
        "label": "Heating",
        "required": True,
        "data_path": "fireSafety.heating",
        "options": [
            "Gas",
            "Electric",
            "Oil",
            "Solid Fuel",
            "Geothermal",
            "Solar",
            "None"
        ]
    },
    "fireAlarm": {
        "type": "checkbox",
        "label": "Fire Alarm",
        "required": False,
        "data_path": "fireSafety.fireAlarm"
    },
    "smokingPolicy": {
        "type": "select",
        "label": "Smoking Policy",
        "required": True,
        "data_path": "fireSafety.smokingPolicy",
        "options": [
            "No smoking allowed",
            "Designated zones only",
            "Unrestricted"
        ]
    },
    "sprinklerSystem": {
        "type": "checkbox",
        "label": "Sprinkler System",
        "required": False,
        "data_path": "fireSafety.sprinklerSystem"
    },
    "fireExtinguishers": {
        "type": "checkbox",
        "label": "Fire Extinguishers",
        "required": False,
        "data_path": "fireSafety.fireExtinguishers"
    },
    "fireDetectorsCoverage": {
        "type": "text",
        "label": "Fire Detectors Coverage",
        "required": True,
        "data_path": "fireSafety.fireDetectorsCoverage"
    },
    "flammableLiquidStored": {
        "type": "checkbox",
        "label": "Flammable Liquid Stored",
        "required": False,
        "data_path": "fireSafety.flammableLiquidStored",
        "triggers_conditional": True
    },
    "flammableLiquids": {
        "type": "text",
        "label": "Flammable Liquids",
        "required": False,
        "data_path": "fireSafety.flammableLiquids",
        "conditional": True,
        "depends_on": "flammableLiquidStored",
        "visible_when": True
    }
}

# Section 5: Coverage Options
COVERAGE_OPTIONS_SCHEMA = {
    # Coverage Group
    "terrorism": {
        "type": "checkbox",
        "label": "Terrorism",
        "required": False,
        "data_path": "coverage.terrorism"
    },
    "subsidence": {
        "type": "checkbox",
        "label": "Subsidence",
        "required": False,
        "data_path": "coverage.subsidence"
    },
    "accidentalDamage": {
        "type": "checkbox",
        "label": "Accidental Damage",
        "required": False,
        "data_path": "coverage.accidentalDamage"
    },
    "sumInsuredLossOfRent": {
        "type": "number",
        "label": "Sum Insured Loss of Rent",
        "required": True,
        "data_path": "coverage.sumInsuredLossOfRent"
    },
    "periodOfIndemnityInMonths": {
        "type": "number",
        "label": "Period of Indemnity in Months",
        "required": True,
        "data_path": "coverage.periodOfIndemnityInMonths"
    },
    "propertyOwnersLiabilityAmount": {
        "type": "number",
        "label": "Property Owners Liability Amount",
        "required": True,
        "data_path": "coverage.propertyOwnersLiabilityAmount"
    },
    
    # Material Damage Group
    "stocksSumInsured": {
        "type": "number",
        "label": "Stocks Sum Insured",
        "required": True,
        "data_path": "materialDamage.stocksSumInsured"
    },
    "buildingSumInsured": {
        "type": "number",
        "label": "Building Sum Insured",
        "required": True,
        "data_path": "materialDamage.buildingSumInsured"
    },
    "tenantsImprovementsSumInsured": {
        "type": "number",
        "label": "Tenants Improvements Sum Insured",
        "required": True,
        "data_path": "materialDamage.tenantsImprovementsSumInsured"
    },
    "electronicOfficeEquipmentSumInsured": {
        "type": "number",
        "label": "Electronic Office Equipment Sum Insured",
        "required": True,
        "data_path": "materialDamage.electronicOfficeEquipmentSumInsured"
    },
    
    # Portable Equipment Group
    "portableEquipmentLocation": {
        "type": "select",
        "label": "Location",
        "required": True,
        "data_path": "materialDamage.portableEquipment.location",
        "options": ["UK", "Europe", "Worldwide", "Worldwide excluding USA/Canada"]
    },
    "toolsSumInsured": {
        "type": "number",
        "label": "Tools Sum Insured",
        "required": True,
        "data_path": "materialDamage.portableEquipment.toolsSumInsured"
    },
    "smartPhoneSumInsured": {
        "type": "number",
        "label": "Smart Phone Sum Insured",
        "required": True,
        "data_path": "materialDamage.portableEquipment.smartPhoneSumInsured"
    },
    "miscellaneousToInsure": {
        "type": "textarea",
        "label": "Miscellaneous to Insure",
        "required": False,
        "data_path": "materialDamage.portableEquipment.miscellaneousToInsure"
    },
    "otherPortableComputerEquipmentSumInsured": {
        "type": "number",
        "label": "Other Portable Computer Equipment Sum Insured",
        "required": True,
        "data_path": "materialDamage.portableEquipment.otherPortableComputerEquipmentSumInsured"
    },
    
    # Submit Button
    "submitButton": {
        "type": "button",
        "label": "Submit",
        "selector": "button[type='submit'], input[type='submit'], button:has-text('Submit'), button:has-text('submit')"
    }
}

# Complete Hard Form Schema
HARD_FORM_SCHEMA = {
    "sections": {
        "contactDetails": CONTACT_DETAILS_SCHEMA,
        "businessInfo": BUSINESS_INFO_SCHEMA,
        "premisesDetails": PREMISES_DETAILS_SCHEMA,
        "securitySafety": SECURITY_SAFETY_SCHEMA,
        "coverageOptions": COVERAGE_OPTIONS_SCHEMA
    },
    "navigation": {
        "contactDetails": {
            "title": "Contact Details",
            "next": "businessInfo",
            "prev": None
        },
        "businessInfo": {
            "title": "Business Info",
            "next": "premisesDetails",
            "prev": "contactDetails"
        },
        "premisesDetails": {
            "title": "Premises Details",
            "next": "securitySafety",
            "prev": "businessInfo"
        },
        "securitySafety": {
            "title": "Security & Safety",
            "next": "coverageOptions",
            "prev": "premisesDetails"
        },
        "coverageOptions": {
            "title": "Coverage Options",
            "next": None,
            "prev": "securitySafety"
        }
    }
}

# Get form schema by form type
def get_form_schema(form_type: str) -> Dict[str, Any]:
    """
    Get the schema for a specific form type.
    
    Args:
        form_type: Type of form ("easy" or "hard")
        
    Returns:
        Schema dictionary for the requested form type
    """
    if form_type == "easy":
        return EASY_FORM_SCHEMA
    elif form_type == "hard":
        return HARD_FORM_SCHEMA
    else:
        raise ValueError(f"Invalid form type: {form_type}. Must be 'easy' or 'hard'")


# Get conditional fields for a form schema
def get_conditional_fields(schema: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Extract all conditional fields from a form schema.
    
    Args:
        schema: Form schema dictionary
        
    Returns:
        Dictionary mapping trigger fields to their dependent fields
    """
    conditional_map = {}
    
    if "sections" in schema:
        # Process each section for hard form
        for section_name, section_schema in schema["sections"].items():
            section_conditionals = _extract_conditional_fields(section_schema)
            conditional_map.update(section_conditionals)
    else:
        # Process direct schema for easy form
        conditional_map = _extract_conditional_fields(schema)
    
    return conditional_map


def _extract_conditional_fields(fields_schema: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Helper function to extract conditional fields from a schema section.
    
    Args:
        fields_schema: Schema dictionary for a form section
        
    Returns:
        Dictionary mapping trigger fields to their dependent fields
    """
    result = {}
    
    # Find all trigger fields
    trigger_fields = {
        field_name: field_info
        for field_name, field_info in fields_schema.items()
        if field_info.get("triggers_conditional", False)
    }
    
    # Find all conditional fields and map them to their triggers
    for field_name, field_info in fields_schema.items():
        if field_info.get("conditional", False) and "depends_on" in field_info:
            trigger_name = field_info["depends_on"]
            
            if trigger_name not in result:
                result[trigger_name] = {}
                
            result[trigger_name][field_name] = {
                "field_info": field_info,
                "visible_when": field_info.get("visible_when", True)
            }
    
    return result


# For debugging and testing
if __name__ == "__main__":
    import json
    
    # Print schemas for debugging
    print("Easy Form Schema:")
    print(json.dumps(EASY_FORM_SCHEMA, indent=2))
    
    print("\nHard Form Schema (first section):")
    print(json.dumps(CONTACT_DETAILS_SCHEMA, indent=2))
    
    # Print conditional fields
    print("\nConditional fields in Easy Form:")
    easy_conditionals = get_conditional_fields(EASY_FORM_SCHEMA)
    print(json.dumps(easy_conditionals, indent=2))
    
    print("\nConditional fields in Hard Form:")
    hard_conditionals = get_conditional_fields(HARD_FORM_SCHEMA)
    print(json.dumps(hard_conditionals, indent=2))