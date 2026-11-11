# GTS Operations Hub — Native Windows Edition

**No Docker, Podman, Minikube, or local container runtime required.**

This educational IT operations platform contains a FastAPI/SQLite CMDB, incident dashboard, dependency records, Prometheus-text metrics, a Terraform local-provider lab, a standalone Keycloak configuration example, a browser-only Kubernetes lab guide, and GitHub Actions + Agile issue templates.

> **Scope:** The dashboard tracks manually registered asset status and incidents. It does **not** discover actual infrastructure or automatically monitor live hosts. Kubernetes exercises are performed separately in a browser lab, not deployed on your PC. Terraform creates local files, not cloud infrastructure. Keycloak OIDC/MFA configuration is an optional lab; the default dashboard does not enforce SSO.

## Quick start on Windows (PowerShell)

### Requirements
- Python **3.12** from https://www.python.org/downloads/
- VS Code (optional) and Git

Open this extracted project folder in VS Code, then open a PowerShell terminal in the root.

```powershell
.\scripts\setup.ps1
.\scripts\run.ps1
```

If PowerShell blocks scripts, run the equivalent commands directly (no policy changes required):

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open **http://127.0.0.1:8000** and click **Load demo data**. Swagger docs: http://127.0.0.1:8000/docs. Stop with **Ctrl+C**.

SQLite database `gts_hub.db` is created automatically in the project folder. It is excluded from Git.

### Try the API in PowerShell

```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/v1/demo/seed
Invoke-RestMethod http://127.0.0.1:8000/api/v1/assets
Invoke-RestMethod http://127.0.0.1:8000/api/v1/overview
Invoke-RestMethod http://127.0.0.1:8000/api/v1/metrics
```

### Tests

```powershell
.\scripts\test.ps1
```

## Optional native PostgreSQL (no containers)

Install PostgreSQL for Windows from https://www.postgresql.org/download/windows/. Using pgAdmin or psql, create a database named `gts_hub`, a user named `gts`, and grant privileges. Example for a **local-only** PostgreSQL administrator session:

```sql
CREATE USER gts WITH PASSWORD 'choose_a_strong_local_password';
CREATE DATABASE gts_hub OWNER gts;
```

In the same PowerShell session, set the database URL **before** starting the app (URL-encode special characters in passwords):

```powershell
$env:DATABASE_URL = 'postgresql+psycopg://gts:YOUR_PASSWORD@localhost:5432/gts_hub'
.\scripts\run.ps1
```

The SQLite quick start is the recommended first run. The application creates its tables automatically for this demo; a real service should use Alembic migrations.

## Terraform lab (no containers or cloud account)

Install Terraform CLI from https://developer.hashicorp.com/terraform/install and ensure `terraform` is in PATH. Then:

```powershell
cd terraform
terraform init
terraform fmt -check
terraform validate
terraform plan
terraform apply
terraform output
Get-Content .\generated\infrastructure-inventory.json
terraform destroy
cd ..
```

Terraform creates two local configuration files. **It does not provision a VM, network, or Kubernetes cluster.** The local provider is a beginner-friendly introduction to IaC state, plan, apply and destroy.

## Keycloak standalone lab (Java, no containers)

1. Install Java 21 (JDK) from https://adoptium.net/.
2. Download the **Keycloak server ZIP** from https://www.keycloak.org/downloads and extract it to a directory such as `C:\tools\keycloak`.
3. Copy `keycloak/realm-export.json` from this project into `<Keycloak folder>/data/import/` before starting Keycloak. Create the import directory if needed.
4. In a PowerShell terminal in the extracted Keycloak directory, run:

```powershell
$env:KC_BOOTSTRAP_ADMIN_USERNAME = 'admin'
$env:KC_BOOTSTRAP_ADMIN_PASSWORD = 'replace_with_a_strong_local_password'
.\bin\kc.bat start-dev --http-port=8081 --import-realm
```

5. Keycloak imports the `gts` realm only if it does not already exist. Open http://localhost:8081/admin and sign in with the admin account you configured.
6. Inspect realm `gts`, its roles (`platform-admin`, `operator`, `viewer`), the `gts-dashboard` OIDC client, and the `demo-operator` user.
7. For MFA practice, configure a TOTP authenticator for the demo user and inspect the realm's required actions / authentication flows.

**Important:** This is an IAM configuration lab, not fully implemented application SSO. The app starts with authentication disabled. `app/auth.py` contains optional JWT validation but enabling it alone is not sufficient for a working browser login. A real end-to-end OIDC integration needs a browser authorization-code flow, callback/token handling, a valid API audience, role checks, and testing. Do not claim that SSO is implemented until that work is done.

## Browser-only Kubernetes exercises

See [KUBERNETES_LABS.md](KUBERNETES_LABS.md). Use https://killercoda.com/ for hosted Kubernetes scenarios. **No local Kubernetes installation is necessary.** The labs use pre-provisioned remote environments; they do not deploy this application on your PC.

## GitHub Actions and Agile

The included `.github/workflows/ci.yml` uses a Windows GitHub-hosted runner, installs Python dependencies and runs tests. No image build or container tooling is used in the workflow.

Create a GitHub Project board with columns `Todo`, `In Progress`, `Review`, and `Done`. Add issues using the backlog in [AGILE_BACKLOG.md](AGILE_BACKLOG.md). Record screenshots and task completion honestly.

## Push to GitHub

Create an empty GitHub repository named `gts-operations-hub`, then from the project root:

```powershell
git init
git add .
git commit -m "Build Windows-native GTS Operations Hub"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/gts-operations-hub.git
git push -u origin main
```

Replace `YOUR_USERNAME`. Verify the **Actions** workflow passes.

## Honest resume positioning

**GTS Operations Hub | Python, FastAPI, SQLite/PostgreSQL, Terraform, GitHub Actions**
- Built a local IT operations dashboard with configuration-item inventory, dependency mapping, incident tracking and operational status summaries.
- Exposed REST APIs and Prometheus-format demo metrics; automated Python tests with GitHub Actions.
- Authored Terraform local-provider configurations to practice declarative infrastructure management.

Mention Keycloak MFA or Kubernetes separately **only after** completing those labs. Do not claim production-grade monitoring, full SSO or cloud infrastructure provisioning.
