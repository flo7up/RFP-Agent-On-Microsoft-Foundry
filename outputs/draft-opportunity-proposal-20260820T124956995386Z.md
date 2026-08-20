# Draft Opportunity Proposal

> Synthetic demonstration content. Review before use.

## Executive Summary
Contoso Health wants to compress prior-authorization (PA) preparation from ~2 hours to ~15 minutes by automating evidence gathering and packet drafting—without moving patient data outside the Microsoft tenant and while requiring authenticated clinician approval for every submission.

We recommend a deterministic, clinician-in-the-loop PA preparation workflow using Microsoft Agent Framework hosted on Foundry Agent Service, grounded by Foundry IQ + Azure AI Search over **approved** payer criteria and internal procedures, and backed by read-only access to **approved clinical records** via Azure Health Data Services (FHIR). This pattern has reduced PA preparation time to the 16–19 minute range in comparable healthcare implementations while maintaining tenant isolation and mandatory clinician approval. [0][1][2]

## Customer Situation
PA specialists and clinical staff spend significant time:
- Locating the correct “approved” clinical documents (orders, notes, labs, imaging results) across EHR views and exports.
- Reconciling payer criteria with the current clinical record and identifying missing evidence.
- Copying data into payer portals and generating attachments, leading to rework when packets are incomplete.

Contoso’s non-negotiable constraints are:
- Use only approved clinical records and approved policy/procedure sources (no ad hoc web search). (Assumption: “approved” means records and documents that have passed organizational validation and are permissioned for use in PA.)
- Keep patient data inside the Contoso tenant boundary.
- Require clinician approval for every submission, with auditable accountability.

## Recommended Architecture
1. **Intake & work item creation**
   1. A PA request is created from the existing workflow (e.g., work queue system) and lands in a controlled queue (Power Automate + Dataverse or a service bus-backed queue). (Recommendation: start with one specialty and 1–2 payers.)
   2. Capture minimal identifiers (patient MRN, encounter/order IDs, payer, procedure/service, urgency flag) and route to the PA preparation workflow.

2. **Approved-source grounding layer (policies + procedures)**
   1. Index payer criteria PDFs, internal checklists, and PA SOPs in **Azure AI Search**.
   2. Use **Foundry IQ** as the retrieval layer to ensure responses and drafts are grounded in the approved corpus with citations, using payer metadata and effective dates to avoid superseded criteria. [1]

3. **Approved clinical record retrieval (read-only)**
   1. Expose clinical data via **Azure Health Data Services (FHIR service)** with least-privilege scopes and “minimum necessary” queries for the PA use case. [0]
   2. Apply field filtering so only clinically relevant sections are supplied to the drafting steps. [1]

4. **Deterministic PA preparation workflow (agent orchestration)**
   1. Implement a bounded, stepwise workflow with **Microsoft Agent Framework** hosted on **Foundry Agent Service** to:
      - Retrieve payer criteria and internal checklists.
      - Retrieve clinical evidence (orders, diagnoses, recent notes, key results).
      - Run completeness checks (rule-based) to identify missing documents.
      - Draft a PA packet (cover letter + evidence checklist + structured answers) with citations.
   2. Use **Azure Functions** for deterministic validations (required fields, attachment list, date recency rules) and to prevent the model from inventing values. [1]
   3. (Optional) Use **Azure Service Bus** for resilient, auditable work queuing and retries across steps. [1]

5. **Clinician approval gate (mandatory human-in-the-loop)**
   1. Route each prepared packet to the responsible clinician (or designated clinical reviewer) using **Power Automate Approvals**.
   2. Block any “submit to payer” step until the clinician approves with authenticated identity and captured rationale/edits. Mandatory clinician approval aligns with prior successful patterns. [0][1]

6. **Submission integration (kept outside the agent until stable)**
   1. Recommendation: keep portal submission or EDI transactions outside the agent during pilot until completeness and groundedness targets are met for a sustained period; this approach reduced risk in similar deployments. [0]
   2. If/when automating submission, place payer integrations behind **Azure API Management** with strict allowlists, logging, and throttling. [0]

7. **Observability & audit**
   1. Capture traces for retrievals, citations, tool calls, drafts, clinician approvals, and final artifacts using **Azure Monitor** and **Application Insights**. [0][2]
   2. Provide an auditable timeline per PA request for compliance and quality review. [0]

## Microsoft Services Used
- Microsoft Foundry, Microsoft Agent Framework, Foundry Agent Service, Foundry IQ [0][1][2]
- Azure AI Search [0][1][2]
- Azure Health Data Services (FHIR service) [0][1][2]
- Power Automate (Approvals) [0][1][2]
- Microsoft Entra ID [0][1][2]
- Azure Key Vault [0][1][2]
- Azure Monitor & Application Insights [0][1][2]
- Microsoft Purview [0][1][2]
- (Recommended/optional as needed) Azure Functions, Azure Service Bus, Azure API Management, SharePoint, Dynamics 365 Customer Service, Dataverse [0][1][2]

