2025-04-16 14:57:29,965 - INFO - Starting hard form navigation test
2025-04-16 14:57:29,965 - INFO - Initializing Nova-ACT for hard form at https://asteroid.ai/form

start session 5623a7b3-483e-4a00-90cc-a2e26a56c835 on https://asteroid.ai/form

2025-04-16 14:57:45,871 - INFO - Browser started successfully
2025-04-16 14:57:45,872 - INFO - Waiting for the form to load
2025-04-16 14:57:49,876 - INFO - Testing navigation to 'Contact Details' tab
2025-04-16 14:57:49,876 - INFO - Navigating to tab: 'Contact Details'
5623> act("Check if you are already at the top of the page and can see the all the form sections/tabs. If you cant see the sections/tabs then Scroll to the top of the page to see all the form sections/tabs. then find and click on the tab or section labeled 'Contact Details'. Wait for the section to fully load.")
.............
5623> think("I am on the Commercial Property Insurance Application page. I see the 'Contact Details' tab is already selected but I am not at the top of the page. I need to scroll up to the top of the page.");
>> agentScroll("up", "<box>0,0,1008,1790</box>");
...................
5623> think("The page has not changed, I am still on the 'Contact Details' section. I am already at the top of the page, as the 'Contact Details' tab is visible and the page has not changed after the last scroll. The task to find and click on the 'Contact Details' tab is complete, and I need to wait for the page to load.");
>> wait(0.0);
.................
5623> think("The page has not changed, I am still on the 'Contact Details' section. The page is already loaded, the task to wait for the page to load is complete.");
>> return;
.....
5623> ** View your act run here: /var/folders/3f/x95cmnkn57s5pfth5lygr5k00000gn/T/tmpt7k_2063_nova_act_logs/5623a7b3-483e-4a00-90cc-a2e26a56c835/act_52d55149-8474-4b08-9d94-626a21879133_output.html

2025-04-16 14:58:19,729 - INFO - Successfully navigated to 'Contact Details' tab
2025-04-16 14:58:19,730 - INFO - Navigation to 'Contact Details' tab PASSED
2025-04-16 14:58:21,727 - INFO - Testing navigation to 'Business Info' tab
2025-04-16 14:58:21,728 - INFO - Navigating to tab: 'Business Info'
5623> act("Check if you are already at the top of the page and can see the all the form sections/tabs. If you cant see the sections/tabs then Scroll to the top of the page to see all the form sections/tabs. then find and click on the tab or section labeled 'Business Info'. Wait for the section to fully load.")
...............
5623> think("I am currently on the 'Contact Details' section of the Commercial Property Insurance Application. My task is to check if I am already at the top of the page and can see all the form sections/tabs. If I can't see the sections/tabs, I need to scroll to the top of the page to see all the form sections/tabs. Then, I need to find and click on the tab or section labeled 'Business Info' and wait for the section to fully load. I can see the 'Business Info' tab at the top of the page, but it has not been selected yet as it is not underlined. I should scroll up to see if there are any other sections or tabs above the 'Contact Details' section.");
>> agentScroll("up", "<box>0,0,1008,1796</box>");
...................
5623> think("The page has not changed, so my last action was incorrect. I am already at the top of the page, as indicated by the scroll bar being at the top of the page. I can see the 'Business Info' tab, but it is not selected. I need to click on the 'Business Info' tab to select it.");
>> agentClick("<box>140,644,162,742</box>");
..................
5623> think("The 'Business Info' tab is now selected, as indicated by the tab being underlined. Therefore, my last action was successful. The 'Business Info' tab is now selected, and the page is fully loaded. My task is complete, and I need to return.");
>> return;
......
5623> ** View your act run here: /var/folders/3f/x95cmnkn57s5pfth5lygr5k00000gn/T/tmpt7k_2063_nova_act_logs/5623a7b3-483e-4a00-90cc-a2e26a56c835/act_519a0e43-f5bf-4960-8ab4-60b730a6033f_output.html

