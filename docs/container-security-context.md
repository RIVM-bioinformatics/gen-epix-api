# Gen-Epix API Container Security Context Analyse

Deze analyse bekijkt de security context eisen voor de Gen-Epix API container gebaseerd op de Dockerfile en applicatie configuratie.

## Huidige Dockerfile Security Setup

### Non-privileged User
De container maakt een dedicated non-privileged user aan:
```dockerfile
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser
```

**Belangrijk:** De Dockerfile definieert wel de user maar activeert deze **NIET** met een `USER` instructie!

### Applicatie Eisen

#### Netwerk
- **Port:** 8000 (HTTP)
- **Host binding:** 0.0.0.0 (alle interfaces)
- **Protocol:** HTTP/HTTPS (SSL cert support aanwezig)

#### Database Connectiviteit
- **ODBC drivers:** Microsoft SQL Server (msodbcsql18)
- **Database types:** Azure SQL, SQL Server, SQLite
- **Connection pooling:** Ja (SQLAlchemy)
- **Retry logic:** Ja (voor Azure SQL autopause)

## Security Context Aanbevelingen

### Kubernetes Security Context

```yaml
securityContext:
  # Container level
  allowPrivilegeEscalation: false
  capabilities:
    drop:
      - ALL
  readOnlyRootFilesystem: true
  runAsNonRoot: true
  runAsUser: 10001
  runAsGroup: 10001
  seccompProfile:
    type: RuntimeDefault

# Pod level security context
podSecurityContext:
  runAsNonRoot: true
  runAsUser: 10001
  runAsGroup: 10001
  fsGroup: 10001
  seccompProfile:
    type: RuntimeDefault
```

### Volume Mounts (Read-Only Root Filesystem)

Omdat `readOnlyRootFilesystem: true`, zijn de volgende writable volumes nodig:

```yaml
volumeMounts:
  # Tijdelijke bestanden
  - name: tmp-volume
    mountPath: /tmp
  - name: var-tmp-volume  
    mountPath: /var/tmp
  
  # Python cache (indien nodig)
  - name: python-cache
    mountPath: /home/appuser/.cache
    
  # Applicatie logs (indien file logging)
  - name: logs-volume
    mountPath: /app/logs
    
  # ODBC configuratie (als je de SECLEVEL wil overschrijven)
  - name: odbc-config
    mountPath: /etc/odbcinst.ini
    subPath: odbcinst.ini

volumes:
  - name: tmp-volume
    emptyDir: {}
  - name: var-tmp-volume
    emptyDir: {}
  - name: python-cache
    emptyDir: {}
  - name: logs-volume
    emptyDir: {}
  - name: odbc-config
    configMap:
      name: odbc-config
```

### ODBC Configuratie ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: odbc-config
data:
  odbcinst.ini: |
    [ODBC Driver 18 for SQL Server]
    Description=Microsoft ODBC Driver 18 for SQL Server
    Driver=/opt/microsoft/msodbcsql18/lib64/libmsodbcsql-18.3.so.2.1
    Threading=1
    SECLEVEL=0
```

## Dockerfile Aanpassingen

De Dockerfile mist de `USER` instructie. Voeg toe voor productie:

```dockerfile
# Na de COPY instructie, voor CMD
USER appuser

# Of als je de UID wil gebruiken
USER 10001:10001
```

## Applicatie Specifieke Eisen

### Geen Speciale Capabilities
- De applicatie heeft geen speciale Linux capabilities nodig
- Draait volledig in userspace (Python/FastAPI)
- Geen directe filesystem/device access nodig

### Netwerk Toegang
- Uitgaande toegang tot databases (Azure SQL, SQL Server)
- Inkomende toegang op poort 8000
- Mogelijk uitgaande HTTPS voor authenticatie (IDP)

### File System Toegang
- **Read-only:** Applicatie code, configuratie, certificaten
- **Write:** Alleen tijdelijke bestanden en cache directories

## Monitoring & Logging

De applicatie logt naar stdout/stderr (zie logging.yaml), wat perfect werkt met:
- `readOnlyRootFilesystem: true`
- Container log aggregation (Fluentd, etc.)
- Kubernetes log collection

## Environment Variabelen

Belangrijke environment variabelen voor configuratie:
```yaml
env:
  - name: SETTINGS_DIR
    value: "/app/gen_epix/casedb/config"  # Of andere service
  - name: SECRETS_DIR
    valueFrom:
      secretKeyRef:
        name: gen-epix-secrets
        key: secrets-dir
  - name: LOGGING_CONFIG_FILE  
    value: "/app/gen_epix/casedb/config/logging.yaml"
```

## Pod Security Standards

Deze configuratie voldoet aan **Restricted** Pod Security Standard:
- ✅ Non-root user (UID 10001)
- ✅ No privilege escalation
- ✅ Read-only root filesystem
- ✅ Dropped all capabilities
- ✅ Seccomp enabled

## Samenvatting

De Gen-Epix API heeft **minimale security eisen**:
1. **Fix Dockerfile:** Voeg `USER 10001` toe
2. **Read-only root filesystem:** Mogelijk met tmp volumes
3. **Non-root user:** Reeds geconfigureerd (UID 10001)
4. **No special capabilities:** Alleen standaard network/compute
5. **Standard security context:** Restricted Pod Security Standard compatible

De applicatie is goed ontworpen voor secure container deployment!