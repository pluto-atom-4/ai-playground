# GitHub Copilot Instructions

This file provides custom instructions for GitHub Copilot when working in this workspace.

## Project Context

**Project Name**: Real-Time Fraud Detection System  
**Description**: Azure-based fraud detection with ML models  
**Primary Language**: Python  
**Frameworks**: Azure SDK, scikit-learn, pandas, fastapi, pytest

### Key Focus Areas
- Model accuracy and performance
- Real-time prediction latency
- Data pipeline reliability
- Monitoring and alerting
- Scalability and cost optimization

## Assistance Priorities

When providing assistance, prioritize in this order:
1. Infrastructure as Code (Terraform)
2. Policy as Code (OPA/Rego)
3. Python application code
4. Bash automation scripts
5. Azure Pipeline configurations
6. Code quality and security
7. Minimal, focused documentation only when needed

## Documentation Rules ⚠️

**CRITICAL**: Suppress excessive meta-documentation generation.

### ❌ DO NOT Generate These Files
- DIRECTORY_OVERVIEW.md
- COMPLETION_DETAILS.md
- START_HERE.md / START_HERE.txt
- QUICK_REFERENCE.md
- MODULE_GUIDE.md
- FILE_STRUCTURE_CHECKLIST.md
- REORGANIZATION_SUMMARY.md
- STRUCTURE_GUIDE.txt
- BEFORE_AFTER.md
- INDEX.md
- PROJECT_COMPLETION_REPORT.md
- INFRASTRUCTURE_SETUP_SUMMARY.md
- Any similar "meta" documentation files

### ✅ Allowed Generated Documentation
If documentation must be generated, ONLY create these files in `generated/docs-copilot/`:
- `task_status.md` - Task progress tracking
- `inspection_report.md` - Code/infrastructure inspection results
- `error_log.md` - Error tracking
- `deployment_log.md` - Deployment status

### Documentation Guidelines
- **Focus on code and configuration files, NOT meta-documentation**
- Prefer inline comments over separate documentation files
- Generate documentation ONLY when explicitly requested
- Avoid redundant "how to use this folder" documents
- Save all generated docs to `generated/docs-copilot/` ONLY

## Python Standards

### Version & Style
- Python 3.8+
- Follow PEP 8 style guide
- Maximum line length: 100 characters

### Dependency Management
**PREFER pyproject.toml over requirements.txt**
- Use `pyproject.toml` for modern Python project configuration
- Include sections: `[project]`, `[build-system]`, `[tool.pytest.ini_options]`, `[tool.black]`
- Build system: setuptools
- Include dev dependencies
- Migrate from requirements.txt to pyproject.toml when possible

### Code Quality Tools
- **Linting**: pylint, flake8 (strict mode enabled)
- **Formatting**: black (100 char line length)
- **Type Checking**: mypy (strict mode)
- **Testing**: pytest with pytest-cov (minimum 80% coverage)

### Code Organization
- Use descriptive names for variables and functions
- Keep functions small and focused (single responsibility principle)
- Document complex logic with comments
- Use type hints for ALL function parameters and return values
- Organize imports in order: standard library, third-party, local
- Use dataclasses for data structures
- Prefer composition over inheritance
- Use context managers for resource management
- Implement proper error handling with custom exceptions
- Add logging at key decision points
- Use async/await for I/O operations
- Leverage pandas for data manipulation
- Use scikit-learn or similar for ML models

### Documentation Standards
- **Docstring style**: Google format
- Include examples in docstrings
- Include type hints in docstrings
- All public functions/classes must have docstrings

### Project Structure
```
src/
├── models/         # ML model definitions
├── services/       # Business logic and services
├── utils/          # Utility functions
├── config/         # Configuration management
└── exceptions/     # Custom exceptions

tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
└── fixtures/       # Test fixtures
```

## Bash Scripting Standards

### Shell Compatibility
- **Shell**: bash (Git Bash on Windows)
- **Shebang**: `#!/usr/bin/env bash`

### Safety First
**Always start scripts with:**
```bash
#!/usr/bin/env bash
set -euo pipefail
```

