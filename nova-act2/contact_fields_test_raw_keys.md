2025-04-18 22:53:17,280 - INFO - Logging to /Users/gauravbindra/Desktop/Asteroid/nova-act2/logs/contact_raw_fields_test_20250418_225317.log
2025-04-18 22:53:17,280 - INFO - Starting test to fill contact fields with raw camelCase JSON keys
2025-04-18 22:53:17,281 - INFO - Successfully loaded contact data with fields: ['title', 'firstName', 'lastName', 'dateOfBirth', 'phoneNumber', 'jointInsured', 'jointInsuredPersonName', 'numberOfYearsAsLandlord']
2025-04-18 22:53:17,281 - INFO - Initializing NovaAct for form at https://asteroid.ai/form

start session 65c37eb5-b68f-4c0b-80c1-3baf154f3596 on https://asteroid.ai/form

2025-04-18 22:53:30,769 - INFO - Browser started successfully
2025-04-18 22:53:30,769 - INFO - Waiting for form to load
2025-04-18 22:53:33,798 - INFO - Processing field 'title' with value 'Prof'
2025-04-18 22:53:33,798 - INFO - Filling field with raw camelCase name 'title' as dropdown with value: Prof
2025-04-18 22:53:33,798 - INFO - Selecting 'Prof' for dropdown 'title'
65c3> act("Find the dropdown field labeled 'title' and select 'Prof'")
...............
65c3> think("I am on a Commercial Property Insurance Application. I do not see a dropdown field labeled 'title'. I should scroll the page down to find the dropdown field labeled 'title'.");
>> agentScroll("down", "<box>0,0,812,1594</box>");
..................
65c3> think("I have scrolled down, and the page has changed. I do not see a dropdown field labeled 'title'. I should scroll the page down to find the dropdown field labeled 'title'.");
>> agentScroll("down", "<box>0,0,812,1594</box>");
....................
65c3> think("I have scrolled down and the page has changed. I see a dropdown field labeled 'title'. I should select the 'Title' dropdown to reveal the options.");
>> agentClick("<box>232,312,262,784</box>");
............
65c3> think("The dropdown requires typing instead of clicking. To choose 'Prof', I will input 'Prof'.");
>> agentType("Prof", "<box>232,312,262,784</box>");
.....................
65c3> think("My last action was to type 'Prof' into the dropdown field labeled 'title'. The current screenshot shows that 'Prof' has been selected, so my last action was successful. The task to find the dropdown field labeled 'title' and select 'Prof' is now complete.");
>> return;
.....
65c3> ** View your act run here: /var/folders/3f/x95cmnkn57s5pfth5lygr5k00000gn/T/tmpy0nu40km_nova_act_logs/65c37eb5-b68f-4c0b-80c1-3baf154f3596/act_fb8069fb-bbe7-4085-90c4-b710231d8a7d_output.html

2025-04-18 22:54:21,644 - INFO - Successfully selected 'Prof' for 'title' dropdown
2025-04-18 22:54:22,647 - INFO - Processing field 'firstName' with value 'Vladimir'
2025-04-18 22:54:22,647 - INFO - Filling field with raw camelCase name 'firstName' as text with value: Vladimir
2025-04-18 22:54:22,647 - INFO - Filling text field 'firstName' with value 'Vladimir'
65c3> act("Find the field labeled 'firstName' and enter 'Vladimir'. Scroll if necessary. Stop scrolling if you see the header or footer.")
.............
65c3> think("I am on a page with a form. My task is to find the field labeled 'firstName' and enter 'Vladimir'. I can see a field labeled 'First Name', which matches what I am looking for. I should type 'Vladimir' into the 'First Name' field to populate it.");
>> agentType("Vladimir", "<box>228,802,264,1268</box>");
...........................................
65c3> think("The 'First Name' field is now populated with 'Vladimir', meaning my last action was successful. I have completed my instructions and nothing else has been asked of me. My task is complete. No specific return information has been asked of me, so I should simply return.");
>> return;
......
65c3> ** View your act run here: /var/folders/3f/x95cmnkn57s5pfth5lygr5k00000gn/T/tmpy0nu40km_nova_act_logs/65c37eb5-b68f-4c0b-80c1-3baf154f3596/act_0085a80c-1444-40aa-b8fc-871a76c7c59b_output.html

