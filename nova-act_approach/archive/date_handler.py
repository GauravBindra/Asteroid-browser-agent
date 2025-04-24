from datetime import datetime
import logging, re
from nova_act import BOOL_SCHEMA

# ─── constants ────────────────────────────────────────────────────────────────
ORDER_PATTERNS = {                      # token order → strftime pieces
    "DMY": ("%d", "%m", "%Y"),
    "MDY": ("%m", "%d", "%Y"),
    "YMD": ("%Y", "%m", "%d"),          # ISO fallback
}

KNOWN_JSON_FORMATS = [                  # accept any of these in input data
    "%d/%m/%Y", "%d-%m-%Y",
    "%m/%d/%Y", "%m-%d-%Y",
    "%Y/%m/%d", "%Y-%m-%d",
]

log = logging.getLogger("nova_form_automation")   # one logger for the module


# ─── helpers ──────────────────────────────────────────────────────────────────
def _detect_order(nova, label) -> tuple[str, str, str] | None:
    """Ask Nova‑ACT which token order the field expects (separator‑agnostic)."""
    for code, pattern in ORDER_PATTERNS.items():
        q = (
            f"Does the date field labeled '{label}' expect the date in {code} order "
            f"(day–month–year, etc.)? Answer true or false."
        )
        r = nova.act(q, schema=BOOL_SCHEMA)
        if r.matches_schema and r.parsed_response:
            log.info(f"[{label}] detected order → {code}")
            return pattern
    log.warning(f"[{label}] could not detect date order")
    return None


def _parse_json_date(raw: str) -> datetime | None:
    """Parse a date string from JSON into a datetime object."""
    cleaned = re.sub(r"[^\d]", "/", raw)        # normalise separators
    for fmt in KNOWN_JSON_FORMATS:
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            pass
    log.error(f"[date‑parse] '{raw}' not recognised as a date")
    return None


# ─── main API ────────────────────────────────────────────────────────────────
def fill_date_field(nova, label: str, raw_value: str) -> bool:
    """
    Fill a date field with proper formatting.
    
    This function:
    • Detects the field's expected date format (DMY, MDY, YMD)
    • Parses the input date from any common JSON format  
    • Converts the date to the expected format
    • Enters only the digits in the proper order
    • Verifies via JS that the entered digits match expected digits
    
    Args:
        nova: NovaAct instance
        label: Field label to look for
        raw_value: Raw date value to enter (e.g. "1975-06-15")
        
    Returns:
        bool: True if successful, False otherwise
    """
    log.info(f"→ Filling date field '{label}' with value '{raw_value}'")

    # Step 1: Detect the field's expected date order (DMY, MDY, YMD)
    order = _detect_order(nova, label)
    if order is None:
        log.error(f"[{label}] Could not detect date format, aborting")
        return False

    # Step 2: Parse the input date value
    dt = _parse_json_date(raw_value)
    if dt is None:
        log.error(f"[{label}] Failed to parse date value '{raw_value}', aborting")
        return False

    # Step 3: Format date components based on detected order
    tokens = {"%Y": dt.strftime("%Y"), "%m": dt.strftime("%m"), "%d": dt.strftime("%d")}
    digits_only = "".join(tokens[p] for p in order)

    # Step 4: Fill the field and verify
    try:
        # Click field, clear it, and enter the formatted date
        nova.act(
            f"Find the field labeled '{label}', click in it, press Ctrl+A then Backspace to clear it, "
            f"type '{digits_only}', and click somewhere else on the page to confirm."
        )
        
        # Verify the input was accepted correctly using JavaScript
        ok = nova.act(
            "return document.querySelector("
            f"\"input[aria-label='{label}']\""
            ").value.replace(/\\D/g, '') === '" + digits_only + "'",
            schema=BOOL_SCHEMA,
        )
        
        # Check verification result
        success = ok.matches_schema and ok.parsed_response
        if success:
            log.info(f"[{label}] ✅ Successfully filled date field")
        else:
            log.error(f"[{label}] ❌ Date verification failed")
        
        return success

    except Exception as e:
        log.exception(f"[{label}] Error filling date field: {e}")
        return False