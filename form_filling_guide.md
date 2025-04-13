# Form Filling Agent Guide

This document outlines the complete strategy for implementing a browser agent that reliably fills out the insurance forms.

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

## 🔧 Core Form Filling Features

### 📌 Robust Element Location Strategies

```javascript
// Prioritize selection by visible labels (most reliable)
const titleField = page.getByLabel('Title');
await titleField.selectOption('Prof');

// Use text-based selection for buttons without labels
const nextButton = page.getByText('Next', { exact: true });
await nextButton.click();

// Use role-based selection for semantic elements
const submitButton = page.getByRole('button', { name: 'Submit' });
await Promise.all([
  page.waitForNavigation(), // Wait for navigation to complete
  submitButton.click()      // Click the submit button
]);

// Use placeholders for fields without labels
await page.getByPlaceholder('dd-mm-yyyy').fill('15-06-1985');

// Fallback to attribute-based selectors when needed
if (!(await page.getByLabel('Joint Insured').isVisible())) {
  await page.locator('input[type="checkbox"][id*="joint"]').click();
}
```

### 📌 Handling Various Field Types

```javascript
// Text inputs with verification
await page.getByLabel('First Name').fill(data.firstName);
const enteredName = await page.getByLabel('First Name').inputValue();
console.log(`First Name validation: ${enteredName === data.firstName}`);

// Checkbox handling with verification
await page.getByLabel('Joint Insured').setChecked(data.jointInsured);
const isChecked = await page.getByLabel('Joint Insured').isChecked();
console.log(`Joint Insured checkbox state: ${isChecked}`);

// Dropdown selection with verification
await page.getByLabel('Business Type').selectOption(data.business.type);
const selectedValue = await page.getByLabel('Business Type').inputValue();
console.log(`Selected business type: ${selectedValue}`);

// Date fields with format conversion
await page.getByLabel('Date of Birth').fill(formatDate(data.dateOfBirth));

// File uploads when needed
await page.setInputFiles('input[type="file"]', 'path/to/file.pdf');
```

### 📌 Data Mapping Implementation

```javascript
// Example of data mapping implementation
async function fillByLabel(page, labelText, value) {
  // Skip empty values if field is optional
  if (value === undefined || value === null) {
    console.log(`Skipping field "${labelText}" - no value provided`);
    return true;
  }
  
  try {
    const field = page.getByLabel(labelText, { exact: false });
    await field.waitFor({ state: 'visible', timeout: 3000 });
    
    // Handle different input types
    const tagName = await field.evaluate(el => el.tagName.toLowerCase());
    const type = await field.evaluate(el => el.type || 'text');
    
    if (tagName === 'select') {
      await field.selectOption(String(value));
    } else if (type === 'checkbox') {
      await field.setChecked(Boolean(value));
    } else if (type === 'date') {
      await field.fill(formatDate(value));
    } else {
      await field.fill(String(value));
    }
    
    return true;
  } catch (error) {
    console.error(`Failed to fill field "${labelText}": ${error.message}`);
    return false;
  }
}

// Implement fuzzy matching for labels
function findBestLabelMatch(fieldName, availableLabels) {
  // Direct match
  if (availableLabels.includes(fieldName)) {
    return fieldName;
  }
  
  // Normalize and check for similarity
  const normalizedFieldName = fieldName.toLowerCase().replace(/[_-\s]/g, '');
  
  for (const label of availableLabels) {
    const normalizedLabel = label.toLowerCase().replace(/[_-\s]/g, '');
    if (normalizedLabel === normalizedFieldName ||
        normalizedLabel.includes(normalizedFieldName) ||
        normalizedFieldName.includes(normalizedLabel)) {
      return label;
    }
  }
  
  return null;
}
```

## ⚠️ Error Handling and Edge Cases

### 📌 Synchronization and Timing Strategies

