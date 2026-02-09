# Helm Chart Design: Todo App

**Feature**: 001-k8s-deployment
**Date**: 2026-02-08
**Purpose**: Detailed Helm chart structure and template specifications

## Chart Overview

**Chart Name**: todo-app
**Chart Version**: 0.1.0
**App Version**: 1.0.0
**Description**: Cloud-native Todo AI Chatbot with Next.js frontend and FastAPI backend

## Chart Structure

```
todo-app/
├── Chart.yaml                 # Chart metadata
├── values.yaml                # Default configuration values
├── values-dev.yaml            # Development overrides
├── .helmignore                # Files to exclude from chart
├── templates/
│   ├── _helpers.tpl           # Template helper functions
│   ├── deployment-frontend.yaml
│   ├── deployment-backend.yaml
│   ├── service-frontend.yaml
│   ├── service-backend.yaml
│   ├── ingress.yaml
│   ├── secrets.yaml
│   ├── configmap.yaml
│   └── NOTES.txt             # Post-install instructions
└── README.md                  # Chart documentation
```

## Chart.yaml

```yaml
apiVersion: v2
name: todo-app
description: Cloud-native Todo AI Chatbot with Kubernetes deployment
type: application
version: 0.1.0
appVersion: "1.0.0"
keywords:
  - todo
  - ai
  - chatbot
  - nextjs
  - fastapi
maintainers:
  - name: Phase IV Team
    email: team@example.com
sources:
  - https://github.com/example/phase04
```

## values.yaml

```yaml
# Global configuration
global:
  environment: production
  imagePullPolicy: Never  # Use local images in Minikube

# Frontend configuration
frontend:
  enabled: true
  name: frontend

  image:
    repository: todo-frontend
    tag: latest
    pullPolicy: Never

  replicas: 1

  service:
    type: ClusterIP
    port: 3000
    targetPort: 3000

  resources:
    requests:
      memory: "256Mi"
      cpu: "200m"
    limits:
      memory: "512Mi"
      cpu: "500m"

  probes:
    readiness:
      enabled: true
      path: /
      initialDelaySeconds: 10
      periodSeconds: 5
      timeoutSeconds: 3
      successThreshold: 1
      failureThreshold: 3
    liveness:
      enabled: true
      path: /
      initialDelaySeconds: 30
      periodSeconds: 10
      timeoutSeconds: 3
      successThreshold: 1
      failureThreshold: 3

  env:
    # API URL for frontend to call backend
    apiUrl: "http://backend:8000"

# Backend configuration
backend:
  enabled: true
  name: backend

  image:
    repository: todo-backend
    tag: latest
    pullPolicy: Never

  replicas: 1

  service:
    type: ClusterIP
    port: 8000
    targetPort: 8000

  resources:
    requests:
      memory: "512Mi"
      cpu: "300m"
    limits:
      memory: "1Gi"
      cpu: "1000m"

  probes:
    readiness:
      enabled: true
      path: /api/health
      initialDelaySeconds: 10
      periodSeconds: 5
      timeoutSeconds: 3
      successThreshold: 1
      failureThreshold: 3
    liveness:
      enabled: true
      path: /api/health
      initialDelaySeconds: 30
      periodSeconds: 10
      timeoutSeconds: 3
      successThreshold: 1
      failureThreshold: 3

  env:
    environment: production

# Ingress configuration
ingress:
  enabled: true
  className: nginx
  host: todo.local
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
  paths:
    - path: /api
      pathType: Prefix
      backend: backend
      port: 8000
    - path: /
      pathType: Prefix
      backend: frontend
      port: 3000

# Secrets configuration (provided at install time)
secrets:
  # Database connection string
  databaseUrl: ""
  # Better Auth JWT secret
  betterAuthSecret: ""
  # Cohere API key
  cohereApiKey: ""

# ConfigMap configuration
config:
  environment: production
  logLevel: info
```

## values-dev.yaml

```yaml
# Development overrides
global:
  environment: development

frontend:
  replicas: 1
  resources:
    requests:
      memory: "128Mi"
      cpu: "100m"
    limits:
      memory: "256Mi"
      cpu: "250m"

backend:
  replicas: 1
  resources:
    requests:
      memory: "256Mi"
      cpu: "150m"
    limits:
      memory: "512Mi"
      cpu: "500m"
  env:
    environment: development

config:
  environment: development
  logLevel: debug
```

## Template: _helpers.tpl

