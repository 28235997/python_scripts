```

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

# === Define categories, indicators, and descriptions ===
categories = {
    "CI/CD Pipeline Maturity": {
        "Build Automation": "Builds trigger automatically via CI for every commit or PR.",
        "Test Automation": "Automated unit/integration tests run in the CI pipeline.",
        "Pipeline Reliability": "Percentage of successful builds and deployments.",
        "Deployment Frequency": "How often the service can be deployed safely (daily/on-demand ideal).",
        "Lead Time for Changes": "Average time from code commit to production deployment.",
        "Rollback Capability": "Ability to quickly roll back to a previous version automatically.",
        "Promotion Path": "Automated promotion of artifacts across environments (dev → prod)."
    },
    "Code & Security Hygiene": {
        "Static Code Analysis": "Automated static code quality scanning (e.g., SonarQube, CodeQL).",
        "Dependency Scanning": "Scan open-source dependencies for known vulnerabilities.",
        "Secret Scanning": "Detect hardcoded credentials or tokens in repositories.",
        "Code Review Enforcement": "Pull requests require mandatory peer review and approval.",
        "Linting / Style Compliance": "Code follows enforced formatting and linting standards.",
        "Open Source License Compliance": "Ensure OSS dependencies have acceptable licenses."
    },
    "Observability & Reliability": {
        "Logging": "Service outputs structured, centralized logs (e.g., Loki, ELK).",
        "Metrics": "Exports Prometheus metrics for performance and business KPIs.",
        "Tracing": "Distributed tracing (e.g., Tempo, Jaeger) to follow requests end-to-end.",
        "Alerting": "Alerts configured for key metrics (latency, error rate, saturation).",
        "SLI/SLO Coverage": "Defined service-level indicators and objectives for key endpoints.",
        "Error Budget Tracking": "Track SLO compliance and alert on error budget burn rate.",
        "Runbook Availability": "Every alert has a corresponding operational runbook."
    },
    "Infrastructure & Environment Management": {
        "Infrastructure as Code (IaC)": "All infrastructure managed declaratively (Terraform, Helm, etc.).",
        "Immutable Deployments": "Deployments create new containers/pods; no manual patching.",
        "Configuration Management": "Configs versioned and managed through Git (GitOps).",
        "Secrets Management": "All credentials managed securely (Vault, KMS, etc.), not hardcoded.",
        "Environment Parity": "Consistency between dev/staging/prod environments.",
        "Auto Scaling": "Automatic scaling rules (HPA/KEDA) in place for load or resource usage."
    },
    "Operational Excellence": {
        "Deployment Approval Workflow": "Deployment gates automated with minimal manual approval.",
        "Incident Response": "Documented response plan and on-call rotation defined.",
        "Postmortems": "Post-incident analysis completed for Sev1/Sev2 issues.",
        "Chaos Testing / Resilience Tests": "Regular failure injection to validate reliability.",
        "Performance Baselines": "Load and performance tests run periodically or before release."
    },
    "Governance & Compliance": {
        "Audit Logging": "All deployment and configuration changes are logged and auditable.",
        "RBAC & Least Privilege": "Access controls implemented following least-privilege principle.",
        "Vulnerability Remediation SLA": "Time-bound SLA for fixing vulnerabilities (e.g., 30 days).",
        "Artifact Provenance": "Images or artifacts are signed and verified (Cosign, Notary)."
    }
}

# === Color palette (category colors + app name color) ===
category_colors = [
    "FFF2CC",  # CI/CD → light yellow
    "DDEBF7",  # Code Hygiene → light blue
    "E2EFDA",  # Observability → light green
    "FCE4D6",  # Infra Mgmt → light orange
    "EAD1DC",  # Operational Excellence → light purple
    "F4CCCC"   # Governance → light red
]
app_name_color = "D9D9D9"  # neutral gray for application names

# === Create workbook ===
wb = Workbook()
ws = wb.active
ws.title = "DevOps Maturity Matrix"

# === Styles ===
bold_font = Font(bold=True)
center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
border = Border(
    left=Side(border_style="thin", color="999999"),
    right=Side(border_style="thin", color="999999"),
    top=Side(border_style="thin", color="999999"),
    bottom=Side(border_style="thin", color="999999")
)

# === Header setup ===
ws.cell(row=1, column=1, value="Application Name").font = bold_font
ws.cell(row=1, column=1).alignment = center_align
ws.merge_cells(start_row=1, start_column=1, end_row=2, end_column=1)
ws.cell(row=1, column=1).fill = PatternFill(start_color=app_name_color, end_color=app_name_color, fill_type="solid")

col = 2
for idx, (category, indicators) in enumerate(categories.items()):
    color = category_colors[idx % len(category_colors)]
    fill = PatternFill(start_color=color, end_color=color, fill_type="solid")

    start_col = col
    end_col = col + len(indicators) - 1

    # Category merged header
    ws.merge_cells(start_row=1, start_column=start_col, end_row=1, end_column=end_col)
    c = ws.cell(row=1, column=start_col, value=category)
    c.font = bold_font
    c.alignment = center_align
    c.fill = fill
    c.border = border

    # Indicator row
    for indicator in indicators.keys():
        c = ws.cell(row=2, column=col, value=indicator)
        c.alignment = center_align
        c.fill = fill
        c.border = border
        col += 1

# === Example apps ===
apps = ["bookservice", "userservice", "paymentservice", "inventoryservice"]

for row_idx, app in enumerate(apps, start=3):
    # App name cell
    c = ws.cell(row=row_idx, column=1, value=app)
    c.font = bold_font
    c.alignment = center_align
    c.fill = PatternFill(start_color=app_name_color, end_color=app_name_color, fill_type="solid")
    c.border = border

    # Fill colored value cells based on category grouping
    col_idx = 2
    for color_index, (category, indicators) in enumerate(categories.items()):
        fill = PatternFill(start_color=category_colors[color_index], end_color=category_colors[color_index], fill_type="solid")
        for _ in indicators.keys():
            cell = ws.cell(row=row_idx, column=col_idx, value="")
            cell.fill = fill
            cell.border = border
            col_idx += 1

# === Formatting ===
ws.freeze_panes = "B3"
ws.column_dimensions['A'].width = 25
for col_cells in ws.iter_cols(min_col=2, max_col=col - 1, min_row=2, max_row=2):
    for cell in col_cells:
        ws.column_dimensions[cell.column_letter].width = 22

# === Add description sheet ===
desc_ws = wb.create_sheet("Indicator Description")
desc_ws.append(["Category", "Indicator", "Description"])
for cell in desc_ws[1]:
    cell.font = bold_font
    cell.fill = PatternFill(start_color="C9C9C9", end_color="C9C9C9", fill_type="solid")
    cell.alignment = center_align

for category, indicators in categories.items():
    for indicator, description in indicators.items():
        desc_ws.append([category, indicator, description])

desc_ws.column_dimensions['A'].width = 35
desc_ws.column_dimensions['B'].width = 40
desc_ws.column_dimensions['C'].width = 100

# === Save ===
wb.save("devops_maturity_matrix_fully_colored.xlsx")
print("✅ Generated: devops_maturity_matrix_fully_colored.xlsx")


```