2025-04-18 22:54:54,971 - INFO - Successfully filled 'firstName' field
2025-04-18 22:54:55,976 - INFO - Processing field 'lastName' with value 'McDougal'
2025-04-18 22:54:55,976 - INFO - Filling field with raw camelCase name 'lastName' as text with value: McDougal
2025-04-18 22:54:55,976 - INFO - Filling text field 'lastName' with value 'McDougal'
65c3> act("Find the field labeled 'lastName' and enter 'McDougal'. Scroll if necessary. Stop scrolling if you see the header or footer.")
.............
65c3> think("I am on a page with a form. My task is to find the field labeled 'lastName' and enter 'McDougal'. I can see a field labeled 'Last Name', which matches what I am looking for. I should enter 'McDougal' into the 'Last Name' field to populate it.");
>> agentType("McDougal", "<box>280,312,326,780</box>");
...................
65c3> think("The 'Last Name' field is now populated with 'McDougal', so my last action was successful. I have completed my instructions and nothing else has been asked of me. My task is complete. No specific return information has been asked of me, so I should simply return.");
>> return;
......
65c3> ** View your act run here: /var/folders/3f/x95cmnkn57s5pfth5lygr5k00000gn/T/tmpy0nu40km_nova_act_logs/65c37eb5-b68f-4c0b-80c1-3baf154f3596/act_d04b5674-bb90-4da7-a9d3-c4f0c115910f_output.html

2025-04-18 22:55:15,998 - INFO - Successfully filled 'lastName' field
2025-04-18 22:55:16,999 - INFO - Processing field 'dateOfBirth' with value '1975-06-15'
2025-04-18 22:55:16,999 - INFO - Filling field with raw camelCase name 'dateOfBirth' as date with value: 1975-06-15
2025-04-18 22:55:16,999 - INFO - Filling date field 'dateOfBirth' with value '1975-06-15'
65c3> act("Find the date field labeled 'dateOfBirth'")
...........
65c3> think("Returning the location of date field labeled 'dateOfBirth'");
>> agentClick("<box>304,802,338,1266</box>");
.................
65c3> think("My last action was to click the date field labeled 'dateOfBirth'. The current screenshot shows that the date field labeled 'dateOfBirth' is selected, so my last action was successful. The task to find the date field labeled 'dateOfBirth' is now complete.");
>> return;
.....
65c3> ** View your act run here: /var/folders/3f/x95cmnkn57s5pfth5lygr5k00000gn/T/tmpy0nu40km_nova_act_logs/65c37eb5-b68f-4c0b-80c1-3baf154f3596/act_1cf9c49a-cae0-455e-b65a-5e83542623a6_output.html

65c3> act("Does the date field 'dateOfBirth' expect the date in dd/mm/yyyy order? Answer true or false., format output with jsonschema: {"type": "boolean"}")
.............
65c3> think("Extracting:  Does the date field 'dateOfBirth' expect the date in dd/mm/yyyy order? Answer true or false.");
>> return "true";
.....
65c3> ** View your act run here: /var/folders/3f/x95cmnkn57s5pfth5lygr5k00000gn/T/tmpy0nu40km_nova_act_logs/65c37eb5-b68f-4c0b-80c1-3baf154f3596/act_a626e1ed-7a83-4489-b4bf-b76b53277ef7_output.html

