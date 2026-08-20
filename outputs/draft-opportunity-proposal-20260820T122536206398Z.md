# Draft Opportunity Proposal

> Synthetic demonstration content. Review before use.

## Executive Summary
Contoso Health aims to reduce prior-authorization (PA) preparation time from ~2 hours to ~15 minutes while ensuring staff only use approved clinical records, all patient data stays inside the Contoso Microsoft tenant, and every PA submission is explicitly approved by a clinician.

We recommend a source-grounded, deterministic agent workflow that retrieves only approved payer-policy and clinical sources, assembles a cited PA packet draft, runs completeness checks, and routes the packet through a mandatory clinician approval gate before any submission step. Similar architectures reduced median preparation time from 118→17 minutes in a prior cardiology/orthopedics pilot while keeping PHI inside the customer tenant and requiring clinician approval. [0]

## Customer Situation
- Current PA preparation is highly manual (searching EHR notes/results, payer criteria, internal procedures), creating rework when evidence is missing or criteria are outdated. This pattern drove 94–118 minute preparation times in similar healthcare authorization workflows. [0][2]
- Contoso requires:
  - **Approved-records only** (bounded to a controlled, attested corpus). [0]
  - **Tenant-contained PHI** (no data movement outside the Microsoft tenant boundary). [0][2]
  - **Clinician approval for every submission** (authenticated, auditable approval). [0][2]

## Recommended Architecture
1. **Intake & work item creation (PA request)**
   - Create/receive a PA work item containing patient MRN/encounter/order identifiers and payer + procedure metadata.
   - *Recommendation/assumption:* Use an existing work queue (e.g., Dynamics 365 or internal system) to track state, SLA, and exceptions.
2. **Retrieve approved payer criteria and internal procedures (grounded RAG)**
   - Index only approved payer policies, criteria PDFs, and internal SOPs in **Azure AI Search** and ground retrieval with **Foundry IQ**. [0][2]
   - Enforce metadata filters (payer, plan, effective date, specialty) to reduce retrieval of superseded criteria (lesson learned). [2]
3. **Retrieve approved clinical evidence (read-only)**
   - Pull minimum-necessary clinical context through **Azure Health Data Services (FHIR)** using read-only tools (orders, diagnoses, relevant observations, prior therapies). [0][2]
   - Apply field filtering to limit PHI exposure per step. [2]
4. **Deterministic workflow orchestration (agent with bounded steps)**
   - Implement the multi-step PA workflow using **Microsoft Agent Framework** hosted on **Foundry Agent Service** (policy retrieval → evidence collection → completeness rules → packet drafting). [0][1][2]
   - Treat retrieved text as untrusted input; prevent documents from changing workflow policy (prompt-injection defenses/output validation). [2]
5. **Completeness & safety checks (non-clinical rules)**
   - Run explicit checks for required fields/evidence per payer checklist (e.g., diagnosis, imaging results, therapy history) using deterministic logic.
   - *Recommendation/assumption:* Implement the rules in **Azure Functions** for testability and versioning; route failures to a human work queue. This mirrors a proven pattern for non-clinical completeness logic. [2]
6. **Packet drafting with citations (no autonomous submission)**
   - Generate a PA packet draft (forms + narrative) that includes:
     - Evidence checklist (present/missing)
     - Citations to payer criteria and clinical sources for each claim
     - Clear “unknown / not found” flags
   - Maintain the boundary that the agent drafts but does not make coverage decisions (safety control). [1]
7. **Mandatory clinician approval gate**
   - Route the draft to the responsible clinician for authenticated approval via **Power Automate**; block any submission action until approval is recorded. [0][2]
   - Capture approval rationale/overrides and preserve an immutable audit trail. [0]
8. **Submission handoff (post-approval)**
   - *Recommendation/assumption:* Keep payer portal/API submission outside the agent initially (manual or tightly governed integration), consistent with prior lessons to stabilize quality before automation. [0]
   - If/when automating submission, front it with **Azure API Management** and scoped credentials. [0]

## Microsoft Services Used
- Microsoft Foundry, Microsoft Agent Framework, Foundry Agent Service, Foundry IQ [0][1][2]
- Azure AI Search [0][1][2]
- Azure Health Data Services (FHIR) [0][1][2]
- Power Automate (clinician approval workflow) [0][1][2]
- Microsoft Entra ID (RBAC, conditional access) [0][1][2]
- Azure Key Vault (secrets, keys), Managed Identities [0][1][2]
- Azure Monitor + Application Insights (traceability/telemetry) [0][1][2]
- Microsoft Purview (classification, governance) [0][1][2]
- *Optional/recommended as needed:* Azure Functions and Azure Service Bus for rules + resilient queues. [2]
- *Optional/recommended as needed:* Azure API Management for payer integrations. [0]

