# API Endpoints Deep Dive

## 1. API Surface Architecture Overview
The endpoint surface is implemented as a FastAPI shell over a command-based application core. Routers are mounted under a versioned prefix (`/v1`), while the root path (`/`) redirects to the configured default route. This means transport-level routing and command execution are intentionally separate concerns. (Source: `gen_epix/commondb/app_setup.py#L27-L35`; Source: `gen_epix/commondb/app_setup.py#L115-L126`; Source: `gen_epix/casedb/config/settings.toml#L8-L9`; Source: `gen_epix/casedb/config/settings.toml#L42-L43`)

OpenAPI output is produced from this assembled app and enriched with app-specific schema metadata at startup, so the contract document reflects the runtime router composition for that app variant. (Source: `gen_epix/casedb/app.py#L11-L17`; Source: `gen_epix/casedb/app.py#L33-L45`; Source: `gen_epix/commondb/app_setup.py#L129-L138`)

```text
HTTP request
  -> FastAPI route (/v1/*)
  -> endpoint function
  -> app.handle(command)
  -> response serialized by route schema/OpenAPI contract
```
(Source: `gen_epix/commondb/app_setup.py#L115-L126`; Source: `gen_epix/commondb/api/auth.py#L24-L34`; Source: `gen_epix/commondb/api/system.py#L76-L90`; Source: `gen_epix/fastapp/app.py#L309-L327`)

Developer Note: this architecture explains why many endpoints look repetitive in the OpenAPI document; much of the surface is generated from model permissions rather than handwritten route functions. (Source: `gen_epix/commondb/api/auth.py#L39-L46`; Source: `gen_epix/commondb/api/system.py#L133-L141`; Source: `gen_epix/fastapp/api/crud_endpoint_generator.py#L759-L835`)

## 2. Contract Authority and Scope
For this deep dive, `docs/openapi.json` is the contract authority. The artifact identifies itself as `Gen-EpiX casedb` and defines operations through the `paths` object. (Source: `docs/openapi.json#L4-L4`; Source: `docs/openapi.json#L18-L18`)

This specific artifact contains tags for `auth`, `organization`, `system`, `ontology`, `geo`, `subject`, `case`, and `abac`, which represent shared/common routes plus casedb-specific routes in this app context. (Source: `docs/openapi.json#L21-L23`; Source: `docs/openapi.json#L47-L49`; Source: `docs/openapi.json#L9417-L9417`; Source: `docs/openapi.json#L10235-L10235`; Source: `docs/openapi.json#L14392-L14392`; Source: `docs/openapi.json#L17120-L17120`; Source: `docs/openapi.json#L18484-L18484`; Source: `docs/openapi.json#L33175-L33175`)

`SEQDB` and `OMOPDB` tags are not evidenced in this file, so endpoint coverage for those app surfaces is `<TBF elsewhere>` via their own OpenAPI artifacts. (Source: `docs/openapi.json#L4-L4`; Source: `docs/openapi.json#L18-L18`)

## 3. How Endpoint Families Are Built
Most resource endpoints follow a generated CRUD family pattern. The generator defines `/batch`, `/query`, `/query/ids`, and `/{object_id}` suffixes and emits operation IDs in a consistent `<resource>__<verb>` style. (Source: `gen_epix/fastapp/api/crud_endpoint_generator.py#L55-L58`; Source: `gen_epix/fastapp/api/crud_endpoint_generator.py#L139-L141`; Source: `gen_epix/fastapp/api/crud_endpoint_generator.py#L220-L223`; Source: `gen_epix/fastapp/api/crud_endpoint_generator.py#L315-L322`; Source: `gen_epix/fastapp/api/crud_endpoint_generator.py#L424-L437`)

The OpenAPI artifact shows this pattern directly for multiple families, such as `users`, `case_types`, and `cases`. (Source: `docs/openapi.json#L8050-L8057`; Source: `docs/openapi.json#L8356-L8363`; Source: `docs/openapi.json#L23624-L23631`; Source: `docs/openapi.json#L23930-L23930`; Source: `docs/openapi.json#L28398-L28405`; Source: `docs/openapi.json#L28704-L28704`)

Handwritten routes are used for explicit workflows that do not fit generic CRUD shape, such as provider listing, health/log, upload, and retrieval operations. (Source: `gen_epix/commondb/api/auth.py#L24-L36`; Source: `gen_epix/commondb/api/system.py#L60-L73`; Source: `gen_epix/commondb/api/system.py#L93-L131`; Source: `docs/openapi.json#L19-L27`; Source: `docs/openapi.json#L18663-L18671`; Source: `docs/openapi.json#L18921-L18929`)

## 4. Security Contract Interpretation
Security is expressed per operation in the contract. Protected operations include OIDC scopes (`openid`, `profile`) in their security requirements. (Source: `docs/openapi.json#L85-L92`; Source: `docs/openapi.json#L115-L122`; Source: `docs/openapi.json#L136-L143`)

Some routes are intentionally outside that protected pattern. `GET /identity_providers` is implemented as a public listing command (`user=None`, `public=True`), and `GET /` is a redirect route rather than a business API endpoint. (Source: `gen_epix/commondb/api/auth.py#L24-L33`; Source: `docs/openapi.json#L19-L27`; Source: `docs/openapi.json#L36616-L36620`; Source: `gen_epix/commondb/app_setup.py#L123-L126`)

Security Note: endpoint-level security declarations in OpenAPI are necessary but not sufficient for full authorization reasoning; command-level policy enforcement remains downstream of route entry. (Source: `gen_epix/fastapp/app.py#L314-L320`; Source: `gen_epix/fastapp/app.py#L347-L360`; Source: `gen_epix/fastapp/app.py#L406-L418`)