2025-04-18 22:55:44,093 - INFO - [dateOfBirth] confirmed format: dd/mm/yyyy
2025-04-18 22:55:44,093 - INFO - Converted date format from 1975-06-15 to 15/06/1975
65c3> act("Enter '15/06/1975' into the date field 'dateOfBirth'")
.............
65c3> think("I'll initiate by opening the date field 'dateOfBirth'.");
>> agentType("15/06/1975", "<box>304,802,338,1252</box>");
..................
65c3> think("I've entered the date '15/06/1975' into the date field 'dateOfBirth'.");
>> return;
.....
65c3> ** View your act run here: /var/folders/3f/x95cmnkn57s5pfth5lygr5k00000gn/T/tmpy0nu40km_nova_act_logs/65c37eb5-b68f-4c0b-80c1-3baf154f3596/act_75bba6d5-936d-47e3-a7d2-46a21ba2c62b_output.html

2025-04-18 22:56:03,148 - INFO - Successfully filled date field 'dateOfBirth' with '15/06/1975'
2025-04-18 22:56:04,153 - INFO - Processing field 'phoneNumber' with value '07823456789'
2025-04-18 22:56:04,153 - INFO - Filling field with raw camelCase name 'phoneNumber' as text with value: 07823456789
2025-04-18 22:56:04,154 - INFO - Filling text field 'phoneNumber' with value '07823456789'
65c3> act("Find the field labeled 'phoneNumber' and enter '07823456789'. Scroll if necessary. Stop scrolling if you see the header or footer.")
..............
65c3> think("I am on a page with a form. My task is to find the field labeled 'phoneNumber' and enter '07823456789'. I need to find the field labeled 'phoneNumber' and I see a field with the label 'Phone Number'. I should type '07823456789' into the 'Phone Number' field to populate it.");
>> agentType("07823456789", "<box>378,312,410,784</box>");
...................
65c3> think("The 'Phone Number' field is now populated with '07823456789', so my last action was successful. I have found the field labeled 'Phone Number' and entered '07823456789'. My task is complete, and I need to return.");
>> return;
.....
65c3> ** View your act run here: /var/folders/3f/x95cmnkn57s5pfth5lygr5k00000gn/T/tmpy0nu40km_nova_act_logs/65c37eb5-b68f-4c0b-80c1-3baf154f3596/act_8c254454-d181-473e-89b1-5cbb99922efc_output.html

2025-04-18 22:56:24,241 - INFO - Successfully filled 'phoneNumber' field
2025-04-18 22:56:25,258 - INFO - Processing field 'jointInsured' with value 'True'
2025-04-18 22:56:25,258 - INFO - Filling field with raw camelCase name 'jointInsured' as checkbox with value: True
2025-04-18 22:56:25,258 - INFO - Checking checkbox 'jointInsured'
2025-04-18 22:56:25,258 - ERROR - Error handling checkbox 'jointInsured': Prompt must be a string.
Traceback (most recent call last):
  File "/Users/gauravbindra/Desktop/Asteroid/nova-act2/fill_fields.py", line 70, in fill_checkbox
    nova.act(query)
    ~~~~~~~~^^^^^^^
  File "/Users/gauravbindra/Desktop/Asteroid/asteroid_env/lib/python3.13/site-packages/nova_act/nova_act.py", line 392, in act
    validate_prompt(prompt)
    ~~~~~~~~~~~~~~~^^^^^^^^
  File "/Users/gauravbindra/Desktop/Asteroid/asteroid_env/lib/python3.13/site-packages/nova_act/impl/inputs.py", line 116, in validate_prompt
    raise InvalidInputLength("Prompt must be a string.")