## Implementation Timeline
| Phase | Timing | Deliverables |
|---|---:|---|
| 1. Discovery, governance, and baseline | Weeks 1–2 | Current-state mapping; baseline time study; risk classification; clinician-in-the-loop definition; approved-source inventory and owners. (Discovery + baseline patterns used previously.) [2] |
| 2. Data + knowledge preparation | Weeks 3–5 | FHIR read-only access patterns; minimum-necessary query set; payer-policy/SOP ingestion into Azure AI Search with effective-date metadata. (Knowledge preparation and metadata lessons.) [2] |
| 3. Agent workflow build | Weeks 6–8 | Bounded Agent Framework workflow in Foundry Agent Service; retrieval + citations; deterministic completeness checks; exception routing. [0][2] |
| 4. Evaluation, red-team, and controls | Weeks 9–10 | Groundedness and safety evaluations; prompt-injection testing; audit trace validation; approval-gate enforcement tests. (Evaluation + red-team patterns.) [2] |
| 5. Supervised pilot | Weeks 11–12 | Pilot for 1–2 specialties/payers; clinician approval workflow live; measurement vs baseline; go/no-go criteria. (Supervised pilot pattern.) [2] |
| 6. Controlled rollout + handover | Weeks 13–14 | Expanded specialty coverage; runbook; monitoring dashboards; governance cadence; operational handover. (Controlled rollout and handover pattern.) [0] |

## Security Considerations
- **Tenant-contained PHI:** Use private networking/private endpoints and network-restricted Search + FHIR services to keep data inside the approved boundary. [2]
- **Identity & access:** Enforce Entra ID RBAC + conditional access; separate roles for authorization staff, clinicians, and admins (least privilege). [0][1]
- **Secrets & encryption:** Managed identities for service-to-service calls; Key Vault for secrets; encryption in transit/at rest; *recommendation:* customer-managed keys where required. [0][2]
- **Minimum necessary:** Limit FHIR queries and field sets per step to reduce PHI exposure. [0][2]
- **Untrusted retrieval defense:** Treat retrieved documents as untrusted input; implement prompt-injection defenses and output validation so retrieved text cannot change workflow policy. [0][2]
- **Clinician approval enforcement:** The system must not submit without authenticated clinician approval. [0][2]

## Governance Controls
- **Approved source corpus & freshness:** Named content owners approve and periodically attest payer-policy freshness (e.g., every 30 days). [1]
- **Clinical ownership of automation boundaries:** Named clinical owner approves what is automated vs always-human. [2]
- **End-to-end traceability:** Log every retrieval, citation, tool call, draft, approval, and submission handoff for auditability. [0][1]
- **Versioning:** Version prompts, policies, evaluation sets, and releases; define rollback criteria. [2]
- **Exception handling:** Failed groundedness, missing evidence, or injection detections route to human-only handling. [1]
- **Quality cadence:** Monthly quality reviews covering groundedness, completeness, access violations, and policy freshness. [0]

## Success Metrics
*Targets are recommendations for Contoso and must be validated in pilot; prior results are not guarantees.*
- **Preparation time:** Median minutes from work item start → clinician-ready draft.
  - Reference outcomes: 118→17 minutes and 94→16 minutes achieved in similar pilots. [0][2]
- **Clinician accountability:** 100% of submitted packets have authenticated clinician approval recorded. [0][2]
- **Citation coverage:** % of packet assertions supported by citations to approved sources (reference levels reached 98–99%). [0][2]
- **First-pass completeness:** % of packets meeting payer checklist without rework (reference completeness reached 96%). [0]
- **Safety/privacy:** # of high-severity privacy/safety incidents (reference pilot recorded none at severity one). [0]

## Lessons Applied
- **Policy ownership and freshness beats prompt tuning:** Assign payer-policy owners and enforce effective-date metadata to prevent outdated criteria retrieval. [0][2]
- **Specialty/payer-specific retrieval improves precision:** Use payer-specific checklists and filters rather than one broad corpus. [0][1]
- **Do not delegate high-risk logic to the model:** Use explicit rules for urgency/completeness; keep coverage decisions with clinicians. [2][1]
- **Keep submission automation gated:** Maintain submission outside the agent until quality metrics stabilize, while still accelerating draft preparation. [0]

## Future Expansion Opportunities
- Extend to additional specialties (e.g., imaging, oncology) using the same grounded pattern. [0][2]
- Add denial appeal drafting with legal/clinical approval workflow. [0][2]
- Implement policy-change detection and regression tests for payer updates. [2]
- Add operational analytics for recurring documentation gaps by facility/specialty and workload forecasting from the queue. [0][2]

## Sources

- [0] Sample Historical Project - Northwind Health Prior Authorization Agent — Northwind Health Network, Healthcare provider (DemoData/Past Projects/Northwind Health Prior Authorization Agent)
- [2] Sample Historical Project - Fabrikam Specialty Care Authorization Copilot — Fabrikam Specialty Care Alliance, Specialty healthcare provider (DemoData/Past Projects/Fabrikam Specialty Care Authorization Copilot)
- [1] Sample Historical Project - Woodgrove Medical Imaging Authorization Agent — Woodgrove Medical Group, Regional healthcare provider (DemoData/Past Projects/Woodgrove Medical Imaging Authorization Agent)
