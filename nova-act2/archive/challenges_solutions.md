# Nova-ACT Field Detection Challenges & Solutions

## Challenges

### 1. BOOL_SCHEMA Viewport Limitation

**Problem Identified:** When using `BOOL_SCHEMA` with `nova.act()`, the agent appears to only evaluate the current viewport and doesn't automatically scroll to find fields that might be outside the visible area. This results in false negatives for field detection, especially for fields that require scrolling to become visible.

**Evidence:** Multiple query formulations were tried:
- `"Are you able to Search for {label} field in {current_tab} section?"`
- `"Look at the {current_tab} section of the form carefully. Is there a field labeled '{label}'?"`

All returned `false` even for fields that should exist, suggesting the agent isn't properly exploring the form.

## Potential Solutions

### 1. Multi-Step Field Detection

Instead of a single boolean query, implement a two-step process:
1. First command: Explicitly instruct the agent to scroll through the entire form section
2. Second command: Then ask if the field exists

### 2. Visual Inventory Approach

Have the agent create an inventory of all visible form elements first, then check if the target field is in that inventory:
```python
# Step 1: Get a list of all form fields
fields_inventory = nova.act("List all form fields visible in the Contact Details section, including any you need to scroll to see.")

# Step 2: Check if our target field appears in the inventory
field_exists = label.lower() in fields_inventory.lower()
```

### 3. Action-Based Detection

Try using actions instead of boolean queries:
```python
try:
    # Try to interact with the field directly
    nova.act(f"Click on the field labeled '{label}'")
    return True  # If no exception, field exists
except Exception:
    return False  # Field likely doesn't exist
```

### 4. Explicit Scroll Commands

Add explicit scroll commands before checking for fields:
```python
# Scroll through the form first
nova.act("Scroll down to see all fields in the Contact Details section")
# Then check for the field
result = nova.act(f"Is there a field labeled '{label}'?", schema=BOOL_SCHEMA)
```

### 5. Handling Composite Fields in JSON Data

**Problem:** The form data JSON contains nested objects (composite fields) such as addresses:

```json
"address": {
  "addressLine1": "42 Nebula Gardens",
  "addressLine2": "Cosmic Quarter",
  "addressLine3": "Starlight District",
  "city": "Newcastle",
  "postcode": "NE1 4XD"
}
```

But our form field mapping is designed for flat key-value pairs.

**Potential Solutions:**

1. **Generic Composite Field Handling:**
   ```python
   # In config.py
   "address": "composite", # Special type for nested objects
   
   # In handler logic
   if field_type == "composite" and isinstance(value, dict):
       for sub_key, sub_value in value.items():
           # Process each sub-field
   ```

2. **Structured Configuration:**
   ```python
   # In config.py
   "address": {
       "type": "composite",
       "fields": ["addressLine1", "addressLine2", "addressLine3", "city", "postcode"]
   }
   ```

3. **Pragmatic Field-Specific Handling (Selected Approach):** 
   Directly handle the known composite fields without overengineering:

   ```python
   # In business_info_handler.py
   if "address" in business_data:
       address_data = business_data["address"]
       
       # Process each address field individually
       if "addressLine1" in address_data:
           fill_text_field(nova, "Address Line 1", address_data["addressLine1"])
       
       if "addressLine2" in address_data:
           fill_text_field(nova, "Address Line 2", address_data["addressLine2"])
       
       # And so on for each subfield
   ```

**Rationale for Selected Approach:**
- Only two fields in the entire form data are composite (addresses in business and premises sections)
- Direct handling is more explicit and easier to understand
- Follows the incremental implementation principle of solving immediate needs
- Avoids complex data structures that might introduce bugs

## Next Steps

- Test the various solutions to determine which provides the most reliable field detection
- Consider combining approaches for maximum reliability
- Document successful patterns for future reference
