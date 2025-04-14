# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Goals: Asteroid Form Challenge
- **Objective**: Build a browser agent that reliably fills out mock forms (easy and hard variants)
- **Success Criteria**: Forms return "ASTEROID_1" code when correctly filled
- **Time Investment**: ~50 hours dedicated to completing this challenge
- **Implementation**: Using a DOM-based approach with Playwright to create a comprehensive POC

## Key Requirements
- **Functionality**: Parse input data and fill out forms end-to-end
- **Robustness**: Handle both easy and complex forms reliably
- **Organization**: Create structured, maintainable code
- **Practical Focus**: Prioritize working solutions for both form types
- **Documentation**: Provide sufficient comments and documentation

## Build/Run Commands
- Setup: `python -m venv asteroid_env && source asteroid_env/bin/activate`
- Install dependencies: `pip install -r requirements.txt`
- Run easy form test: `python main.py --form easy --data easy_form_demo_data.txt`
- Run hard form test: `python main.py --form hard --data hard_form_demo_data.txt`

## Code Structure Guidelines
- **Architecture**: Well-organized code with appropriate modularity
- **Logging**: Integrate with existing logger.py for comprehensive reporting
- **DOM Interaction**: Use Playwright's modern locators (getByLabel, getByRole)
- **Data Handling**: Implement effective mapping between input data and form fields
- **Error Recovery**: Include retry mechanisms and graceful failure handling