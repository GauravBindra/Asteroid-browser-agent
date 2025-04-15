# Easy Form Structure and Flow

## Form URL
- https://asteroid.ai/form2

## Overview
A single-page "Personal Information Form" for a commercial property insurance policy application.

## Form Fields

### Input Fields
1. **First Name** (text)
   - Required: Yes
   - Label: "First Name"

2. **Last Name** (text)
   - Required: Yes
   - Label: "Last Name"

3. **Date of Birth** (text)
   - Required: Yes
   - Label: "Date of Birth (dd-mm-yyyy)"
   - Format: dd-mm-yyyy
   - Placeholder: "dd-mm-yyyy"

4. **Email** (email)
   - Required: Yes
   - Label: "Email"

5. **Phone Number** (tel)
   - Required: Yes
   - Label: "Phone Number"

### Checkbox Fields
1. **Insurance** (checkbox)
   - ID: "hasInsurance"
   - Label: "Do you currently have insurance?"
   - Required: Yes (must be set according to input data)

2. **Newsletter** (checkbox)
   - ID: "wantsNewsletter"
   - Label: "Would you like to receive our newsletter?"
   - Required: Yes (must be set according to input data)

3. **Terms and Conditions** (checkbox)
   - ID: "agreeToTerms"
   - Label: "I agree to the terms and conditions"
   - Required: Yes (must be checked, shows validation error if not checked)

## Form Flow

### Step 1: Fill Form
- User fills out all text fields
- User checks/unchecks relevant checkboxes according to the input data
- The "Review" button appears at the bottom right

### Step 2: Review and Submit
- After clicking "Review", the user sees the review screen
- On this screen, user must click the "Submit" button
- The success/failure code appears on the same review screen after submission

### Step 3: Success/Failure Code
- After clicking "Submit", a code appears on the same screen:
  - "ASTEROID_1" if the form was filled correctly
  - "ASTEROID_0" if there were any errors in filling the form
- The code needs to be extracted and validated

## Validation Notes
- All fields including checkboxes must be filled according to the input data
- Terms and conditions must be checked
- Error messages appear inline when validation fails
- Date format must follow dd-mm-yyyy pattern
- All fields must be correctly filled for successful submission

## Input Data Example
```json
{
  "firstName": "John",
  "lastName": "Smith",
  "dateOfBirth": "15-06-1985",
  "email": "john.smith@example.com",
  "phoneNumber": "07700900123",
  "hasInsurance": true,
  "wantsNewsletter": false,
  "agreeToTerms": true
}
```