```javascript
// Wait for page to be fully loaded
await page.waitForLoadState('networkidle');

// Explicit wait for element to be both visible and enabled
await page.getByLabel('First Name').waitFor({ 
  state: 'visible', 
  timeout: 5000 
});

// Safe navigation with verification
async function navigateToNextSection(page) {
  try {
    const nextButton = page.getByRole('button', { name: 'Next' });
    await nextButton.waitFor({ state: 'visible', timeout: 2000 });
    
    // Wait for both the click and navigation to complete
    await Promise.all([
      page.waitForNavigation({ timeout: 5000 }).catch(() => {}),
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

### 📌 Conditional Field Handling

```javascript
// Toggle a checkbox and wait for conditional field to appear
async function handleConditionalField(page, triggerSelector, fieldSelector, value, maxRetries = 3) {
  // Find and toggle the trigger element
  const trigger = page.locator(triggerSelector);
  await trigger.setChecked(true);
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      // Wait for conditional field to appear
      await page.locator(fieldSelector).waitFor({ state: 'visible', timeout: 2000 });
      
      // Fill the conditional field
      await page.locator(fieldSelector).fill(value);
      return true;
    } catch (error) {
      console.log(`Retry ${i+1} for conditional field: ${error.message}`);
      
      // Toggle the trigger off and on again to try to reveal the field
      if (i < maxRetries - 1) {
        await trigger.setChecked(false);
        await page.waitForTimeout(500);
        await trigger.setChecked(true);
      }
    }
  }
  
  console.error(`Failed to handle conditional field after ${maxRetries} attempts`);
  return false;
}
```

### 📌 Retry Logic for Form Filling

```javascript
// Implement retry logic for form filling
async function fillFieldWithRetry(page, fieldSelector, value, maxRetries = 3) {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      const field = page.locator(fieldSelector);
      await field.waitFor({ state: 'visible', timeout: 2000 });
      await field.fill(String(value));
      
      // Verify the value was properly entered
      const enteredValue = await field.inputValue();
      if (enteredValue === String(value)) {
        return true;
      }
      console.log(`Value verification failed for ${fieldSelector}, retrying...`);
    } catch (error) {
      console.log(`Attempt ${attempt+1} failed: ${error.message}`);
      await page.waitForTimeout(500); // Brief pause before retry
    }
  }
  console.error(`Failed to fill field after ${maxRetries} attempts`);
  return false;
}
```

### 📌 Form Validation Error Handling

```javascript
// Check for validation errors after submission attempt
async function checkForValidationErrors(page) {
  // Common error selectors across many forms
  const errorSelectors = [
    '.error', '.invalid-feedback', '[aria-invalid="true"]',
    '.form-error', '.validation-error', '.error-message'
  ];
  
  const errors = [];
  
  for (const selector of errorSelectors) {
    const errorElements = await page.locator(selector).all();
    for (const element of errorElements) {
      if (await element.isVisible()) {
        const text = await element.innerText();
        const nearbyLabel = await element.evaluate(el => {
          // Find nearby label or input with name
          const input = el.closest('.form-group')?.querySelector('input, select, textarea');
          return input?.name || input?.id || 'Unknown field';
        });
        errors.push({ field: nearbyLabel, message: text });
      }
    }
  }
  
  return errors;
}
```

## ✅ Validation and Monitoring

### 📌 Automatic Field Validation

```javascript
// Validate all filled fields against expected values
async function validateFormData(page, formData) {
  const results = { match: [], mismatch: [], missing: [] };
  
  for (const [fieldName, expectedValue] of Object.entries(formData)) {
    try {
      // Try using label
      const field = page.getByLabel(fieldName, { exact: false });
      if (await field.count() > 0) {
        // Get actual value based on field type
        let actualValue;
        const type = await field.evaluate(el => el.type).catch(() => 'text');
        
        if (type === 'checkbox' || type === 'radio') {
          actualValue = await field.isChecked();
        } else {
          actualValue = await field.inputValue();
        }
        
        // Compare values (with type conversion)
        const isMatch = String(actualValue) === String(expectedValue);
        if (isMatch) {
          results.match.push({ field: fieldName, value: expectedValue });
        } else {
          results.mismatch.push({ 
            field: fieldName, 
            expected: expectedValue, 
            actual: actualValue 
          });
        }
      } else {
        results.missing.push({ field: fieldName });
      }
    } catch (error) {
      results.missing.push({ field: fieldName, error: error.message });
    }
  }
  
  return results;
}
```

### 📌 Comprehensive Logging

```javascript
// Enhanced logging with telemetry
class FormAutomationLogger {
  constructor(formName) {
    this.startTime = Date.now();
    this.formName = formName;
    this.actions = [];
    this.errors = [];
    this.screenshots = [];
  }
  
