from datetime import datetime
import logging, re
from nova_act import BOOL_SCHEMA


log = logging.getLogger("nova_form_automation")   # one logger for the module


# ─── helpers ──────────────────────────────────────────────────────────────────
def detect_order(nova, label, pattern) -> bool:
    """
    Check if a date field's format matches the specified pattern.
    
    Args:
        nova: NovaAct instance
        label: Label of the date field
        pattern: Date pattern to check (e.g. "dd/mm/yyyy")
        
    Returns:
        bool: True if the field expects the specified pattern, False otherwise
    """
    query = (
        f"Does the date field '{label}' expect the date in {pattern} order? "
        f"Answer true or false."
    )
    
    # Ask Nova-ACT about the pattern
    result = nova.act(query, schema=BOOL_SCHEMA)
    
    # If the result doesn't match the schema, retry once
    if not result.matches_schema:
        result = nova.act(query, schema=BOOL_SCHEMA)
    
    # Return the result or False if still no valid response
    if result.matches_schema and result.parsed_response:
        log.info(f"[{label}] confirmed format: {pattern}")
        return True
    else:
        log.info(f"[{label}] does not use format: {pattern}")
        return False

def convert_date(date_str: str) -> str:
    """
    Convert date from yyyy-mm-dd format to dd/mm/yyyy format.
    
    Args:
        date_str: Date string in yyyy-mm-dd format (e.g., "1975-06-15")
        
    Returns:
        str: Date string in dd/mm/yyyy format (e.g., "15/06/1975")
    """
    # Split by hyphen and rearrange
    year, month, day = date_str.split("-")
    return f"{day}/{month}/{year}"


def format_date_for_easy_form(date_str: str) -> str:
    """
    Format date specifically for the easy form, which expects dd-mm-yyyy format.
    
    Args:
        date_str: Date string in any common format (will handle various formats)
        
    Returns:
        str: Date string in dd-mm-yyyy format as required by the easy form
    """
    log.info(f"Formatting date '{date_str}' for easy form")
    
    # Check if the date is already in dd-mm-yyyy format
    if re.match(r'^\d{1,2}-\d{1,2}-\d{4}$', date_str):
        log.info(f"Date '{date_str}' is already in dd-mm-yyyy format")
        return date_str
    
    # Handle yyyy-mm-dd format
    if re.match(r'^\d{4}-\d{1,2}-\d{1,2}$', date_str):
        year, month, day = date_str.split("-")
        return f"{day}-{month}-{year}"
    
    # Handle dd/mm/yyyy format
    if re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', date_str):
        day, month, year = date_str.split("/")
        return f"{day}-{month}-{year}"
    
    # Handle mm/dd/yyyy format
    if re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', date_str) and "/" in date_str:
        parts = date_str.split("/")
        # This is a heuristic - if first part is >12, assume it's a day
        if int(parts[0]) > 12:
            day, month, year = parts
        else:
            month, day, year = parts
        return f"{day}-{month}-{year}"
    
    # Try to parse with datetime for other formats
    try:
        # Try various formats
        for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y"]:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%d-%m-%Y")
            except ValueError:
                continue
                
        # If we get here, none of the formats worked
        log.warning(f"Could not parse date '{date_str}', returning as is")
        return date_str
        
    except Exception as e:
        log.error(f"Error formatting date '{date_str}': {e}")
        return date_str


def fill_easy_form_date(nova, label, value):
    """
    Specialized function for filling date fields in the easy form.
    
    Args:
        nova: NovaAct instance
        label: Field label to look for
        value: Date value to enter (will be formatted to dd-mm-yyyy)
        
    Returns:
        bool: True if successful
    """
    log.info(f"Filling easy form date field '{label}' with value '{value}'")
    
    try:
        # Format the date for the easy form (dd-mm-yyyy)
        formatted_date = format_date_for_easy_form(value)
        log.info(f"Formatted date for easy form: '{formatted_date}'")
        
        # Use Nova-ACT to fill the field
        query = (
            f"Find the date field labeled '{label}'. "
            f"Clear any existing value and enter '{formatted_date}' (in dd-mm-yyyy format)."
        )
        nova.act(query, max_steps=5)
        
        log.info(f"Successfully filled date field '{label}' with '{formatted_date}'")
        return True
        
    except Exception as e:
        log.exception(f"Error filling date field '{label}': {e}")
        return False


# Goals = " whenever the fill_date_field function is called : \
#     These steps should be followed \
#         1. Detect the format of the date field in the form \
#             a. Loop through the various common date formats  \
#             b. Ask Nova‑ACT which token order the field expects (separator‑agnostic). (eg dd/mm/yyyy) \
#         2. Parse the value to be filled that we have got from the json file\
#         3. Check if the current format of the value to be filled matches with the expected format\
#         4. If not, convert the value to the expected format\
#         5. Fill the field with the converted value using nova-act"