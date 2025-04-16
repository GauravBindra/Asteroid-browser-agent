# Nova-ACT Best Practices

Based on the official Nova-ACT GitHub README, examples, and our experiences with form automation, here are comprehensive best practices for using Nova-ACT effectively.

## Official Prompting Guidelines

### 1. Be Prescriptive and Succinct

❌ DON'T use vague, high-level descriptions:
```python
nova.act("Let's see what routes VTA offers")
nova.act("I want to go and meet a friend. I should figure out when the Orange Line comes next.")
```

✅ DO use clear, actionable instructions:
```python
nova.act("Navigate to the routes tab")
nova.act(f"Find the next departure time for the Orange Line from Government Center after {time}")
```

### 2. Break Large Tasks into Smaller Steps

❌ DON'T try to accomplish too much in one command:
```python
nova.act("book me a hotel that costs less than $100 with the highest star rating")
```

✅ DO break the process into sequential steps:
```python
nova.act(f"search for hotels in Houston between {startdate} and {enddate}")
nova.act("sort by avg customer review")
nova.act("hit book on the first hotel that is $100 or less")
nova.act(f"fill in my name, address, and DOB according to {blob}")
```

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

### Special Handling Techniques

#### 1. Form Submission & Search
For search operations or form submissions, explicitly tell the agent to press Enter:
```python
nova.act("search for cats. type enter to initiate the search.")
```

#### 2. Date Selection
Always use absolute dates rather than relative ones:
```python
# Good
nova.act("select dates march 23 to march 28")

# Avoid
nova.act("select dates for next weekend")
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

### Conditional Verification
Check for completion or specific states using schemas:

```python
from nova_act import BOOL_SCHEMA

result = nova.act("Is there a captcha on the screen?", schema=BOOL_SCHEMA)
if result.matches_schema and result.parsed_response:
    input("Please solve the captcha and hit return when done")
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

5. **Navigation Complexity**
   - Multi-section forms require clear navigation instructions
   - Use conditional checks: "Check if you can see X, if not then scroll to find it"
   - For navigation between tabs/sections, be very specific about location

6. **Empty Section Detection**
   - The agent may not realize it successfully navigated if content is empty
   - Include expectations about what might be visible after navigation
   - Handle cases where UI might be in a loading state

## Known Limitations from Official Documentation

1. Nova-ACT is unreliable with high-level prompts
2. Cannot interact with elements hidden behind mouseover/hover states
3. Cannot interact with browser window itself (browser modals)
4. Will not solve CAPTCHAs (requires user intervention)

## Recommended Implementation Approach

Based on these learnings, an optimized approach for form automation would be:

```python
def select_dropdown_option(nova, label, value):
    """Optimized dropdown selection."""
    # Single command approach with clear, specific instructions
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

def navigate_to_tab(nova, tab_name):
    """Optimized tab navigation."""
    # Use conditional instructions
    nova.act(f"Check if you can see the tab labeled '{tab_name}' at the top of the form. "
             f"If not, scroll to the top of the page first. Then click on the tab labeled '{tab_name}'. "
             f"Wait for the section to load completely.")
    return True
```

This approach balances conciseness, clarity, and performance while maintaining reliability for form automation.