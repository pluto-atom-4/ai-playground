# Automated Inspection and Policy-as-Code (PaC) Guide

## Overview

This document outlines the strategy and implementation for automated inspection after Terraform provisioning and Azure Pipeline deployment using Policy-as-Code (PaC) frameworks. The approach combines Open Policy Agent (OPA) for flexible policy enforcement with Azure-native services for compliance and governance.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Open Policy Agent (OPA) Integration](#open-policy-agent-opa-integration)
3. [Azure-Native Policy Services](#azure-native-policy-services)
4. [Terraform Integration](#terraform-integration)
5. [Azure Pipeline Integration](#azure-pipeline-integration)
6. [Policy Examples](#policy-examples)
7. [Testing and Validation](#testing-and-validation)
8. [Monitoring and Alerting](#monitoring-and-alerting)
9. [Best Practices](#best-practices)

---

## Architecture Overview

### Inspection Points

```
┌─────────────────────────────────────────────────────────────┐
│                    Policy Enforcement Layers                 │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. Pre-Deployment (Plan Phase)                              │
│     ├── OPA/Conftest for Terraform Plans                     │
│     ├── Azure Policy Guest Configuration                     │
│     └── Custom validation scripts                            │
│                                                               │
│  2. During Deployment (Apply Phase)                          │
│     ├── Azure Policy (Deny/Audit effects)                    │
│     └── Azure Blueprints                                     │
│                                                               │
│  3. Post-Deployment (Runtime)                                │
│     ├── OPA Gatekeeper for Kubernetes                        │
│     ├── Azure Policy for Azure Resources                     │
│     ├── Azure Defender for Cloud                             │
│     └── Automated compliance scanning                        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

- **Open Policy Agent (OPA)**: General-purpose policy engine for pre-deployment validation
- **Conftest**: OPA-based tool for testing Terraform plans
- **OPA Gatekeeper**: Kubernetes admission controller for runtime policy enforcement
- **Azure Policy**: Native Azure service for governance and compliance
- **Azure Defender for Cloud**: Security posture management and threat protection
- **Azure DevOps Extensions**: Custom tasks for pipeline integration

---

## Open Policy Agent (OPA) Integration

### 1. Setup OPA/Conftest

#### Installation in Azure Pipeline

```yaml
# File: pipelines/validation/opa-setup.yml
steps:
- task: Bash@3
  displayName: 'Install Conftest'
  inputs:
    targetType: 'inline'
    script: |
      # Install Conftest
      wget https://github.com/open-policy-agent/conftest/releases/download/v0.48.0/conftest_0.48.0_Linux_x86_64.tar.gz
      tar xzf conftest_0.48.0_Linux_x86_64.tar.gz
      sudo mv conftest /usr/local/bin/
      conftest --version
      
      # Verify installation
      which conftest

- task: Bash@3
  displayName: 'Install OPA CLI'
  inputs:
    targetType: 'inline'
    script: |
      # Install OPA
      curl -L -o opa https://openpolicyagent.org/downloads/latest/opa_linux_amd64
      chmod 755 ./opa
      sudo mv opa /usr/local/bin/
      opa version
```

### 2. OPA Policy Structure

Create a policy directory structure:

```
policies/
├── terraform/
│   ├── azure/
│   │   ├── resource_tags.rego
│   │   ├── network_security.rego
│   │   ├── storage_encryption.rego
│   │   ├── aks_security.rego
│   │   └── naming_conventions.rego
│   └── general/
│       ├── cost_control.rego
│       └── resource_limits.rego
├── kubernetes/
│   ├── security.rego
│   ├── resource_limits.rego
│   └── network_policies.rego
└── tests/
    ├── terraform_test.rego
    └── kubernetes_test.rego
```

### 3. Example OPA Policies for Terraform

#### Resource Tagging Policy

```rego
# File: policies/terraform/azure/resource_tags.rego
package terraform.azure.tags

import future.keywords

# Required tags for all resources
required_tags := ["Environment", "Project", "ManagedBy", "CostCenter"]

# Deny resources without required tags
deny[msg] {
    resource := input.resource_changes[_]
    resource.mode == "managed"
    
    # Check if resource type supports tags
    resource_supports_tags(resource.type)
    
    # Get current tags
    tags := object.get(resource.change.after, "tags", {})
    
    # Find missing tags
    missing_tags := [tag | tag := required_tags[_]; not tags[tag]]
    count(missing_tags) > 0
    
    msg := sprintf(
        "Resource '%s' of type '%s' is missing required tags: %v",
        [resource.address, resource.type, missing_tags]
    )
}

# Define resources that support tags
resource_supports_tags(resource_type) {
    supported := [
        "azurerm_resource_group",
        "azurerm_storage_account",
        "azurerm_kubernetes_cluster",
        "azurerm_machine_learning_workspace",
        "azurerm_cosmosdb_account",
        "azurerm_key_vault",
        "azurerm_servicebus_namespace"
    ]
    resource_type == supported[_]
}

# Warn about recommended tags
warn[msg] {
    resource := input.resource_changes[_]
    resource.mode == "managed"
    resource_supports_tags(resource.type)
    
    tags := object.get(resource.change.after, "tags", {})
    
    # Recommended but not required
    not tags["Owner"]
    
    msg := sprintf(
        "Resource '%s' should have an 'Owner' tag for better accountability",
        [resource.address]
    )
}
```

#### Network Security Policy

```rego
# File: policies/terraform/azure/network_security.rego
package terraform.azure.network

import future.keywords

# Deny public IP access to storage accounts
deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "azurerm_storage_account"
    
    network_rules := object.get(resource.change.after, "network_rules", [])
    
    # Check if public network access is allowed (default behavior)
    count(network_rules) == 0
    
    msg := sprintf(
        "Storage account '%s' must have network_rules configured to restrict public access",
        [resource.address]
    )
}

# Deny NSG rules that allow unrestricted inbound access
deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "azurerm_network_security_rule"
    
    rule := resource.change.after
    rule.direction == "Inbound"
    rule.access == "Allow"
    rule.source_address_prefix == "*"
    
    # Critical ports that should never be open to the internet
    critical_ports := [22, 3389, 1433, 3306, 5432]
    rule.destination_port_range == sprintf("%d", [critical_ports[_]])
    
    msg := sprintf(
        "NSG rule '%s' allows unrestricted inbound access on critical port %s",
        [resource.address, rule.destination_port_range]
    )
}

# Ensure AKS uses network policy
deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "azurerm_kubernetes_cluster"
    
    network_profile := object.get(resource.change.after, "network_profile", [{}])
    
    # Check if network_policy is enabled
    network_policy := object.get(network_profile[0], "network_policy", "")
    not network_policy in ["azure", "calico"]
    
    msg := sprintf(
        "AKS cluster '%s' must have network_policy enabled (azure or calico)",
        [resource.address]
    )
}
```

#### Storage Encryption Policy

```rego
# File: policies/terraform/azure/storage_encryption.rego
package terraform.azure.storage

import future.keywords

# Ensure storage accounts use HTTPS only
deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "azurerm_storage_account"
    
    https_only := object.get(resource.change.after, "enable_https_traffic_only", false)
    not https_only
    
    msg := sprintf(
        "Storage account '%s' must enable HTTPS traffic only",
        [resource.address]
    )
}

# Ensure storage accounts have encryption enabled
deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "azurerm_storage_account"
    
    # Check minimum TLS version
    min_tls := object.get(resource.change.after, "min_tls_version", "TLS1_0")
    min_tls != "TLS1_2"
    
    msg := sprintf(
        "Storage account '%s' must use minimum TLS version 1.2",
        [resource.address]
    )
}

# Ensure CosmosDB uses encryption at rest
deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "azurerm_cosmosdb_account"
    
    # CosmosDB encryption is enabled by default, but check if explicitly disabled
    capabilities := object.get(resource.change.after, "capabilities", [])
    
    msg := sprintf(
        "CosmosDB account '%s' must maintain encryption at rest (enabled by default)",
        [resource.address]
    )
}
```

#### AKS Security Policy

```rego
# File: policies/terraform/azure/aks_security.rego
package terraform.azure.aks

import future.keywords

# Ensure AKS uses managed identity
deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "azurerm_kubernetes_cluster"
    
    identity := object.get(resource.change.after, "identity", [])
    
    # Check if managed identity is used
    count(identity) == 0
    
    msg := sprintf(
        "AKS cluster '%s' must use managed identity instead of service principal",
        [resource.address]
    )
}

# Ensure AKS has RBAC enabled
deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "azurerm_kubernetes_cluster"
    
    rbac_enabled := object.get(resource.change.after, "role_based_access_control_enabled", false)
    not rbac_enabled
    
    msg := sprintf(
        "AKS cluster '%s' must have RBAC enabled",
        [resource.address]
    )
}

