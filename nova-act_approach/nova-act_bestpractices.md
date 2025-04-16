# Nova-ACT Best Practices

Based on the official Nova-ACT GitHub examples and our experiences with form automation, here are best practices for using Nova-ACT effectively.

## Command Structure Patterns

### Pattern 1: Sequential Operations in a Single Command
When operations are closely related and don't require waiting for UI changes:

```python
nova.act(
    "Find the dropdown field labeled 'Title', clear it, and type 'Prof'. "
    "Then click somewhere else on the page to move focus away."
)
```

**Best for:**
- Related actions that don't need to wait for page updates
- Complete workflows that can be described in natural language
- Minimizing network round-trips and improving performance

**Example from official repo:**
```python
nova.act(
    "If there is a cookie banner, close it. "
    "Click Menu at the top of the page. "
    "Click Delivery on the sidebar. "
    "Select 'Home' address. "
    f"Scroll down and click on '{order}'. "
    "Click 'Add to Bag'. "
)
```

### Pattern 2: Separate Commands for Page Transitions
When operations trigger page navigation or UI state changes:

```python
nova.act("search for a coffee maker")
nova.act("select the first result")
nova.act("scroll down or up until you see 'add to cart' and then click 'add to cart'")
```

**Best for:**
- Actions that cause page loads or significant UI changes
- When you need to wait for a page to load before continuing
- When sending separate, distinct instructions

## Performance Optimization

### Consolidate Related Actions
Combine multiple related actions into a single command when they don't require UI updates between steps:

```python
# INEFFICIENT: Multiple round-trips
nova.act("Find the field labeled 'First Name'")
nova.act("Clear it")
nova.act("Type 'John'")

# EFFICIENT: Single round-trip
nova.act("Find the field labeled 'First Name', clear it, and type 'John'")
```

### Strategic Waiting
Use explicit waits only when necessary:

```python
# For page transitions
nova.act("Click the 'Next' button")
time.sleep(2)  # Wait for page transition

# For related actions, no wait needed between steps
nova.act("Find the dropdown labeled 'Title', clear it, and type 'Prof'")
```

## Error Handling

### Robust Recovery
Include fallback methods when critical operations might fail:

```python
try:
    # Primary approach
    nova.act("Find the date field and enter '15/06/1985'")
except Exception:
    # Fallback approach
    nova.act("Find the date picker icon and click it")
    nova.act("Select June 15, 1985 from the calendar")
```

### Clear Instructions

Provide clear, direct instructions in natural language:

```python
# VAGUE: May lead to incorrect action
nova.act("Fill the form")

# CLEAR: Specific and actionable
nova.act("Find the form section labeled 'Contact Details'. "
         "In this section, find the 'Email' field and type 'user@example.com'")
```

## Lessons from Our Implementation

1. **Too Many Separate Acts Are Slow**
   - Each `nova.act()` call involves a network round-trip and agent thinking
   - Our implementation with 4-5 separate calls for a single field was too slow
   - Consolidating to 1-2 calls per field significantly improves performance

2. **Verification Causes Duplication**
   - The agent often repeats actions when asked to verify
   - Instead of separate verification, include success criteria in the main command

3. **Format Compatibility Issues**
   - Date formats need explicit handling (YYYY-MM-DD vs DD/MM/YYYY)
   - For critical format-sensitive fields, include explicit format instructions

4. **Tab Key Problems**
   - The Tab key can cause field values to be reset in some forms
   - Use clicks outside the field instead to move focus

## Recommended Implementation Approach

Based on these learnings, an optimized approach for form automation would be:

```python
def select_dropdown_option(nova, label, value):
    """Optimized dropdown selection."""
    # Single command approach
    nova.act(f"Find the dropdown field labeled '{label}', clear it, and type '{value}'. "
             f"Then click somewhere else on the page to confirm.")
    return True

def fill_date_field(nova, label, value):
    """Optimized date field filling."""
    # Convert format (YYYY-MM-DD to DD/MM/YYYY)
    year, month, day = value.split('-')
    formatted_date = f"{day}/{month}/{year}"
    
    # Single command approach with format specifics
    nova.act(f"Find the date field labeled '{label}', clear it, and type '{formatted_date}' "
             f"(day/month/year format). Then click somewhere else to confirm.")
    return True
```

This approach balances conciseness, clarity, and performance while maintaining reliability for form automation.