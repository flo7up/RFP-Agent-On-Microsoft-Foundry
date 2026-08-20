# Draft Opportunity Proposal

> Synthetic demonstration content. Review before use.

## Executive Summary
Contoso Health can reduce prior-authorization (PA) preparation time by implementing a tenant-contained, source-grounded “PA Preparation Agent” that assembles an evidence checklist and drafts a submission packet for clinician review and approval.

This approach follows successful patterns used in prior healthcare PA agent deployments that reduced median preparation time from 118 to 17 minutes while keeping PHI inside the Azure tenant and requiring clinician approval for every packet [0], and from 94 to 16 minutes with authenticated clinician approval for every submission [2]. These results are historical references, not guaranteed outcomes for Contoso.

## Customer Situation
Contoso Health’s staff currently spends roughly two hours preparing a PA submission by:
- Finding relevant clinical notes and diagnostics across approved record systems.
- Locating payer criteria and internal procedures.
- Manually assembling supporting evidence and completing payer-facing forms.

Constraints and requirements:
- Use only approved clinical records and approved payer/procedure guidance as sources.
- Keep patient data inside Contoso’s Microsoft tenant boundary.
- Require an authenticated clinician to approve every PA submission.

Assumptions (to be validated during discovery): clinical data can be accessed via standards-based APIs (e.g., FHIR) and payer criteria/internal SOPs can be curated into an approved knowledge corpus (e.g., SharePoint), similar to prior implementations [0][2].

## Recommended Architecture
1. **Work intake and case creation**: A PA request is created from the existing work queue (recommended: Dynamics 365 Customer Service if Contoso needs queueing and SLA management, as used in specialty authorization workflows [1]; otherwise integrate with the current ticketing/EMR worklist).
2. **Identity and access enforcement**: Microsoft Entra ID controls access with role separation for PA specialists vs. clinicians vs. admins, reflecting least-privilege approaches used in prior deployments [1].
3. **Approved-source retrieval (grounding layer)**:
   - Index approved payer criteria, internal SOPs, and templates in **Azure AI Search** with strict source curation and metadata (payer, specialty, effective date) to avoid superseded criteria retrieval, a documented lesson learned [2].
   - Use **Foundry IQ** to ground agent outputs in retrieved sources with citations, as done in prior PA solutions [0][1][2].
4. **Clinical record access (read-only tools)**:
   - Expose approved clinical records via **Azure Health Data Services (FHIR service)** using read-only scoped queries and minimum-necessary field selection, consistent with prior architectures [0][2].
5. **Deterministic agent workflow orchestration**:
   - Implement a bounded, stepwise workflow with **Microsoft Agent Framework** hosted in **Foundry Agent Service**, separating: policy retrieval, evidence extraction, completeness checks, and drafting (mirroring prior proven patterns) [0][1][2].
6. **Completeness and rules checks (non-clinical)**:
   - Use **Azure Functions** (recommended) to run deterministic completeness rules (required attachments, diagnosis/procedure codes present, date ranges, payer-specific checklist), aligning with prior imaging authorization implementations [2].
7. **Draft packet generation (reviewable, not final)**:
   - The agent generates a draft packet containing:
     - A payer-specific evidence checklist.
     - A structured summary with links/citations to each supporting record.
     - Identified gaps and required follow-ups.
   - The agent is explicitly not permitted to make coverage decisions, consistent with safety boundaries used previously [1].
8. **Mandatory clinician approval gate**:
   - Route the draft to the responsible clinician using **Power Automate Approvals**, requiring authenticated approval before any submission step proceeds, as implemented in multiple prior projects [0][1][2].
   - Capture approval/override rationale for auditability (recommended; aligns to retained approval and override reasons governance patterns) [2].
9. **Submission and audit trail**:
   - After approval, either:
     - (Recommended initially) staff submits via payer portal manually, while the system records the final approved packet; prior teams kept portal submission outside the agent until stability targets were met [0].
     - (Optional later) integrate payer submission via APIs behind **Azure API Management** governance, as used in prior PA integrations [0].
10. **Observability and traceability**:
   - Use **Azure Monitor** and **Application Insights** to trace each retrieval, tool call, draft, and approval event (as used for end-to-end tracing in earlier deployments) [0][1].

## Microsoft Services Used
- Microsoft Foundry, Microsoft Agent Framework, Foundry Agent Service, Foundry IQ [0][1][2]
- Azure AI Search [0][1][2]
- Azure Health Data Services (FHIR service) [0][1][2]
- Power Automate (Approvals) [0][1][2]
- Microsoft Entra ID [0][1][2]
- Azure Key Vault [0][1][2]
- Azure Monitor and Application Insights [0][1][2]
- Microsoft Purview [0][1][2]
- (Recommended as needed) Azure Functions, Azure Service Bus for resilient queues [2]
- (Optional for case management) Dynamics 365 Customer Service [1]
- (Optional for governed integrations) Azure API Management [0]
- SharePoint for approved policy/SOP repository [0][1][2]