2025-04-16 14:58:53,539 - INFO - Successfully navigated to 'Business Info' tab
2025-04-16 14:58:53,539 - INFO - Navigation to 'Business Info' tab PASSED
2025-04-16 14:58:55,543 - INFO - Testing navigation to 'Premises Details' tab
2025-04-16 14:58:55,543 - INFO - Navigating to tab: 'Premises Details'
5623> act("Check if you are already at the top of the page and can see the all the form sections/tabs. If you cant see the sections/tabs then Scroll to the top of the page to see all the form sections/tabs. then find and click on the tab or section labeled 'Premises Details'. Wait for the section to fully load.")
............
5623> think("I am on the Commercial Property Insurance Application page. I can see all the form sections/tabs. I need to click on the tab labeled 'Premises Details'. I need to click Premises Details tab");
>> agentClick("<box>130,792,166,976</box>");
..................
5623> think("I am now on the 'Premises Details' section. The task is complete, and I need to return.");
>> return;
......
5623> ** View your act run here: /var/folders/3f/x95cmnkn57s5pfth5lygr5k00000gn/T/tmpt7k_2063_nova_act_logs/5623a7b3-483e-4a00-90cc-a2e26a56c835/act_4d29b9be-786b-47c2-ab79-7c6a5b6c00e6_output.html

2025-04-16 14:59:15,428 - INFO - Successfully navigated to 'Premises Details' tab
2025-04-16 14:59:15,428 - INFO - Navigation to 'Premises Details' tab PASSED
2025-04-16 14:59:17,433 - INFO - Testing navigation to 'Security & Safety' tab
2025-04-16 14:59:17,433 - INFO - Navigating to tab: 'Security & Safety'
5623> act("Check if you are already at the top of the page and can see the all the form sections/tabs. If you cant see the sections/tabs then Scroll to the top of the page to see all the form sections/tabs. then find and click on the tab or section labeled 'Security & Safety'. Wait for the section to fully load.")
............
5623> think("I am on the Commercial Property Insurance Application page. I do not see the form sections/tabs. I need to scroll down to see if the form sections/tabs are visible.");
>> agentScroll("up", "<box>0,0,1008,1796</box>");
..................
5623> think("The page has not changed, so my last action was incorrect. I am already at the top of the page, as indicated by the scroll bar being at the top of its range. I can see the tab labeled 'Security & Safety', but it is not selected. I should click on the 'Security & Safety' tab to select it.");
>> agentClick("<box>136,994,166,1174</box>");
..................
5623> think("The 'Security & Safety' tab is now selected, as indicated by the change in the color of the tab. Therefore, my last action was successful. The section has not fully loaded, as indicated by the empty fields and the 'Next' button being grayed out. I should wait for the section to fully load.");
>> wait(0.0);
................
5623> think("The page has not changed, so my last action was incorrect. The section has loaded fully, as indicated by the 'Next' button being clickable. My task is complete, and I need to return.");
>> return;
......
5623> ** View your act run here: /var/folders/3f/x95cmnkn57s5pfth5lygr5k00000gn/T/tmpt7k_2063_nova_act_logs/5623a7b3-483e-4a00-90cc-a2e26a56c835/act_43c29b26-71b7-490e-be46-eec9ed893f52_output.html

