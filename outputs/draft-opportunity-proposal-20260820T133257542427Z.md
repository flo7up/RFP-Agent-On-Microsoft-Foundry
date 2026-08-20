# Draft Opportunity Proposal

> Synthetic demonstration content. Review before use.

## Executive Summary
Contoso Health wants to reduce prior-authorization (PA) preparation time from ~2 hours to ~15 minutes while ensuring: (1) staff work only from approved clinical records and payer/operational guidance, (2) patient data remains inside Contoso’s tenant, and (3) every submission is explicitly approved by a credentialed clinician.

We recommend a clinician-in-the-loop, source-grounded PA “preparation agent” implemented as a deterministic Microsoft Agent Framework workflow hosted on Microsoft Foundry Agent Service, using Foundry IQ with Azure AI Search for citation-backed retrieval over approved sources, and Azure Health Data Services (FHIR) for read-only access to clinical records—mirroring proven patterns used for prior authorization preparation while keeping PHI inside the customer’s Azure tenant and enforcing authenticated clinician approval before any packet can be submitted. [0]

## Customer Situation
PA specialists and clinical staff are spending significant time assembling clinical evidence and payer-required fields, leading to delays, rework, and inconsistent packet completeness—an operating model similar to other healthcare organizations that manually searched EHR content, payer criteria documents, and internal procedures before portal entry. [0]

Contoso’s non-negotiables are:
- **Approved sources only**: PA packets must be prepared from approved clinical records and governed payer/procedure content. [0]
- **Tenant-contained PHI**: no patient data leaves Contoso’s tenant boundary. [0]
- **Clinician accountability**: every submission requires clinician approval (no “auto-submit”). [0]

Assumption: Contoso can provide read access to clinical data (e.g., via FHIR APIs) and can identify an initial specialty/service line for a controlled pilot (e.g., cardiology, orthopedics, imaging, or specialty meds).

## Recommended Architecture
1. **Intake & work orchestration**
   - Create a PA work item with required metadata (payer, service line, ordering provider, due date).
   - Route work items into a controlled queue for agent processing and human review (recommendation: use Dynamics 365 Customer Service for work tracking, consistent with prior deployments). [1]

2. **Approved-source corpus and retrieval**
   - Index approved payer policies, checklists, and internal operating procedures from SharePoint into **Azure AI Search** with document-level permissions.
   - Use **Foundry IQ** to ground outputs with citations from this approved corpus and to prevent non-cited drafting. [0]

3. **Read-only clinical record access (approved clinical records)**
   - Expose required clinical context through **Azure Health Data Services (FHIR)** via read-only tools (minimum necessary queries).
   - Normalize and filter patient context fields supplied to the workflow to reduce PHI exposure while preserving evidence completeness (e.g., problem list, orders, key observations, recent notes). This pattern aligns with prior authorization implementations using FHIR context as an approved clinical record source. [0]

4. **Deterministic PA preparation workflow (agentic, but bounded)**
   - Implement a stepwise **Microsoft Agent Framework** workflow hosted in **Foundry Agent Service** that:
     1) retrieves payer criteria and internal checklist content,
     2) retrieves the relevant clinical evidence,
     3) checks for missing required evidence via explicit rules,
     4) drafts a PA packet narrative and evidence list with citations,
     5) generates an “evidence checklist” for fast clinician review.
   - This separation of retrieval, evidence collection, completeness checking, and drafting follows a proven approach used for authorization copilots to improve precision and safety. [1]

5. **Completeness checks and exception handling**
   - Apply deterministic, non-clinical validation rules (e.g., required fields present, document recency, payer-specific attachments) using **Azure Functions**.
   - If the workflow detects missing evidence or conflicting records, it routes the case to a human-only queue and requires remediation before approval—matching prior implementations that forced human handling on missing evidence. [1]

6. **Clinician approval gate (mandatory)**
   - Use **Power Automate approvals** to route the drafted packet and evidence checklist to the responsible clinician.
   - Enforce a hard gate: no packet can be finalized or transmitted without authenticated clinician approval, consistent with prior PA implementations. [0]

7. **Submission integration (kept outside the agent until stable)**
   - Recommendation: initially keep payer portal submission as a manual step performed after approval, reflecting lessons learned to keep portal submission outside the agent until quality and completeness are stable. [0]
   - If Contoso later chooses to automate submission, govern outbound integrations through **Azure API Management** (for APIs) and/or controlled automation with auditable steps. [0]

8. **Monitoring, auditability, and classification**
   - Use **Azure Monitor** and **Application Insights** to trace each retrieval, tool call, draft, approval, and finalization event for auditability. [0]
   - Use **Microsoft Purview** for sensitive data classification and policy enforcement across content sources. [0]

## Microsoft Services Used
- Microsoft Foundry, Microsoft Agent Framework, Foundry Agent Service, Foundry IQ [0]
- Azure AI Search [0]
- Azure Health Data Services (FHIR) [0]
- Power Automate (Approvals) [0]
- Microsoft Entra ID [0]
- Azure Key Vault [0]
- Azure Monitor, Application Insights [0]
- Microsoft Purview [0]
- SharePoint (approved policy/procedure content source) [0]
- (Recommendation) Dynamics 365 Customer Service for case/work-item tracking [1]
- (Optional for future) Azure Functions, Azure API Management [0]