# Ensure AKS uses Azure AD integration
warn[msg] {
    resource := input.resource_changes[_]
    resource.type == "azurerm_kubernetes_cluster"
    
    azure_ad := object.get(resource.change.after, "azure_active_directory_role_based_access_control", [])
    count(azure_ad) == 0
    
    msg := sprintf(
        "AKS cluster '%s' should use Azure AD integration for enhanced security",
        [resource.address]
    )
}

# Ensure private cluster is enabled for production
deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "azurerm_kubernetes_cluster"
    
    tags := object.get(resource.change.after, "tags", {})
    environment := object.get(tags, "Environment", "")
    environment == "prod"
    
    private_enabled := object.get(resource.change.after, "private_cluster_enabled", false)
    not private_enabled
    
    msg := sprintf(
        "AKS cluster '%s' in production must be a private cluster",
        [resource.address]
    )
}
```

#### Cost Control Policy

```rego
# File: policies/terraform/general/cost_control.rego
package terraform.general.cost

import future.keywords

# Limit expensive VM SKUs
deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "azurerm_kubernetes_cluster"
    
    default_node_pool := resource.change.after.default_node_pool[0]
    vm_size := default_node_pool.vm_size
    
    # Restrict expensive VM sizes in non-production
    expensive_vms := ["Standard_D16s_v3", "Standard_E16s_v3", "Standard_F16s_v2"]
    vm_size in expensive_vms
    
    tags := object.get(resource.change.after, "tags", {})
    environment := object.get(tags, "Environment", "")
    environment != "prod"
    
    msg := sprintf(
        "AKS cluster '%s' in '%s' environment uses expensive VM size '%s'. Consider using smaller VMs for non-production.",
        [resource.address, environment, vm_size]
    )
}

# Warn about high replica counts in dev
warn[msg] {
    resource := input.resource_changes[_]
    resource.type == "azurerm_kubernetes_cluster"
    
    default_node_pool := resource.change.after.default_node_pool[0]
    node_count := default_node_pool.node_count
    
    tags := object.get(resource.change.after, "tags", {})
    environment := object.get(tags, "Environment", "")
    environment == "dev"
    
    node_count > 3
    
    msg := sprintf(
        "AKS cluster '%s' in dev environment has %d nodes. Consider reducing for cost optimization.",
        [resource.address, node_count]
    )
}
```

### 4. Kubernetes OPA Policies

```rego
# File: policies/kubernetes/security.rego
package kubernetes.security

import future.keywords

# Deny privileged containers
deny[msg] {
    input.kind == "Deployment"
    container := input.spec.template.spec.containers[_]
    container.securityContext.privileged
    
    msg := sprintf(
        "Container '%s' in deployment '%s' must not run in privileged mode",
        [container.name, input.metadata.name]
    )
}

# Deny containers running as root
deny[msg] {
    input.kind == "Deployment"
    container := input.spec.template.spec.containers[_]
    
    not container.securityContext.runAsNonRoot
    
    msg := sprintf(
        "Container '%s' in deployment '%s' must run as non-root user",
        [container.name, input.metadata.name]
    )
}

# Require resource limits
deny[msg] {
    input.kind == "Deployment"
    container := input.spec.template.spec.containers[_]
    
    not container.resources.limits
    
    msg := sprintf(
        "Container '%s' in deployment '%s' must define resource limits",
        [container.name, input.metadata.name]
    )
}

