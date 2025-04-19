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



# Goals = " whenever the fill_date_field function is called : \
#     These steps should be followed \
#         1. Detect the format of the date field in the form \
#             a. Loop through the various common date formats  \
#             b. Ask Nova‑ACT which token order the field expects (separator‑agnostic). (eg dd/mm/yyyy) \
#         2. Parse the value to be filled that we have got from the json file\
#         3. Check if the current format of the value to be filled matches with the expected format\
#         4. If not, convert the value to the expected format\
#         5. Fill the field with the converted value using nova-act"
        