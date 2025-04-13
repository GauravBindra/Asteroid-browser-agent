#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
import json
import os
import time

def explore_form(url):
    """
    Explore a form at the given URL, extract its structure, and take a screenshot.
    """
    print(f"Exploring form at: {url}")
    
    with sync_playwright() as p:
        # Launch browser in non-headless mode to see the process
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # Navigate to the form
            page.goto(url, wait_until="networkidle")
            print("Page loaded successfully")
            
            # Wait for the page to be fully loaded
            page.wait_for_timeout(2000)  # Wait 2 seconds to ensure everything is loaded
            
            # Extract form elements
            form_elements = page.evaluate("""() => {
                // Find all input elements, selects, textareas, and submit buttons
                const elements = Array.from(document.querySelectorAll('input, select, textarea, button[type="submit"]'));
                
                return elements.map(el => {
                    // Try to find associated label
                    let labelText = 'none';
                    
                    // Check for label with 'for' attribute
                    if (el.id) {
                        const label = document.querySelector(`label[for="${el.id}"]`);
                        if (label) {
                            labelText = label.textContent.trim();
                        }
                    }
                    
                    // Check for parent label
                    if (labelText === 'none') {
                        const parentLabel = el.closest('label');
                        if (parentLabel) {
                            // Get text content excluding the text of the input itself
                            const clone = parentLabel.cloneNode(true);
                            const inputs = clone.querySelectorAll('input, select, textarea');
                            inputs.forEach(input => input.remove());
                            labelText = clone.textContent.trim();
                        }
                    }
                    
                    // Check for nearby label or text
                    if (labelText === 'none') {
                        // Look for preceding element that might be a label
                        const prevSibling = el.previousElementSibling;
                        if (prevSibling && prevSibling.tagName !== 'INPUT' && prevSibling.tagName !== 'SELECT' && prevSibling.tagName !== 'TEXTAREA') {
                            labelText = prevSibling.textContent.trim();
                        }
                    }
                    
                    // For checkboxes and radios, look for text nodes next to them
                    if ((el.type === 'checkbox' || el.type === 'radio') && labelText === 'none') {
                        const parent = el.parentElement;
                        if (parent) {
                            const textContent = parent.textContent.trim();
                            if (textContent) {
                                labelText = textContent;
                            }
                        }
                    }
                    
                    // Get options for select elements
                    let options = [];
                    if (el.tagName.toLowerCase() === 'select') {
                        options = Array.from(el.options).map(opt => ({
                            value: opt.value,
                            text: opt.textContent.trim()
                        }));
                    }
                    
                    return {
                        type: el.tagName.toLowerCase(),
                        inputType: el.type || 'none',
                        id: el.id || 'none',
                        name: el.name || 'none',
                        placeholder: el.placeholder || 'none',
                        label: labelText,
                        value: el.value || 'none',
                        checked: el.checked || false,
                        required: el.required || false,
                        options: options
                    };
                });
            }""")
            
            # Save form structure to a JSON file
            form_name = url.split('/')[-1] or 'form'
            with open(f"{form_name}_structure.json", 'w') as f:
                json.dump(form_elements, f, indent=2)
            
            print(f"Form structure saved to {form_name}_structure.json")
            print("Form elements:")
            print(json.dumps(form_elements, indent=2))
            
            # Take a screenshot
            screenshot_path = f"{form_name}_screenshot.png"
            page.screenshot(path=screenshot_path)
            print(f"Screenshot saved as {screenshot_path}")
            
            # Wait a bit to allow manual inspection
            print("Waiting 10 seconds for manual inspection...")
            time.sleep(10)
            
        except Exception as e:
            print(f"Error exploring form: {e}")
        finally:
            browser.close()

def main():
    # Create a directory for outputs if it doesn't exist
    os.makedirs("form_exploration", exist_ok=True)
    os.chdir("form_exploration")
    
    # Explore both forms
    print("Starting form exploration...")
    
    # Easy form
    explore_form("https://asteroid.ai/form2")
    
    # Hard form
    explore_form("https://asteroid.ai/form")
    
    print("Form exploration completed")

if __name__ == "__main__":
    main()