# Require readiness and liveness probes
warn[msg] {
    input.kind == "Deployment"
    container := input.spec.template.spec.containers[_]
    
    not container.livenessProbe
    
    msg := sprintf(
        "Container '%s' in deployment '%s' should define a liveness probe",
        [container.name, input.metadata.name]
    )
}

# Deny latest image tag
deny[msg] {
    input.kind == "Deployment"
    container := input.spec.template.spec.containers[_]
    
    endswith(container.image, ":latest")
    
    msg := sprintf(
        "Container '%s' in deployment '%s' must not use 'latest' tag",
        [container.name, input.metadata.name]
    )
}
```

---

## Azure-Native Policy Services

### 1. Azure Policy Setup

#### Core Azure Policy Definitions

```json
{
  "properties": {
    "displayName": "Fraud Detection System - Required Tags",
    "policyType": "Custom",
    "mode": "Indexed",
    "description": "Enforces required tags on all resources in the fraud detection system",
    "metadata": {
      "category": "Tags",
      "version": "1.0.0"
    },
    "parameters": {
      "tagNames": {
        "type": "Array",
        "metadata": {
          "displayName": "Tag Names",
          "description": "List of required tag names"
        },
        "defaultValue": [
          "Environment",
          "Project",
          "ManagedBy",
          "CostCenter"
        ]
      }
    },
    "policyRule": {
      "if": {
        "anyOf": [
          {
            "field": "[concat('tags[', parameters('tagNames')[0], ']')]",
            "exists": "false"
          },
          {
            "field": "[concat('tags[', parameters('tagNames')[1], ']')]",
            "exists": "false"
          },
          {
            "field": "[concat('tags[', parameters('tagNames')[2], ']')]",
            "exists": "false"
          },
          {
            "field": "[concat('tags[', parameters('tagNames')[3], ']')]",
            "exists": "false"
          }
        ]
      },
      "then": {
        "effect": "deny"
      }
    }
  }
}
```

#### Azure Policy for Storage Security

```json
{
  "properties": {
    "displayName": "Storage accounts should use HTTPS only",
    "policyType": "Custom",
    "mode": "Indexed",
    "description": "Enforce HTTPS traffic for storage accounts in fraud detection system",
    "metadata": {
      "category": "Storage",
      "version": "1.0.0"
    },
    "policyRule": {
      "if": {
        "allOf": [
          {
            "field": "type",
            "equals": "Microsoft.Storage/storageAccounts"
          },
          {
            "field": "Microsoft.Storage/storageAccounts/supportsHttpsTrafficOnly",
            "notEquals": "true"
          }
        ]
      },
      "then": {
        "effect": "deny"
      }
    }
  }
}
```

### 2. Azure Policy as Code with Terraform

```hcl
# File: infrastructure/terraform/modules/azure_policy/main.tf

resource "azurerm_policy_definition" "required_tags" {
  name         = "fraud-detection-required-tags"
  policy_type  = "Custom"
  mode         = "Indexed"
  display_name = "Fraud Detection - Required Tags"
  description  = "Enforces required tags on all resources"

  metadata = jsonencode({
    category = "Tags"
    version  = "1.0.0"
  })

  policy_rule = jsonencode({
    if = {
      anyOf = [
        {
          field  = "tags['Environment']"
          exists = "false"
        },
        {
          field  = "tags['Project']"
          exists = "false"
        },
        {
          field  = "tags['ManagedBy']"
          exists = "false"
        }
      ]
    }
    then = {
      effect = "deny"
    }
  })
}

resource "azurerm_policy_assignment" "required_tags" {
  name                 = "fraud-detection-required-tags-assignment"
  scope                = var.resource_group_id
  policy_definition_id = azurerm_policy_definition.required_tags.id
  description          = "Enforce required tags on fraud detection resources"
  display_name         = "Fraud Detection - Required Tags Assignment"

  metadata = jsonencode({
    assignedBy = "Terraform"
  })
}

resource "azurerm_policy_definition" "storage_https_only" {
  name         = "fraud-detection-storage-https"
  policy_type  = "Custom"
  mode         = "Indexed"
  display_name = "Storage accounts must use HTTPS only"

  policy_rule = jsonencode({
    if = {
      allOf = [
        {
          field  = "type"
          equals = "Microsoft.Storage/storageAccounts"
        },
        {
          field     = "Microsoft.Storage/storageAccounts/supportsHttpsTrafficOnly"
          notEquals = "true"
        }
      ]
    }
    then = {
      effect = "deny"
    }
  })
}

resource "azurerm_policy_assignment" "storage_https_only" {
  name                 = "fraud-detection-storage-https-assignment"
  scope                = var.resource_group_id
  policy_definition_id = azurerm_policy_definition.storage_https_only.id
}

# Initiative (Policy Set) for Fraud Detection
resource "azurerm_policy_set_definition" "fraud_detection_initiative" {
  name         = "fraud-detection-security-initiative"
  policy_type  = "Custom"
  display_name = "Fraud Detection Security Initiative"
  description  = "Collection of security and compliance policies for fraud detection system"

  metadata = jsonencode({
    category = "Security"
    version  = "1.0.0"
  })

  policy_definition_reference {
    policy_definition_id = azurerm_policy_definition.required_tags.id
    parameter_values = jsonencode({})
  }

  policy_definition_reference {
    policy_definition_id = azurerm_policy_definition.storage_https_only.id
    parameter_values = jsonencode({})
  }

  # Reference built-in policies
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/e3576e28-8b17-4677-84c3-db2990658d64"
    reference_id         = "aks-authorized-ip-ranges"
  }

  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/0e246bcf-5f6f-4f87-bc6f-775d4712c7ea"
    reference_id         = "aks-pod-security"
  }
}