## Implementation Timeline
| Phase | Timing | Deliverables |
|---|---:|---|
| Discovery, risk mapping, and baseline | Weeks 1–2 | Current-state process map; baseline cycle-time and rework metrics; clinical/compliance risk review and automation boundaries (similar discovery and risk mapping timing has been used previously) [0][2] |
| Data and knowledge readiness | Weeks 3–6 | FHIR read-only access patterns; approved source corpus in SharePoint; Azure AI Search index with payer/specialty/effective-date metadata (metadata to prevent superseded criteria retrieval reflects lessons learned) [2] |
| Agent workflow build (bounded steps) | Weeks 7–10 | Agent Framework workflow in Foundry Agent Service; Foundry IQ grounding; deterministic completeness rules (Functions); draft packet template and evidence checklist [0][1][2] |
| Evaluation, red-team, and clinician UAT | Weeks 11–12 | Groundedness evaluation set by specialty/payer; prompt/versioning; prompt-injection and safety tests (red-team testing phase has been used in prior imaging authorization work) [2] |
| Pilot rollout (single specialty/payer set) | Weeks 13–14 | Supervised pilot; Power Automate approval gate live; operational dashboards; go/no-go criteria for broader rollout (prior teams ran supervised pilots before expansion) [2] |

## Security Considerations
- **Tenant boundary & private networking**: Keep PHI within Contoso’s tenant; use private endpoints and network-restricted services (Search/FHIR) as used to keep data inside approved boundaries [2].
- **Least privilege**: Role-based access and separation of duties with Entra ID groups for PA specialists, clinicians, and admins (approach used in prior authorization copilots) [1].
- **Secrets and encryption**: Store secrets in Key Vault; use encryption in transit/at rest; consider customer-managed keys for high-sensitivity workloads (used in prior projects) [2].
- **Minimum necessary data**: Apply field filtering and scoped FHIR queries to reduce PHI exposure [0][2].
- **Prompt-injection and untrusted input**: Treat retrieved documents as untrusted; prevent retrieved text from altering workflow policy; apply output validation and injection defenses (explicitly implemented previously) [0][2].
- **Mandatory clinician approval**: Enforce that no packet can be submitted without authenticated clinician approval (a hard control used across prior implementations) [0][2].

## Governance Controls
- **Approved-source governance**: Clinical/compliance owners approve the source corpus and evaluation set; content owners attest payer-policy freshness on a regular cadence (e.g., every 30 days) as used previously [0][1].
- **Automation boundary ownership**: Assign a named clinical owner for each automation boundary and release, matching governance practices from prior deployments [2].
- **Versioning and release controls**: Version prompts, policies, and evaluations; require go/no-go review before expanding beyond pilot [2].
- **Auditability**: Trace every retrieval, citation, tool call, draft, approval, override, and final packet artifact; retain approval evidence for compliance (end-to-end tracing and retention were key controls in earlier projects) [0][2].
- **Exception handling**: Route missing-evidence cases and groundedness failures to a human-only queue, consistent with prior “high-risk exceptions” handling [0][1].

## Success Metrics
Measured during baseline and pilot; targets are recommended and should be validated against Contoso’s workflow complexity.
- **Median PA prep time**: Track reduction from ~120 minutes toward 15 minutes (aspirational goal); comparable pilots achieved 118→17 minutes [0] and 94→16 minutes [2].
- **Clinician approval rate**: 100% of submitted packets have authenticated clinician approval (required; prior projects achieved this) [0][2].
- **First-pass completeness / acceptance**: Increase packet completeness (e.g., target ≥95% completeness); prior work reported 96% completeness [0] and improved first-pass acceptance by 22 percentage points [1].
- **Citation coverage**: ≥95% of packet assertions linked to approved sources; prior implementations reported 97–99% citation coverage [1][2].
- **Privacy and safety incidents**: Zero severity-one privacy/safety incidents (prior pilot reported none) [0].

## Lessons Applied
- **Policy ownership and curation are critical**: Governance over payer policy content and ownership mattered more than prompt tuning in prior PA deployments [0].
- **Specialty/payer-specific evaluation improves quality**: Specialty-specific evaluation sets and retrieval filters exposed missing evidence early and improved precision [0][1].
- **Metadata prevents superseded criteria**: Effective dates and payer metadata reduced retrieval of outdated criteria [2].
- **Keep submission outside the agent until stable**: Prior teams kept portal submission out of the agent until approval and completeness targets were stable for multiple weeks [0].

## Future Expansion Opportunities
- Extend the workflow to additional specialties (e.g., oncology, imaging, specialty meds), as demonstrated in prior roadmaps [0][2].
- Add denial appeal drafting with governed clinical/legal approval, as identified as a next step in prior programs [0][2].
- Add policy-change detection and regression tests to identify when payer criteria changes require updates to checklists and evaluations [2].
- Add operational analytics to identify recurring documentation gaps by specialty or facility and feed upstream documentation guidance [0][2].

## Sources

- [0] Sample Historical Project - Northwind Health Prior Authorization Agent — Northwind Health Network, Healthcare provider (DemoData/Past Projects/Northwind Health Prior Authorization Agent)
- [2] Sample Historical Project - Fabrikam Specialty Care Authorization Copilot — Fabrikam Specialty Care Alliance, Specialty healthcare provider (DemoData/Past Projects/Fabrikam Specialty Care Authorization Copilot)
- [1] Sample Historical Project - Woodgrove Medical Imaging Authorization Agent — Woodgrove Medical Group, Regional healthcare provider (DemoData/Past Projects/Woodgrove Medical Imaging Authorization Agent)
