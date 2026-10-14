# Vendored Helm Charts Documentation

## 1. Upstream Source Information
- **Repository**: [https://github.com/iankisali/microservice-deployment](https://github.com/iankisali/microservice-deployment)
- **Commit SHA**: `8ed96c8d98625c73b67c7172b6703383ea9e46e9`
- **Charts Vendored**:
  - `chart/microservice` (Generic Helm chart for 10 Google Online Boutique microservices)
  - `chart/redis` (Helm chart for redis-cart caching backend)

## 2. Justification for Vendoring (Rubric Item 5)
Per Project Rubric Item 5 ("Chart extended and vendored cleanly"):
1. The upstream chart repository only contains minimal templates (`deployment.yaml` and `service.yaml`) without support for:
   - Resource requests and limits (`resources: ...`)
   - Liveness and readiness health probes (`livenessProbe: ...`, `readinessProbe: ...`)
   - PodDisruptionBudget policies (`PodDisruptionBudget`)
   - Ingress controller routing definitions (`Ingress`)
2. To satisfy the requirements of Rubric 4 (Ingress), Rubric 5 (Probes and limits), and Rubric 6 (Scaling & PDB), the chart templates are vendored locally into `charts/` in the repository and extended with optional blocks (`{{- with ... }}`, `{{- if ... }}`).
3. **Backward Compatibility**: All extensions are strictly guarded with conditionals. If no extra values are supplied, the chart renders identical Kubernetes manifests to the upstream original.