  logAction(action, fieldName, value, success = true) {
    this.actions.push({
      timestamp: Date.now(),
      action,
      fieldName,
      value: typeof value === 'string' && value.length > 100 
        ? `${value.substring(0, 100)}...` : value,
      success
    });
  }
  
  logError(error, fieldName = null) {
    this.errors.push({
      timestamp: Date.now(),
      message: error.message || String(error),
      stack: error.stack,
      fieldName
    });
  }
  
  async takeScreenshot(page, name) {
    const path = `./screenshots/${this.formName}_${name}_${Date.now()}.png`;
    await page.screenshot({ path, fullPage: true });
    this.screenshots.push({ timestamp: Date.now(), name, path });
  }
  
  getSummary() {
    return {
      formName: this.formName,
      duration: Date.now() - this.startTime,
      actionCount: this.actions.length,
      errorCount: this.errors.length,
      screenshotCount: this.screenshots.length,
      success: this.errors.length === 0
    };
  }
  
  saveToFile() {
    const filename = `./logs/${this.formName}_${Date.now()}.json`;
    require('fs').writeFileSync(
      filename, 
      JSON.stringify({
        summary: this.getSummary(),
        actions: this.actions,
        errors: this.errors,
        screenshots: this.screenshots
      }, null, 2)
    );
    return filename;
  }
}
```

### 📌 Performance Metrics

```javascript
// Collect performance metrics
async function collectPerformanceMetrics(page) {
  // Navigation and load times
  const timingJson = await page.evaluate(() => JSON.stringify(performance.timing));
  const timing = JSON.parse(timingJson);
  
  // Calculate key metrics
  const metrics = {
    domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
    load: timing.loadEventEnd - timing.navigationStart,
    networkLatency: timing.responseEnd - timing.requestStart,
    processingTime: timing.domComplete - timing.domLoading,
    totalTime: timing.loadEventEnd - timing.navigationStart
  };
  
  // Collect Core Web Vitals
  const webVitals = await page.evaluate(() => {
    return {
      cls: window.cumulativeLayoutShift?.value || 0,
      lcp: window.largestContentfulPaint?.value || 0,
      fid: window.firstInputDelay?.value || 0
    };
  });
  
  return { ...metrics, ...webVitals };
}
```

## 🧠 Implementation Framework

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
  
  // Initialize logger
  const formType = formUrl.includes('/form2') ? 'easy_form' : 'hard_form';
  const logger = new FormAutomationLogger(formType);
  
  // Start tracing for debugging
  await context.tracing.start({ screenshots: true, snapshots: true });
  
  const page = await context.newPage();
  
  // Setup event handlers for dialogs and console messages
  page.on('dialog', async dialog => {
    logger.logAction('dialog', dialog.type(), dialog.message());
    await dialog.accept();
  });
  
  page.on('console', msg => {
    if (msg.type() === 'error') {
      logger.logAction('console', 'error', msg.text());
    }
  });
  
  try {
    // 2. Navigate to form with timeout and waitUntil
    await page.goto(formUrl, { 
      waitUntil: 'networkidle',
      timeout: 30000 
    });
    
    // Take initial screenshot
    await logger.takeScreenshot(page, 'initial_load');
    
    // 3. Determine form type and select strategy
    const isHardForm = formUrl.includes('/form') && !formUrl.includes('/form2');
    const isEasyForm = formUrl.includes('/form2');

    let result = false;
    
    if (isEasyForm) {
      result = await fillEasyForm(page, formData, logger);
    } else if (isHardForm) {
      result = await fillHardForm(page, formData, logger);
    }
    
    // 4. Validate form values after filling
    const validationResult = await validateFormData(page, formData);
    logger.logAction('validation', 'complete', validationResult);
    
    // 5. Submit the form and check for success
    await submitForm(page, logger);
    
    // Wait for response
    await page.waitForSelector('.result-code', { timeout: 10000 })
      .catch(() => logger.logError(new Error("Could not find result code")));
    
    // Take final screenshot
    await logger.takeScreenshot(page, 'final_state');
    
    // Get result code
    const resultText = await page.textContent('.result-code')
      .catch(() => "UNKNOWN");
    
    logger.logAction('result', 'form_submission', resultText);
    
    // Save trace for debugging
    await context.tracing.stop({ path: `./traces/${formType}_${Date.now()}.zip` });
    
    // Log final summary
    const logFile = logger.saveToFile();
    
    return {
      success: resultText.includes('ASTEROID_1'),
      result: resultText,
      formType: isEasyForm ? 'easy' : 'hard',
      logFile,
      validation: {
        matchCount: validationResult.match.length,
        mismatchCount: validationResult.mismatch.length,
        missingCount: validationResult.missing.length
      },
      timestamp: new Date().toISOString()
    };
    
  } catch (error) {
    // Log error and take screenshot
    logger.logError(error);
    await logger.takeScreenshot(page, 'error_state');
    
    // Save trace for debugging
    await context.tracing.stop({ path: `./traces/${formType}_error_${Date.now()}.zip` });
    
    // Log final summary
    const logFile = logger.saveToFile();
    
    return {
      success: false,
      error: error.message,
      logFile
    };
  } finally {
    await browser.close();
  }
}
```

