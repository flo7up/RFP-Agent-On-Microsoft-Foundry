# Draft Opportunity Proposal

> Synthetic demonstration content. Review before use.

## Executive Summary
Contoso Health can reduce prior-authorization (PA) preparation time by implementing a tenant-contained, source-grounded PA preparation agent that assembles a complete, cited submission packet from approved clinical records and payer criteria, then enforces mandatory clinician approval before any submission is released. This approach mirrors proven patterns where AI-assisted PA workflows reduced median prep time from ~94–118 minutes to ~16–17 minutes while keeping PHI inside the customer tenant and enforcing clinician approval for every packet [0][1].

## Customer Situation
- Current-state PA preparation takes ~2 hours per request, driven by manual search across clinical records and payer criteria.
- Contoso requirements:
  - Use only approved clinical records and approved payer policy sources.
  - Keep patient data inside Contoso’s Microsoft tenant boundary.
  - Require a clinician to approve every PA submission (no “auto-submit”).
- Assumptions (recommendations to validate in discovery):
  - Contoso’s EHR data is available via FHIR APIs (or can be exposed via Azure Health Data Services FHIR).
  - Payer criteria/policies and internal PA SOPs can be curated in SharePoint and/or a controlled document repository.
  - Submission to payer portals will remain a human step until Contoso meets defined quality and safety thresholds, consistent with lessons learned in similar projects [0].

## Recommended Architecture
1. **Intake & work item creation**: A PA request enters a queue (e.g., from an existing case/work queue system). For resilient processing, use a queue pattern similar to Service Bus-backed work queues used in imaging authorization implementations [1].
2. **Identity, context, and patient selection**: The user authenticates with Microsoft Entra ID; the workflow binds a unique request ID, patient ID, payer, and requested service. Entra ID enforces role separation among authorization staff and clinicians [2].
3. **Retrieve approved payer criteria and internal SOPs (grounding corpus)**:
   - Index payer policy PDFs, internal checklists, and clinical guidance in Azure AI Search with strict content ownership and effective-date metadata to avoid superseded criteria, reflecting lessons from prior imaging authorization work [1].
   - Use Foundry IQ to retrieve the most relevant policy passages with citations, as used in prior PA agent patterns [0][1].
4. **Retrieve approved clinical evidence (read-only)**:
   - Query clinical records through Azure Health Data Services (FHIR) using minimum-necessary fields and read-only access, matching prior implementations [0][1].
   - Apply field filtering so only required data elements are provided to downstream steps, consistent with prior security patterns [1].
5. **Deterministic completeness checks (non-clinical rules)**:
   - Use Azure Functions to compute payer- and service-specific completeness rules (e.g., “must include recent imaging report,” “include problem list,” “include failed conservative therapy documentation”), following the pattern where functions handled non-clinical rules while the agent focused on drafting [1].
   - If critical evidence is missing, route to a human work queue with a clear “missing evidence checklist,” consistent with lessons that visible checklists accelerate review [1][2].
6. **Draft the PA packet (assistive, not decisional)**:
   - A Microsoft Agent Framework workflow hosted on Foundry Agent Service assembles a structured packet draft (summary, evidence table, citations, and payer-question mapping) as used in comparable PA implementations [0][1].
   - The agent is explicitly constrained to preparation activities and cannot make coverage or treatment decisions, aligning to safeguards used for specialty medication authorizations [2].
7. **Clinician review and mandatory approval gate**:
   - Power Automate routes the draft packet to the responsible clinician for approval with an authenticated attestation; the workflow cannot proceed without this step, matching the “cannot submit without clinician approval” control used in prior PA solutions [0][1].
   - Capture clinician edits/override reasons to improve evaluations and policy checklists over time [1][2].
8. **Submission handoff (controlled release)**:
   - After approval, the finalized packet is released to staff for submission into payer portals (human-in-the-loop). Keeping portal submission outside the agent initially is consistent with lessons learned to stabilize completeness/approval targets before automating further [0].
   - Optionally govern any API-based payer integrations through Azure API Management, consistent with prior PA architectures [0].
9. **Audit, traceability, and monitoring**:
   - Log every retrieval, tool call, draft, approval, and release event to Application Insights/Azure Monitor, consistent with prior traceability requirements [0][2].

## Microsoft Services Used
- Microsoft Foundry, Microsoft Agent Framework, Foundry Agent Service, Foundry IQ [0][1]
- Azure AI Search [0][1][2]
- Azure Health Data Services (FHIR) [0][1][2]
- Microsoft Entra ID [0][1][2]
- Power Automate [0][1][2]
- Azure Functions (completeness rules) [1]
- Azure Service Bus (work queues) [1]
- Azure API Management (payer integrations governance) [0]
- Azure Key Vault (secrets) [0][1][2]
- Azure Monitor + Application Insights (telemetry/audit) [0][1][2]
- Microsoft Purview (data classification/governance) [0][1][2]
- SharePoint (approved policy/SOP content) [0][1][2]

