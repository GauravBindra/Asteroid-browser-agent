# Data Mapping Strategy

This document outlines how to map data from our input JSON structures to the corresponding form fields on the website.

## Easy Form Mapping

```javascript
const easyFormMapping = {
  // Map from form field label to data property
  "First Name": data.firstName,
  "Last Name": data.lastName,
  "Date of Birth (dd-mm-yyyy)": data.dateOfBirth,
  "Email": data.email,
  "Phone Number": data.phoneNumber,
  "Do you currently have insurance?": data.hasInsurance,
  "Would you like to receive our newsletter?": data.wantsNewsletter,
  "I agree to the terms and conditions": data.agreeToTerms
};
```

## Hard Form Mapping

```javascript
const hardFormMapping = {
  // Contact Details section
  "Title": data.contact.title,
  "First Name": data.contact.firstName,
  "Last Name": data.contact.lastName,
  "Date of Birth": data.contact.dateOfBirth,
  "Phone Number": data.contact.phoneNumber,
  "Years as Landlord": data.contact.numberOfYearsAsLandlord,
  "Joint Insured": data.contact.jointInsured,
  "Joint Insured Person Name": data.contact.jointInsuredPersonName,
  
  // Business Info section
  "Business Name": data.business.name,
  "Business Type": data.business.type,
  "Business Trade": data.business.trade,
  "Address Line 1": data.business.address.addressLine1,
  "Address Line 2": data.business.address.addressLine2,
  "Address Line 3": data.business.address.addressLine3,
  "City": data.business.address.city,
  "Postcode": data.business.address.postcode,
  "ERN Tax Code": data.business.ernTaxCode,
  "Exempt from ERN Code": data.business.exemptFromERNCode,
  "Website URL": data.business.websiteUrl,
  "Business Description": data.business.description,
  "Years of Experience": data.business.yearsOfExperience,
  "Description of Experience": data.business.descriptionOfExperience,
  
  // Premises Details section
  "Premises Type": data.premises.identity.type,
  "Listed Status": data.premises.identity.listed,
  "Premises Address Line 1": data.premises.identity.address.addressLine1,
  "Premises Address Line 2": data.premises.identity.address.addressLine2,
  "Premises Address Line 3": data.premises.identity.address.addressLine3,
  "Premises City": data.premises.identity.address.city,
  "Premises Postcode": data.premises.identity.address.postcode,
  "Number of Flats in Block": data.premises.identity.numberOfFlatsInBlock,
  "Number of Flats to be Insured": data.premises.identity.numberOfFlatsToBeInsured,
  "Roof Type": data.premises.construction.roofType,
  "Wall Type": data.premises.construction.wallType,
  "Floor Type": data.premises.construction.floorType,
  "Stair Type": data.premises.construction.stairType,
  "Has Flat Roof": data.premises.construction.hasFlatRoof,
  "Percentage of Flat Roof": data.premises.construction.percentageOfFlatRoof,
  "Flat Roof Last Inspected": data.premises.construction.flatRoofLastInspected,
  "Have Cold Stores": data.premises.construction.haveColdStores,
  "Rebuilding Cost": data.premises.construction.rebuildingCost,
  "Roof Last Relaid": data.premises.construction.roofLastRelaid,
  "Number of Storeys": data.premises.construction.numberOfStoreys,
  "Any Composite Panels": data.premises.construction.anyCompositePanels,
  "Warehouse Floor Area": data.premises.construction.warehouseFloorArea,
  "Year of Construction": data.premises.construction.yearOfConstruction,
  "Construction Details": data.premises.construction.constructionDetails,
  "Is Building Purpose Built": data.premises.construction.isBuildingPurposeBuilt,
  "Is Undergoing Building Works": data.premises.construction.isUndergoingBuildingWorks,
  
  // Security & Safety section
  "CCTV": data.security.cctv,
  "CCTV Type": data.security.cctvType,
  "CCTV Coverage": data.security.cctvCoverage,
  "Self Contained": data.security.selfContained,
  "Door Security Type": data.security.doorSecurityType,
  "Fitted with Smoke Alarms": data.security.fittedWithSmokeAlarms,
  "Intruder Alarm": data.security.intruderAlarm,
  "Intruder Alarm Type": data.security.intruderAlarmType,
  "Require Terrorism Cover": data.security.requireTerrorismCover,
  "Heating": data.fireSafety.heating,
  "Fire Alarm": data.fireSafety.fireAlarm,
  "Smoking Policy": data.fireSafety.smokingPolicy,
  "Sprinkler System": data.fireSafety.sprinklerSystem,
  "Fire Extinguishers": data.fireSafety.fireExtinguishers,
  "Fire Detectors Coverage": data.fireSafety.fireDetectorsCoverage,
  "Flammable Liquid Stored": data.fireSafety.flammableLiquidStored,
  "Flammable Liquids": data.fireSafety.flammableLiquids,
  
  // Coverage Options section
  "Terrorism": data.coverage.terrorism,
  "Subsidence": data.coverage.subsidence,
  "Accidental Damage": data.coverage.accidentalDamage,
  "Sum Insured Loss of Rent": data.coverage.sumInsuredLossOfRent,
  "Period of Indemnity in Months": data.coverage.periodOfIndemnityInMonths,
  "Property Owners Liability Amount": data.coverage.propertyOwnersLiabilityAmount,
  "Stocks Sum Insured": data.materialDamage.stocksSumInsured,
  "Building Sum Insured": data.materialDamage.buildingSumInsured,
  "Tenants Improvements Sum Insured": data.materialDamage.tenantsImprovementsSumInsured,
  "Electronic Office Equipment Sum Insured": data.materialDamage.electronicOfficeEquipmentSumInsured,
  "Location": data.materialDamage.portableEquipment.location,
  "Tools Sum Insured": data.materialDamage.portableEquipment.toolsSumInsured,
  "Smart Phone Sum Insured": data.materialDamage.portableEquipment.smartPhoneSumInsured,
  "Miscellaneous to Insure": data.materialDamage.portableEquipment.miscellaneousToInsure,
  "Other Portable Computer Equipment Sum Insured": data.materialDamage.portableEquipment.otherPortableComputerEquipmentSumInsured
};
```

## Implementation Considerations

1. **Field Identification**
   - Primary strategy: Match by label text
   - Fallback strategy: Match by placeholder or nearby text
   - Last resort: Use CSS/XPath selectors for position-based identification

2. **Value Formatting**
   - Date format conversion (YYYY-MM-DD to DD-MM-YYYY if needed)
   - Currency formatting for monetary values
   - Dropdown option exact text matching

3. **Conditional Fields**
   - Check if a field needs to be displayed by toggling its parent checkbox/radio
   - Wait for conditional fields to appear after toggling

4. **Validation Handling**
   - Prepare fallback values for required fields
   - Handle format validation errors

5. **Dynamic Mapping**
   - Build the mapping at runtime by analyzing the form structure
   - Allow for fuzzy matching of field labels when exact matches aren't found