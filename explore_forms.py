#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
import json
import os
import time
from datetime import datetime

def explore_form(url):
    """
    Comprehensively explore a form at the given URL, capturing its full structure,
    interaction states, and taking screenshots of all sections.
    """
    print(f"\n{'='*80}\nExploring form at: {url}\n{'='*80}")
    
    form_dir = url.split('/')[-1] or 'form'
    os.makedirs(form_dir, exist_ok=True)
    
    with sync_playwright() as p:
        # Launch browser with larger viewport to see more content
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={'width': 1280, 'height': 1024})
        page = context.new_page()
        
        try:
            # Navigate to the form
            page.goto(url, wait_until="networkidle")
            print("✅ Page loaded successfully")
            
            # Wait for the page to be fully loaded
            page.wait_for_timeout(2000)
            
            # Take a full initial screenshot
            initial_path = os.path.join(form_dir, "initial_view.png")
            page.screenshot(path=initial_path, full_page=True)
            print(f"✅ Initial full-page screenshot saved as {initial_path}")
            
            # 1. Find all form sections and tabs
            print("\nLocating form sections and navigation elements...")
            
            # Look for tab navigation and section indicators
            tab_selectors = [
                'button[role="tab"]', 
                '.nav-item', 
                '.tab', 
                '.section-tab',
                'ul.nav li',
                '.form-section',
                '.step-indicator'
            ]
            
            # Try different selectors until we find sections
            tabs = []
            for selector in tab_selectors:
                tabs = page.query_selector_all(selector)
                if tabs and len(tabs) > 0:
                    print(f"✅ Found {len(tabs)} form sections using selector: {selector}")
                    break
            
            # Manual check for next buttons if no tabs found
            if not tabs:
                next_buttons = page.query_selector_all('button:has-text("Next"), button:has-text("Continue"), .next-button, .btn-next')
                if next_buttons:
                    print(f"✅ Found {len(next_buttons)} next/continue buttons. Form appears to be multi-step.")
                else:
                    print("⚠️ No explicit sections or next buttons found. Form might be single-page.")
            
            # 2. Explore all form sections
            section_data = []
            
            # If we found tabs, explore each one
            if tabs and len(tabs) > 0:
                for i, tab in enumerate(tabs):
                    section_name = tab.inner_text().strip() or f"Section {i+1}"
                    print(f"\nExploring section: {section_name}")
                    
                    # Click on the tab/section
                    try:
                        tab.scroll_into_view_if_needed()
                        tab.click()
                        page.wait_for_timeout(1000)  # Wait for content to load
                        print(f"✅ Navigated to {section_name}")
                    except Exception as e:
                        print(f"⚠️ Could not click section tab: {e}")
                        continue
                    
                    # Capture this section
                    _capture_current_section(page, form_dir, section_name, i, section_data)
            
            # If we found next buttons or no sections, explore sequentially
            else:
                section_count = 0
                has_next = True
                
                while has_next:
                    section_name = f"Step {section_count+1}"
                    print(f"\nExploring {section_name}")
                    
                    # Capture current state
                    _capture_current_section(page, form_dir, section_name, section_count, section_data)
                    
                    # Look for a next button
                    next_buttons = page.query_selector_all('button:has-text("Next"), button:has-text("Continue"), .next-button, .btn-next')
                    
                    if next_buttons and section_count < 10:  # Limit to prevent infinite loops
                        try:
                            next_buttons[0].scroll_into_view_if_needed()
                            next_buttons[0].click()
                            page.wait_for_timeout(1500)  # Wait longer for next section to load
                            print(f"✅ Navigated to next step")
                            section_count += 1
                        except Exception as e:
                            print(f"⚠️ Could not click next button: {e}")
                            has_next = False
                    else:
                        has_next = False
                        print("✅ Reached final section or no more next buttons found")
            
            # 3. Save the complete form data
            form_data = {
                "url": url,
                "exploration_time": datetime.now().isoformat(),
                "sections": section_data
            }
            
            data_path = os.path.join(form_dir, "form_data.json")
            with open(data_path, 'w') as f:
                json.dump(form_data, f, indent=2)
            
            print(f"\n✅ Form exploration completed. Data saved to {data_path}")
            
            # Final full screenshot
            final_path = os.path.join(form_dir, "complete_form.png")
            page.screenshot(path=final_path, full_page=True)
            
        except Exception as e:
            print(f"❌ Error exploring form: {e}")
        finally:
            browser.close()

