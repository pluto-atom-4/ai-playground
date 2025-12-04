# Policy-as-Code (PaC) Implementation

This directory contains comprehensive Policy-as-Code definitions for automated compliance and security validation across Terraform infrastructure and Kubernetes deployments.

## 📋 Overview

This implementation provides a comprehensive Policy-as-Code solution combining:
- **Open Policy Agent (OPA)**: General-purpose policy engine
- **Conftest**: OPA-based tool for testing Terraform plans
- **OPA Gatekeeper**: Kubernetes admission controller
- **Azure Policy**: Native Azure governance service
- **Security Scanning**: Checkov and tfsec integration

## 📁 Directory Structure

```
policies/
├── README.md                                    # This file
├── QUICK_REFERENCE.md                           # Quick start guide
├── .conftest.yaml                               # Conftest configuration
├── test-policies.sh                             # Policy testing script
├── terraform/
│   └── azure/
│       ├── resource_tags.rego                   # Tagging enforcement
│       └── storage_encryption.rego              # Storage security
├── kubernetes/
│   ├── security.rego                            # Container security
│   └── gatekeeper/
│       ├── required-labels.yaml                 # Label requirements
│       ├── container-limits.yaml                # Resource limits
│       └── no-privileged-containers.yaml        # Security constraints
└── tests/
    └── (test files go here)
```

## 🎯 Key Features

### Multi-Layer Policy Enforcement

```
┌─────────────────────────────────────┐
│   Pre-Deployment (Development)      │
│   • OPA/Conftest validation         │
│   • Terraform plan checks           │
│   • Security scanning               │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│   During Deployment                 │
│   • Azure Policy enforcement        │
│   • Real-time validation            │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│   Post-Deployment (Runtime)         │
│   • OPA Gatekeeper (Kubernetes)     │
│   • Azure Defender scanning         │
│   • Continuous compliance           │
└─────────────────────────────────────┘
```

### Policy Categories

#### Terraform Policies
- ✅ **Resource Tagging**: Enforce Environment, Project, ManagedBy, CostCenter tags
- ✅ **Storage Security**: HTTPS-only, TLS 1.2+, encryption
- ✅ **Network Security**: NSG rules, private endpoints, network policies
- ✅ **AKS Security**: RBAC, managed identity, Azure AD integration
- ✅ **Cost Control**: VM size restrictions, node count limits

#### Kubernetes Policies
- ✅ **Security Context**: No privileged containers, non-root users
- ✅ **Resource Management**: CPU/memory limits and requests
- ✅ **Image Security**: No 'latest' tags, image scanning
- ✅ **Network Isolation**: Host network restrictions
- ✅ **Health Checks**: Liveness and readiness probes

## 🚀 Quick Start

### 1. Test Policies Locally

```bash
# Navigate to policies directory
cd policies

# Run all policy tests
./test-policies.sh

# Or use OPA directly
opa test . -v
```

### 2. Test Against Terraform Plan

```bash
# Generate plan
cd infrastructure/terraform
terraform plan -out=tfplan
terraform show -json tfplan > tfplan.json

# Run policy checks
conftest test tfplan.json -p ../../policies/terraform
```

### 3. Test Kubernetes Manifests

```bash
# Test deployment manifest
conftest test pipelines/deployment/decision_service_deployment.yaml \
  -p policies/kubernetes
```

### 4. Deploy in Pipeline

The pipeline automatically runs all policy checks when you push to main/develop branches.

## 📊 Policy Enforcement Flow

```
1. Developer commits code
   ↓
2. Pipeline triggered
   ↓
3. Install policy tools (OPA, Conftest, Checkov, tfsec)
   ↓
4. Run policy unit tests
   ↓
5. Generate Terraform plan
   ↓
6. Convert plan to JSON
   ↓
7. Run Conftest policy checks
   ↓
8. Run security scans (Checkov, tfsec)
   ↓
9. Check Azure Policy compliance
   ↓
10. If all pass → Apply changes
   ↓
11. Post-deployment validation
   ↓
12. Trigger compliance scan
   ↓
13. Generate compliance report
```

## 🔍 Example Policy Violations

### Terraform Example

**Violation:**
```
Resource 'azurerm_storage_account.data' is missing required tags: [CostCenter, Owner]
```

**Fix:**
```hcl
resource "azurerm_storage_account" "data" {
  # ... other configuration ...
  
  tags = {
    Environment = "prod"
    Project     = "fraud-detection"
    ManagedBy   = "Terraform"
    CostCenter  = "engineering"  # ← Added
    Owner       = "data-team"    # ← Added
  }
}
```

### Kubernetes Example

**Violation:**
```
Container 'fraud-decision-container' must define resource limits
```

**Fix:**
```yaml
containers:
- name: fraud-decision-container
  image: fraud-decision:v1.2.3
  resources:  # ← Added
    requests:
      cpu: "500m"
      memory: "512Mi"
    limits:
      cpu: "1"
      memory: "1Gi"
```