2025-04-16 14:59:55,429 - INFO - Successfully navigated to 'Security & Safety' tab
2025-04-16 14:59:55,430 - INFO - Navigation to 'Security & Safety' tab PASSED
2025-04-16 14:59:57,434 - INFO - Testing navigation to 'Coverage Options' tab
2025-04-16 14:59:57,434 - INFO - Navigating to tab: 'Coverage Options'
5623> act("Check if you are already at the top of the page and can see the all the form sections/tabs. If you cant see the sections/tabs then Scroll to the top of the page to see all the form sections/tabs. then find and click on the tab or section labeled 'Coverage Options'. Wait for the section to fully load.")
...............
5623> think("I am currently on the 'Security Details' section of the Commercial Property Insurance Application. My task is to check if I am already at the top of the page and can see all the form sections/tabs. If I can't see the sections/tabs, I need to scroll to the top of the page to see all the form sections/tabs. Then, I need to find and click on the tab or section labeled 'Coverage Options' and wait for the section to fully load. I can see the 'Contact Details', 'Business Info', 'Premises Details', 'Security & Safety', and 'Coverage Options' tabs at the top of the page, so I am already at the top of the page. The 'Coverage Options' tab is visible, but it has not been selected yet as it is not underlined. I should click on the 'Coverage Options' tab to select it and view the corresponding section.");
>> agentClick("<box>130,1166,166,1368</box>");
.................
5623> think("The 'Coverage Options' tab is now underlined, so my last action was a success. The 'Coverage Options' tab is selected, but the section is not visible yet. I need to wait for the section to fully load. I will wait for the 'Coverage Options' section to load.");
>> wait(0.0);
.................
5623> think("I see that the page has not changed, so my last action was incorrect. I see that the 'Coverage Options' tab is still selected, but I do not see the section. I need to scroll down to see the 'Coverage Options' section. I should scroll down to see the 'Coverage Options' section.");
>> agentScroll("down", "<box>0,0,1008,1790</box>");
...................
5623> think("I see that the page has scrolled down, so my last action was successful. I see that the footer is now visible, but I do not see the 'Coverage Options' section. I need to scroll up to see the 'Coverage Options' section. I should scroll up to see the 'Coverage Options' section.");
>> agentScroll("up", "<box>0,0,1008,1790</box>");
..................
5623> think("I see that the page has scrolled up, so my last action was successful. I see that the 'Coverage Options' tab is now visible, but I do not see the section. I need to scroll up to see the 'Coverage Options' section. I should scroll up to see the 'Coverage Options' section.");
>> agentScroll("up", "<box>0,0,1008,1790</box>");
..................
5623> think("I see that the page has not changed, so my last action was not successful. I see that the 'Coverage Options' tab is now visible, but I do not see the section. I need to click on the 'Coverage Options' tab to see the section. I should click on the 'Coverage Options' tab to see the section.");
>> agentClick("<box>136,1174,166,1368</box>");
..................
5623> think("I see that the page has not changed, so my last action was not successful. I see that the 'Coverage Options' tab is now selected, but I do not see the section. I need to scroll down to see the 'Coverage Options' section. I should scroll down to see the 'Coverage Options' section.");
>> agentScroll("down", "<box>0,0,1008,1796</box>");
..................
5623> think("I see that the page has scrolled down, so my last action was successful. I see that the 'Coverage Options' section is not visible, but I need to wait for the page to load. I should wait for the page to load.");
>> wait(0.0);
.................
5623> think("I see that the page has not changed, so my last action was successful. I see that the 'Coverage Options' section is not visible, and I am at the bottom of the page. I need to scroll up to see the 'Coverage Options' section. I should scroll up to see the 'Coverage Options' section.");
>> agentScroll("up", "<box>0,0,1008,1790</box>");
....................
5623> think("I see that the page has scrolled up, so my last action was successful. I see that the 'Coverage Options' section is now visible, but it is not selected. I need to click on the 'Coverage Options' tab to select it. I should click on the 'Coverage Options' tab to select it.");
>> agentClick("<box>136,1174,162,1368</box>");
..................
5623> think("I see that the 'Coverage Options' tab is now selected, so my last action was successful. I see that the page has not changed, so I need to wait for the page to load.");
>> wait(0.0);
.................
5623> think("I see that the page has not changed, so my last action was successful. I see that the page is still loading, so I need to wait for the page to load.");
>> wait(0.0);
......2025-04-16 15:01:50,471 - ERROR - Error navigating to 'Coverage Options' tab: 

ActError(
    message = An error occurred during act()
    metadata = ActMetadata(
        session_id = 5623a7b3-483e-4a00-90cc-a2e26a56c835
        act_id = 95022148-4ff9-4b7f-b219-556d16620f2e
        num_steps_executed = 12
        start_time = 2025-04-16 14:59:57.435541 EDT
        end_time = None
        prompt = 'Check if you are already at the top of the page and can see the all the form sections/tabs. If you cant see the sections/tabs then Scroll to the top of the page to see all the form sections/tabs. then find and click on the tab or section labeled 'Coverage Options'. Wait for the section to fully load.'
    )
)