## Implementation Timeline
| Phase | Timing | Deliverables |
|---|---:|---|
| Discovery & clinical risk mapping | Weeks 1–2 | Current-state process map, baseline timing, specialty selection, approval workflow definition, risk controls and “no-autosubmit” boundary documented. [0] |
| Data & knowledge onboarding | Weeks 3–6 | FHIR read-only access patterns, approved-source corpus in SharePoint, Azure AI Search index with permissions, payer metadata (effective dates) and checklists. [0] |
| Agent workflow build | Weeks 7–10 | Agent Framework workflow in Foundry Agent Service; Foundry IQ grounding; completeness rules; evidence checklist output; clinician approval integration. [0] |
| Evaluation & red-team testing | Weeks 11–12 | Groundedness/citation tests, missing-evidence forcing, prompt-injection defenses, operational runbooks and rollback criteria. [2] |
| Supervised pilot | Weeks 13–14 | Pilot with one specialty/service line; measured prep time and completeness; weekly clinical review; go/no-go gates for expansion. [0] |

## Security Considerations
- **Identity & access**: Use Microsoft Entra ID with least privilege and role separation (PA specialists vs clinicians vs admins). [1]
- **Tenant-contained PHI**: Use private endpoints and network restrictions for search and FHIR services; use encryption in transit/at rest and (recommendation) customer-managed keys where required. [2]
- **Secrets management**: Store secrets in Azure Key Vault; use managed identities for service-to-service access. [0]
- **Minimum necessary access**: Restrict FHIR queries and filter clinical fields passed into tools/workflow steps. [0]
- **Prompt-injection and untrusted content handling**: Treat retrieved documents as untrusted input; use prompt-injection defenses and output validation so retrieved content cannot change workflow policy. [2]
- **Submission safety**: Enforce that the agent cannot submit/finish without clinician approval. [0]

## Governance Controls
- **Approved-source governance**: Named clinical/compliance owners approve the source corpus and maintain payer-policy freshness attestations on a fixed cadence (e.g., every 30 days). [1]
- **Versioning and release management**: Version prompts, policies, evaluations, and agent releases; define rollback criteria. [2]
- **Audit trail**: Record every retrieval, citation, tool call, draft, approval, override reason, and final output for compliance review. [0]
- **Quality gates**: Require citations for all evidence; failed groundedness or missing-evidence checks force human-only handling. [1]
- **Operational reviews**: Establish monthly quality reviews for groundedness, completeness, access violations, and payer-policy freshness. [0]

## Success Metrics
Targets are recommendations; measured results will vary by specialty, payer mix, and source quality.
- **Preparation time**: Reduce median PA preparation time toward 15–20 minutes (similar pilots achieved 118→17 minutes and 105→19 minutes). [0] [1]
- **Clinician accountability**: 100% of submitted packets have authenticated clinician approval. [0]
- **Citation coverage**: ≥97–99% of generated packet statements include citations to approved sources (prior implementations reached 97–99%). [1] [2]
- **Packet completeness**: Increase first-pass completeness/acceptance (e.g., prior deployments reported 96% completeness and +22 percentage point acceptance improvement). [0] [1]
- **Safety/privacy**: Zero severity-one privacy/safety incidents during pilot (as observed in a prior pilot). [0]

## Lessons Applied
- **Keep submission outside the agent until stable**: Prior teams delayed portal submission automation until completeness and approval targets were stable for multiple weeks; Contoso should follow the same staged approach. [0]
- **Policy ownership beats prompt tuning**: Strong content ownership and payer-specific checklists materially improved retrieval precision and outcomes. [0]
- **Specialty-specific retrieval and evaluation**: Launching broadly reduced precision; specialty filters and evaluation sets exposed missing evidence early and improved trust. [1]
- **Use explicit rules for operational classification**: Urgency/priority classification required explicit rules and should not be delegated to the language model. [2]

## Future Expansion Opportunities
- Expand to additional specialties (e.g., imaging, oncology, specialty meds) after pilot success. [0]
- Add denial analytics and missing-document pattern reporting to reduce upstream documentation gaps. [2]
- Implement policy-change detection and regression testing against evaluation sets to keep payer criteria current. [2]
- Add governed appeal packet drafting with legal/clinical approval workflows. [0]

## Sources

- [0] Sample Historical Project - Northwind Health Prior Authorization Agent — Northwind Health Network, Healthcare provider (DemoData/Past Projects/Northwind Health Prior Authorization Agent)
- [1] Sample Historical Project - Fabrikam Specialty Care Authorization Copilot — Fabrikam Specialty Care Alliance, Specialty healthcare provider (DemoData/Past Projects/Fabrikam Specialty Care Authorization Copilot)
- [2] Sample Historical Project - Woodgrove Medical Imaging Authorization Agent — Woodgrove Medical Group, Regional healthcare provider (DemoData/Past Projects/Woodgrove Medical Imaging Authorization Agent)