### Best Practices
- Quote variables to prevent word splitting: `"$variable"`
- Use `[[ ]]` for conditionals instead of `[ ]`
- Use `$()` for command substitution instead of backticks
- Add descriptive comments for complex logic
- Use functions for reusable code blocks
- Validate input parameters at script start
- Provide usage/help messages
- Use meaningful exit codes (0=success, 1-255=error)

### Error Handling
- Check command exit codes explicitly when needed
- Use `trap` for cleanup on script exit
- Log errors to stderr using `>&2`
- Provide clear error messages with context

### Code Organization
- Define functions before they are called
- Group related functions together
- Use `main()` function for script entry point
- Keep scripts modular and focused
- Source common functions from shared library files

### Common Patterns
- Use `readonly` for constants
- Use `local` for function variables
- Prefer `printf` over `echo` for formatted output
- Use arrays for lists of items
- Validate required commands exist: `command -v tool || exit 1`

### Testing
- Test scripts with `shellcheck` for linting
- Test on Git Bash on Windows
- Handle both Unix and Windows path formats if needed

## Terraform Standards

### Version
- Terraform >= 1.0

### File Structure
```
terraform/
├── main.tf          # Primary resource definitions
├── variables.tf     # Input variable declarations
├── outputs.tf       # Output value definitions
├── backend.tf       # Backend configuration
├── providers.tf     # Provider configurations (optional)
└── versions.tf      # Version constraints (optional)
```

### Best Practices
- Use consistent naming: lowercase_with_underscores
- Group related resources in modules
- Use variables for ALL configurable values
- Add descriptions to ALL variables and outputs
- Use data sources to reference existing resources
- Tag all resources consistently
- Use remote state storage (Azure Storage Account)
- Implement state locking

### Variable Files
Maintain environment-specific variable files:
- `terraform.tfvars.example` - Template with example values
- `dev.tfvars` - Development environment
- `staging.tfvars` - Staging environment
- `prod.tfvars` - Production environment

**IMPORTANT**:
- Never commit actual `terraform.tfvars` with secrets
- Use Azure Key Vault for sensitive values
- Document required variables in README

### Module Patterns
- Keep modules focused on single resource types
- Document module inputs, outputs, and examples
- Version modules appropriately
- Use module outputs for cross-module dependencies

### Security
- Enable encryption at rest for all storage
- Use managed identities over service principals
- Implement network security groups and private endpoints
- Enable diagnostic logging for all resources
- Use Azure Policy for governance

### Validation & Testing
Before applying changes:
```bash
terraform fmt           # Format code
terraform validate      # Validate syntax
tfsec .                 # Security scanning
checkov -d .            # Policy compliance
conftest test .         # OPA policy testing
```

## Azure Pipelines Standards

### File Naming
- Use descriptive names: `*-pipeline.yml`
- Separate concerns: deployment, training, validation
- Use lowercase with hyphens

### YAML Structure
- Define variables at the top
- Use templates for reusable components
- Organize stages logically: build → test → deploy
- Use stage dependencies explicitly
- Define conditions for conditional execution

### Best Practices
- Use variable groups for environment-specific values
- Store secrets in Azure Key Vault
- Use service connections for Azure resources
- Implement approval gates for production deployments
- Add manual validation steps where appropriate
- Use pipeline templates for common patterns
- Enable pipeline caching for dependencies

### Job Organization
- Separate jobs by concern (build, test, security scan, deploy)
- Use job dependencies to control execution order
- Set appropriate timeouts for long-running jobs
- Use matrix strategy for multi-environment deployments

### Security Scanning
Always include:
- SAST (Static Application Security Testing)
- Container image scanning before deployment
- Credential leak detection
- Infrastructure validation with policy checks
- Dependency vulnerability scans

### ARM Templates
- Use ARM templates for Azure resource deployment
- Validate templates before deployment
- Use parameter files for environment-specific values
- Implement what-if checks for impact analysis
- Use incremental deployment mode by default

## Open Policy Agent (OPA) Standards

### File Conventions
- **Extension**: `.rego`
- **Naming**: `snake_case.rego`