resource "azurerm_policy_assignment" "fraud_detection_initiative" {
  name                 = "fraud-detection-initiative-assignment"
  scope                = var.subscription_id
  policy_definition_id = azurerm_policy_set_definition.fraud_detection_initiative.id
  display_name         = "Fraud Detection Security Initiative"
  location             = var.location

  identity {
    type = "SystemAssigned"
  }
}
```

### 3. Azure Defender for Cloud Integration

```hcl
# File: infrastructure/terraform/modules/defender/main.tf

resource "azurerm_security_center_subscription_pricing" "defender_servers" {
  tier          = "Standard"
  resource_type = "VirtualMachines"
}

resource "azurerm_security_center_subscription_pricing" "defender_containers" {
  tier          = "Standard"
  resource_type = "Containers"
}

resource "azurerm_security_center_subscription_pricing" "defender_storage" {
  tier          = "Standard"
  resource_type = "StorageAccounts"
}

resource "azurerm_security_center_subscription_pricing" "defender_keyvault" {
  tier          = "Standard"
  resource_type = "KeyVaults"
}

resource "azurerm_security_center_contact" "security_contact" {
  email               = var.security_contact_email
  phone               = var.security_contact_phone
  alert_notifications = true
  alerts_to_admins    = true
}

# Continuous export to Log Analytics
resource "azurerm_security_center_automation" "export_to_log_analytics" {
  name                = "export-defender-logs"
  location            = var.location
  resource_group_name = var.resource_group_name

  action {
    type              = "loganalytics"
    resource_id       = var.log_analytics_workspace_id
  }

  source {
    event_source = "Alerts"
    rule_set {
      rule {
        property_path  = "properties.metadata.severity"
        operator       = "Equals"
        expected_value = "High"
        property_type  = "String"
      }
    }
  }

  scope {
    description  = "Export high severity alerts to Log Analytics"
    resource_ids = [var.subscription_id]
  }

  enabled = true
}
```

---

## Terraform Integration

### Pipeline Configuration for Terraform Validation

```yaml
# File: pipelines/infrastructure/terraform-validation-pipeline.yml

trigger:
  branches:
    include:
    - main
    - develop
  paths:
    include:
    - infrastructure/terraform/*

variables:
  terraformVersion: '1.6.0'
  workingDirectory: '$(System.DefaultWorkingDirectory)/infrastructure/terraform'

stages:
- stage: Validate
  displayName: 'Policy Validation Stage'
  jobs:
  - job: TerraformValidation
    displayName: 'Terraform Plan & Policy Check'
    pool:
      vmImage: 'ubuntu-latest'
    
    steps:
    # Install Terraform
    - task: TerraformInstaller@0
      displayName: 'Install Terraform'
      inputs:
        terraformVersion: $(terraformVersion)
    
    # Install Conftest
    - task: Bash@3
      displayName: 'Install Conftest'
      inputs:
        targetType: 'inline'
        script: |
          wget https://github.com/open-policy-agent/conftest/releases/download/v0.48.0/conftest_0.48.0_Linux_x86_64.tar.gz
          tar xzf conftest_0.48.0_Linux_x86_64.tar.gz
          sudo mv conftest /usr/local/bin/
          conftest --version
    
    # Install TFLint
    - task: Bash@3
      displayName: 'Install TFLint'
      inputs:
        targetType: 'inline'
        script: |
          curl -s https://raw.githubusercontent.com/terraform-linters/tflint/master/install_linux.sh | bash
          tflint --version
    
    # Terraform Init
    - task: TerraformTaskV4@4
      displayName: 'Terraform Init'
      inputs:
        provider: 'azurerm'
        command: 'init'
        workingDirectory: $(workingDirectory)
        backendServiceArm: 'azure-service-connection'
        backendAzureRmResourceGroupName: 'rg-terraform-state'
        backendAzureRmStorageAccountName: 'stterraformstate'
        backendAzureRmContainerName: 'tfstate'
        backendAzureRmKey: 'fraud-detection.tfstate'
    
    # Terraform Format Check
    - task: Bash@3
      displayName: 'Terraform Format Check'
      inputs:
        targetType: 'inline'
        workingDirectory: $(workingDirectory)
        script: |
          terraform fmt -check -recursive
          if [ $? -ne 0 ]; then
            echo "##vso[task.logissue type=error]Terraform files are not properly formatted"
            exit 1
          fi
    
    # Terraform Validate
    - task: TerraformTaskV4@4
      displayName: 'Terraform Validate'
      inputs:
        provider: 'azurerm'
        command: 'validate'
        workingDirectory: $(workingDirectory)
    
    # TFLint
    - task: Bash@3
      displayName: 'Run TFLint'
      inputs:
        targetType: 'inline'
        workingDirectory: $(workingDirectory)
        script: |
          tflint --init
          tflint --format=junit > tflint-report.xml || true
          tflint
    
    # Terraform Plan
    - task: TerraformTaskV4@4
      displayName: 'Terraform Plan'
      inputs:
        provider: 'azurerm'
        command: 'plan'
        workingDirectory: $(workingDirectory)
        environmentServiceNameAzureRM: 'azure-service-connection'
        commandOptions: '-out=tfplan -var-file="environments/$(Environment).tfvars"'
    
    # Convert Plan to JSON
    - task: Bash@3
      displayName: 'Convert Terraform Plan to JSON'
      inputs:
        targetType: 'inline'
        workingDirectory: $(workingDirectory)
        script: |
          terraform show -json tfplan > tfplan.json
    
    # Run Conftest on Terraform Plan
    - task: Bash@3
      displayName: 'Run Conftest Policy Checks'
      inputs:
        targetType: 'inline'
        workingDirectory: $(workingDirectory)
        script: |
          # Run Conftest with all policies
          conftest test tfplan.json \
            -p $(System.DefaultWorkingDirectory)/policies/terraform \
            --all-namespaces \
            --output json > conftest-results.json || true
          
          # Display results
          cat conftest-results.json | jq '.'
          
          # Check for failures
          FAILURES=$(cat conftest-results.json | jq '[.[] | select(.failures != null) | .failures[]] | length')
          
          if [ "$FAILURES" -gt 0 ]; then
            echo "##vso[task.logissue type=error]Conftest found $FAILURES policy violations"
            cat conftest-results.json | jq -r '.[] | .failures[]? | "ERROR: " + .'
            exit 1
          fi
          
          # Display warnings
          WARNINGS=$(cat conftest-results.json | jq '[.[] | select(.warnings != null) | .warnings[]] | length')
          if [ "$WARNINGS" -gt 0 ]; then
            echo "##vso[task.logissue type=warning]Conftest found $WARNINGS policy warnings"
            cat conftest-results.json | jq -r '.[] | .warnings[]? | "WARNING: " + .'
          fi
    
    # Security Scan with Checkov
    - task: Bash@3
      displayName: 'Run Checkov Security Scan'
      inputs:
        targetType: 'inline'
        workingDirectory: $(workingDirectory)
        script: |
          # Install Checkov
          pip install checkov
          
          # Run Checkov
          checkov -d . \
            --framework terraform \
            --output junitxml \
            --output-file-path checkov-report.xml \
            --soft-fail || true
          
          # Run Checkov with JSON output for detailed analysis
          checkov -d . \
            --framework terraform \
            --output json > checkov-results.json || true
          
          # Check for high severity issues
          HIGH_SEVERITY=$(cat checkov-results.json | jq '[.results.failed_checks[] | select(.check_class contains "HIGH")] | length' || echo 0)
          
          if [ "$HIGH_SEVERITY" -gt 0 ]; then
            echo "##vso[task.logissue type=error]Found $HIGH_SEVERITY high severity security issues"
            cat checkov-results.json | jq -r '.results.failed_checks[] | select(.check_class contains "HIGH") | "HIGH: " + .check_name + " in " + .file_path'
          fi
    
    # Run TFSEC
    - task: Bash@3
      displayName: 'Run tfsec Security Scanner'
      inputs:
        targetType: 'inline'
        workingDirectory: $(workingDirectory)
        script: |
          # Install tfsec
          curl -s https://raw.githubusercontent.com/aquasecurity/tfsec/master/scripts/install_linux.sh | bash
          
          # Run tfsec
          tfsec . \
            --format json \
            --out tfsec-results.json \
            --soft-fail || true
          
          # Check for HIGH/CRITICAL issues
          CRITICAL=$(cat tfsec-results.json | jq '[.results[] | select(.severity == "CRITICAL")] | length')
          HIGH=$(cat tfsec-results.json | jq '[.results[] | select(.severity == "HIGH")] | length')
          
          if [ "$CRITICAL" -gt 0 ] || [ "$HIGH" -gt 0 ]; then
            echo "##vso[task.logissue type=error]Found $CRITICAL critical and $HIGH high severity issues"
            cat tfsec-results.json | jq -r '.results[] | select(.severity == "CRITICAL" or .severity == "HIGH") | .severity + ": " + .description'
            exit 1
          fi
    
    # Publish Test Results
    - task: PublishTestResults@2
      displayName: 'Publish TFLint Results'
      condition: always()
      inputs:
        testResultsFormat: 'JUnit'
        testResultsFiles: '**/tflint-report.xml'
        testRunTitle: 'TFLint Results'
    
    - task: PublishTestResults@2
      displayName: 'Publish Checkov Results'
      condition: always()
      inputs:
        testResultsFormat: 'JUnit'
        testResultsFiles: '**/checkov-report.xml'
        testRunTitle: 'Checkov Security Scan'
    
    # Publish Artifacts
    - task: PublishBuildArtifacts@1
      displayName: 'Publish Policy Check Results'
      condition: always()
      inputs:
        PathtoPublish: '$(workingDirectory)'
        ArtifactName: 'policy-check-results'
        publishLocation: 'Container'