def _capture_current_section(page, form_dir, section_name, section_index, section_data):
    """Helper function to capture the current section's state and elements"""
    safe_name = section_name.replace(' ', '_').replace('/', '_').lower()
    
    # Take screenshot of current section
    screenshot_path = os.path.join(form_dir, f"{safe_name}.png")
    page.screenshot(path=screenshot_path, full_page=True)
    print(f"✅ Screenshot saved as {screenshot_path}")
    
    # Expand all collapsible sections
    _expand_collapsible_elements(page)
    
    # Extract all form elements in this section
    form_elements = _extract_form_elements(page)
    
    # Try to interact with special elements (dropdowns, checkboxes)
    interactive_elements = _interact_with_elements(page, form_elements, form_dir, safe_name)
    
    # Save section data
    section_info = {
        "name": section_name,
        "index": section_index,
        "elements": form_elements,
        "interactive_elements": interactive_elements
    }
    section_data.append(section_info)
    
    # Save individual section data
    section_data_path = os.path.join(form_dir, f"{safe_name}_data.json")
    with open(section_data_path, 'w') as f:
        json.dump(section_info, f, indent=2)
    
    print(f"✅ Identified {len(form_elements)} form elements in this section")
    return section_info

def _expand_collapsible_elements(page):
    """Find and expand all collapsible elements"""
    # Common selectors for collapsible elements
    collapsible_selectors = [
        '.collapse-header', '.accordion-header', '.expandable', 
        'details:not([open])', '.collapsible', '[aria-expanded="false"]',
        'button[data-toggle="collapse"]', '.dropdown-toggle'
    ]
    
    expanded_count = 0
    for selector in collapsible_selectors:
        collapsibles = page.query_selector_all(selector)
        for elem in collapsibles:
            try:
                elem.scroll_into_view_if_needed()
                elem.click()
                page.wait_for_timeout(300)  # Brief wait for animation
                expanded_count += 1
            except:
                continue  # Skip if can't expand
    
    if expanded_count > 0:
        print(f"✅ Expanded {expanded_count} collapsible elements")
        page.wait_for_timeout(500)  # Wait for all expansions to complete

def _extract_form_elements(page):
    """Extract all form elements and their properties"""
    return page.evaluate("""() => {
        // Find all input elements, selects, textareas, and submit buttons
        const elements = Array.from(document.querySelectorAll(
            'input, select, textarea, button[type="submit"], .form-control, .input-field, [role="combobox"], .checkbox, .radio, .toggle'
        ));
        
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
                
                // For form groups, look for label within the same parent
                const formGroup = el.closest('.form-group, .input-group, .field-container');
                if (formGroup) {
                    const groupLabel = formGroup.querySelector('label, .label, .form-label');
                    if (groupLabel) {
                        labelText = groupLabel.textContent.trim();
                    }
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
            
            // Get validation attributes
            const validationAttrs = {};
            ['required', 'minlength', 'maxlength', 'min', 'max', 'pattern'].forEach(attr => {
                if (el.hasAttribute(attr)) {
                    validationAttrs[attr] = el.getAttribute(attr);
                }
            });
            
            // Get ARIA attributes
            const ariaAttrs = {};
            Array.from(el.attributes)
                .filter(attr => attr.name.startsWith('aria-'))
                .forEach(attr => {
                    ariaAttrs[attr.name] = attr.value;
                });
                
            // Extract CSS classes that might hint at field purpose
            const significantClasses = Array.from(el.classList)
                .filter(cls => 
                    /phone|email|name|date|address|zip|postal|city|state|country|currency|number|price|amount/.test(cls)
                );
            
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
                options: options,
                validation: validationAttrs,
                aria: ariaAttrs,
                classes: significantClasses,
                isVisible: el.offsetParent !== null,
                isDisabled: el.disabled || el.readOnly
            };
        });
    }""")

