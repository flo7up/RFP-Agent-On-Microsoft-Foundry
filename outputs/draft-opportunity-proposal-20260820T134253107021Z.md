# Draft Opportunity Proposal

> Synthetic demonstration content. Review before use.

## Executive Summary
Contoso Health aims to reduce prior authorization (PA) preparation time from ~2 hours to ~15 minutes while ensuring staff use only approved clinical records, PHI remains within the Contoso tenant boundary, and a clinician approves every submission. We propose a tenant-contained, source-grounded PA packet generation workflow using Microsoft Agent Framework hosted on Foundry Agent Service. Retrieval is grounded in approved payer policies and internal guidance via Foundry IQ and Azure AI Search, following patterns that reduced preparation time to ~16–19 minutes in similar healthcare implementations while preserving clinician accountability. [0][1][2]

## Customer Situation
PA specialists and clinical staff spend significant time locating relevant records, validating payer-specific criteria, and assembling evidence and narratives for submission packets across multiple systems and repositories. Similar organizations reported 94–118 minutes average/median preparation time due to multi-system navigation and payer-site interactions, plus rework from incomplete packets. [0][2]

Contoso requires:
- Only approved clinical records are used as evidence in the packet (no “free-form” external sources). (Requirement)
- Protected health information (PHI) remains within the Contoso tenant boundary. (Requirement)
- Every submission is reviewed and approved by a clinician with authenticated sign-off. (Requirement)

Assumptions (to be validated in discovery):
- Contoso can expose clinical data through FHIR APIs (e.g., via Azure Health Data Services) or another governed read-only interface. [0][2]
- Payer requirements and internal PA procedures can be curated in SharePoint or a similar controlled repository for indexing. [0][2]

## Recommended Architecture
1. **Curate “approved sources” corpus**: Establish a controlled, versioned set of payer policy PDFs, internal PA checklists, specialty protocols, and submission templates in SharePoint. Index only this corpus for retrieval. Similar projects emphasized policy ownership and payer-specific checklists to improve retrieval precision. [0]
2. **Index and ground retrieval**: Use Foundry IQ with Azure AI Search to retrieve payer criteria and internal procedures with citations and metadata (payer, specialty, effective date) to reduce use of superseded criteria. [0][2]
3. **Read-only clinical record retrieval**: Expose required EHR data via Azure Health Data Services (FHIR) using minimum-necessary queries and field filtering. Retrieve only the note sections, orders, observations, and prior results required for the current request. [0][2]
4. **Deterministic workflow orchestration**: Implement a bounded Microsoft Agent Framework workflow hosted on Foundry Agent Service. Separate steps for policy retrieval, clinical evidence collection, completeness checks, and packet drafting (rather than a single unconstrained chat). This separation pattern was used in prior authorization implementations. [0][2]
5. **Rule-based completeness gate** (recommendation): Add an Azure Functions–based rules engine to verify required artifacts (e.g., imaging order, diagnosis codes, recent labs, prior conservative therapy) before drafting/approval, reflecting the approach of applying explicit rules outside the model. [2]
6. **Draft packet assembly**: Generate a PA packet draft that includes:
   - Evidence checklist mapped to payer criteria
   - Cited excerpts from approved sources and retrieved clinical records
   - Structured narrative summary for the submission form
   - “Missing evidence” section when requirements are not met  
   This mirrors solutions that assembled cited evidence and highlighted missing items for review. [1][2]
7. **Clinician approval (hard stop)**: Route every draft through a Power Automate approval to the responsible clinician (or pharmacist where applicable). The workflow must not allow final submission without authenticated clinician approval, consistent with implementations requiring clinician approval for every packet. [0][2]
8. **Submission integration** (recommendation): After approval, hand off to a controlled submission step:
   - Option A: API-based integration via Azure API Management (where payers support APIs)
   - Option B: Assisted portal entry (human-in-the-loop) until stability thresholds are met, reflecting the lesson to keep portal submission outside the agent early. [0]
9. **End-to-end auditability**: Log every retrieval, citation, tool call, draft version, approval event, override reason, and submission artifact in centralized logging and tracing for compliance review. [0][1]

## Microsoft Services Used
- Microsoft Foundry, Microsoft Agent Framework, Foundry Agent Service, Foundry IQ [0][2]
- Azure AI Search [0][2]
- Azure Health Data Services (FHIR) [0][2]
- Power Automate (clinician approval workflow) [0][2]
- Microsoft Entra ID (RBAC/Conditional Access) [0][2]
- Azure Key Vault (secrets/keys), Azure Monitor + Application Insights (telemetry) [0][2]
- Microsoft Purview (data classification, DLP support) [0][1]
- Optional: Azure Functions (completeness rules), Azure Service Bus (work queue), Azure API Management (payer integrations) [2][0]