- stage: AzurePolicyCheck
  displayName: 'Azure Policy Compliance Check'
  dependsOn: Validate
  condition: succeeded()
  jobs:
  - job: PolicyCompliance
    displayName: 'Check Azure Policy Compliance'
    pool:
      vmImage: 'ubuntu-latest'
    
    steps:
    - task: AzureCLI@2
      displayName: 'Check Policy Compliance State'
      inputs:
        azureSubscription: 'azure-service-connection'
        scriptType: 'bash'
        scriptLocation: 'inlineScript'
        inlineScript: |
          # Get policy compliance state
          az policy state list \
            --resource-group rg-fraud-detection-$(Environment) \
            --filter "ComplianceState eq 'NonCompliant'" \
            --output json > policy-compliance.json
          
          # Check for non-compliant resources
          NON_COMPLIANT=$(cat policy-compliance.json | jq 'length')
          
          if [ "$NON_COMPLIANT" -gt 0 ]; then
            echo "##vso[task.logissue type=warning]Found $NON_COMPLIANT non-compliant resources"
            cat policy-compliance.json | jq -r '.[] | "Policy: " + .policyDefinitionName + " | Resource: " + .resourceId'
          else
            echo "All resources are compliant with Azure Policies"
          fi
    
    - task: AzureCLI@2
      displayName: 'Get Defender for Cloud Recommendations'
      inputs:
        azureSubscription: 'azure-service-connection'
        scriptType: 'bash'
        scriptLocation: 'inlineScript'
        inlineScript: |
          # Get security recommendations
          az security assessment list \
            --output json > security-recommendations.json
          
          # Filter high severity recommendations
          HIGH_SEVERITY=$(cat security-recommendations.json | jq '[.[] | select(.status.severity == "High")] | length')
          
          if [ "$HIGH_SEVERITY" -gt 0 ]; then
            echo "##vso[task.logissue type=error]Found $HIGH_SEVERITY high severity security recommendations"
            cat security-recommendations.json | jq -r '.[] | select(.status.severity == "High") | "HIGH: " + .displayName'
          fi

- stage: Apply
  displayName: 'Terraform Apply'
  dependsOn: 
    - Validate
    - AzurePolicyCheck
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
  jobs:
  - deployment: TerraformApply
    displayName: 'Apply Terraform Changes'
    pool:
      vmImage: 'ubuntu-latest'
    environment: 'production'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: TerraformTaskV4@4
            displayName: 'Terraform Apply'
            inputs:
              provider: 'azurerm'
              command: 'apply'
              workingDirectory: $(workingDirectory)
              environmentServiceNameAzureRM: 'azure-service-connection'
              commandOptions: 'tfplan'