Please consider providing feedback: https://amazonexteu.qualtrics.com/jfe/form/SV_bd8dHa7Em6kNkMe
Traceback (most recent call last):
  File "/Users/gauravbindra/Desktop/Asteroid/asteroid_env/lib/python3.13/site-packages/nova_act/nova_act.py", line 414, in act
    response = self.dispatcher.dispatch_and_wait_for_prompt_completion(act)
  File "/Users/gauravbindra/Desktop/Asteroid/asteroid_env/lib/python3.13/site-packages/nova_act/impl/extension.py", line 253, in dispatch_and_wait_for_prompt_completion
    self._poll_playwright(DEFAULT_POLL_SLEEP_S)
    ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/gauravbindra/Desktop/Asteroid/asteroid_env/lib/python3.13/site-packages/nova_act/impl/extension.py", line 93, in _poll_playwright
    self._playwright_manager.main_page.evaluate("() => {}")
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/gauravbindra/Desktop/Asteroid/asteroid_env/lib/python3.13/site-packages/nova_act/impl/playwright.py", line 290, in main_page
    return self.get_page(-1)
           ~~~~~~~~~~~~~^^^^
  File "/Users/gauravbindra/Desktop/Asteroid/asteroid_env/lib/python3.13/site-packages/nova_act/impl/playwright.py", line 298, in get_page
    return self._active_page
           ^^^^^^^^^^^^^^^^^
  File "/Users/gauravbindra/Desktop/Asteroid/asteroid_env/lib/python3.13/site-packages/nova_act/impl/playwright.py", line 284, in _active_page
    assert self._context is not None and len(self._context.pages) > 0
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/Users/gauravbindra/Desktop/Asteroid/nova-act_approach/hard_form_automation4.py", line 147, in navigate_to_tab
    nova.act(command)
    ~~~~~~~~^^^^^^^^^
  File "/Users/gauravbindra/Desktop/Asteroid/asteroid_env/lib/python3.13/site-packages/nova_act/nova_act.py", line 420, in act
    raise ActError(metadata=act.metadata) from e
nova_act.types.act_errors.ActError: 

ActError(
    message = An error occurred during act()
    metadata = ActMetadata(
        session_id = 5623a7b3-483e-4a00-90cc-a2e26a56c835
        act_id = 95022148-4ff9-4b7f-b219-556d16620f2e
        num_steps_executed = 12
        start_time = 2025-04-16 14:59:57.435541 EDT
        end_time = None
        prompt = 'Check if you are already at the top of the page and can see the all the form sections/tabs. If you cant see the sections/tabs then Scroll to the top of the page to see all the form sections/tabs. then find and click on the tab or section labeled 'Coverage Options'. Wait for the section to fully load.'
    )
)

Please consider providing feedback: https://amazonexteu.qualtrics.com/jfe/form/SV_bd8dHa7Em6kNkMe
2025-04-16 15:01:50,482 - INFO - Trying fallback approach for navigating to 'Coverage Options'
5623> act("Look for any navigation menu, tabs, or breadcrumbs at the top of the form. Find the option that says 'Coverage Options' and click on it. If you don't see it immediately, try scrolling to the top of the page first.")
2025-04-16 15:01:50,484 - ERROR - Fallback navigation also failed: 

ActError(
    message = An error occurred during act()
    metadata = ActMetadata(
        session_id = 5623a7b3-483e-4a00-90cc-a2e26a56c835
        act_id = 72c6922f-2153-4371-9eca-f38aa11868cc
        num_steps_executed = 0
        start_time = 2025-04-16 15:01:50.483320 EDT
        end_time = None
        prompt = 'Look for any navigation menu, tabs, or breadcrumbs at the top of the form. Find the option that says 'Coverage Options' and click on it. If you don't see it immediately, try scrolling to the top of the page first.'
    )
)