## Implementation Timeline
| Phase | Timing | Deliverables |
|---|---:|---|
| 1. Discovery, baseline & clinical risk mapping | Weeks 1–2 | Current-state PA process map; baseline time study; specialty/payer selection for pilot; clinical safety boundaries and “approved sources” definition. Similar projects started with discovery and baseline measurement. [2] |
| 2. Data & knowledge preparation | Weeks 3–5 | SharePoint policy corpus with ownership/effective dates; Azure AI Search index with metadata filters; FHIR read-only connectivity and minimum-necessary data contract. Similar timelines allocated multiple weeks for data/policy connections. [0][2] |
| 3. Workflow build (agent + rules + approvals) | Weeks 6–8 | Agent Framework orchestration in Foundry Agent Service; completeness rules; draft packet template; Power Automate clinician approval; logging/audit instrumentation. [0][2] |
| 4. Evaluation, red-team, and governance readiness | Weeks 9–10 | Groundedness and citation tests; prompt-injection defenses and output validation; operational runbooks; rollback criteria and release/versioning practices. Similar projects included evaluation and red-team testing. [2] |
| 5. Pilot (supervised) | Weeks 11–12 | Pilot in one specialty/payer set; parallel-run comparison to manual process; clinician feedback loop; KPI dashboard for time-to-draft and time-to-approval. Similar projects ran supervised pilots. [2] |
| 6. Controlled rollout & handover | Weeks 13–14 | Expanded payer set; training; support transition; steady-state governance cadence. A comparable rollout and handover phase followed pilot in similar work. [0] |

## Security Considerations
- **Tenant boundary & networking**: Use Private Endpoints and network-restricted access for Search and FHIR services to keep PHI inside the approved boundary. [2]
- **Identity & least privilege**: Enforce Microsoft Entra ID RBAC with separate groups for PA specialists, clinicians, and administrators; use managed identities for service-to-service calls. [1][2]
- **Key/secrets management**: Store secrets and encryption keys in Azure Key Vault; use encryption in transit and at rest. [0][2]
- **Minimum necessary & field filtering**: Restrict FHIR queries and filter fields so tools receive only what the current request requires. [0][2]
- **Prompt-injection and untrusted documents**: Treat retrieved documents as untrusted input; implement prompt-injection defenses and output validation so retrieved text cannot alter workflow policy. [0][2]
- **No autonomous submission**: The system cannot submit an authorization packet without authenticated clinician approval. [0]

## Governance Controls
- **Clinical ownership and boundary approval**: Assign a named clinical owner to approve automation boundaries and escalation criteria. [2]
- **Source corpus governance**: Content owners attest payer-policy freshness on a recurring cadence (e.g., every 30 days); require effective dates and payer metadata to reduce superseded-criteria retrieval. [1][2]
- **Versioning and release discipline**: Version prompts, policies, evaluations, and agent releases; define rollback criteria before expanding beyond pilot. [1][2]
- **Full traceability**: Retain a complete audit trail of retrievals, citations, drafts, approvals, and final submission artifacts. [0][1]
- **Exception handling**: Route failed groundedness, missing evidence, or policy conflicts into a human-only work queue. [1]

## Success Metrics
Measured in pilot and monitored post-go-live (not guaranteed outcomes):
- **Time-to-draft packet** (median/p95)
- **End-to-end PA preparation time** (median/p95) toward the 15-minute target (goal)
- **Packet completeness rate** (first-pass acceptance proxy), referencing completeness improvements observed elsewhere (e.g., 96% completeness in a pilot). [0]
- **Clinician approval coverage**: 100% of submitted packets have authenticated clinician approval (control requirement). Similar programs retained 100% clinician approval. [0][2]
- **Citation coverage**: Percentage of packet claims linked to approved source citations (targets informed by 97–99% citation coverage in similar work). [0][1][2]
- **Safety/privacy incidents**: Track and target zero severity-one privacy/safety incidents, consistent with a pilot reporting none. [0]

## Lessons Applied
- Prioritize **policy ownership and payer-specific checklists** to improve retrieval precision (often more impactful than prompt tuning). [0]
- Keep **urgency classification and other routing decisions rule-based**, not delegated to the model. [2]
- Require **effective dates and payer metadata** in source documents to reduce superseded-criteria retrieval. [2]
- Keep **portal submission outside the agent initially**; expand automation only after stability thresholds are met. [0]
- Provide a visible **evidence checklist** to accelerate clinician review and improve feedback quality. [2]

## Future Expansion Opportunities
- Extend to additional specialties (e.g., oncology, imaging, infusion) following patterns used to expand beyond initial pilots. [0][2]
- Add denial/appeal packet drafting with governed legal + clinical approval, building on appeal-drafting expansion ideas. [0][1][2]
- Implement policy-change detection and regression testing to monitor payer criteria updates. [1][2]
- Add operational analytics to identify recurring documentation gaps by facility, specialty, and payer. [0][2]

## Sources

- [0] Sample Historical Project - Northwind Health Prior Authorization Agent — Northwind Health Network, Healthcare provider (DemoData/Past Projects/Northwind Health Prior Authorization Agent)
- [1] Sample Historical Project - Fabrikam Specialty Care Authorization Copilot — Fabrikam Specialty Care Alliance, Specialty healthcare provider (DemoData/Past Projects/Fabrikam Specialty Care Authorization Copilot)
- [2] Sample Historical Project - Woodgrove Medical Imaging Authorization Agent — Woodgrove Medical Group, Regional healthcare provider (DemoData/Past Projects/Woodgrove Medical Imaging Authorization Agent)