nova_act.types.errors.InvalidInputLength: Prompt must be a string.
2025-04-18 22:56:26,385 - INFO - Processing field 'jointInsuredPersonName' with value 'Zelda Winterbottom'
2025-04-18 22:56:26,385 - INFO - Filling field with raw camelCase name 'jointInsuredPersonName' as text with value: Zelda Winterbottom
2025-04-18 22:56:26,386 - INFO - Filling text field 'jointInsuredPersonName' with value 'Zelda Winterbottom'
65c3> act("Find the field labeled 'jointInsuredPersonName' and enter 'Zelda Winterbottom'. Scroll if necessary. Stop scrolling if you see the header or footer.")
..............
65c3> think("I am on a page with a form. My task is to find the field labeled 'jointInsuredPersonName' and enter 'Zelda Winterbottom'. I need to find the field labeled 'jointInsuredPersonName'. I can see a 'Joint Insured' checkbox, but it is not a field. I should scroll up to find the field labeled 'jointInsuredPersonName'.");
>> agentScroll("up", "<box>0,0,812,1594</box>");
..................
65c3> think("The webpage has scrolled up and new content is visible, meaning my previous action was successful. I do not see a field labeled 'jointInsuredPersonName', and I do not see the header, so I can scroll up the page. I should scroll up the page to reveal the rest of the page.");
>> agentScroll("up", "<box>0,0,812,1594</box>");
..................
65c3> think("The webpage has scrolled up and new content is visible, meaning my previous action was successful. I do not see a field labeled 'jointInsuredPersonName', and I do not see the header, so I can scroll up the page. I should scroll up the page to reveal the rest of the page.");
>> agentScroll("up", "<box>0,0,812,1594</box>");
...................
65c3> think("My last action was to scroll up which is incorrect. I did not need to scroll up to find the field labeled 'jointInsuredPersonName'. I need to scroll down to find the field labeled 'jointInsuredPersonName' instead of scrolling up to find it. I should now scroll down to find the field labeled 'jointInsuredPersonName'.");
>> agentScroll("down", "<box>0,0,812,1594</box>");
.................
65c3> think("The webpage has scrolled down and new content is visible, meaning my previous action was successful. I do not see a field labeled 'jointInsuredPersonName', so I need to continue to scroll down. I should scroll down the page to reveal the rest of the page.");
>> agentScroll("down", "<box>0,0,812,1594</box>");
.................
65c3> think("The webpage has scrolled down and new content is visible, meaning my previous action was successful. I do not see a field labeled 'jointInsuredPersonName', so I need to continue to scroll down. I should scroll down the page to reveal the rest of the page.");
>> agentScroll("down", "<box>0,0,812,1594</box>");
..................
65c3> think("The webpage scrolled down and I am at the bottom of the page, meaning my previous action was successful. I can now see the webpage footer, and the slider has reached the bottom, indicating that I am at the bottom of the page. Since I still cannot locate a field labeled 'jointInsuredPersonName', I should trigger an agent error to inform the user that the field labeled 'jointInsuredPersonName' cannot be found.");
>> throw new AgentError("The field labeled 'jointInsuredPersonName' is not available on the page.");
.
65c3> ** View your act run here: /var/folders/3f/x95cmnkn57s5pfth5lygr5k00000gn/T/tmpy0nu40km_nova_act_logs/65c37eb5-b68f-4c0b-80c1-3baf154f3596/act_3a697cdf-6dd6-4fda-b415-185afbb4c537_output.html

2025-04-18 22:57:30,937 - ERROR - Error filling 'jointInsuredPersonName' field: 

ActAgentError(
    message = The field labeled 'jointInsuredPersonName' is not available on the page.
    metadata = ActMetadata(
        session_id = 65c37eb5-b68f-4c0b-80c1-3baf154f3596
        act_id = 3a697cdf-6dd6-4fda-b415-185afbb4c537
        num_steps_executed = 7
        start_time = 2025-04-18 22:56:26.386263 EDT
        end_time = 2025-04-18 22:57:30.306067 EDT
        prompt = 'Find the field labeled 'jointInsuredPersonName' and enter 'Zelda Winterbottom'. Scroll if necessary. Stop scrolling if you see the header or footer.'
    )
)

Please consider providing feedback: https://amazonexteu.qualtrics.com/jfe/form/SV_bd8dHa7Em6kNkMe
Traceback (most recent call last):
  File "/Users/gauravbindra/Desktop/Asteroid/nova-act2/fill_fields.py", line 34, in fill_text_field
    nova.act(query)
    ~~~~~~~~^^^^^^^
  File "/Users/gauravbindra/Desktop/Asteroid/asteroid_env/lib/python3.13/site-packages/nova_act/nova_act.py", line 416, in act
    raise response
