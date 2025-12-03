# File: policies/kubernetes/security.rego
}
    )
        [input.metadata.name]
        "Deployment '%s' should define pod-level securityContext",
    msg := sprintf(

    not input.spec.template.spec.securityContext
    input.kind == "Deployment"
warn[msg] {
# Require security context at pod level

}
    )
        [input.metadata.name]
        "Deployment '%s' must not use host PID namespace (hostPID: false)",
    msg := sprintf(

    input.spec.template.spec.hostPID
    input.kind == "Deployment"
deny[msg] {
# Deny host PID namespace

}
    )
        [input.metadata.name]
        "Deployment '%s' must not use host network (hostNetwork: false)",
    msg := sprintf(

    input.spec.template.spec.hostNetwork
    input.kind == "Deployment"
deny[msg] {
# Deny host network access

}
    )
        [container.name, input.metadata.name]
        "Container '%s' in deployment '%s' should use read-only root filesystem (securityContext.readOnlyRootFilesystem: true)",
    msg := sprintf(

    not container.securityContext.readOnlyRootFilesystem

    container := input.spec.template.spec.containers[_]
    input.kind == "Deployment"
warn[msg] {
# Ensure read-only root filesystem

}
    )
        [container.name, input.metadata.name]
        "Container '%s' in deployment '%s' should explicitly set imagePullPolicy",
    msg := sprintf(

    not container.imagePullPolicy

    container := input.spec.template.spec.containers[_]
    input.kind == "Deployment"
warn[msg] {
# Deny containers without image pull policy

}
    )
        [container.name, input.metadata.name]
        "Container '%s' in deployment '%s' must not use 'latest' tag. Use specific version tags for reproducibility.",
    msg := sprintf(

    endswith(container.image, ":latest")

    container := input.spec.template.spec.containers[_]
    input.kind == "Deployment"
deny[msg] {
# Deny latest image tag

}
    )
        [container.name, input.metadata.name]
        "Container '%s' in deployment '%s' should define a liveness probe",
    msg := sprintf(

    not container.livenessProbe

    container := input.spec.template.spec.containers[_]
    input.kind == "Deployment"
warn[msg] {
# Require liveness probes

}
    )
        [container.name, input.metadata.name]
        "Container '%s' in deployment '%s' should define a readiness probe",
    msg := sprintf(

    not container.readinessProbe

    container := input.spec.template.spec.containers[_]
    input.kind == "Deployment"
warn[msg] {
# Require readiness probes

}
    )
        [container.name, input.metadata.name]
        "Container '%s' in deployment '%s' must define resource requests (cpu and memory)",
    msg := sprintf(

    not container.resources.requests

    container := input.spec.template.spec.containers[_]
    input.kind == "Deployment"
deny[msg] {
# Require resource requests

}
    )
        [container.name, input.metadata.name]
        "Container '%s' in deployment '%s' must define resource limits (cpu and memory)",
    msg := sprintf(

    not container.resources.limits

    container := input.spec.template.spec.containers[_]
    input.kind == "Deployment"
deny[msg] {
# Require resource limits

}
    )
        [container.name, input.metadata.name]
        "Container '%s' in deployment '%s' must run as non-root user (set securityContext.runAsNonRoot: true)",
    msg := sprintf(

    not container.securityContext.runAsNonRoot

    container := input.spec.template.spec.containers[_]
    input.kind == "Deployment"
deny[msg] {
# Deny containers running as root

}
    )
        [container.name, input.metadata.name]
        "Container '%s' in deployment '%s' must not run in privileged mode",
    msg := sprintf(

    container.securityContext.privileged
    container := input.spec.template.spec.containers[_]
    input.kind == "Deployment"
deny[msg] {
# Deny privileged containers

import future.keywords

package kubernetes.security