```yaml
{{/*
Expand the name of the chart.
*/}}
{{- define "todo-app.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "todo-app.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "todo-app.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "todo-app.labels" -}}
helm.sh/chart: {{ include "todo-app.chart" . }}
{{ include "todo-app.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "todo-app.selectorLabels" -}}
app.kubernetes.io/name: {{ include "todo-app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Frontend labels
*/}}
{{- define "todo-app.frontend.labels" -}}
{{ include "todo-app.labels" . }}
app.kubernetes.io/component: frontend
{{- end }}

{{/*
Frontend selector labels
*/}}
{{- define "todo-app.frontend.selectorLabels" -}}
{{ include "todo-app.selectorLabels" . }}
app.kubernetes.io/component: frontend
{{- end }}

{{/*
Backend labels
*/}}
{{- define "todo-app.backend.labels" -}}
{{ include "todo-app.labels" . }}
app.kubernetes.io/component: backend
{{- end }}

{{/*
Backend selector labels
*/}}
{{- define "todo-app.backend.selectorLabels" -}}
{{ include "todo-app.selectorLabels" . }}
app.kubernetes.io/component: backend
{{- end }}
```

## Template: deployment-frontend.yaml

```yaml
{{- if .Values.frontend.enabled }}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "todo-app.fullname" . }}-frontend
  labels:
    {{- include "todo-app.frontend.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.frontend.replicas }}
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      {{- include "todo-app.frontend.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "todo-app.frontend.selectorLabels" . | nindent 8 }}
    spec:
      containers:
      - name: {{ .Values.frontend.name }}
        image: "{{ .Values.frontend.image.repository }}:{{ .Values.frontend.image.tag }}"
        imagePullPolicy: {{ .Values.frontend.image.pullPolicy }}
        ports:
        - name: http
          containerPort: {{ .Values.frontend.service.targetPort }}
          protocol: TCP
        env:
        - name: NEXT_PUBLIC_API_URL
          value: {{ .Values.frontend.env.apiUrl | quote }}
        - name: NODE_ENV
          value: {{ .Values.global.environment | quote }}
        resources:
          {{- toYaml .Values.frontend.resources | nindent 10 }}
        {{- if .Values.frontend.probes.readiness.enabled }}
        readinessProbe:
          httpGet:
            path: {{ .Values.frontend.probes.readiness.path }}
            port: http
          initialDelaySeconds: {{ .Values.frontend.probes.readiness.initialDelaySeconds }}
          periodSeconds: {{ .Values.frontend.probes.readiness.periodSeconds }}
          timeoutSeconds: {{ .Values.frontend.probes.readiness.timeoutSeconds }}
          successThreshold: {{ .Values.frontend.probes.readiness.successThreshold }}
          failureThreshold: {{ .Values.frontend.probes.readiness.failureThreshold }}
        {{- end }}
        {{- if .Values.frontend.probes.liveness.enabled }}
        livenessProbe:
          httpGet:
            path: {{ .Values.frontend.probes.liveness.path }}
            port: http
          initialDelaySeconds: {{ .Values.frontend.probes.liveness.initialDelaySeconds }}
          periodSeconds: {{ .Values.frontend.probes.liveness.periodSeconds }}
          timeoutSeconds: {{ .Values.frontend.probes.liveness.timeoutSeconds }}
          successThreshold: {{ .Values.frontend.probes.liveness.successThreshold }}
          failureThreshold: {{ .Values.frontend.probes.liveness.failureThreshold }}
        {{- end }}
{{- end }}
```

## Template: deployment-backend.yaml

