# Draft Opportunity Proposal

> Synthetic demonstration content. Review before use.

## Executive Summary

This proposal responds to the healthcare RFP by recommending a tenant-contained, source-grounded agent solution that accelerates prior-authorization/authorization packet preparation while ensuring **clinician approval remains mandatory** before any submission or decision. The approach uses a **Microsoft Agent Framework workflow** orchestrated in **Microsoft Foundry Agent Service**, grounded on approved payer/clinical guidance with citations, and integrated into the customer’s existing work-queue processes (recommendation), reflecting proven implementation patterns in similar healthcare authorization copilots [0][1][2].

## Customer Situation

The RFP indicates a healthcare need to streamline authorization-related administrative burden while maintaining clinical accountability and strong PHI protections (assumption). Common constraints and requirements for this pattern include:
- Keeping PHI inside the customer’s tenant boundary [0][1].
- Grounding outputs in approved payer policies/clinical guidance with citations to reduce outdated or inconsistent criteria usage [0][1][2].
- Routing every packet through authenticated human review—typically a pharmacist or responsible clinician—before submission [0][1][2].
- Establishing complete audit history for retrieval, drafting, approvals, and exceptions [1][2].

## Recommended Architecture

1. **Intake & work item creation**
   - Create/receive authorization request and assign to an operations queue (recommendation).
   - Track status, ownership, and SLA targets in a case/work-item system (pattern: Dynamics 365 Customer Service used for work tracking) [0].

2. **Policy & guidance retrieval (grounded RAG)**
   - Index approved payer policies, internal procedures, and clinical guidance in **Azure AI Search** with **Foundry IQ** so the agent can retrieve authoritative sources and attach citations [0][1][2].
   - Apply **specialty/payer-specific retrieval filters and checklists** to increase precision (pattern) [0][1].

3. **Clinical context retrieval (read-only)**
   - Retrieve minimum-necessary clinical data from EHR via **Azure Health Data Services (FHIR)** using read-only access (pattern) [0][1][2].
   - Apply field/record scoping to limit PHI exposure in each workflow step (pattern) [2].

4. **Deterministic workflow orchestration**
   - Implement a bounded-step workflow in **Microsoft Agent Framework** hosted on **Foundry Agent Service** to separate:
     - policy matching,
     - evidence collection,
     - completeness checks,
     - packet drafting,
     - approval routing [0][1][2].

5. **Completeness rules & exception handling**
   - Implement non-clinical completeness rules in a deterministic compute component (recommendation; pattern: Azure Functions used for completeness rules) [2].
   - Route missing-evidence, low-groundedness, or conflicting-record cases to a human-only exception queue (pattern) [0][1].

6. **Human approval (clinician retained) and submission boundary**
   - Require authenticated clinician (or pharmacist where applicable) approval via an approval workflow before any packet is marked ready for submission [0][1][2].
   - Keep portal submission/integration outside the agent until quality/approval thresholds are stable (pattern) [1].

7. **Observability & audit**
   - Capture end-to-end traceability of retrievals, citations, tool calls, drafts, approvals, and final actions (pattern) [1][2].
   - Monitor with Azure Monitor / Application Insights (pattern) [0][1][2].

## Microsoft Services Used

- Microsoft Foundry [0][1][2]  
- Microsoft Agent Framework [0][1][2]  
- Foundry Agent Service [0][1][2]  
- Foundry IQ [0][1][2]  
- Azure AI Search [0][1][2]  
- Azure Health Data Services (FHIR service) [0][1][2]  
- Power Automate (approvals) [0][1][2]  
- SharePoint (policy/procedure content repository) [0][1][2]  
- Microsoft Entra ID [0][1][2]  
- Azure Key Vault [0][1][2]  
- Azure Monitor + Application Insights [0][1][2]  
- Microsoft Purview [0][1][2]  
- (Recommended as needed) Dynamics 365 Customer Service for work-item tracking [0]  
- (Recommended as needed) Azure API Management for payer/portal integrations governance [1]  
- (Recommended as needed) Azure Functions and Azure Service Bus for rules/queues and resiliency [2]

## Implementation Timeline

| Phase | Timing | Deliverables |
|---|---:|---|
| Discovery, process mapping, and clinical-risk mapping | Weeks 1–2 (recommendation; aligns to similar discovery phases) [1][2] | Workflow mapping; role definitions; initial success metrics baseline plan; automation boundaries with clinician sign-off (recommendation) |
| Governance and data/knowledge readiness | Weeks 3–6 (recommendation; aligns to governance + connections phases) [0][1] | Source corpus definition and ownership; SharePoint ingestion; Azure AI Search indexing with Foundry IQ grounding [0][1][2]; FHIR connectivity plan and minimum-necessary data scope [1][2] |
| Agent workflow build (bounded steps) | Weeks 7–10 (recommendation; aligns to workflow/agent development durations) [0][1][2] | Agent Framework workflow in Foundry Agent Service [0][1][2]; completeness checks (recommendation; Functions pattern) [2]; draft packet templates with citation formatting (recommendation) |
| Evaluation, safety testing, and red-team exercises | Weeks 11–12 (recommendation; aligns to safety/evaluation emphasis) [0][2] | Groundedness and completeness evaluation set (pattern) [1]; prompt-injection and untrusted-document handling validation (pattern) [1][2]; rollback criteria (pattern) [0] |
| Supervised pilot | Weeks 13–14 (recommendation; aligns to supervised pilot phases) [0][1][2] | Pilot with selected specialty/payer scope (recommendation); clinician approval workflow in Power Automate [0][1][2]; operational dashboarding and audit trails [1][2] |
| Controlled rollout and handover | Weeks 15–16 (recommendation; aligns to controlled rollout patterns) [0][1] | Production hardening; runbooks; monthly quality review cadence (pattern) [1]; scale plan and backlog for next specialties (recommendation) |

