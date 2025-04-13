const puppeteer = require('puppeteer');

async function exploreForm(url) {
  console.log(`Exploring form at: ${url}`);
  
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();
  
  try {
    // Navigate to the form
    await page.goto(url, { waitUntil: 'networkidle2' });
    console.log('Page loaded successfully');
    
    // Wait for form elements to be visible
    await page.waitForSelector('form', { timeout: 5000 })
      .catch(() => console.log('No direct form element found, looking for input elements'));
    
    // Get all form elements
    const formElements = await page.evaluate(() => {
      // Find all input elements
      const inputs = Array.from(document.querySelectorAll('input, select, textarea, button[type="submit"]'));
      
      return inputs.map(el => {
        return {
          type: el.tagName.toLowerCase(),
          inputType: el.type || 'none',
          id: el.id || 'none',
          name: el.name || 'none',
          placeholder: el.placeholder || 'none',
          label: el.labels && el.labels[0] ? el.labels[0].textContent.trim() : 'none',
          value: el.value || 'none',
          checked: el.checked,
          required: el.required,
          options: el.tagName.toLowerCase() === 'select' ? 
            Array.from(el.options).map(opt => opt.textContent) : []
        };
      });
    });
    
    console.log('Form structure:');
    console.log(JSON.stringify(formElements, null, 2));
    
    // Take a screenshot
    await page.screenshot({ path: `${url.split('/').pop()}_screenshot.png` });
    console.log(`Screenshot saved as ${url.split('/').pop()}_screenshot.png`);
    
    // Wait a bit to allow manual inspection
    await new Promise(resolve => setTimeout(resolve, 10000));
    
  } catch (error) {
    console.error('Error exploring form:', error);
  } finally {
    await browser.close();
  }
}

// Explore both forms
(async () => {
  // Easy form
  await exploreForm('https://asteroid.ai/form2');
  
  // Hard form
  await exploreForm('https://asteroid.ai/form');
  
  console.log('Form exploration completed');
})();
