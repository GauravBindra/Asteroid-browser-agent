# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build/Run Commands
- Setup: `npm install` 
- Start development server: `npm run dev`
- Build: `npm run build`
- Lint: `npm run lint`
- Format code: `npm run format`
- Test: `npm run test`
- Run single test: `npm test -- -t "test name"`

## Code Style Guidelines
- **Formatting**: Follow consistent indentation (2 spaces) and line length
- **Naming**: Use descriptive camelCase for variables/functions, PascalCase for components
- **Form Components**: Keep form components modular and reusable
- **Validation**: Implement client-side validation with clear error messages
- **Accessibility**: Ensure form elements have proper labels and ARIA attributes
- **State Management**: Use React hooks for form state (useState, useForm)
- **TypeScript**: Define interfaces for form data structures
- **Error Handling**: Provide user-friendly feedback for form submission errors
- **Documentation**: Document form field requirements and validation rules