![Gen-EpiX Logo](./docs/assets/gen-epix_logo_full.svg)

[![tests](https://github.com/RIVM-bioinformatics/gen-epix-api/actions/workflows/main.yml/badge.svg)](https://github.com/RIVM-bioinformatics/gen-epix-api/actions/workflows/main.yml) [![sonarqube](https://sonarcloud.io/api/project_badges/measure?project=RIVM-bioinformatics_gen-epix-api&metric=alert_status&token=2b7eb8082cf1e05fb2fd03714413c6e5f8f4b74c)](https://sonarcloud.io/dashboard?id=RIVM-bioinformatics_gen-epix-api) [![coverage](https://sonarcloud.io/api/project_badges/measure?project=RIVM-bioinformatics_gen-epix-api&metric=coverage&token=2b7eb8082cf1e05fb2fd03714413c6e5f8f4b74c)](https://sonarcloud.io/dashboard?id=RIVM-bioinformatics_gen-epix-api)

---

# Gen-EpiX: Genomic Epidemiology platform for disease X (beta version)

Gen-EpiX is a platform for visualizing and analyzing genomic epidemiology data. It has fine-grained access controls for collaboration between multiple organizations.

The platform is currently at the beta release stage and as such not yet usable for production. We are currently working to get the platform released, for use in the Netherlands as the official national platform for laboratory-based surveillance of infectious diseases. Feel free to contact us <a href="mailto:ivo.van.walle@rivm.nl">here</a> if you are interested.

This repository contains the code for the backend and is one of several that together comprise the platform. See https://github.com/RIVM-bioinformatics/gen-epix for an overview of the repositories.

## Architecture and Project Structure

Gen-EpiX is a multi-service backend. Each service runs as its own FastAPI app with a dedicated database and a consistent hexagonal layout (api/domain/services/repositories/policies/config). Core entrypoints are in `run.py` (service startup, ETL, tests) and `etl.py` (data loading). Shared functionality lives under `gen_epix/fastapp`, `gen_epix/filter`, and `gen_epix/transform`.

Services:

| Service | Port | Layer | Description |
|---------|------|-------|-------------|
| `CASEDB` | 8000 | Gold | Case management and epidemiological analysis. Handles case search, filtering, signal detection, and visualization. |
| `SEQDB` | 8001 | Silver | Genetic sequence data and phylogenetic tree computation. Enables genetic similarity searches linked to cases. |
| `OMOPDB` | 8002 | Silver | Normalized patient/subject data compliant with OMOP Common Data Model. |

Supporting modules:
- `COMMONDB` (port 8010): Shared resources (users, organizations, authentication). Handles fine-grained access control (ABAC/RBAC).
- `FASTAPP`: Shared FastAPI utilities and common functionality across all services.

Project tree (trimmed to the main structure):
```
.
├── gen_epix
│   ├── commondb/                  # shared users, orgs, and cross-service resources
│   │   ├── api/                   # FastAPI endpoints and HTTP models
│   │   ├── domain/                # business models, commands, and policies
│   │   ├── services/              # application orchestration and CRUD flows
│   │   ├── repositories/          # data access (SQLAlchemy or in-memory)
│   │   ├── policies/              # ABAC and RBAC policy logic
│   │   ├── config/                # service settings and Dynaconf config
│   │   └── app.py                 # FastAPI app object
│   ├── casedb/, omopdb/, seqdb/   # other service modules with the same layout
│   │   ├── api/
│   │   ├── domain/
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── policies/
│   │   ├── config/
│   │   └── app.py
│   ├── fastapp/                   # shared FastAPI utilities and base wiring
│   ├── filter/                    # shared filtering utilities
│   └── transform/                 # shared transformation utilities
├── config/                        # global Dynaconf and identity provider configuration
├── docs/                          # documentation and assets
├── test/                          # unit, integration, and end-to-end tests
├── run.py                         # CLI entrypoint for API, ETL, and tests
└── etl.py                         # ETL entry script
```

## Key Features

- **Visualisation**: Visualize cases by time, place, person and also by genome through a phylogenetic tree coupled to the cases.
- **Fine-grained access**: Give different organizations different access rights per disease, down to individual variables. Organizations can manage access of their own users by themselves.
- **Search**: Search and filter cases, including on genetic similarity.
- **Signal detection**: Detect, define and share sets of cases, signals and outbreaks. Detection can be manual through the web application, or through your own algorithm using the API.
- **Disease X**: Any disease and corresponding analysis variables can be added.
- **Data**: Adheres to the Medallion data architecture design pattern. The silver layer consists of normalized and standardized patient or subject data compliant with the [OMOP Common Data Model](https://www.ohdsi.org/data-standardization), and a dedicated database for genetic sequence data and computation of phylogenetic trees. The gold layer consists of case data ready for analysis in the form of a single row of data per case.
- **Tech**: OpenAPI compliant API, deployable on cloud or on-premise, support for multiple authentication providers. Python/FastAPI backend and default TypeScript/React frontend available from gen-epix-web.

## Deliberately not in scope

- **Disease-specific knowledge**: Every organization has their own variables that are important for analysis, as well as their own bioinformatics to process genetic sequence data. We therefore avoided any disease-specific code both for the generation of these data and for the analysis variables that can be defined. Only the results are stored. 
- **Collaboration-specific knowledge**: Every collaboration or country (e.g. for public health surveillance of diseases) has their own specifics in terms of access rights and any relevant geographic regions. We therefore avoided any country-specific code, both for the type of organizations that have access, and for any geographic data. 

---

# Installation 

1. Install ODBC development headers:
   ```console
   # Linux
   sudo apt-get update
   sudo apt-get install -y unixodbc-dev
   ```

2. Create and activate a conda environment:
   ```console
   conda create --name gen-epix python=3.14
   conda activate gen-epix
   ```

3. Install dependencies*:
   ```console
   pip install -r requirements.txt
   pip install --no-binary :all: pyodbc==5.2.*
   ```
   **Some hardware architectures (especially Apple M1/M2/M3 chips) require pyodbc to be compiled from source for compatibility***


4. For development, add testing tools:
   ```console
   pip install -r dev-requirements.txt
   ```


**SSL Certificate Setup**

1. Install mkcert:
   ```console
   # Linux
   sudo apt install mkcert
   
   # macOS
   brew install mkcert
   ```

2. Generate certificates:
   ```console
   mkcert -install
   mkcert -key-file key.pem -cert-file cert.pem localhost 127.0.0.1
   ```

3. Copy the generated files:
   ```console
   cp key.pem cert.pem /path/to/project/cert/
   ```

4. For WSL users: Run the commands in Windows PowerShell and copy files to both the project cert directory and your WSL home directory.

---

## Usage

### Starting the API

1. Activate the conda environment:
```console
conda activate gen-epix
```
2. Run the application:
```console
python run.py <command> <service> <idp_config> <repository_config>
```
- `command`: Entry point to run (e.g., `api`).
- `service`: `CASEDB`, `SEQDB`, `OMOPDB`, or `COMMONDB`.
- `idp_config`: `IDPS` or `MOCK`.
- `repository_config`: `DICT_DEMO`, `SA_SQLITE_DEMO`, or `SA_SQL`.

---

### Example

```console
conda activate gen-epix
python run.py api casedb none dict_demo
```

See other examples in [.vscode/launch.json](.vscode/launch.json)

| ![Example documentation screenshot](https://github.com/RIVM-bioinformatics/gen-epix-api/blob/main/docs/assets/example_docs.png?raw=true) |
|:--:|

---

## Dependencies

Gen-EpiX relies on several Python packages to provide its functionality:

**Core Dependencies**
* [`fastapi`](https://fastapi.tiangolo.com) - Modern, high-performance web framework
* [`sqlalchemy`](https://www.sqlalchemy.org) - SQL toolkit and Object-Relational Mapping (ORM) library
* [`pydantic`](https://docs.pydantic.dev) - Data validation and settings management
* [`biopython`](https://biopython.org) - Tools for computational molecular biology

**Database Connectors**
* [`pyodbc`](https://github.com/mkleehammer/pyodbc) - ODBC database adapter

**Development Tools**
* [`pytest`](https://docs.pytest.org) - Testing framework
* [`black`](https://black.readthedocs.io) - Code formatter
* [`pylint`](https://pylint.org) - Static code analyzer
* [`mypy`](https://mypy.readthedocs.io) - Static type checker

For a complete list of dependencies, refer to:
- [requirements.txt](requirements.txt) - Production dependencies
- [dev-requirements.txt](dev-requirements.txt) - Development dependencies

**Python Version**
Gen-EpiX requires Python 3.14 or higher.

## Funding

This work was funded by the European Union under the EU4Health Programme (EU4H), project IDs 101102070 (UNITED4Surveillance) and 101113520 (NLWGSHERA2).

![EU Funding Logo](./docs/assets/cofunded_EU_logo.png)

*Disclaimer: Funded by the European Union. Views and opinions expressed are however those of the author(s) only and do not necessarily reflect those of the European Union or Health and Digital Executive Agency. Neither the European Union nor the granting authority can be held responsible for them.*