Please consider providing feedback: https://amazonexteu.qualtrics.com/jfe/form/SV_bd8dHa7Em6kNkMe
Traceback (most recent call last):
  File "/Users/gauravbindra/Desktop/Asteroid/asteroid_env/lib/python3.13/site-packages/nova_act/nova_act.py", line 414, in act
    response = self.dispatcher.dispatch_and_wait_for_prompt_completion(act)
  File "/Users/gauravbindra/Desktop/Asteroid/asteroid_env/lib/python3.13/site-packages/nova_act/impl/extension.py", line 253, in dispatch_and_wait_for_prompt_completion
    self._poll_playwright(DEFAULT_POLL_SLEEP_S)
    ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/gauravbindra/Desktop/Asteroid/asteroid_env/lib/python3.13/site-packages/nova_act/impl/extension.py", line 93, in _poll_playwright
    self._playwright_manager.main_page.evaluate("() => {}")
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/gauravbindra/Desktop/Asteroid/asteroid_env/lib/python3.13/site-packages/nova_act/impl/playwright.py", line 290, in main_page
    return self.get_page(-1)
           ~~~~~~~~~~~~~^^^^
  File "/Users/gauravbindra/Desktop/Asteroid/asteroid_env/lib/python3.13/site-packages/nova_act/impl/playwright.py", line 298, in get_page
    return self._active_page
           ^^^^^^^^^^^^^^^^^
  File "/Users/gauravbindra/Desktop/Asteroid/asteroid_env/lib/python3.13/site-packages/nova_act/impl/playwright.py", line 284, in _active_page
    assert self._context is not None and len(self._context.pages) > 0
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/Users/gauravbindra/Desktop/Asteroid/nova-act_approach/hard_form_automation4.py", line 147, in navigate_to_tab
    nova.act(command)
    ~~~~~~~~^^^^^^^^^
  File "/Users/gauravbindra/Desktop/Asteroid/asteroid_env/lib/python3.13/site-packages/nova_act/nova_act.py", line 420, in act
    raise ActError(metadata=act.metadata) from e
nova_act.types.act_errors.ActError: 

ActError(
    message = An error occurred during act()
    metadata = ActMetadata(
        session_id = 5623a7b3-483e-4a00-90cc-a2e26a56c835
        act_id = 95022148-4ff9-4b7f-b219-556d16620f2e
        num_steps_executed = 12
        start_time = 2025-04-16 14:59:57.435541 EDT
        end_time = None
        prompt = 'Check if you are already at the top of the page and can see the all the form sections/tabs. If you cant see the sections/tabs then Scroll to the top of the page to see all the form sections/tabs. then find and click on the tab or section labeled 'Coverage Options'. Wait for the section to fully load.'
    )
)