def _interact_with_elements(page, elements, form_dir, section_name):
    """Interact with special elements to reveal additional options/fields"""
    interactive_data = []
    
    # Handle select elements (dropdowns)
    select_elements = [el for el in elements if el['type'] == 'select']
    if select_elements:
        print(f"Examining {len(select_elements)} dropdown elements...")
        
        for i, select in enumerate(select_elements):
            select_id = select.get('id', '')
            select_name = select.get('name', '')
            label = select.get('label', f"Dropdown {i+1}")
            
            if select_id != 'none':
                selector = f"select#{select_id}"
            elif select_name != 'none':
                selector = f"select[name='{select_name}']"
            else:
                continue
                
            try:
                # Capture dropdown interaction
                dropdown_info = {"type": "dropdown", "label": label, "options": []}
                
                # Click to open the dropdown
                dropdown = page.query_selector(selector)
                if not dropdown:
                    continue
                    
                dropdown.scroll_into_view_if_needed()
                
                # Take screenshot of dropdown in default state
                pre_path = os.path.join(form_dir, f"{section_name}_dropdown_{i+1}_closed.png")
                page.screenshot(path=pre_path, full_page=False, clip={"x": 0, "y": 0, "width": 1280, "height": 1024})
                
                # Open the dropdown
                dropdown.click()
                page.wait_for_timeout(500)
                
                # Take screenshot with dropdown open
                open_path = os.path.join(form_dir, f"{section_name}_dropdown_{i+1}_open.png")
                page.screenshot(path=open_path, full_page=False, clip={"x": 0, "y": 0, "width": 1280, "height": 1024})
                
                # Get all options
                options = dropdown.evaluate("""select => {
                    return Array.from(select.options).map(opt => ({
                        value: opt.value,
                        text: opt.textContent.trim()
                    }));
                }""")
                
                dropdown_info["options"] = options
                interactive_data.append(dropdown_info)
                
                # Click elsewhere to close the dropdown
                page.click("body", position={"x": 10, "y": 10})
                page.wait_for_timeout(300)
                
            except Exception as e:
                print(f"⚠️ Error interacting with dropdown: {e}")
    
    # Handle checkbox elements that might reveal conditional fields
    checkbox_elements = [el for el in elements if el['inputType'] == 'checkbox']
    if checkbox_elements:
        print(f"Examining {len(checkbox_elements)} checkbox elements for conditional fields...")
        
        for i, checkbox in enumerate(checkbox_elements):
            checkbox_id = checkbox.get('id', '')
            if checkbox_id == 'none':
                continue
                
            try:
                # Find the checkbox
                cb_selector = f"#{checkbox_id}"
                cb = page.query_selector(cb_selector)
                if not cb:
                    continue
                    
                cb.scroll_into_view_if_needed()
                
                # Get elements count before toggling
                elements_before = page.evaluate("() => document.querySelectorAll('input, select, textarea').length")
                
                # Screenshot before toggle
                before_path = os.path.join(form_dir, f"{section_name}_checkbox_{i+1}_before.png")
                page.screenshot(path=before_path, full_page=True)
                
                # Toggle the checkbox
                cb.evaluate("cb => cb.click()")
                page.wait_for_timeout(1000)  # Wait for conditional fields to appear
                
                # Screenshot after toggle
                after_path = os.path.join(form_dir, f"{section_name}_checkbox_{i+1}_after.png")
                page.screenshot(path=after_path, full_page=True)
                
                # Get elements count after toggling
                elements_after = page.evaluate("() => document.querySelectorAll('input, select, textarea').length")
                
                # Check if new elements appeared
                if elements_after > elements_before:
                    print(f"✅ Checkbox {checkbox_id} revealed {elements_after - elements_before} new field(s)")
                    
                    # Find and document the new elements
                    new_elements = _extract_form_elements(page)
                    
                    interactive_data.append({
                        "type": "conditional_fields",
                        "trigger": checkbox_id,
                        "revealed_count": elements_after - elements_before,
                        "fields": new_elements
                    })
                
                # Toggle back to original state
                cb.evaluate("cb => cb.click()")
                page.wait_for_timeout(500)
                
            except Exception as e:
                print(f"⚠️ Error with conditional fields for checkbox {checkbox_id}: {e}")
    
    return interactive_data

def main():
    # Create a directory for outputs if it doesn't exist
    output_dir = "form_exploration"
    os.makedirs(output_dir, exist_ok=True)
    os.chdir(output_dir)
    
    # Explore both forms
    print("Starting comprehensive form exploration...")
    
    # Easy form
    explore_form("https://asteroid.ai/form2")
    
    # Hard form
    explore_form("https://asteroid.ai/form")
    
    print("\n✅ Form exploration completed. Results saved in the form_exploration directory.")

if __name__ == "__main__":
    main()