## Security Considerations

- **Identity & access**
  - Enforce role-based access with Microsoft Entra ID (pattern) [0][1][2].
  - Separate least-privilege groups for operations staff, clinicians/pharmacists, and admins (pattern) [0].

- **PHI containment and network controls**
  - Keep data inside the customer’s tenant boundary (pattern) [0][1][2].
  - Use managed identities, private endpoints/private networking where applicable, and encrypt data in transit/at rest (pattern) [0][1][2].
  - Limit FHIR queries to minimum-necessary scope (pattern) [1].

- **Secrets and logging**
  - Store secrets in Azure Key Vault (pattern) [0][1][2].
  - Exclude clinical payloads from logs where feasible (pattern) [0].

- **Model safety and untrusted content handling**
  - Treat retrieved documents as untrusted input and implement prompt-injection defenses/output validation (pattern) [1][2].
  - Enforce a hard boundary: the agent cannot determine coverage or approve treatment; humans retain decision authority (pattern) [0].

## Governance Controls

- **Clinical governance**
  - Establish a clinical AI review board (or equivalent) to approve use cases, risk classification, evaluation thresholds, and rollback criteria (pattern) [0].
  - Assign a named clinical owner to approve automation boundaries and expansion beyond the pilot (pattern) [2].

- **Content governance**
  - Require content owners to attest payer-policy freshness on a defined cadence (pattern: every 30 days used) [0].
  - Ensure source documents include effective dates and payer metadata to reduce superseded retrieval risk (pattern) [2].

- **Auditability and quality operations**
  - Trace every retrieval, citation, tool call, draft, approval, and final submission action (pattern) [1].
  - Version prompts, policies, evaluations, and agent releases (pattern) [2].
  - Route failures (missing evidence, low groundedness, prompt-injection detection) to human-only handling (pattern) [0].

## Success Metrics

Measured during pilot and rollout (recommendation). Historical results from other organizations are **not guaranteed** and are provided as reference only [0][1][2].

- Median authorization packet preparation time (tracked pre/post; historical examples observed reductions) [0][1][2]
- Packet completeness rate / first-pass acceptance (historical examples tracked and improved) [0][1]
- Citation coverage for evidence statements (historical examples achieved high coverage) [0][1][2]
- Rework rate due to missing documentation (historical example tracked reductions) [0]
- Percentage of submissions with authenticated clinician approval (target 100%; historical pattern maintained) [0][1][2]
- Privacy/safety incident rate (historical pilots tracked for high-severity incidents) [1]

## Lessons Applied

- Apply **specialty/payer-specific retrieval filters, checklists, and evaluation sets** to improve precision and expose missing evidence early [0][1].
- Favor **clear missing-evidence explanations and visible evidence checklists** to speed clinician review and increase trust [0][2].
- Keep workflow embedded in the **existing work queue** to drive adoption rather than creating a parallel interface (pattern) [0].
- Do not delegate **urgency classification** or other deterministic routing decisions to the language model; implement explicit rules (pattern) [2].
- Keep **portal submission outside the agent** until approval and completeness performance is stable (pattern) [1].
- Emphasize **policy ownership and freshness** as a primary quality driver (pattern) [1].

## Future Expansion Opportunities

- Extend to additional specialties (e.g., oncology, imaging, referrals) using the same governed workflow pattern [1][2].
- Add policy-change detection and impact summaries with regression tests against evaluation sets (pattern) [0][2].
- Add denial-reason analytics and documentation-gap insights for operational improvement (pattern) [0][1][2].
- Implement a governed appeal-drafting workflow with legal and clinical approval gates (pattern) [0][1][2].
- Add proactive renewal alerts and patient-status notifications within the governed work-queue process (pattern) [0].

## Sources

- [0] Sample Historical Project - Fabrikam Specialty Care Authorization Copilot — Fabrikam Specialty Care Alliance, Specialty healthcare provider (DemoData/Past Projects/Fabrikam Specialty Care Authorization Copilot)
- [1] Sample Historical Project - Northwind Health Prior Authorization Agent — Northwind Health Network, Healthcare provider (DemoData/Past Projects/Northwind Health Prior Authorization Agent)
- [2] Sample Historical Project - Woodgrove Medical Imaging Authorization Agent — Woodgrove Medical Group, Regional healthcare provider (DemoData/Past Projects/Woodgrove Medical Imaging Authorization Agent)
