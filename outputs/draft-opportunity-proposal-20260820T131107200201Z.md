# Draft Opportunity Proposal

> Synthetic demonstration content. Review before use.

## Executive Summary
Contoso Health wants to reduce prior-authorization (PA) preparation from ~2 hours to ~15 minutes by automating evidence gathering and packet drafting while keeping patient data inside the Contoso tenant and requiring clinician approval for every submission. We recommend a tenant-contained, source-grounded agent workflow that retrieves only approved clinical records and payer criteria, assembles a cited draft packet, performs deterministic completeness checks, and routes the draft to a licensed clinician for authenticated approval before any submission.

Comparable healthcare implementations using Microsoft Agent Framework and Foundry Agent Service achieved large cycle-time reductions while keeping PHI within the provider’s Azure tenant and enforcing clinician approval gates (e.g., 118→17 minutes and 94→16 minutes in pilots) [0][2]. These results are not guaranteed for Contoso, but they inform the proposed architecture and controls.

## Customer Situation
- Authorization specialists currently spend ~2 hours per request locating the right clinical evidence, confirming payer criteria, and composing the submission packet.
- Contoso requires:
  - Use of **approved clinical records** only as evidence (no ad-hoc/unvetted sources).
  - **Patient data remains inside the Contoso tenant** (no external storage or uncontrolled sharing).
  - **Clinician approval for every submission** (explicit accountability and safety boundary).

Assumptions (to be validated during discovery):
- Contoso can provide read-only access to clinical records via HL7 FHIR (preferred) or another governed API/export, and payer criteria/procedures exist in a controlled repository (e.g., SharePoint) with clear ownership and effective dates.

## Recommended Architecture
1. **Intake & work orchestration**
   - Prior-auth requests enter a controlled work queue (e.g., Dynamics 365 Customer Service case or a SharePoint/Dataverse list), capturing patient, order, payer, and requested service metadata (pattern aligned to using Dynamics work items for authorizations) [1].
2. **Approved-source knowledge plane (policies + internal SOPs)**
   - Index payer policy PDFs, internal PA checklists, and clinical guidance stored in SharePoint into **Azure AI Search** with metadata (payer, line of business, specialty, effective date) to reduce retrieval of superseded criteria (effective-date + payer metadata highlighted as critical) [2].
   - Use **Foundry IQ** to ground responses with citations to approved documents (used for grounded retrieval in prior-auth workflows) [0][1][2].
3. **Clinical evidence retrieval (tenant-contained, minimum necessary)**
   - Expose patient clinical records via **Azure Health Data Services (FHIR)** as read-only tools to the agent workflow (this pattern was used to retrieve clinical context for PA preparation) [0][1][2].
   - Apply field- and scope-filtering (“minimum necessary” queries) to limit PHI exposed per step (implemented in prior solutions) [0][2].
4. **Deterministic workflow with clinician-in-the-loop**
   - Implement a **Microsoft Agent Framework** workflow hosted on **Foundry Agent Service** to separate bounded steps: policy retrieval, evidence extraction, completeness checking, and packet drafting (used to improve safety and repeatability) [0][1][2].
   - Add deterministic rules (e.g., required fields by payer/service) via **Azure Functions** so critical routing/urgency/completeness logic is not delegated to the language model (rule-based approach and “don’t delegate urgency” lesson) [2].
5. **Packet drafting with citations and evidence checklist**
   - Produce a structured PA packet draft (forms + narrative + attachments list) that includes:
     - An evidence checklist for faster clinician review (shown to improve review speed and feedback quality) [2].
     - Citations back to the approved corpus and clinical record excerpts used.
6. **Mandatory clinician approval gate (no exceptions)**
   - Route every draft packet to the responsible clinician using **Power Automate Approvals**, requiring authenticated approval (this gate was enforced in prior PA agents) [0][2].
   - Block downstream actions until approval is recorded; capture override reason when the clinician edits or rejects.
7. **Submission boundary (recommendation)**
   - Keep payer-portal submission **outside** the agent until Contoso meets agreed stability thresholds (mirroring the lesson of keeping portal submission outside automation early) [0].
   - Optional later phase: integrate governed submission via **Azure API Management** for payer integrations where available (APIM governance pattern used previously) [0].
8. **Observability, audit, and quality evaluation**
   - Instrument workflow traces (retrievals, citations, tool calls, draft versions, approvals) in **Application Insights/Azure Monitor** (end-to-end traceability was a core control in earlier deployments) [0][1][2].
   - Maintain specialty/payer-specific evaluation sets and run regression tests for groundedness/completeness before expanding scope (specialty-specific evaluation sets improved precision) [0][1].

## Microsoft Services Used
- Microsoft Foundry (Foundry Agent Service, Foundry IQ) [0][1][2]
- Microsoft Agent Framework [0][1][2]
- Azure AI Search [0][1][2]
- Azure Health Data Services (FHIR) [0][1][2]
- Power Automate (Approvals) [0][1][2]
- Microsoft Entra ID [0][1][2]
- Azure Key Vault [0][1][2]
- Azure Monitor + Application Insights [0][1][2]
- Microsoft Purview [0][1][2]
- SharePoint (approved document repository) [0][1][2]
- Optional/phase-based: Dynamics 365 Customer Service for work items [1], Azure Functions and Service Bus for rules/queues [2], Azure API Management for payer integrations [0]

