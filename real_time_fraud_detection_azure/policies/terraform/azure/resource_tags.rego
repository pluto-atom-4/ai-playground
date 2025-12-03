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
        "azurerm_servicebus_namespace",
        "azurerm_virtual_network",
        "azurerm_subnet",
        "azurerm_network_security_group",
        "azurerm_application_insights",
        "azurerm_log_analytics_workspace"
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

# Validate tag values format
deny[msg] {
    resource := input.resource_changes[_]
    resource.mode == "managed"
    resource_supports_tags(resource.type)

    tags := object.get(resource.change.after, "tags", {})
    environment := object.get(tags, "Environment", "")

    # Environment must be one of: dev, staging, prod
    count(environment) > 0
    not environment in ["dev", "staging", "prod"]

    msg := sprintf(
        "Resource '%s' has invalid Environment tag value '%s'. Must be one of: dev, staging, prod",
        [resource.address, environment]
    )
}