```

---

## Azure Pipeline Integration

### Kubernetes Deployment with OPA Gatekeeper

```yaml
# File: pipelines/deployment/kubernetes-deployment-pipeline.yml

trigger:
  branches:
    include:
    - main
  paths:
    include:
    - pipelines/deployment/*
    - src/*

variables:
  aksClusterName: 'aks-fraud-detection-prod'
  aksResourceGroup: 'rg-fraud-detection-prod'
  containerRegistry: 'acrfrauddetection.azurecr.io'

stages:
- stage: Build
  displayName: 'Build and Push Image'
  jobs:
  - job: BuildJob
    displayName: 'Build Docker Image'
    pool:
      vmImage: 'ubuntu-latest'
    
    steps:
    - task: Docker@2
      displayName: 'Build and Push Docker Image'
      inputs:
        containerRegistry: 'acr-service-connection'
        repository: 'fraud-decision-service'
        command: 'buildAndPush'
        Dockerfile: 'src/Dockerfile'
        tags: |
          $(Build.BuildId)
          latest

- stage: PolicyValidation
  displayName: 'Validate Kubernetes Manifests'
  dependsOn: Build
  jobs:
  - job: KubernetesValidation
    displayName: 'Validate K8s with OPA'
    pool:
      vmImage: 'ubuntu-latest'
    
    steps:
    # Install Conftest
    - task: Bash@3
      displayName: 'Install Conftest'
      inputs:
        targetType: 'inline'
        script: |
          wget https://github.com/open-policy-agent/conftest/releases/download/v0.48.0/conftest_0.48.0_Linux_x86_64.tar.gz
          tar xzf conftest_0.48.0_Linux_x86_64.tar.gz
          sudo mv conftest /usr/local/bin/
    
    # Update image tag in manifests
    - task: Bash@3
      displayName: 'Update Image Tag'
      inputs:
        targetType: 'inline'
        script: |
          sed -i 's|:latest|:$(Build.BuildId)|g' pipelines/deployment/decision_service_deployment.yaml
    
    # Validate with Conftest
    - task: Bash@3
      displayName: 'Validate Kubernetes Manifests with OPA'
      inputs:
        targetType: 'inline'
        script: |
          # Run Conftest
          conftest test pipelines/deployment/*.yaml \
            -p policies/kubernetes \
            --all-namespaces \
            --output json > k8s-conftest-results.json || true
          
          cat k8s-conftest-results.json | jq '.'
          
          # Check for failures
          FAILURES=$(cat k8s-conftest-results.json | jq '[.[] | select(.failures != null) | .failures[]] | length')
          
          if [ "$FAILURES" -gt 0 ]; then
            echo "##vso[task.logissue type=error]Found $FAILURES policy violations in Kubernetes manifests"
            exit 1
          fi
    
    # Validate with kubeconform
    - task: Bash@3
      displayName: 'Validate Kubernetes Schema'
      inputs:
        targetType: 'inline'
        script: |
          # Install kubeconform
          wget https://github.com/yannh/kubeconform/releases/latest/download/kubeconform-linux-amd64.tar.gz
          tar xf kubeconform-linux-amd64.tar.gz
          sudo mv kubeconform /usr/local/bin/
          
          # Validate
          kubeconform -summary pipelines/deployment/*.yaml
    
    # Security scan with Trivy
    - task: Bash@3
      displayName: 'Scan Image with Trivy'
      inputs:
        targetType: 'inline'
        script: |
          # Install Trivy
          wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
          echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
          sudo apt-get update
          sudo apt-get install trivy
          
          # Scan image
          trivy image \
            --severity HIGH,CRITICAL \
            --format json \
            --output trivy-results.json \
            $(containerRegistry)/fraud-decision-service:$(Build.BuildId)
          
          # Check for vulnerabilities
          CRITICAL=$(cat trivy-results.json | jq '[.Results[].Vulnerabilities[]? | select(.Severity == "CRITICAL")] | length')
          HIGH=$(cat trivy-results.json | jq '[.Results[].Vulnerabilities[]? | select(.Severity == "HIGH")] | length')
          
          echo "Found $CRITICAL critical and $HIGH high severity vulnerabilities"
          
          if [ "$CRITICAL" -gt 0 ]; then
            echo "##vso[task.logissue type=error]Found $CRITICAL critical vulnerabilities"
            exit 1
          fi

- stage: Deploy
  displayName: 'Deploy to AKS'
  dependsOn: PolicyValidation
  condition: succeeded()
  jobs:
  - deployment: DeployToAKS
    displayName: 'Deploy to AKS'
    pool:
      vmImage: 'ubuntu-latest'
    environment: 'production-aks'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: AzureCLI@2
            displayName: 'Get AKS Credentials'
            inputs:
              azureSubscription: 'azure-service-connection'
              scriptType: 'bash'
              scriptLocation: 'inlineScript'
              inlineScript: |
                az aks get-credentials \
                  --resource-group $(aksResourceGroup) \
                  --name $(aksClusterName) \
                  --overwrite-existing
          
          - task: Bash@3
            displayName: 'Verify OPA Gatekeeper is Running'
            inputs:
              targetType: 'inline'
              script: |
                # Check if Gatekeeper is installed
                kubectl get pods -n gatekeeper-system
                
                if [ $? -ne 0 ]; then
                  echo "##vso[task.logissue type=warning]OPA Gatekeeper is not installed. Installing..."
                  kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/master/deploy/gatekeeper.yaml
                  
                  # Wait for Gatekeeper to be ready
                  kubectl wait --for=condition=Ready pods --all -n gatekeeper-system --timeout=300s
                fi
          
          - task: Bash@3
            displayName: 'Apply Gatekeeper Constraints'
            inputs:
              targetType: 'inline'
              script: |
                # Apply constraint templates
                kubectl apply -f policies/kubernetes/gatekeeper/
          
          - task: KubernetesManifest@0
            displayName: 'Deploy to AKS'
            inputs:
              action: 'deploy'
              kubernetesServiceConnection: 'aks-service-connection'
              namespace: 'fraud-detection'
              manifests: |
                pipelines/deployment/decision_service_deployment.yaml
              containers: |
                $(containerRegistry)/fraud-decision-service:$(Build.BuildId)

- stage: PostDeploymentValidation
  displayName: 'Post-Deployment Validation'
  dependsOn: Deploy
  jobs:
  - job: ValidationJob
    displayName: 'Validate Deployment'
    pool:
      vmImage: 'ubuntu-latest'
    
    steps:
    - task: AzureCLI@2
      displayName: 'Run Post-Deployment Checks'
      inputs:
        azureSubscription: 'azure-service-connection'
        scriptType: 'bash'
        scriptLocation: 'inlineScript'
        inlineScript: |
          # Get AKS credentials
          az aks get-credentials \
            --resource-group $(aksResourceGroup) \
            --name $(aksClusterName) \
            --overwrite-existing
          
          # Check deployment status
          kubectl rollout status deployment/fraud-decision-service -n fraud-detection --timeout=5m
          
          # Check for Gatekeeper violations
          echo "Checking for OPA Gatekeeper violations..."
          VIOLATIONS=$(kubectl get constraintpodstatuses -A -o json | jq '[.items[] | select(.status.violations != null)] | length')
          
          if [ "$VIOLATIONS" -gt 0 ]; then
            echo "##vso[task.logissue type=error]Found $VIOLATIONS OPA Gatekeeper violations"
            kubectl get constraintpodstatuses -A -o json | jq '.items[] | select(.status.violations != null)'
            exit 1
          fi
          
          # Check resource usage
          kubectl top pods -n fraud-detection
    
    - task: AzureCLI@2
      displayName: 'Check Azure Policy Compliance'
      inputs:
        azureSubscription: 'azure-service-connection'
        scriptType: 'bash'
        scriptLocation: 'inlineScript'
        inlineScript: |
          # Trigger policy scan
          az policy state trigger-scan \
            --resource-group $(aksResourceGroup) \
            --no-wait
          
          # Wait a bit for scan to complete
          sleep 30
          
          # Check compliance
          az policy state list \
            --resource-group $(aksResourceGroup) \
            --filter "ComplianceState eq 'NonCompliant'" \
            --output table
```

---

## Policy Examples

### OPA Gatekeeper Constraint Templates

```yaml
# File: policies/kubernetes/gatekeeper/constraint-template-required-labels.yaml

apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8srequiredlabels
  annotations:
    description: Requires all resources to have specified labels
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredLabels
      validation:
        openAPIV3Schema:
          type: object
          properties:
            labels:
              type: array
              items:
                type: string
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequiredlabels

        violation[{"msg": msg, "details": {"missing_labels": missing}}] {
          provided := {label | input.review.object.metadata.labels[label]}
          required := {label | label := input.parameters.labels[_]}
          missing := required - provided
          count(missing) > 0
          msg := sprintf("You must provide labels: %v", [missing])
        }
---
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredLabels
metadata:
  name: deployment-must-have-labels
spec:
  match:
    kinds:
      - apiGroups: ["apps"]
        kinds: ["Deployment"]
  parameters:
    labels:
      - "app"
      - "environment"
      - "version"
```

```yaml
# File: policies/kubernetes/gatekeeper/constraint-template-container-limits.yaml

apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8scontainerlimits
  annotations:
    description: Requires containers to have resource limits defined
spec:
  crd:
    spec:
      names:
        kind: K8sContainerLimits
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8scontainerlimits

        violation[{"msg": msg}] {
          container := input.review.object.spec.template.spec.containers[_]
          not container.resources.limits
          msg := sprintf("Container <%v> has no resource limits", [container.name])
        }

        violation[{"msg": msg}] {
          container := input.review.object.spec.template.spec.containers[_]
          not container.resources.requests
          msg := sprintf("Container <%v> has no resource requests", [container.name])
        }
---
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sContainerLimits
metadata:
  name: container-must-have-limits
spec:
  match:
    kinds:
      - apiGroups: ["apps"]
        kinds: ["Deployment"]
```

```yaml
# File: policies/kubernetes/gatekeeper/constraint-template-no-privileged.yaml

apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8spsprivilegedcontainer
  annotations:
    description: Prevents privileged containers
spec:
  crd:
    spec:
      names:
        kind: K8sPSPrivilegedContainer
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8spsprivilegedcontainer

        violation[{"msg": msg}] {
          container := input.review.object.spec.template.spec.containers[_]
          container.securityContext.privileged
          msg := sprintf("Privileged container is not allowed: %v", [container.name])
        }
---
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sPSPrivilegedContainer
metadata:
  name: psp-privileged-container
spec:
  match:
    kinds:
      - apiGroups: ["apps"]
        kinds: ["Deployment", "StatefulSet", "DaemonSet"]
```

---

## Testing and Validation

### Unit Testing OPA Policies

```rego
# File: policies/tests/terraform_test.rego
package terraform.azure.tags_test

import future.keywords

test_required_tags_present {
    result := deny with input as {
        "resource_changes": [{
            "address": "azurerm_storage_account.test",
            "mode": "managed",
            "type": "azurerm_storage_account",
            "change": {
                "after": {
                    "tags": {
                        "Environment": "prod",
                        "Project": "fraud-detection",
                        "ManagedBy": "Terraform",
                        "CostCenter": "engineering"
                    }
                }
            }
        }]
    }
    count(result) == 0
}

test_missing_required_tags {
    result := deny with input as {
        "resource_changes": [{
            "address": "azurerm_storage_account.test",
            "mode": "managed",
            "type": "azurerm_storage_account",
            "change": {
                "after": {
                    "tags": {
                        "Environment": "prod"
                    }
                }
            }
        }]
    }
    count(result) > 0
}
```

### Running Policy Tests Locally

```bash
# File: scripts/test-policies.sh
#!/bin/bash

set -e

echo "Running OPA Policy Tests..."

# Test Terraform policies
echo "Testing Terraform policies..."
conftest verify --policy policies/terraform

# Run unit tests
opa test policies/ -v

# Test Kubernetes policies
echo "Testing Kubernetes policies..."
conftest verify --policy policies/kubernetes

echo "All policy tests passed!"
```

---

## Monitoring and Alerting

### Log Analytics Queries for Policy Violations

```kusto
// Query: Azure Policy Violations
AzureActivity
| where CategoryValue == "Policy"
| where OperationNameValue contains "Microsoft.Authorization/policies"
| where ActivityStatusValue == "Failed"
| project TimeGenerated, Caller, OperationNameValue, Properties
| order by TimeGenerated desc

// Query: OPA Gatekeeper Violations
ContainerLog
| where ContainerName == "gatekeeper-audit"
| where LogEntry contains "violation"
| extend ViolationDetails = parse_json(LogEntry)
| project TimeGenerated, ViolationDetails
| order by TimeGenerated desc

// Query: Non-compliant Resources
policyResources
| where type == "microsoft.policyinsights/policystates"
| where properties.complianceState == "NonCompliant"
| project 
    TimeGenerated = properties.timestamp,
    ResourceId = properties.resourceId,
    PolicyDefinition = properties.policyDefinitionName,
    ComplianceState = properties.complianceState
| order by TimeGenerated desc
```

### Azure Monitor Alerts

```json
{
  "name": "Policy-Violation-Alert",
  "description": "Alert when critical policy violations are detected",
  "severity": 2,
  "enabled": true,
  "scopes": [
    "/subscriptions/{subscription-id}/resourceGroups/rg-fraud-detection-prod"
  ],
  "evaluationFrequency": "PT5M",
  "windowSize": "PT15M",
  "criteria": {
    "allOf": [
      {
        "query": "AzureActivity | where CategoryValue == 'Policy' | where ActivityStatusValue == 'Failed' | summarize count() by bin(TimeGenerated, 5m)",
        "timeAggregation": "Total",
        "operator": "GreaterThan",
        "threshold": 5
      }
    ]
  },
  "actions": [
    {
      "actionGroupId": "/subscriptions/{subscription-id}/resourceGroups/rg-fraud-detection-prod/providers/microsoft.insights/actionGroups/security-team"
    }
  ]
}
```

---

## Best Practices

### 1. Policy Development

- **Start with Audit Mode**: Begin with audit-only policies before enforcing deny
- **Version Control**: Keep all policies in Git with proper versioning
- **Test Thoroughly**: Write unit tests for all policies
- **Documentation**: Document each policy's purpose and remediation steps
- **Progressive Rollout**: Deploy policies to dev → staging → production

### 2. Policy Organization

- **Namespace Separation**: Use clear namespaces (e.g., `terraform.azure.security`)
- **Modular Policies**: Keep policies focused and modular
- **Reusable Functions**: Create helper functions for common checks
- **Clear Naming**: Use descriptive names for policies and rules

### 3. Integration Strategy

- **Fail Fast**: Run policy checks early in the pipeline
- **Multiple Tools**: Use complementary tools (OPA, Azure Policy, Checkov)
- **Automated Remediation**: Provide suggestions or automated fixes
- **Continuous Monitoring**: Monitor compliance post-deployment

### 4. Performance Considerations

- **Optimize Queries**: Keep OPA queries efficient
- **Caching**: Cache policy decisions when appropriate
- **Parallel Execution**: Run independent checks in parallel
- **Resource Limits**: Set appropriate timeouts and resource limits

### 5. Security

- **Policy as Code Review**: Treat policies like application code with reviews
- **Least Privilege**: Grant minimal permissions needed for policy enforcement
- **Audit Logging**: Log all policy decisions and violations
- **Regular Updates**: Keep policy engines and definitions updated

---

## Appendix

### A. Useful Commands

```bash
# Test OPA policy locally
opa test policies/ -v

# Run Conftest on Terraform plan
terraform plan -out=tfplan
terraform show -json tfplan > tfplan.json
conftest test tfplan.json -p policies/terraform

# Check Azure Policy compliance
az policy state list --filter "ComplianceState eq 'NonCompliant'"

# Install OPA Gatekeeper
kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/master/deploy/gatekeeper.yaml

# Check Gatekeeper constraints
kubectl get constraints
kubectl describe constraint <constraint-name>

# View Gatekeeper violations
kubectl get constraintpodstatuses -A
```

### B. Additional Resources

- [Open Policy Agent Documentation](https://www.openpolicyagent.org/docs/latest/)
- [Conftest Documentation](https://www.conftest.dev/)
- [OPA Gatekeeper](https://open-policy-agent.github.io/gatekeeper/)
- [Azure Policy Documentation](https://docs.microsoft.com/azure/governance/policy/)
- [Terraform Compliance](https://terraform-compliance.com/)
- [Checkov Documentation](https://www.checkov.io/)

### C. Tool Comparison

| Tool | Use Case | Pros | Cons |
|------|----------|------|------|
| OPA/Conftest | Pre-deployment validation | Flexible, language-agnostic | Requires policy development |
| Azure Policy | Runtime governance | Native integration, managed | Azure-specific |
| OPA Gatekeeper | Kubernetes admission control | Real-time enforcement | K8s only |
| Checkov | Security scanning | Pre-built checks | Limited customization |
| TFSec | Terraform security | Fast, easy to use | Terraform-specific |
| TFLint | Terraform linting | Catches common errors | Basic checks only |

---

## Conclusion

Implementing Policy-as-Code with OPA and Azure-native services provides comprehensive governance and compliance for your fraud detection system. The multi-layered approach ensures:

- **Pre-deployment validation** catches issues before they reach production
- **Runtime enforcement** maintains compliance continuously
- **Automated remediation** reduces manual intervention
- **Comprehensive audit trails** for compliance reporting

Regular review and updates of policies ensure they evolve with your infrastructure and security requirements.