## Implementation Timeline
| Phase | Timing | Deliverables |
|---|---:|---|
| 0. Discovery, safety boundaries, and baseline | Weeks 1–2 | Current-state process map; baseline prep-time measurement; approved-source inventory; clinical risk assessment and automation boundaries (discovery + clinical-risk mapping approach used previously) [0][2] |
| 1. Data and knowledge connections | Weeks 3–5 | FHIR read-only access patterns; SharePoint content governance; Azure AI Search index with payer/effective-date metadata; initial Purview classification (policy and data connections pattern) [0][2] |
| 2. Agent workflow build (bounded steps) | Weeks 6–8 | Foundry Agent Service workflow; Foundry IQ grounding; deterministic completeness rules (Agent Framework bounded-step approach) [1][2] |
| 3. Evaluation, red-team, and clinician UX | Weeks 9–10 | Specialty/payer evaluation sets; groundedness/citation checks; prompt-injection testing and output validation (evaluation + red-team emphasis) [2] |
| 4. Supervised pilot (one specialty/payer set) | Weeks 11–12 | Pilot go-live with manual submission; Power Automate clinician approval enforced; weekly quality review loop (supervised pilot approach) [2] |
| 5. Controlled rollout and handover | Weeks 13–14 | Add additional payers/specialties; operations runbook; monitoring dashboards; content attestation cadence; transition to Contoso operations (controlled rollout pattern) [0] |

## Security Considerations
- **Tenant-contained PHI**: Keep clinical data in Contoso-controlled Azure services; use private endpoints and network-restricted services for Search and FHIR where possible (controls used to keep data inside boundary) [2].
- **Identity and access**: Enforce Entra ID RBAC and Conditional Access; separate roles for PA specialists, clinicians, and admins (least-privilege separation used previously) [0][1].
- **Secrets and keys**: Use managed identities and store secrets in Key Vault; consider customer-managed keys for sensitive stores (pattern used previously) [2].
- **Data minimization**: Minimum-necessary FHIR queries; field filtering so the agent only receives required clinical context (implemented previously) [0][2].
- **Prompt-injection and untrusted content**: Treat retrieved documents as untrusted; enforce output validation and prevent retrieved content from changing workflow policy (explicit prompt-injection defenses and output validation were applied) [2].
- **Auditability**: Record every retrieval, citation, tool call, and approval action for defensibility (end-to-end traceability control) [0].

## Governance Controls
- **Approved-source governance**: Clinical/compliance owners approve the source corpus and evaluation sets (owner-approved corpus control) [0].
- **Payer policy freshness**: Content owners attest payer-policy currency on a defined cadence (e.g., every 30 days) as done in similar programs [1].
- **Release and change management**: Version prompts, policies, rules, and evaluations; define rollback criteria before expanding scope (versioning + rollback governance) [2].
- **Human approval gate**: 100% clinician approval required before any submission; capture approval identity and override reasons (clinician accountability enforced in prior solutions) [0][2].
- **Operational quality reviews**: Monthly (or more frequent during pilot) reviews for groundedness, completeness, access violations, and policy freshness (monthly quality review model) [0].
- **Exception handling**: Route failed groundedness/missing-evidence cases to a human-only queue (human-only handling on failure) [1].

## Success Metrics
Measured during pilot and compared to baseline (targets are goals, not guarantees):
- Cycle time: median PA preparation time reduction from baseline toward 15 minutes (prior pilots achieved 118→17 and 94→16 minutes) [0][2].
- First-pass completeness/acceptance: increase in complete packets and reduced rework (improved completeness and first-pass acceptance observed in similar implementations) [0][1].
- Safety and compliance:
  - 100% submissions with authenticated clinician approval (achieved in prior deployments) [0][2].
  - Citation coverage (percentage of drafted statements backed by approved sources) similar programs tracked 97–99% citation coverage [1][2].
- Operational: same-day completion rate improvement (observed increase in an imaging PA pilot) [2].

## Lessons Applied
- **Clinician accountability is non-negotiable**: Prior implementations required clinician/pharmacist approval for every authorization; we adopt the same hard gate for Contoso [0][1][2].
- **Workflow determinism beats “one big prompt”**: Bounded, stepwise agent workflows improved repeatability and safety in similar programs [0][1][2].
- **Metadata and content ownership matter**: Effective dates and payer metadata reduce retrieval of superseded criteria; explicit content ownership and attestation reduce drift [1][2].
- **Keep portal submission out of scope initially**: Similar teams kept portal submission outside the agent until quality thresholds stabilized; we recommend the same phased approach [0].
- **Make review fast with evidence checklists**: Visible evidence checklists improved clinician review speed and feedback loops; we include this in the draft packet format [2].

## Future Expansion Opportunities
- Expand from the initial specialty/payer set to additional service lines (oncology, imaging, specialty meds) following patterns proven in other healthcare providers [0][2].
- Add denial-appeal packet drafting with legal/clinical approval gates (appeal drafting identified as a next step) [0][1][2].
- Implement payer-policy change detection and automated regression tests against evaluation sets to prevent quality regressions as policies evolve [2].
- Add operational analytics to identify recurring documentation gaps by specialty/facility and drive upstream clinical documentation improvements [0].

## Sources

- [0] Sample Historical Project - Northwind Health Prior Authorization Agent — Northwind Health Network, Healthcare provider (DemoData/Past Projects/Northwind Health Prior Authorization Agent)
- [2] Sample Historical Project - Woodgrove Medical Imaging Authorization Agent — Woodgrove Medical Group, Regional healthcare provider (DemoData/Past Projects/Woodgrove Medical Imaging Authorization Agent)
- [1] Sample Historical Project - Fabrikam Specialty Care Authorization Copilot — Fabrikam Specialty Care Alliance, Specialty healthcare provider (DemoData/Past Projects/Fabrikam Specialty Care Authorization Copilot)
