# Form Architecture Documentation

## Easy Form (form2) Architecture

```
EasyForm
│
└── PersonalInformationSection
    ├── TextField: firstName
    ├── TextField: lastName
    ├── TextField: dateOfBirth (format: dd-mm-yyyy)
    ├── EmailField: email
    ├── TelField: phoneNumber
    ├── Checkbox: hasInsurance
    ├── Checkbox: wantsNewsletter
    ├── Checkbox: agreeToTerms
    └── SubmitButton
```

## Hard Form (form) Architecture

```
HardForm
│
├── NavigationTabs
│   ├── ContactDetails
│   ├── BusinessInfo
│   ├── PremisesDetails
│   ├── SecurityAndSafety
│   └── CoverageOptions
│
├── ContactDetailsSection
│   ├── SelectField: title
│   ├── TextField: firstName
│   ├── TextField: lastName
│   ├── DateField: dateOfBirth
│   ├── TelField: phoneNumber
│   ├── NumberField: yearsAsLandlord
│   ├── Checkbox: jointInsured
│   └── ConditionalField: jointInsuredPersonName (appears when jointInsured is checked)
│
├── BusinessInfoSection
│   ├── TextField: businessName
│   ├── SelectField: businessType
│   ├── TextField: businessTrade
│   ├── AddressGroup:
│   │   ├── TextField: addressLine1
│   │   ├── TextField: addressLine2
│   │   ├── TextField: addressLine3
│   │   ├── TextField: city
│   │   └── TextField: postcode
│   ├── TextField: ernTaxCode
│   ├── Checkbox: exemptFromERNCode
│   ├── TextField: websiteUrl
│   ├── TextField: businessDescription
│   ├── NumberField: yearsOfExperience
│   └── TextareaField: descriptionOfExperience
│
├── PremisesDetailsSection
│   ├── IdentityGroup:
│   │   ├── SelectField: premisesType
│   │   ├── SelectField: listedStatus
│   │   ├── AddressGroup:
│   │   │   ├── TextField: addressLine1
│   │   │   ├── TextField: addressLine2
│   │   │   ├── TextField: addressLine3
│   │   │   ├── TextField: city
│   │   │   └── TextField: postcode
│   │   ├── NumberField: numberOfFlatsInBlock
│   │   └── NumberField: numberOfFlatsToBeInsured
│   └── ConstructionGroup:
│       ├── SelectField: roofType
│       ├── SelectField: wallType
│       ├── SelectField: floorType
│       ├── SelectField: stairType
│       ├── Checkbox: hasFlatRoof
│       ├── ConditionalField: percentageOfFlatRoof (appears when hasFlatRoof is checked)
│       ├── ConditionalField: flatRoofLastInspected (appears when hasFlatRoof is checked)
│       ├── Checkbox: haveColdStores
│       ├── NumberField: rebuildingCost
│       ├── DateField: roofLastRelaid
│       ├── NumberField: numberOfStoreys
│       ├── SelectField: anyCompositePanels
│       ├── TextField: warehouseFloorArea
│       ├── DateField: yearOfConstruction
│       ├── TextareaField: constructionDetails
│       ├── Checkbox: isBuildingPurposeBuilt
│       └── Checkbox: isUndergoingBuildingWorks
│
├── SecurityAndSafetySection
│   ├── SecurityGroup:
│   │   ├── Checkbox: cctv
│   │   ├── ConditionalField: cctvType (appears when cctv is checked)
│   │   ├── ConditionalField: cctvCoverage (appears when cctv is checked)
│   │   ├── Checkbox: selfContained
│   │   ├── SelectField: doorSecurityType
│   │   ├── Checkbox: fittedWithSmokeAlarms
│   │   ├── Checkbox: intruderAlarm
│   │   ├── ConditionalField: intruderAlarmType (appears when intruderAlarm is checked)
│   │   └── Checkbox: requireTerrorismCover
│   └── FireSafetyGroup:
│       ├── SelectField: heating
│       ├── Checkbox: fireAlarm
│       ├── SelectField: smokingPolicy
│       ├── Checkbox: sprinklerSystem
│       ├── Checkbox: fireExtinguishers
│       ├── TextField: fireDetectorsCoverage
│       ├── Checkbox: flammableLiquidStored
│       └── ConditionalField: flammableLiquids (appears when flammableLiquidStored is checked)
│
└── CoverageOptionsSection
    ├── CoverageGroup:
    │   ├── Checkbox: terrorism
    │   ├── Checkbox: subsidence
    │   ├── Checkbox: accidentalDamage
    │   ├── NumberField: sumInsuredLossOfRent
    │   ├── NumberField: periodOfIndemnityInMonths
    │   └── NumberField: propertyOwnersLiabilityAmount
    ├── MaterialDamageGroup:
    │   ├── NumberField: stocksSumInsured
    │   ├── NumberField: buildingSumInsured
    │   ├── NumberField: tenantsImprovementsSumInsured
    │   ├── NumberField: electronicOfficeEquipmentSumInsured
    │   └── PortableEquipmentGroup:
    │       ├── SelectField: location
    │       ├── NumberField: toolsSumInsured
    │       ├── NumberField: smartPhoneSumInsured
    │       ├── TextareaField: miscellaneousToInsure
    │       └── NumberField: otherPortableComputerEquipmentSumInsured
    └── SubmitButton
```