# Draft Opportunity Proposal

> Synthetic demonstration content. Review before use.

## Executive Summary
Contoso Health wants to reduce prior-authorization preparation time from ~2 hours to ~15 minutes while ensuring staff use only approved clinical records, keep patient data inside the Microsoft tenant boundary, and require clinician approval for every submission (assumptions: initial scope targets one high-volume specialty and one payer portal/workflow).

We recommend a tenant-contained, source-grounded prior-authorization preparation solution built on Microsoft Agent Framework hosted in Foundry Agent Service, with Foundry IQ + Azure AI Search for grounded retrieval of approved payer policies and internal procedures, and Azure Health Data Services (FHIR) for read-only access to approved clinical records—paired with a Power Automate clinician approval gate before any packet can be submitted. This approach follows patterns that reduced median preparation time from 118 to 17 minutes in a similar prior-auth implementation while keeping PHI inside the customer’s Azure tenant and enforcing clinician approval. [0]

## Customer Situation
Authorization staff currently spend significant time locating relevant clinical documentation, matching payer criteria, and assembling submission packets—work that is error-prone and often leads to rework when evidence is missing or criteria are outdated, as seen in comparable healthcare organizations. [0]

Contoso’s non-negotiable requirements are:
- Only approved clinical records may be used as evidence (no “best guess” content).
- Patient data must remain inside the Contoso tenant boundary.
- A licensed clinician must approve every prior-authorization submission.

## Recommended Architecture
1. **Intake & work queue**: Create a prior-auth “case” (request) in a work system (recommendation: Dynamics 365 Customer Service work queue pattern) and capture order details and payer metadata to drive specialty/payer routing. (Dynamics-based work tracking was used in a specialty authorization copilot pattern.) [1]
2. **Approved clinical record retrieval (read-only)**: Use Azure Health Data Services FHIR service to retrieve only minimum-necessary clinical artifacts (orders, diagnoses, relevant notes/observations) via a read-only tool interface. [0]
3. **Approved knowledge retrieval for payer criteria**: Store payer policy PDFs, internal SOPs, and specialty checklists in SharePoint as the governed content source and index them with Azure AI Search; use Foundry IQ to ground retrieval with citations and metadata filters (payer, specialty, effective date). [0]
4. **Deterministic workflow orchestration**: Implement a bounded, stepwise Microsoft Agent Framework workflow hosted on Foundry Agent Service to:
   - Match payer criteria to request type.
   - Extract required evidence elements from FHIR.
   - Run non-clinical completeness checks (e.g., required attachments present) using Azure Functions (pattern used in imaging authorization). [2]
   - Draft a submission packet with an evidence checklist and citations back to source documents and FHIR artifacts. (Evidence checklist pattern improved clinician review.) [2]
5. **Clinician human-in-the-loop approval (hard gate)**: Route the packet through Power Automate approval to the responsible clinician; block any “submit” action unless a clinician approves with authenticated identity and (recommendation) a reason/attestation. Similar solutions enforced that the agent could not submit without clinician approval. [0]
6. **Submission integration (post-approval)**: After approval, submit via a controlled integration layer (Azure API Management) where integrations exist; otherwise generate a portal-ready packet for manual upload (recommendation: keep portal submission out of the agent until quality is stable, consistent with prior lessons). [0]
7. **Audit, monitoring, and evaluations**: Capture end-to-end traceability (retrievals, citations, tool calls, drafts, approvals, and final output) in Azure Monitor/Application Insights; maintain specialty/payer evaluation sets for groundedness and completeness before expanding. Comparable implementations traced every step and used specialty-specific evaluation sets. [0]

## Microsoft Services Used
- Microsoft Foundry, Microsoft Agent Framework, Foundry Agent Service, Foundry IQ [0]
- Azure AI Search [0]
- Azure Health Data Services (FHIR) [0]
- SharePoint (governed policy/procedure repository) [0]
- Power Automate (clinician approvals) [0]
- Microsoft Entra ID (RBAC and conditional access) [0]
- Azure Key Vault (secrets/keys) [0]
- Azure Monitor + Application Insights (traceability/telemetry) [1]
- Azure Functions (non-clinical completeness rules) [2]
- Azure API Management (governed external/payer integrations) [0]
- Microsoft Purview (data classification and policy) [0]