nova_act.types.act_errors.ActAgentError: 

ActAgentError(
    message = The field labeled 'jointInsuredPersonName' is not available on the page.
    metadata = ActMetadata(
        session_id = 65c37eb5-b68f-4c0b-80c1-3baf154f3596
        act_id = 3a697cdf-6dd6-4fda-b415-185afbb4c537
        num_steps_executed = 7
        start_time = 2025-04-18 22:56:26.386263 EDT
        end_time = 2025-04-18 22:57:30.306067 EDT
        prompt = 'Find the field labeled 'jointInsuredPersonName' and enter 'Zelda Winterbottom'. Scroll if necessary. Stop scrolling if you see the header or footer.'
    )
)

Please consider providing feedback: https://amazonexteu.qualtrics.com/jfe/form/SV_bd8dHa7Em6kNkMe
2025-04-18 22:57:31,942 - INFO - Processing field 'numberOfYearsAsLandlord' with value '12'
2025-04-18 22:57:31,943 - INFO - Filling field with raw camelCase name 'numberOfYearsAsLandlord' as text with value: 12
2025-04-18 22:57:31,943 - INFO - Filling text field 'numberOfYearsAsLandlord' with value '12'
65c3> act("Find the field labeled 'numberOfYearsAsLandlord' and enter '12'. Scroll if necessary. Stop scrolling if you see the header or footer.")
.............
65c3> think("I am on a page with a form. My task is to find the field labeled 'numberOfYearsAsLandlord' and enter the number 12 into it. I need to find the field labeled 'numberOfYearsAsLandlord'. I see a field labeled 'Years as Landlord', which might be the one I need. I should type '12' into the 'Years as Landlord' field to populate it.");
>> agentType("12", "<box>240,802,264,1270</box>");
...................
65c3> think("The 'Years as Landlord' field is now populated with '12', so my last action was successful. I have found the field labeled 'numberOfYearsAsLandlord' and entered '12' into it. The task is complete, and I need to return.");
>> return;
......
65c3> ** View your act run here: /var/folders/3f/x95cmnkn57s5pfth5lygr5k00000gn/T/tmpy0nu40km_nova_act_logs/65c37eb5-b68f-4c0b-80c1-3baf154f3596/act_fe81ee8b-d552-4e7d-9fb5-53199cc4ac69_output.html

2025-04-18 22:57:52,197 - INFO - Successfully filled 'numberOfYearsAsLandlord' field
2025-04-18 22:57:53,201 - INFO - Field filling complete: 6/8 fields filled successfully
2025-04-18 22:57:53,202 - INFO - ✅ Success: title
2025-04-18 22:57:53,202 - INFO - ✅ Success: firstName
2025-04-18 22:57:53,202 - INFO - ✅ Success: lastName
2025-04-18 22:57:53,202 - INFO - ✅ Success: dateOfBirth
2025-04-18 22:57:53,202 - INFO - ✅ Success: phoneNumber
2025-04-18 22:57:53,202 - INFO - ❌ Failed: jointInsured
2025-04-18 22:57:53,202 - INFO - ❌ Failed: jointInsuredPersonName
2025-04-18 22:57:53,202 - INFO - ✅ Success: numberOfYearsAsLandlord
2025-04-18 22:57:53,202 - INFO - Attempting to proceed to next section
65c3> act("Find and click the Next button")
...........
65c3> think("Returning the location of Next button");
>> agentClick("<box>374,1206,410,1274</box>");
....................
65c3> think("My last action was clicking on the Next button. The current screenshot shows the Commercial Property Insurance Application page, which means my last action was successful. The task to click the Next button is now complete.");
>> return;
.......
65c3> ** View your act run here: /var/folders/3f/x95cmnkn57s5pfth5lygr5k00000gn/T/tmpy0nu40km_nova_act_logs/65c37eb5-b68f-4c0b-80c1-3baf154f3596/act_d4eb0936-9031-405c-89ad-1ab1de1a7105_output.html


end session

