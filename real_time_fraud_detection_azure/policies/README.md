# Policies Directory

This directory contains Policy-as-Code (PaC) definitions for automated compliance and security validation.

## Structure

```
policies/
├── terraform/          # Policies for Terraform infrastructure
│   ├── azure/         # Azure-specific policies
│   └── general/       # General infrastructure policies
├── kubernetes/        # Policies for Kubernetes resources
│   └── gatekeeper/   # OPA Gatekeeper constraint templates
└── tests/            # Unit tests for policies
```

## Usage

### Testing Policies Locally

```bash
# Test all policies
opa test policies/ -v

# Test specific namespace
opa test policies/terraform/azure -v

# Run Conftest on Terraform plan
terraform plan -out=tfplan
terraform show -json tfplan > tfplan.json
conftest test tfplan.json -p policies/terraform

# Test Kubernetes manifests
conftest test deployment.yaml -p policies/kubernetes
```

## Policy Categories

### Terraform Policies
- **Resource Tags**: Enforce required tagging standards
- **Network Security**: Validate network configurations
- **Storage Encryption**: Ensure encryption is enabled
- **AKS Security**: Kubernetes cluster security requirements
- **Cost Control**: Prevent expensive resource configurations

### Kubernetes Policies
- **Security**: Container security contexts and privileges
- **Resource Limits**: CPU and memory constraints
- **Network Policies**: Network isolation rules
- **Image Security**: Image scanning and tag restrictions

## Adding New Policies

1. Create a new `.rego` file in the appropriate directory
2. Define the policy package and rules
3. Add unit tests in the `tests/` directory
4. Document the policy purpose and remediation steps
5. Test locally before committing
6. Update this README with the new policy

## Documentation

See `docs/policy_as_code_inspection_automation.md` for complete documentation on:
- Policy development guidelines
- Integration with CI/CD pipelines
- Testing strategies
- Best practices