### Code Structure
```rego
package terraform.azure.storage  # Package declaration

import data.utils               # Import statements

# Helper functions/rules
required_tags := ["Environment", "Project", "ManagedBy"]

# Main policy rules
deny[msg] {
    # Policy logic
    msg := "Violation message with actionable guidance"
}
```

### Best Practices
- Use meaningful package names (e.g., `terraform.azure.storage`)
- Write clear rule names that describe what is being checked
- Add comments explaining policy intent
- Include violation messages with actionable guidance
- Use helper rules for complex logic
- Test ALL policies with unit tests

### Policy Patterns
- Use `deny` rules for hard failures
- Use `violation` rules for compliance checks
- Use `warn` rules for best practice suggestions
- Return structured messages with `msg` field
- Include resource references in violation messages
- Use arrays/sets for allowed/denied values

### Testing
- Write unit tests for all policy rules in `*_test.rego` files
- Use `opa test . -v` to run tests
- Test both positive and negative cases
- Use descriptive test names

### Integration
- Use `conftest` for testing infrastructure as code
- Integrate with CI/CD pipelines
- Use OPA Gatekeeper for Kubernetes admission control
- Validate Terraform plans as JSON
- Validate Kubernetes manifests before apply

### Documentation
- Document policy intent and scope
- Provide examples of compliant and non-compliant resources
- Include remediation steps in violation messages
- Link to relevant standards or regulations

## Git Bash Console Operations

### Platform
- **Shell**: Git Bash
- **Platform**: Windows

### Common Commands

#### Terraform Operations
```bash
cd infrastructure/terraform
terraform init
terraform plan -var-file=environments/dev.tfvars
terraform apply -var-file=environments/dev.tfvars
terraform destroy -var-file=environments/dev.tfvars
```

#### Policy Testing
```bash
cd policies
./test-policies.sh
conftest test ../infrastructure/terraform -p terraform/
opa test . -v
```

#### Python Operations
```bash
python -m pip install -e .
python -m pytest tests/
python -m black src/
python -m pylint src/
```

#### Azure CLI
```bash
az login
az account set --subscription <subscription-id>
az group create --name <rg-name> --location <location>
az deployment group create --resource-group <rg> --template-file <template>
```

### Path Handling
- Use forward slashes in paths for cross-platform compatibility
- Convert Windows paths when needed: `cygpath -u "C:\\path"`
- Use `$(pwd)` for current directory in scripts

### Environment Variables
- Use `.env` files for local environment variables
- **Never commit .env files with secrets**
- Use `source .env` to load environment variables
- Validate required environment variables in scripts

## General Standards

### Git Commit Messages
- Follow conventional commits format
- Maximum subject length: 72 characters
- Issue reference not required but recommended

### File Naming Conventions
- **Python modules**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`

### Output Formats
When generating code or configurations, prefer:
- Markdown for documentation
- JSON for structured data
- YAML for configurations

## Copilot Behavior

### Response Style
- **Verbosity**: Detailed
- **Explanation depth**: Comprehensive
- **Include examples**: Yes
- **Consider performance**: Always
- **Consider security**: Always
- **Consider cost**: Always (Azure cost optimization)

### When Suggesting Code
- Always consider performance implications
- Always consider security implications
- Always consider Azure cost optimization
- Provide comprehensive explanations
- Include examples where helpful
- Follow all standards defined in this document

## Summary

When working in this codebase:
1. ✅ **Focus on code**, not meta-documentation
2. ✅ **Use pyproject.toml** for Python dependencies
3. ✅ **Write safe bash scripts** with `set -euo pipefail`
4. ✅ **Follow Terraform best practices** with security scanning
5. ✅ **Test OPA policies** with unit tests
6. ✅ **Structure Azure Pipelines** with security gates
7. ✅ **Optimize for Git Bash** on Windows
8. ❌ **Do NOT generate** excessive meta-documentation files
9. ❌ **Do NOT create** START_HERE, QUICK_REFERENCE, MODULE_GUIDE, etc.
10. ✅ **Save generated docs ONLY** to `generated/docs-copilot/`