Please consider providing feedback: https://amazonexteu.qualtrics.com/jfe/form/SV_bd8dHa7Em6kNkMe

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/Users/gauravbindra/Desktop/Asteroid/asteroid_env/lib/python3.13/site-packages/nova_act/nova_act.py", line 414, in act
    response = self.dispatcher.dispatch_and_wait_for_prompt_completion(act)
  File "/Users/gauravbindra/Desktop/Asteroid/asteroid_env/lib/python3.13/site-packages/nova_act/impl/extension.py", line 236, in dispatch_and_wait_for_prompt_completion
    retry_call(
    ~~~~~~~~~~^
        self._dispatch_prompt_and_wait_for_ack,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<3 lines>...
        tries=DEFAULT_RETRY_TRIES if self._retry else 1,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/Users/gauravbindra/Desktop/Asteroid/asteroid_env/lib/python3.13/site-packages/retry/api.py", line 101, in retry_call
    return __retry_internal(partial(f, *args, **kwargs), exceptions, tries, delay, max_delay, backoff, jitter, logger)
  File "/Users/gauravbindra/Desktop/Asteroid/asteroid_env/lib/python3.13/site-packages/retry/api.py", line 33, in __retry_internal
    return f()
  File "/Users/gauravbindra/Desktop/Asteroid/asteroid_env/lib/python3.13/site-packages/nova_act/impl/extension.py", line 197, in _dispatch_prompt_and_wait_for_ack
    self._playwright_manager.main_page.evaluate(POST_MESSAGE_EXPRESSION, encrypted_message)
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/gauravbindra/Desktop/Asteroid/asteroid_env/lib/python3.13/site-packages/nova_act/impl/playwright.py", line 290, in main_page
    return self.get_page(-1)
           ~~~~~~~~~~~~~^^^^
  File "/Users/gauravbindra/Desktop/Asteroid/asteroid_env/lib/python3.13/site-packages/nova_act/impl/playwright.py", line 298, in get_page
    return self._active_page
           ^^^^^^^^^^^^^^^^^
  File "/Users/gauravbindra/Desktop/Asteroid/asteroid_env/lib/python3.13/site-packages/nova_act/impl/playwright.py", line 284, in _active_page
    assert self._context is not None and len(self._context.pages) > 0
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/Users/gauravbindra/Desktop/Asteroid/nova-act_approach/hard_form_automation4.py", line 168, in navigate_to_tab
    nova.act(fallback_command)
    ~~~~~~~~^^^^^^^^^^^^^^^^^^
  File "/Users/gauravbindra/Desktop/Asteroid/asteroid_env/lib/python3.13/site-packages/nova_act/nova_act.py", line 420, in act
    raise ActError(metadata=act.metadata) from e
nova_act.types.act_errors.ActError: 

ActError(
    message = An error occurred during act()
    metadata = ActMetadata(
        session_id = 5623a7b3-483e-4a00-90cc-a2e26a56c835
        act_id = 72c6922f-2153-4371-9eca-f38aa11868cc
        num_steps_executed = 0
        start_time = 2025-04-16 15:01:50.483320 EDT
        end_time = None
        prompt = 'Look for any navigation menu, tabs, or breadcrumbs at the top of the form. Find the option that says 'Coverage Options' and click on it. If you don't see it immediately, try scrolling to the top of the page first.'
    )
)

Please consider providing feedback: https://amazonexteu.qualtrics.com/jfe/form/SV_bd8dHa7Em6kNkMe
2025-04-16 15:01:50,487 - ERROR - Navigation to 'Coverage Options' tab FAILED
2025-04-16 15:01:50,488 - ERROR - Error during navigation tests: 
Traceback (most recent call last):
  File "/Users/gauravbindra/Desktop/Asteroid/asteroid_env/lib/python3.13/site-packages/nova_act/nova_act.py", line 332, in _stop
    self._dispatcher.cancel_prompt()
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "/Users/gauravbindra/Desktop/Asteroid/asteroid_env/lib/python3.13/site-packages/nova_act/impl/extension.py", line 110, in cancel_prompt
    self._playwright_manager.main_page.evaluate(POST_MESSAGE_EXPRESSION, encrypted_message)
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/gauravbindra/Desktop/Asteroid/asteroid_env/lib/python3.13/site-packages/nova_act/impl/playwright.py", line 290, in main_page
    return self.get_page(-1)
           ~~~~~~~~~~~~~^^^^
  File "/Users/gauravbindra/Desktop/Asteroid/asteroid_env/lib/python3.13/site-packages/nova_act/impl/playwright.py", line 298, in get_page
    return self._active_page
           ^^^^^^^^^^^^^^^^^
  File "/Users/gauravbindra/Desktop/Asteroid/asteroid_env/lib/python3.13/site-packages/nova_act/impl/playwright.py", line 284, in _active_page
    assert self._context is not None and len(self._context.pages) > 0
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/Users/gauravbindra/Desktop/Asteroid/nova-act_approach/test_navigation4.py", line 49, in run_tests
    with nova:
         ^^^^
  File "/Users/gauravbindra/Desktop/Asteroid/asteroid_env/lib/python3.13/site-packages/nova_act/nova_act.py", line 256, in __exit__
    self.stop()
    ~~~~~~~~~^^
  File "/Users/gauravbindra/Desktop/Asteroid/asteroid_env/lib/python3.13/site-packages/nova_act/nova_act.py", line 346, in stop
    self._stop()
    ~~~~~~~~~~^^
  File "/Users/gauravbindra/Desktop/Asteroid/asteroid_env/lib/python3.13/site-packages/nova_act/nova_act.py", line 339, in _stop
    raise StopFailed from e
nova_act.types.errors.StopFailed