## Implementation Timeline
| Phase | Timing | Deliverables |
|---|---:|---|
| Discovery, baseline, and clinical risk mapping | Weeks 1–2 | Current-state process map; baseline timing/quality metrics; specialty/payer pilot scope; automation boundaries and clinician accountability model (pattern used in prior-auth discovery). [0] |
| Data + knowledge readiness | Weeks 3–5 | FHIR read-only access configuration; minimum-necessary field set; SharePoint governed corpus with payer/effective-date metadata; Azure AI Search index; source attestation workflow. [2] |
| Agent workflow build | Weeks 6–8 | Microsoft Agent Framework orchestration in Foundry Agent Service; retrieval + drafting steps; Azure Functions completeness checks; audit events and packet template. [2] |
| Evaluation, red-team, and safety hardening | Weeks 9–10 | Groundedness and completeness evaluations; prompt-injection defenses and output validation; go/no-go thresholds; rollback plan (pattern used in imaging authorization). [2] |
| Supervised pilot + handover | Weeks 11–12 | Supervised clinician-approved pilot; runbook; operational dashboards; training; controlled rollout plan. [2] |

## Security Considerations
- **Tenant boundary / PHI containment**: Use private endpoints and network-restricted services for Search and FHIR; keep service-to-service traffic private; store secrets in Key Vault. (These controls were used to keep data inside the approved boundary.) [2]
- **Least privilege access**: Entra ID roles and groups separate authorization staff, clinicians, and admins; use managed identities for the agent’s tool access. [1]
- **Minimum necessary clinical context**: Field filtering on FHIR queries to reduce PHI exposure while still meeting payer criteria. [0]
- **Treat retrieved content as untrusted**: Apply prompt-injection defenses and output validation so retrieved documents cannot alter workflow policy (e.g., cannot bypass approvals). [2]
- **No autonomous submission**: The workflow must not submit any packet without clinician approval, enforced as a hard gate. [0]

## Governance Controls
- **Content governance**: Named owners approve the “approved records” and policy corpus; payer-policy freshness attestation cadence (e.g., every 30 days) before documents remain searchable. [1]
- **Versioning and release governance**: Version prompts, policies, evaluation sets, and agent releases; define rollback criteria before expanding scope. [2]
- **Traceability**: Log every retrieval, citation, tool call, draft, approval, and submission artifact for audit. [0]
- **Exception handling**: Missing evidence, failed groundedness, or policy conflicts route to a human-only work queue. (Comparable solutions forced human-only handling on failures.) [1]

## Success Metrics
(These are target metrics; similar implementations achieved comparable improvements but results are not guaranteed.)
- Median prior-auth prep time reduced toward 15 minutes (reference outcomes: 118→17 minutes; 94→16 minutes). [0][2]
- ≥95% packet completeness on first review (reference outcome: 96%). [0]
- 100% of submissions with authenticated clinician approval (reference outcome: 100%). [0]
- ≥97% citation coverage tying packet statements to source documents/records (reference outcomes: 97–99%). [1][2]
- Zero severity-one privacy/safety incidents in pilot (reference outcome: none recorded in pilot). [0]

## Lessons Applied
- **Keep portal submission outside the agent until stable**: Maintain clinician approval and completeness targets before enabling deeper submission automation. [0]
- **Specialty/payer-specific retrieval and evaluations**: Use specialty-specific filters and evaluation sets to improve precision and expose gaps early. [0][1]
- **Metadata discipline for payer criteria**: Require effective dates and payer metadata to avoid retrieving superseded documents. [2]
- **Make evidence visible**: Provide an explicit evidence checklist to speed clinician review and increase trust. [2]

## Future Expansion Opportunities
- Expand to additional specialties (e.g., imaging, oncology) using the same governed workflow pattern. [0]
- Add denial appeal drafting with governed review and approval gates (pattern identified as a future extension). [0][2]
- Implement payer-policy change detection and regression tests to ensure retrieval remains current and safe. [2]
- Add operational analytics to identify recurring documentation gaps by facility, specialty, or payer. [0]

## Sources

- [0] Sample Historical Project - Northwind Health Prior Authorization Agent — Northwind Health Network, Healthcare provider (DemoData/Past Projects/Northwind Health Prior Authorization Agent)
- [1] Sample Historical Project - Woodgrove Medical Imaging Authorization Agent — Woodgrove Medical Group, Regional healthcare provider (DemoData/Past Projects/Woodgrove Medical Imaging Authorization Agent)
- [2] Sample Historical Project - Fabrikam Specialty Care Authorization Copilot — Fabrikam Specialty Care Alliance, Specialty healthcare provider (DemoData/Past Projects/Fabrikam Specialty Care Authorization Copilot)
