# Form Filling Agent Guide

This document outlines the strategy for implementing a browser agent that reliably fills out the insurance forms.

## Form Navigation Strategy

### Easy Form (form2)
```
1. Load the form page
2. Wait for all form elements to be visible
3. Fill all fields in a single view:
   a. Enter text fields (firstName, lastName, dateOfBirth, email, phoneNumber)
   b. Toggle checkboxes as needed (hasInsurance, wantsNewsletter, agreeToTerms)
4. Submit the form
5. Wait for response and verify success (ASTEROID_1 code)
```

### Hard Form (form)
```
1. Load the form page
2. Navigate through each tab in sequence:

   a. CONTACT DETAILS
      - Select title from dropdown
      - Fill personal information fields
      - Toggle Joint Insured checkbox if needed
      - Fill any revealed conditional fields
      - Click Next button

   b. BUSINESS INFO
      - Fill business name, type, and trade
      - Complete address fields
      - Enter ERN code and website
      - Fill description and experience fields
      - Click Next button

   c. PREMISES DETAILS
      - Complete premises type and listed status
      - Fill premises address
      - Enter flat details if applicable
      - Complete all construction fields
      - Toggle checkboxes and fill conditional fields
      - Click Next button

   d. SECURITY & SAFETY
      - Complete all security fields
      - Toggle CCTV and fill related fields if enabled
      - Toggle intruder alarm and fill related fields if enabled
      - Complete fire safety section
      - Toggle flammable storage and complete if enabled
      - Click Next button

   e. COVERAGE OPTIONS
      - Complete all coverage checkboxes
      - Fill amount fields
      - Complete material damage section
      - Fill portable equipment details
      - Submit the form

3. Wait for response and verify success (ASTEROID_1 code)
```

## Error Recovery Strategies

1. **Field Not Found**
   - Try alternative selectors
   - Use visual search if text-based selectors fail
   - Skip non-required fields and continue

2. **Invalid Input**
   - If error message appears, parse the message
   - Adjust the input based on error feedback
   - Retry with corrected value

3. **Navigation Issues**
   - If Next button not found, try scrolling to reveal it
   - Check for validation errors preventing navigation
   - Look for alternative navigation elements

4. **Conditional Fields**
   - After toggling a checkbox, explicitly wait for new fields
   - Check DOM changes to verify field appearance

5. **Submission Failures**
   - Take screenshot of final state
   - Check for any highlighted error fields
   - Verify all required fields are filled

## Debugging and Monitoring

1. **Logging**
   - Log each field interaction
   - Record element selectors used
   - Log any input transformations applied

2. **Screenshots**
   - Capture state before/after each section completion
   - Capture any error states
   - Take final screenshot showing result code

3. **Field Validation**
   - Validate that entered values match expected values
   - Verify dropdown selections are correct
   - Confirm checkbox states match expected values

4. **Performance Metrics**
   - Track time taken for each section
   - Measure overall form completion time
   - Record success rate across multiple attempts

## Implementation Framework

```javascript
async function fillForm(formUrl, formData) {
  // 1. Initialize browser and navigate to form
  const browser = await playwright.chromium.launch({ headless: false });
  const page = await browser.newPage();
  await page.goto(formUrl);

  // 2. Determine form type and select strategy
  const isHardForm = formUrl.includes('/form');
  const isEasyForm = formUrl.includes('/form2');

  if (isEasyForm) {
    await fillEasyForm(page, formData);
  } else if (isHardForm) {
    await fillHardForm(page, formData);
  }

  // 3. Check result and return success/failure
  const resultText = await page.textContent('.result-code');
  await browser.close();
  
  return {
    success: resultText.includes('ASTEROID_1'),
    result: resultText
  };
}
```