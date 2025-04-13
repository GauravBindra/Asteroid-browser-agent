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

## Advanced Playwright Techniques

### 1. Robust Element Selection

```javascript
// Prioritize selection by visible labels (most reliable)
const titleField = page.getByLabel('Title');
await titleField.selectOption('Prof');

// Use text-based selection for buttons and elements without labels
const nextButton = page.getByText('Next', { exact: true });
await nextButton.click();

// Use role-based selection for standard elements
const submitButton = page.getByRole('button', { name: 'Submit' });
await Promise.all([
  page.waitForNavigation(), // Wait for navigation to complete
  submitButton.click()      // Click the submit button
]);

// Fallback to CSS selectors when needed
if (!(await page.getByLabel('Joint Insured').isVisible())) {
  await page.locator('input[type="checkbox"][id*="joint"]').click();
}
```

### 2. Form Interaction Best Practices

```javascript
// Wait for element to be both visible and enabled before interaction
await page.getByLabel('First Name').waitFor({ state: 'visible', timeout: 5000 });
await page.getByLabel('First Name').fill(data.firstName);

// Clear input fields before filling them
await page.getByLabel('Phone Number').fill('');
await page.getByLabel('Phone Number').fill(data.phoneNumber);

// Checkbox handling with verification
await page.getByLabel('Joint Insured').setChecked(data.jointInsured);
const isChecked = await page.getByLabel('Joint Insured').isChecked();
console.log(`Joint Insured checkbox state: ${isChecked}`);

// Dropdown selection with verification
await page.getByLabel('Business Type').selectOption(data.business.type);
const selectedValue = await page.getByLabel('Business Type').inputValue();
console.log(`Selected business type: ${selectedValue}`);

// Handling date fields (which may have special format requirements)
await page.getByLabel('Date of Birth').fill(formatDate(data.dateOfBirth));
```

### 3. Handling Conditional Fields

```javascript
// Toggle a checkbox and wait for conditional field to appear
await page.getByLabel('CCTV').setChecked(true);
await page.waitForSelector('text=CCTV Type', { state: 'visible', timeout: 2000 });
await page.getByLabel('CCTV Type').selectOption(data.security.cctvType);

// Retry logic for conditional fields that may be slow to appear
async function fillConditionalField(trigger, fieldLabel, value, maxRetries = 3) {
  await trigger.setChecked(true);
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      await page.getByLabel(fieldLabel).waitFor({ state: 'visible', timeout: 2000 });
      await page.getByLabel(fieldLabel).fill(value);
      return true;
    } catch (error) {
      console.log(`Retry ${i+1} for conditional field ${fieldLabel}`);
      // Toggle the trigger off and on again to try to reveal the field
      if (i < maxRetries - 1) {
        await trigger.setChecked(false);
        await page.waitForTimeout(500);
        await trigger.setChecked(true);
      }
    }
  }
  
  return false;
}
```

### 4. Multi-Step Form Navigation

```javascript
// Safe navigation between form sections
async function navigateToNextSection(page) {
  try {
    const nextButton = page.getByRole('button', { name: 'Next' });
    await nextButton.waitFor({ state: 'visible', timeout: 2000 });
    
    // Wait for both the click and navigation to complete
    await Promise.all([
      page.waitForURL('**/next-section', { timeout: 5000 }).catch(() => {}),
      nextButton.click()
    ]);
    
    // Verify navigation success
    await page.waitForTimeout(1000); // Allow time for new section to fully load
    return true;
  } catch (error) {
    console.error('Navigation failed:', error);
    return false;
  }
}
```

### 5. Error Handling with Retry Logic

```javascript
// Implement retry logic for form filling
async function fillFieldWithRetry(page, fieldLabel, value, maxRetries = 3) {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      const field = page.getByLabel(fieldLabel);
      await field.waitFor({ state: 'visible', timeout: 2000 });
      await field.fill(value);
      
      // Verify the value was properly entered
      const enteredValue = await field.inputValue();
      if (enteredValue === value) {
        return true;
      }
      console.log(`Value verification failed for ${fieldLabel}, retrying...`);
    } catch (error) {
      console.log(`Attempt ${attempt+1} failed for ${fieldLabel}: ${error.message}`);
      await page.waitForTimeout(500); // Brief pause before retry
    }
  }
  console.error(`Failed to fill ${fieldLabel} after ${maxRetries} attempts`);
  return false;
}
```

## Updated Implementation Framework

```javascript
async function fillForm(formUrl, formData) {
  // 1. Initialize browser with improved settings
  const browser = await playwright.chromium.launch({ 
    headless: false,
    slowMo: 50, // Slow down operations by 50ms for better stability
  });
  
  const context = await browser.newContext({
    viewport: { width: 1280, height: 1024 },
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
  });
  
  const page = await context.newPage();
  
  // Setup event handlers for dialogs and console messages
  page.on('dialog', async dialog => {
    console.log(`Dialog message: ${dialog.message()}`);
    await dialog.accept();
  });
  
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.log(`Console error: ${msg.text()}`);
    }
  });
  
  try {
    // 2. Navigate to form with timeout and waitUntil
    await page.goto(formUrl, { 
      waitUntil: 'networkidle',
      timeout: 30000 
    });
    
    // 3. Determine form type and select strategy
    const isHardForm = formUrl.includes('/form') && !formUrl.includes('/form2');
    const isEasyForm = formUrl.includes('/form2');

    let result = false;
    
    if (isEasyForm) {
      result = await fillEasyForm(page, formData);
    } else if (isHardForm) {
      result = await fillHardForm(page, formData);
    }
    
    // 4. Check result and capture final state
    await page.screenshot({ path: 'form-submission-result.png' });
    const resultText = await page.textContent('.result-code');
    
    return {
      success: resultText.includes('ASTEROID_1'),
      result: resultText,
      formType: isEasyForm ? 'easy' : 'hard',
      timestamp: new Date().toISOString()
    };
    
  } catch (error) {
    console.error('Form submission failed:', error);
    await page.screenshot({ path: 'form-error-state.png' });
    return {
      success: false,
      error: error.message
    };
  } finally {
    await browser.close();
  }
}
```