## High-Level Architecture and Quality Metrics

### Form Automation Class Structure

```javascript
class AsteroidFormAutomator {
  constructor(options = {}) {
    this.headless = options.headless ?? false;
    this.slowMo = options.slowMo ?? 50;
    this.logger = options.logger ?? new FormAutomationLogger();
    this.browser = null;
    this.context = null;
    this.metrics = {
      totalRuns: 0,
      successfulRuns: 0,
      fieldMatchAccuracy: 0,
      averageCompletionTime: 0,
      domCoverage: 0
    };
  }
  
  async initialize() {
    this.browser = await playwright.chromium.launch({
      headless: this.headless,
      slowMo: this.slowMo
    });
    this.context = await this.browser.newContext({
      viewport: { width: 1280, height: 1024 }
    });
    return this;
  }
  
  async fillForm(formUrl, formData) {
    // Implementation details here
  }
  
  async runBatch(testCases) {
    const results = [];
    for (const testCase of testCases) {
      results.push(await this.fillForm(testCase.url, testCase.data));
    }
    return {
      results,
      summary: this.getMetricsSummary()
    };
  }
  
  getMetricsSummary() {
    return {
      fieldMatchAccuracy: `${this.metrics.fieldMatchAccuracy.toFixed(2)}%`,
      successRate: `${(this.metrics.successfulRuns / this.metrics.totalRuns * 100).toFixed(2)}%`,
      averageCompletionTime: `${this.metrics.averageCompletionTime.toFixed(2)}ms`,
      domCoverage: `${this.metrics.domCoverage.toFixed(2)}%`,
      totalRuns: this.metrics.totalRuns
    };
  }
  
  async close() {
    if (this.browser) {
      await this.browser.close();
    }
  }
}
```

This comprehensive guide provides a complete strategy for developing a robust form-filling agent for the Asteroid Form Challenge.