## 🛠️ Tools Used

| Tool | Purpose | Documentation |
|------|---------|---------------|
| **OPA** | Policy engine | [openpolicyagent.org](https://www.openpolicyagent.org) |
| **Conftest** | Policy testing | [conftest.dev](https://www.conftest.dev) |
| **Checkov** | Security scanning | [checkov.io](https://www.checkov.io) |
| **tfsec** | Terraform security | [tfsec.dev](https://tfsec.dev) |
| **Azure Policy** | Azure governance | [docs.microsoft.com](https://docs.microsoft.com/azure/governance/policy/) |
| **OPA Gatekeeper** | K8s admission control | [open-policy-agent.github.io/gatekeeper](https://open-policy-agent.github.io/gatekeeper/) |

## 📖 Documentation

For complete documentation, see:
- **`docs/policy_as_code_inspection_automation.md`** - Comprehensive guide (22,000+ words) covering:
  - Architecture and design patterns
  - OPA/Conftest integration details
  - Azure Policy setup and configuration
  - Terraform and Kubernetes policy examples
  - Azure Pipeline integration
  - Testing strategies
  - Monitoring and best practices
- **`QUICK_REFERENCE.md`** - Quick reference guide for common tasks

## 🎓 Best Practices

1. ✅ **Fail Fast**: Policies checked early in pipeline
2. ✅ **Multiple Tools**: Complementary validation (OPA, Checkov, tfsec)
3. ✅ **Clear Messages**: Descriptive error messages with remediation
4. ✅ **Version Control**: All policies in Git
5. ✅ **Testing**: Unit tests for all policies
6. ✅ **Documentation**: Comprehensive guides and examples
7. ✅ **Gradual Rollout**: Warnings before strict enforcement
8. ✅ **Audit Trail**: All violations logged

## 🔐 Security Coverage

- ✅ Encryption at rest and in transit
- ✅ Network security (NSGs, private endpoints)
- ✅ Identity and access management (RBAC, managed identities)
- ✅ Container security (non-root, no privileged)
- ✅ Secret management (Key Vault integration)
- ✅ Compliance (tagging, audit logging)
- ✅ Vulnerability scanning (image scanning, dependency checks)

## 📝 Adding New Policies

1. Create a new `.rego` file in the appropriate directory (terraform/ or kubernetes/)
2. Define the policy package and rules
3. Add unit tests in the `tests/` directory
4. Document the policy purpose and remediation steps
5. Test locally before committing:
   ```bash
   ./test-policies.sh
   ```
6. Update this README with the new policy

## 📈 Metrics & Monitoring

The implementation includes monitoring for:
- Policy violation counts
- Compliance state trends
- Security recommendation severity
- Resource compliance by type
- Policy evaluation performance

## 🤝 Integration Points

### CI/CD Integration
- ✅ Azure DevOps (primary)
- ✅ GitHub Actions (examples in docs)
- ✅ GitLab CI (examples in docs)

### Cloud Services
- ✅ Azure Policy
- ✅ Azure Defender for Cloud
- ✅ Azure Monitor / Log Analytics
- ✅ Azure Key Vault

### Kubernetes
- ✅ OPA Gatekeeper admission controller
- ✅ Pod Security Standards
- ✅ Network Policies

## 📝 Next Steps

1. **Customize Policies**: Review and adjust policies for your requirements
2. **Set Up Pipeline**: Configure Azure DevOps service connections
3. **Test Locally**: Run policy tests on your infrastructure
4. **Deploy Gatekeeper**: Install OPA Gatekeeper on AKS
5. **Configure Monitoring**: Set up alerts for policy violations
6. **Train Team**: Share documentation with development team

## 💡 Key Benefits

1. **🛡️ Security**: Prevent misconfigurations before deployment
2. **📋 Compliance**: Enforce organizational standards
3. **💰 Cost Control**: Prevent expensive resource deployments
4. **🚀 Automation**: Reduce manual review burden
5. **📊 Visibility**: Clear compliance reporting
6. **🔄 Consistency**: Enforce standards across environments
7. **📖 Documentation**: Self-documenting infrastructure policies

## 🎉 Success Metrics

After implementation, you should see:
- ⬇️ Reduced security incidents
- ⬇️ Fewer configuration errors in production
- ⬆️ Faster deployment cycles (less rework)
- ⬆️ Higher compliance scores
- ⬆️ Better resource tagging
- ⬆️ Team confidence in deployments

---

## Support

For detailed technical information and troubleshooting:
1. Review the comprehensive guide: `docs/policy_as_code_inspection_automation.md`
2. Check examples in this directory
3. Test with verbose output: `opa test -v`
4. Review pipeline logs for specific violations

**Ready to enforce compliance and security at scale! 🚀**

