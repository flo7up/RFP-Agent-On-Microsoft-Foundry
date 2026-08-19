# Draft Opportunity Proposal

> Synthetic demonstration content. Review before use.

## Executive Summary

Contoso Health seeks to reduce prior-authorization preparation time from ~2 hours to ~15 minutes while ensuring staff only use approved clinical records, all patient data remains inside the Contoso tenant, and every submission is approved by a clinician.

We propose an AI-assisted, tenant-contained prior-authorization preparation workflow using Microsoft Agent Framework orchestrated via Foundry Agent Service, grounded with Foundry IQ + Azure AI Search over Contoso-approved policy/procedure content, with read-only access to clinical records (FHIR) and a mandatory clinician approval gate before any submission—reusing proven workflow patterns from prior implementations in healthcare prior authorization and imaging authorization scenarios [0][2].

## Customer Situation

- Authorization staff spend significant time gathering documentation across clinical records and payer criteria, then manually drafting packets for submission.
- Contoso requirements:
  - Use only **approved** clinical records and payer/policy content (source-grounded drafting) [0][1].
  - Keep **all PHI inside the Contoso tenant** with appropriate isolation controls [0][2].
  - Require **clinician approval for every submission** with authenticated accountability [0][2].

## Recommended Architecture

**Pattern reused (evidence-based):** Deterministic, step-bounded agent workflow for (1) record retrieval, (2) policy matching, (3) evidence extraction, (4) completeness checking, (5) packet drafting, and (6) clinician approval prior to submission [0][1][2].

**Proposed logical flow (recommendation):**
1. **Intake & work item creation (recommendation):** Authorization request initiated from Contoso’s current intake channel (EHR workqueue / portal / CRM).  
2. **Read-only clinical retrieval:** Retrieve relevant patient context from Azure Health Data Services FHIR via a read-only tool interface as used in prior patterns [0][2].  
3. **Payer criteria & internal guidance retrieval:** Foundry IQ grounds the workflow using Azure AI Search over an approved corpus of payer policies and internal procedures with citations [0][1][2].  
4. **Evidence checklist & completeness rules:**  
   - Use bounded steps for completeness checking (separating retrieval vs. validation) consistent with prior designs [1][2].  
   - **Recommendation:** Implement non-clinical completeness rules (e.g., required fields present, date ranges, attached note types) via Azure Functions for deterministic validation, mirroring prior imaging workflow patterns [2].  
5. **Packet drafting with citations:** Generate a draft packet with a visible evidence checklist and citations back to approved sources, aligning with prior emphasis on auditability and faster review [2].  
6. **Clinician approval gate (mandatory):** Route the packet to the responsible clinician for authenticated approval and capture approval/override reasons; no submission proceeds without this step [0][2].  
7. **Submission step boundary:**  
   - **Recommendation:** Keep payer portal submission outside the agent until quality and completeness thresholds are stable, aligning with prior lessons that withheld submission automation until stability [0].  
   - If submission integration is required later, govern outbound calls via Azure API Management as used previously [0].

## Microsoft Services Used

- **Microsoft Foundry** (agent hosting/orchestration) and **Microsoft Agent Framework** for bounded workflow steps [0][1][2]  
- **Foundry Agent Service** for hosting the agent workflow [0][2]  
- **Foundry IQ** + **Azure AI Search** for grounded retrieval over approved payer/internal content with citations [0][1][2]  
- **Azure Health Data Services (FHIR)** for read-only clinical record access [0][1][2]  
- **Power Automate** for clinician approval workflow and audit-friendly routing [0][1][2]  
- **Microsoft Entra ID** for RBAC/conditional access and separation of duties [0][1][2]  
- **Azure Key Vault** for secrets and key management [0][1][2]  
- **Azure Monitor** + **Application Insights** for tracing, quality monitoring, and operational telemetry [0][1][2]  
- **Microsoft Purview** for data classification and governance controls [0][1][2]  
- **SharePoint** as a governed repository for internal procedures/payer documents (if already used by Contoso) [0][1][2]  
- **Optional (recommendation):** Azure Functions for deterministic completeness rules [2]  
- **Optional (recommendation):** Azure API Management for governed external/payer integrations [0]

## Implementation Timeline

**Recommendation: 12–16 weeks** depending on number of payers/specialties in initial scope, aligning with prior delivery timelines that included discovery, connections, agent build, evaluation, and a supervised pilot [0][1][2].

- **Weeks 1–2: Discovery & clinical-risk mapping**
  - Process mapping, automation boundaries, clinician accountability design [0][2]
  - Define “approved source” corpus and ownership model [0][1]
- **Weeks 3–6: Data & knowledge connections**
  - FHIR read-only access patterns and minimum-necessary queries [0][2]
  - Index payer criteria + internal SOPs in Azure AI Search with metadata (payer, effective date) [2]
- **Weeks 7–10: Agent workflow implementation**
  - Step-bounded retrieval, extraction, checklist, and draft packet generation [1][2]
  - Power Automate clinician approval gate [0][2]
