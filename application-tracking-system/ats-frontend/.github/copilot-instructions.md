# GitHub Copilot Agent Instructions

## Project Overview
This project is a modern web application built with a cutting-edge tech stack.

## Development Environment

### Package Manager
- **Primary Package Manager**: pnpm
- All dependencies should be managed through pnpm
- Use `pnpm install`, `pnpm add`, and `pnpm remove` commands

### Command Execution Environment
- **Shell**: Git Bash (bash.exe on Windows)
- All commands should be executable in a Git Bash console
- Use Unix-style command syntax and paths with forward slashes

### Documentation Generation
- Generated documentation should be saved under: `./generated/docs-copilot`
- Focus on quality over quantity - avoid creating excessive documentation
- Document only essential features, APIs, and setup procedures

## Technology Stack

The project uses the following technologies and frameworks:

### Core Framework & Language
- **Next.js**: React framework for production
- **TypeScript**: Static typing for JavaScript
- **React**: Version 19.2 - Modern component library with latest features

### AI & Utilities
- **@ai-sdk**: AI integration library for LLM interactions
- **@ai-sdk/react**: React hooks and utilities for AI features
- **zod**: Schema validation and type inference library

### Styling
- **Tailwind CSS**: Version 4 - Utility-first CSS framework
- TailwindUI compatible components recommended

### Code Quality
- **ESLint**: JavaScript/TypeScript linting and code style enforcement
- Follow existing ESLint configuration rules
- Ensure code passes all linting checks before committing

## Development Workflow

1. **Before Starting**: Run `pnpm install` to install all dependencies
2. **Development**: Use `pnpm dev` to start the development server
3. **Linting**: Run `pnpm lint` to check code quality
4. **Building**: Use `pnpm build` to create production build
5. **Type Checking**: Run `pnpm type-check` if available (TypeScript)

## Code Guidelines

- Write TypeScript with strict mode enabled
- Use React functional components with hooks
- Leverage Zod for runtime schema validation
- Implement error boundaries for better error handling
- Use Tailwind CSS utilities instead of custom CSS when possible
- Keep components small and focused on single responsibility

## Documentation Standards

When generating documentation:
- Include setup and installation instructions
- Document public APIs and main components
- Provide code examples for complex features
- Keep examples concise and runnable
- Update documentation when making breaking changes

## Notes

- Ensure all generated files are properly formatted
- Test changes locally before committing
- Follow the existing code style and patterns in the project
