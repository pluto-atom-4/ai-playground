# Policy-as-Code Quick Reference

## Quick Start

### 1. Install Required Tools

```bash
# Install OPA
curl -L -o opa https://openpolicyagent.org/downloads/latest/opa_linux_amd64
chmod 755 ./opa
sudo mv opa /usr/local/bin/

# Install Conftest
wget https://github.com/open-policy-agent/conftest/releases/download/v0.48.0/conftest_0.48.0_Linux_x86_64.tar.gz
tar xzf conftest_0.48.0_Linux_x86_64.tar.gz
sudo mv conftest /usr/local/bin/
```

### 2. Test Policies Locally

```bash
# From the policies directory
cd policies
./test-policies.sh

# Or manually
opa test . -v
```

### 3. Test Terraform Plans

```bash
# Generate Terraform plan
cd infrastructure/terraform
terraform init
terraform plan -out=tfplan

# Convert to JSON
terraform show -json tfplan > tfplan.json

# Run policy checks
conftest test tfplan.json -p ../../policies/terraform

# Or with specific policies
conftest test tfplan.json \
  -p ../../policies/terraform/azure/resource_tags.rego \
  -p ../../policies/terraform/azure/storage_encryption.rego
```

### 4. Test Kubernetes Manifests

```bash
# Test single manifest
conftest test pipelines/deployment/decision_service_deployment.yaml \
  -p policies/kubernetes

# Test all manifests in a directory
conftest test pipelines/deployment/*.yaml \
  -p policies/kubernetes
```

## Common Commands

### OPA Commands

```bash
# Run tests
opa test policies/ -v

# Check syntax
opa check policies/

# Format code
opa fmt -w policies/

# Evaluate a policy
opa eval -d policies/terraform/azure/resource_tags.rego -i tfplan.json 'data.terraform.azure.tags.deny'
```

### Conftest Commands

```bash
# Test with output formats
conftest test tfplan.json --output json
conftest test tfplan.json --output table
conftest test tfplan.json --output tap

# Update policies from OCI registry
conftest pull oci://ghcr.io/your-org/policies

# Verify policies have tests
conftest verify -p policies/
```

## Policy Namespaces

### Terraform Policies
- `terraform.azure.tags` - Resource tagging requirements
- `terraform.azure.storage` - Storage security and encryption
- `terraform.azure.network` - Network security rules
- `terraform.azure.aks` - AKS security configuration
- `terraform.general.cost` - Cost control and optimization

### Kubernetes Policies
- `kubernetes.security` - Container security requirements
- `kubernetes.resources` - Resource limits and requests
- `kubernetes.network` - Network policies

## Common Policy Violations

### Terraform

**Missing Tags**
```
Violation: Resource is missing required tags: [Environment, CostCenter]
Remediation: Add missing tags to resource definition
```

**Insecure Storage**
```
Violation: Storage account must enable HTTPS traffic only
Remediation: Set enable_https_traffic_only = true
```

**Old TLS Version**
```
Violation: Must use minimum TLS version 1.2
Remediation: Set min_tls_version = "TLS1_2"
```

### Kubernetes

**Missing Resource Limits**
```
Violation: Container has no resource limits defined
Remediation: Add resources.limits.cpu and resources.limits.memory
```

**Privileged Container**
```
Violation: Privileged container is not allowed
Remediation: Remove or set securityContext.privileged: false
```

**Latest Tag**
```
Violation: Must not use 'latest' tag
Remediation: Use specific version tags (e.g., v1.2.3)
```

## Integration Examples

### GitHub Actions

```yaml
- name: Policy Check
  run: |
    conftest test tfplan.json \
      -p policies/terraform \
      --fail-on-warn
```

### Azure DevOps

```yaml
- task: Bash@3
  displayName: 'Policy Check'
  inputs:
    targetType: 'inline'
    script: |
      conftest test tfplan.json \
        -p $(System.DefaultWorkingDirectory)/policies/terraform \
        --output json > policy-results.json
```

### GitLab CI

```yaml
policy-check:
  stage: validate
  script:
    - conftest test tfplan.json -p policies/terraform
  artifacts:
    reports:
      junit: policy-results.xml
```

## Troubleshooting

### Policy Not Running

1. Check namespace matches: `package terraform.azure.tags`
2. Verify policy path: `conftest test -p policies/terraform`
3. Check input format: Use `terraform show -json`

### False Positives

1. Review policy logic
2. Check input structure with: `jq . tfplan.json`
3. Use `trace` for debugging: `conftest test --trace`

### Performance Issues

1. Limit policy scope
2. Optimize Rego queries
3. Use parallel execution in pipeline
4. Cache policy results

## Resources

- [OPA Documentation](https://www.openpolicyagent.org/docs/latest/)
- [Conftest Documentation](https://www.conftest.dev/)
- [OPA Playground](https://play.openpolicyagent.org/)
- [Rego Style Guide](https://www.styra.com/rego-style-guide/)

## Support

For issues or questions:
1. Check the main documentation: `docs/policy_as_code_inspection_automation.md`
2. Review policy examples in `policies/`
3. Run tests with verbose output: `opa test -v`