- **Weeks 11–12: Evaluation, red-team, and safety testing**
  - Groundedness, missing-evidence detection, prompt-injection testing [1][2]
- **Weeks 13–16 (as needed): Supervised pilot & controlled rollout**
  - Pilot in one specialty/payer set; expand based on quality gates [0][2]

## Security Considerations

Security controls will follow previously proven tenant-contained healthcare patterns:

- **Tenant isolation & access control:** Entra ID RBAC and (recommendation) Conditional Access; least-privilege separation for authorization staff vs. clinicians vs. admins [0][1].  
- **Service-to-service protection:** Managed identities, private endpoints/private networking (recommendation), and Key Vault for secrets [0][1][2].  
- **Minimum necessary clinical context:** Field filtering/minimum-necessary FHIR queries to reduce PHI exposure [0][2].  
- **Treat retrieved content as untrusted:** Apply prompt-injection defenses and output validation so retrieved documents cannot alter workflow policy or controls [2].  
- **Hard approval gate:** Agent cannot proceed to submission without authenticated clinician approval [0][2].  
- **Logging hygiene:** **Recommendation** based on prior pattern: exclude clinical payloads from logs while retaining traceability of tool calls and citations [1].

## Governance Controls

- **Clinical/compliance ownership of sources and evaluations:** Named owners approve the source corpus and evaluation set; high-risk exceptions route to human handling [0][2].  
- **Policy freshness attestation:** Content owners attest payer-policy freshness on a defined cadence (e.g., every 30 days) [1].  
- **End-to-end traceability:** Trace every retrieval, citation, tool call, draft, approval, and final outcome for auditability [0].  
- **Versioning and release controls:** Version prompts, policies, evaluations, and agent releases; implement rollback criteria before expansion [2].  
- **Quality reviews:** Regular reviews (e.g., monthly) for groundedness, completeness, access violations, and payer-policy freshness [0].  

## Success Metrics

**Contoso target (new):** Reduce preparation time to ~15 minutes (target; not guaranteed).

**Recommended measurable KPIs (grounded in prior measurement patterns):**
- Median preparation time (baseline vs. pilot vs. rollout), comparable to how prior projects tracked median preparation time improvements [0][1][2].  
- Packet completeness / missing-evidence rate, consistent with prior focus on completeness and rework reduction [0][1][2].  
- Clinician approval compliance: 100% of submissions require authenticated clinician approval (hard control, aligned to prior designs) [0][2].  
- Citation coverage (percent of key assertions supported by approved sources), reflecting prior citation coverage tracking [0][1][2].  
- Privacy/safety incidents and access violations, consistent with prior monitoring and governance expectations [0][2].

*Note:* Historical outcomes (e.g., time reductions in other organizations) are evidence of feasibility but are not guaranteed for Contoso [0][1][2].

## Lessons Applied

- **Policy ownership over prompt tuning:** Establish clear ownership and governance for payer policies and internal guidance; this was a key lesson previously [0].  
- **Use payer/specialty-specific filters and evaluation sets:** Improves retrieval precision and exposes missing evidence early [0][1].  
- **Do not delegate high-impact classification to the model:** Use explicit rules for items like urgency/priority rather than relying on the language model (recommendation to apply same principle to any prioritization Contoso requests) [2].  
- **Require effective dates and metadata on source documents:** Avoid retrieving superseded criteria by enforcing payer metadata/effective dates in the indexed corpus [2].  
- **Keep submission gated until stable:** Maintain portal submission outside the agent until completeness and quality targets are stable (recommendation aligned with prior rollout strategy) [0].  
- **Visible evidence checklist accelerates clinician review:** Include an evidence checklist to streamline review and feedback loops [2].

## Future Expansion Opportunities

- Expand to additional specialties (e.g., oncology, imaging, referrals) using the same repeatable controls [0][2].  
- Add governed appeal packet drafting for denials with appropriate legal/clinical approval gates [0][1][2].  
- Implement payer-policy change detection and regression testing to reduce drift and outdated criteria retrieval [0][2].  
- Add operational analytics to identify recurring documentation gaps by facility/specialty and improve upstream documentation quality [0].  
- **Recommendation:** Integrate with Contoso’s existing work management system (e.g., CRM/work queue) to drive adoption, consistent with the pattern of writing back into existing queues rather than creating a separate interface [1].

## Sources

- [0] Sample Historical Project - Northwind Health Prior Authorization Agent — Northwind Health Network, Healthcare provider (DemoData/Past Projects/Northwind Health Prior Authorization Agent)
- [2] Sample Historical Project - Woodgrove Medical Imaging Authorization Agent — Woodgrove Medical Group, Regional healthcare provider (DemoData/Past Projects/Woodgrove Medical Imaging Authorization Agent)
- [1] Sample Historical Project - Fabrikam Specialty Care Authorization Copilot — Fabrikam Specialty Care Alliance, Specialty healthcare provider (DemoData/Past Projects/Fabrikam Specialty Care Authorization Copilot)