## Implementation Timeline
| Phase | Timing | Deliverables |
|---|---:|---|
| 1. Discovery, baseline, and safety boundaries | Weeks 1–2 | Current-state PA mapping; baseline time study; specialty + payer scope selection; clinical risk mapping; definition of “approved sources”; evaluation plan and acceptance criteria (groundedness, completeness, safety). [0][1] |
| 2. Data & knowledge onboarding | Weeks 3–5 | FHIR read-only integration and minimum-necessary queries; approved payer criteria + SOP ingestion into AI Search with metadata/effective dates; access model and permission trimming. [0][1] |
| 3. Workflow build (agent + rules + UI) | Weeks 6–8 | Agent Framework orchestration on Foundry Agent Service; rule-based completeness checks (Functions); draft packet format with citations; work queue/Dataverse integration; clinician approval flow in Power Automate. [0][1] |
| 4. Evaluation, red-team, and controls hardening | Weeks 9–10 | Groundedness and missing-evidence tests; prompt-injection and retrieval safety testing; audit logging validation; operational runbooks; pilot readiness sign-off. [1][2] |
| 5. Supervised pilot & measurement | Weeks 11–12 | Live pilot for selected specialty/payers; daily review huddles; KPI dashboard; go/no-go for submission automation; handover and backlog for next wave. [0][1] |

## Security Considerations
- **Tenant boundary / data residency:** Keep PHI within Contoso’s Azure tenant using private networking (e.g., private endpoints) for Search and FHIR and restrict egress. Comparable deployments used private endpoints and network restrictions to keep data inside the approved boundary. [1]
- **Identity and access:** Enforce role-based access and conditional access with **Microsoft Entra ID**; separate roles for PA staff, clinicians, and admins. [0][2]
- **Secrets and encryption:** Store secrets in **Azure Key Vault** and use encryption in transit/at rest; consider customer-managed keys where required. [0][1]
- **Minimum necessary clinical access:** Limit FHIR queries and apply field filtering to reduce PHI exposure. [0][1]
- **Prompt-injection and untrusted content handling:** Treat retrieved documents as untrusted input; apply prompt-injection defenses and output validation so retrieved content cannot modify workflow policy. [0][1]
- **No autonomous clinical decisions:** The system drafts and checks completeness; it does not determine coverage or approve treatment. Prior implementations explicitly retained clinician/pharmacist responsibility. [2]

## Governance Controls
- **Approved corpus ownership:** Assign clinical/compliance owners to approve and periodically attest payer-policy and procedure freshness; similar programs used regular attestations and monthly reviews. [0][2]
- **Versioning and release governance:** Version prompts, policies, evaluations, and releases; require sign-off before expanding scope. [1]
- **Human approval boundary:** Enforce 100% clinician approval with captured override reasons and a hard technical gate prior to any submission step. [0][1]
- **Auditability:** Trace every retrieval, citation, tool call, draft, approval, and final output; maintain evidence for compliance and investigation. [0]
- **Exception handling:** Route low-confidence, missing-evidence, groundedness failures, or safety detections into a human-only queue for manual processing. [2]

## Success Metrics
- **Preparation time:** Reduce median PA preparation time toward 15 minutes (tracked by specialty/payer); comparable pilots achieved 16–19 minutes medians. [0][1][2]
- **Packet completeness:** % of packets meeting checklist on first pass (target set during discovery); comparable completeness reached 96%. [0]
- **Clinician approval compliance:** 100% of submissions include authenticated clinician approval. [0][1]
- **Citation coverage:** % of drafted statements supported by citations to approved sources (target ≥97–99% as an internal quality bar, informed by similar implementations). [0][1][2]
- **Rework/denial drivers:** Reduction in avoidable missing-document denials/rework (baseline vs. pilot). [1][2]

## Lessons Applied
- **Content ownership beats prompt tuning:** Establish clear payer-policy ownership and checklists early; this proved more impactful than prompt iteration in similar PA agent work. [0]
- **Use explicit, deterministic rules for key classifications:** Urgency and completeness rules should be explicit and not delegated to the language model. [1]
- **Prevent outdated criteria retrieval:** Maintain effective dates and payer metadata to avoid superseded criteria surfacing in retrieval. [1]
- **Start with a safe boundary for submission:** Keep portal/transaction submission out of the agent until completeness and approval processes are stable over time. [0]
- **Specialty-specific scope improves precision:** Begin with a narrow specialty and expand with specialty-specific retrieval filters and evaluation sets. [0][2]

## Future Expansion Opportunities
- **Denial appeal drafting workflow** with legal/clinical review gates. [0][1][2]
- **Policy-change detection and regression testing** when payer criteria updates occur. [1][2]
- **Broaden to additional specialties** (e.g., imaging, oncology, infusion) using the same governance and evaluation framework. [0][1][2]
- **Operational analytics** to identify recurring documentation gaps by facility/specialty and improve upstream ordering workflows. [0]

## Sources

- [0] Sample Historical Project - Northwind Health Prior Authorization Agent — Northwind Health Network, Healthcare provider (DemoData/Past Projects/Northwind Health Prior Authorization Agent)
- [1] Sample Historical Project - Woodgrove Medical Imaging Authorization Agent — Woodgrove Medical Group, Regional healthcare provider (DemoData/Past Projects/Woodgrove Medical Imaging Authorization Agent)
- [2] Sample Historical Project - Fabrikam Specialty Care Authorization Copilot — Fabrikam Specialty Care Alliance, Specialty healthcare provider (DemoData/Past Projects/Fabrikam Specialty Care Authorization Copilot)