```yaml
{{- if .Values.backend.enabled }}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "todo-app.fullname" . }}-backend
  labels:
    {{- include "todo-app.backend.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.backend.replicas }}
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      {{- include "todo-app.backend.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "todo-app.backend.selectorLabels" . | nindent 8 }}
    spec:
      containers:
      - name: {{ .Values.backend.name }}
        image: "{{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag }}"
        imagePullPolicy: {{ .Values.backend.image.pullPolicy }}
        ports:
        - name: http
          containerPort: {{ .Values.backend.service.targetPort }}
          protocol: TCP
        envFrom:
        - secretRef:
            name: {{ include "todo-app.fullname" . }}-secrets
        - configMapRef:
            name: {{ include "todo-app.fullname" . }}-config
        resources:
          {{- toYaml .Values.backend.resources | nindent 10 }}
        {{- if .Values.backend.probes.readiness.enabled }}
        readinessProbe:
          httpGet:
            path: {{ .Values.backend.probes.readiness.path }}
            port: http
          initialDelaySeconds: {{ .Values.backend.probes.readiness.initialDelaySeconds }}
          periodSeconds: {{ .Values.backend.probes.readiness.periodSeconds }}
          timeoutSeconds: {{ .Values.backend.probes.readiness.timeoutSeconds }}
          successThreshold: {{ .Values.backend.probes.readiness.successThreshold }}
          failureThreshold: {{ .Values.backend.probes.readiness.failureThreshold }}
        {{- end }}
        {{- if .Values.backend.probes.liveness.enabled }}
        livenessProbe:
          httpGet:
            path: {{ .Values.backend.probes.liveness.path }}
            port: http
          initialDelaySeconds: {{ .Values.backend.probes.liveness.initialDelaySeconds }}
          periodSeconds: {{ .Values.backend.probes.liveness.periodSeconds }}
          timeoutSeconds: {{ .Values.backend.probes.liveness.timeoutSeconds }}
          successThreshold: {{ .Values.backend.probes.liveness.successThreshold }}
          failureThreshold: {{ .Values.backend.probes.liveness.failureThreshold }}
        {{- end }}
{{- end }}
```

## Template: service-frontend.yaml

```yaml
{{- if .Values.frontend.enabled }}
apiVersion: v1
kind: Service
metadata:
  name: {{ include "todo-app.fullname" . }}-frontend
  labels:
    {{- include "todo-app.frontend.labels" . | nindent 4 }}
spec:
  type: {{ .Values.frontend.service.type }}
  ports:
  - port: {{ .Values.frontend.service.port }}
    targetPort: {{ .Values.frontend.service.targetPort }}
    protocol: TCP
    name: http
  selector:
    {{- include "todo-app.frontend.selectorLabels" . | nindent 4 }}
{{- end }}
```

## Template: service-backend.yaml

```yaml
{{- if .Values.backend.enabled }}
apiVersion: v1
kind: Service
metadata:
  name: {{ include "todo-app.fullname" . }}-backend
  labels:
    {{- include "todo-app.backend.labels" . | nindent 4 }}
spec:
  type: {{ .Values.backend.service.type }}
  ports:
  - port: {{ .Values.backend.service.port }}
    targetPort: {{ .Values.backend.service.targetPort }}
    protocol: TCP
    name: http
  selector:
    {{- include "todo-app.backend.selectorLabels" . | nindent 4 }}
{{- end }}
```

## Template: ingress.yaml

```yaml
{{- if .Values.ingress.enabled }}
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ include "todo-app.fullname" . }}
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
  {{- with .Values.ingress.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
spec:
  ingressClassName: {{ .Values.ingress.className }}
  rules:
  - host: {{ .Values.ingress.host }}
    http:
      paths:
      {{- range .Values.ingress.paths }}
      - path: {{ .path }}
        pathType: {{ .pathType }}
        backend:
          service:
            name: {{ include "todo-app.fullname" $ }}-{{ .backend }}
            port:
              number: {{ .port }}
      {{- end }}
{{- end }}
```

## Template: secrets.yaml

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: {{ include "todo-app.fullname" . }}-secrets
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
type: Opaque
data:
  DATABASE_URL: {{ .Values.secrets.databaseUrl | b64enc | quote }}
  BETTER_AUTH_SECRET: {{ .Values.secrets.betterAuthSecret | b64enc | quote }}
  COHERE_API_KEY: {{ .Values.secrets.cohereApiKey | b64enc | quote }}
```

## Template: configmap.yaml

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "todo-app.fullname" . }}-config
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
data:
  ENVIRONMENT: {{ .Values.config.environment | quote }}
  LOG_LEVEL: {{ .Values.config.logLevel | quote }}
```

## Template: NOTES.txt

```
Thank you for installing {{ .Chart.Name }}!

Your release is named {{ .Release.Name }}.

To access your application:

{{- if .Values.ingress.enabled }}
1. Add the following entry to your /etc/hosts file:
   127.0.0.1 {{ .Values.ingress.host }}

2. Access the application at:
   http://{{ .Values.ingress.host }}

3. API endpoints are available at:
   http://{{ .Values.ingress.host }}/api
{{- else }}
1. Get the frontend URL by running:
   kubectl port-forward svc/{{ include "todo-app.fullname" . }}-frontend 3000:3000

2. Get the backend URL by running:
   kubectl port-forward svc/{{ include "todo-app.fullname" . }}-backend 8000:8000
{{- end }}

To check the status of your deployment:
  kubectl get pods -l "app.kubernetes.io/instance={{ .Release.Name }}"

To view logs:
  kubectl logs -l "app.kubernetes.io/instance={{ .Release.Name }}" -f

For more information, visit: https://github.com/example/phase04
```