## Implementation Timeline
| Phase | Timing | Deliverables |
|---|---:|---|
| Discovery, risk mapping, and baseline | Weeks 1–2 | Current-state mapping; baseline prep-time measurement; clinician-approval workflow definition; initial evaluation plan aligned to clinical risk mapping [0][1] |
| Source and data onboarding | Weeks 3–5 | Approved-source registry; payer policy/SOP ingestion to Search; FHIR read-only connectivity; minimum-necessary data mapping [0][1] |
| Workflow build (agent + rules + queues) | Weeks 6–8 | Foundry Agent Service workflow; Functions-based completeness checks; queue-based processing; draft packet templates and evidence checklist [0][1] |
| Evaluation, red-team, and governance gates | Weeks 9–10 | Groundedness/citation tests; prompt-injection and output validation tests; versioning and release gates [1][2] |
| Supervised pilot (single service line) | Weeks 11–12 | Clinician-reviewed pilot; operational dashboards; tuning of payer checklists and retrieval filters [1][2] |
| Controlled rollout and handover | Weeks 13–14 | Expanded rollout plan; runbooks; support transition; monthly quality review cadence [0] |

## Security Considerations
- **Tenant-contained PHI**: Use private endpoints and network-restricted services (FHIR/Search) to keep data inside the approved boundary, as done in prior authorization implementations [1].
- **Least privilege and separation of duties**: Entra ID role groups separating authorization specialists, clinicians, and admins [2].
- **Secrets and encryption**: Store secrets in Key Vault and use encryption in transit/at rest, consistent with prior patterns [0][1].
- **Minimum necessary clinical queries**: Read-only FHIR access with constrained queries and field filtering to reduce PHI exposure [0][1].
- **Prompt-injection defenses**: Treat retrieved documents as untrusted input and apply output validation so documents cannot alter workflow policy [0][1].
- **No autonomous submission**: The system must not release a packet for submission without clinician authenticated approval [0][1].

## Governance Controls
- **Approved source corpus**: Clinical/compliance owners approve which payer policies, SOPs, and clinical guidance are indexed and used, consistent with prior governance controls [0].
- **Versioning and change control**: Version prompts, policies, evaluations, and releases with rollback criteria, as practiced in similar deployments [1].
- **Policy freshness**: Assign content owners to attest payer-policy freshness on a regular cadence (e.g., every 30 days) as used in specialty authorization governance [2].
- **End-to-end traceability**: Retain auditable records of retrievals, citations, drafts, approvals, and overrides [0][2].
- **Exception handling**: Route missing-evidence, low-groundedness, or high-risk exceptions to a human-only queue [0][2].

## Success Metrics
- **Cycle time**: Median PA preparation time (baseline vs. pilot vs. rollout). Similar programs achieved reductions to ~16–19 minutes median, but Contoso results will depend on specialty, payer complexity, and data quality [0][1][2].
- **Clinician approval compliance**: 100% of released packets have an authenticated clinician approval recorded [0][1].
- **Packet completeness**: Percentage of packets meeting payer checklist on first pass [0].
- **Citation coverage**: Percentage of required data elements and policy assertions backed by citations [0][1].
- **Rework/denial drivers**: Rate of avoidable missing-document denials [1].
- **Safety/privacy**: Count and severity of privacy/safety incidents; target zero high-severity events [0].

## Lessons Applied
- **Keep submission outside the agent until stable**: Prior projects kept portal submission out of the agent until completeness and approval targets were stable for weeks [0]. We recommend the same staged approach for Contoso.
- **Deterministic rules for urgency/completeness**: Explicit, non-LLM rules improved reliability; urgency classification and completeness checks should be deterministic and testable [1].
- **Metadata and specialty/payer filters improve retrieval**: Effective dates and payer metadata reduce retrieval of superseded criteria; specialty-specific retrieval filters and evaluation sets increase precision [1][2].
- **Trust comes from clear missing-evidence checklists**: Clinicians and staff adopt faster when the system highlights exactly what’s missing, not just a confidence score [2].

## Future Expansion Opportunities
- Extend the PA preparation workflow to additional specialties (e.g., oncology, imaging, specialty medications), following expansion patterns from earlier programs [0][1][2].
- Add denial appeal drafting with legal/clinical approval gates [0][1][2].
- Implement payer-policy change detection and automated regression tests against evaluation sets [1][2].
- Add operational analytics to identify recurring documentation gaps by facility/service line and predict staffing demand from work queues [0][1].

## Sources

- [0] Sample Historical Project - Northwind Health Prior Authorization Agent — Northwind Health Network, Healthcare provider (DemoData/Past Projects/Northwind Health Prior Authorization Agent)
- [1] Sample Historical Project - Woodgrove Medical Imaging Authorization Agent — Woodgrove Medical Group, Regional healthcare provider (DemoData/Past Projects/Woodgrove Medical Imaging Authorization Agent)
- [2] Sample Historical Project - Fabrikam Specialty Care Authorization Copilot — Fabrikam Specialty Care Alliance, Specialty healthcare provider (DemoData/Past Projects/Fabrikam Specialty Care Authorization Copilot)