## 5. Service Surface Map (from this artifact)
This artifact mixes shared/common surfaces with casedb domain surfaces, which is why a single OpenAPI file has both platform-level and case-specific endpoints. (Source: `docs/openapi.json#L21-L23`; Source: `docs/openapi.json#L47-L49`; Source: `docs/openapi.json#L18484-L18484`; Source: `docs/openapi.json#L33175-L33175`)

Common/platform-facing examples:
1. `/v1/identity_providers` (provider discovery)
2. `/v1/invite_user` and constraints
3. `/v1/health`, `/v1/log`, `/v1/retrieve/licenses`, `/v1/retrieve/outages`
(Source: `docs/openapi.json#L19-L27`; Source: `docs/openapi.json#L45-L57`; Source: `docs/openapi.json#L95-L103`; Source: `docs/openapi.json#L9414-L9422`; Source: `docs/openapi.json#L9469-L9477`; Source: `docs/openapi.json#L9436-L9443`; Source: `docs/openapi.json#L9517-L9524`)

Case-domain examples:
1. CRUD families under `/v1/cases`, `/v1/case_types`, `/v1/case_sets`
2. Workflow endpoints such as `/v1/upload/cases`, `/v1/create/case_set`, `/v1/retrieve/cases_by_ids`, `/v1/retrieve/genetic_sequence/fasta`
3. ABAC policy resources under `/v1/organization_access_case_policies*`
(Source: `docs/openapi.json#L28398-L28405`; Source: `docs/openapi.json#L23624-L23631`; Source: `docs/openapi.json#L30444-L30451`; Source: `docs/openapi.json#L18663-L18671`; Source: `docs/openapi.json#L18713-L18721`; Source: `docs/openapi.json#L18921-L18929`; Source: `docs/openapi.json#L19246-L19254`; Source: `docs/openapi.json#L33888-L33895`)

## 6. Operational Interpretation
For contract governance, treat this OpenAPI file as the externally consumable boundary for casedb runtime plus shared common routes in that runtime. Do not treat it as full platform coverage for seqdb/omopdb. (Source: `docs/openapi.json#L4-L4`; Source: `docs/openapi.json#L18-L18`; Source: `docs/openapi.json#L18484-L18484`)

Operator Note: when externally exposing this API, review which routes are intentionally public (`identity_providers`, root redirect) versus routes that declare OAuth scopes. That split is explicit in the contract and endpoint code. (Source: `docs/openapi.json#L19-L27`; Source: `docs/openapi.json#L85-L92`; Source: `docs/openapi.json#L36616-L36620`; Source: `gen_epix/commondb/api/auth.py#L24-L33`)

Developer Note: automated endpoint inventory and consistency checks should key off operation ID and route-family conventions generated by `CrudEndpointGenerator`; this is more stable than ad hoc string matching over descriptions. (Source: `gen_epix/fastapp/api/crud_endpoint_generator.py#L55-L58`; Source: `gen_epix/fastapp/api/crud_endpoint_generator.py#L702-L757`; Source: `docs/openapi.json#L8056-L8057`; Source: `docs/openapi.json#L28404-L28404`; Source: `docs/openapi.json#L18928-L18928`)

## 7. Constraints & Guardrails
1. This deep dive is bounded to one artifact (`docs/openapi.json`) and therefore cannot claim complete seqdb/omopdb API coverage. (Source: `docs/openapi.json#L4-L4`; Source: `docs/openapi.json#L18-L18`)
2. Root path behavior is a redirect endpoint and is outside tag-grouped service surfaces. (Source: `docs/openapi.json#L36616-L36620`; Source: `gen_epix/commondb/app_setup.py#L123-L126`)
3. CRUD route shapes are determined by generator defaults (`/batch`, `/query`, `/ids`) and permission-derived endpoint type selection, not manually per endpoint in each module. (Source: `gen_epix/fastapp/api/crud_endpoint_generator.py#L55-L58`; Source: `gen_epix/fastapp/api/crud_endpoint_generator.py#L955-L970`; Source: `gen_epix/fastapp/api/crud_endpoint_generator.py#L872-L879`)

## 8. Open Questions / <TBF elsewhere>
1. Full OpenAPI coverage for `SEQDB` and `OMOPDB` endpoint contracts: `<TBF elsewhere>`.
2. External API deprecation/versioning policy beyond current `/v1` prefix and generated operation IDs: `<TBF elsewhere>`. (Source: `gen_epix/casedb/config/settings.toml#L42-L43`; Source: `docs/openapi.json#L8056-L8057`)
3. Gateway- or ingress-level controls (WAF, IP allowlists, external rate-limit policy) are not evidenced in this artifact-level analysis: `<TBF elsewhere>`.

## 9. Evidence Index
- `docs/openapi.json#L4-L4`
- `docs/openapi.json#L18-L18`
- `docs/openapi.json#L19-L27`
- `docs/openapi.json#L45-L57`
- `docs/openapi.json#L85-L92`
- `docs/openapi.json#L9414-L9422`
- `docs/openapi.json#L18663-L18671`
- `docs/openapi.json#L18921-L18929`
- `docs/openapi.json#L28398-L28405`
- `docs/openapi.json#L33888-L33895`
- `docs/openapi.json#L36616-L36620`
- `gen_epix/commondb/app_setup.py#L115-L126`
- `gen_epix/commondb/api/auth.py#L24-L36`
- `gen_epix/commondb/api/system.py#L47-L141`
- `gen_epix/fastapp/api/crud_endpoint_generator.py#L55-L58`
- `gen_epix/fastapp/api/crud_endpoint_generator.py#L702-L757`
- `gen_epix/fastapp/app.py#L309-L418`