## .helmignore

```
# Patterns to ignore when building packages
.git/
.gitignore
.DS_Store
*.swp
*.bak
*.tmp
*.orig
*~
.project
.idea/
*.tmproj
.vscode/
```

## Installation Examples

### Basic Installation

```bash
helm install todo-app ./infra/helm/todo-app \
  --set secrets.betterAuthSecret="your-secret-here" \
  --set secrets.cohereApiKey="your-api-key-here" \
  --set secrets.databaseUrl="postgresql://..."
```

### Installation with Custom Values

```bash
helm install todo-app ./infra/helm/todo-app \
  --values ./infra/helm/todo-app/values-dev.yaml \
  --set secrets.betterAuthSecret="your-secret-here" \
  --set secrets.cohereApiKey="your-api-key-here" \
  --set secrets.databaseUrl="postgresql://..."
```

### Dry Run (Test Without Installing)

```bash
helm install todo-app ./infra/helm/todo-app \
  --dry-run --debug \
  --set secrets.betterAuthSecret="test" \
  --set secrets.cohereApiKey="test" \
  --set secrets.databaseUrl="test"
```

### Upgrade Existing Release

```bash
helm upgrade todo-app ./infra/helm/todo-app \
  --set secrets.betterAuthSecret="your-secret-here" \
  --set secrets.cohereApiKey="your-api-key-here" \
  --set secrets.databaseUrl="postgresql://..."
```

### Rollback to Previous Version

```bash
# List revisions
helm history todo-app

# Rollback to specific revision
helm rollback todo-app 1
```

### Uninstall Release

```bash
helm uninstall todo-app
```

## Validation and Testing

### Lint Chart

```bash
helm lint ./infra/helm/todo-app
```

### Template Rendering

```bash
helm template todo-app ./infra/helm/todo-app \
  --set secrets.betterAuthSecret="test" \
  --set secrets.cohereApiKey="test" \
  --set secrets.databaseUrl="test"
```

### Verify Installation

```bash
# Check release status
helm status todo-app

# List all releases
helm list

# Get release values
helm get values todo-app

# Get release manifest
helm get manifest todo-app
```

## Customization Guide

### Changing Resource Limits

Edit `values.yaml`:
```yaml
frontend:
  resources:
    requests:
      memory: "512Mi"  # Increased from 256Mi
      cpu: "400m"      # Increased from 200m
```

### Adding Environment Variables

Edit `values.yaml`:
```yaml
backend:
  env:
    environment: production
    customVar: "custom-value"  # Add new variable
```

Update `deployment-backend.yaml` to include new env vars.

### Enabling Multiple Replicas

Edit `values.yaml`:
```yaml
frontend:
  replicas: 3  # Increased from 1

backend:
  replicas: 3  # Increased from 1
```

### Changing Ingress Host

Edit `values.yaml`:
```yaml
ingress:
  host: myapp.local  # Changed from todo.local
```

Update `/etc/hosts` accordingly.

## Best Practices

1. **Never commit secrets to values.yaml** - Always use --set flags or external secret management
2. **Use values-dev.yaml for development** - Keep production values in values.yaml
3. **Test with dry-run first** - Validate templates before actual installation
4. **Version your charts** - Increment version in Chart.yaml for each change
5. **Document customizations** - Update README.md with any custom configurations
6. **Use semantic versioning** - Follow semver for chart versions
7. **Validate with lint** - Run helm lint before committing changes
8. **Keep templates simple** - Avoid complex logic in templates, use values.yaml

## Troubleshooting

### Chart fails to install

```bash
# Check template rendering
helm template todo-app ./infra/helm/todo-app --debug

# Check for syntax errors
helm lint ./infra/helm/todo-app
```

### Pods not starting

```bash
# Check pod status
kubectl get pods

# Describe pod for events
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>
```

### Ingress not working

```bash
# Check ingress status
kubectl get ingress

# Describe ingress
kubectl describe ingress <ingress-name>

# Check ingress controller logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx
```

### Secrets not loading

```bash
# Check secret exists
kubectl get secret <secret-name>

# Decode secret values
kubectl get secret <secret-name> -o jsonpath='{.data.DATABASE_URL}' | base64 -d
```
