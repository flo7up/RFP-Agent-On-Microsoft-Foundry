# Draft Opportunity Proposal

> Synthetic demonstration content. Review before use.

## Executive Summary

Contoso Health wants to compress prior-authorization (PA) preparation time from ~2 hours to ~15 minutes while (1) using only approved clinical records and payer criteria, (2) keeping patient data inside the Contoso tenant, and (3) ensuring a clinician approves every submission.

We propose an AI-assisted PA preparation workflow using Microsoft Agent Framework orchestrated by Foundry Agent Service to retrieve approved records and payer policies, generate a cited draft packet, run completeness checks, and route each packet for authenticated clinician approval before any submission step—reusing proven workflow patterns from prior healthcare PA implementations while tailoring governance and controls to Contoso’s environment. Patterns: agent-orchestrated retrieval + drafting + mandatory clinician approval [0][2].

## Customer Situation

- Current PA prep is slow (target reduction from two hours to fifteen minutes) and typically involves manual collection of clinical evidence and payer requirements (assumption based on common PA workflows; recommendation to confirm in discovery).
- Contoso requires:
  - **Approved-source grounding** (only sanctioned clinical records and policy content) [0][1].
  - **Tenant-contained PHI** with private connectivity and least-privilege access [0][2].
  - **Clinician accountability**: every submission must be clinician-approved (explicit requirement; aligns with patterns where packets cannot be submitted without clinician approval) [0][2].

## Recommended Architecture

**High-level workflow (deterministic, bounded steps):**
1. **Work item intake** (recommendation): PA request created/ingested (from existing queue/EHR workflow).
2. **Policy retrieval & matching**: Foundry IQ grounded by Azure AI Search retrieves the *payer’s current criteria* and internal approved procedures with citations [0][1][2].
3. **Clinical evidence retrieval (read-only)**: Azure Health Data Services (FHIR) exposes approved clinical records via a restricted tool (minimum-necessary queries) [0][2].
4. **Evidence extraction & checklist completeness**:
   - Agent extracts required data elements and assembles an **evidence checklist** for reviewer efficiency (pattern: visible evidence checklist accelerates review) [2].
   - Optional rules engine for **non-clinical completeness** (e.g., presence of required attachments/fields) implemented using Azure Functions (pattern) [2]. *(Recommendation; scope-confirm during discovery.)*
5. **Draft PA packet generation**: Agent drafts a submission packet with **required citations** to source policies and clinical records [0][2].
6. **Clinician approval gate (mandatory)**: Power Automate routes to the responsible clinician; packet cannot progress without authenticated approval (pattern) [0][2].
7. **Submission boundary**:
   - Recommendation: keep payer portal submission **outside the agent** initially until quality and completeness targets stabilize (pattern) [0].
   - If/when automated submission is introduced, govern via Azure API Management for integration controls (pattern) [0].

**Orchestration & hosting:**
- Microsoft Agent Framework workflow hosted by Foundry Agent Service (pattern) [0][2].
- Work queue resiliency (optional): Azure Service Bus for asynchronous processing and retries (pattern) [2]. *(Recommendation.)*

## Microsoft Services Used

- **Microsoft Foundry**, **Microsoft Agent Framework**, **Foundry Agent Service** (agent workflow orchestration) [0][2]  
- **Foundry IQ** + **Azure AI Search** (grounded retrieval with citations) [0][1][2]  
- **Azure Health Data Services (FHIR)** (read-only clinical record access) [0][1][2]  
- **Power Automate** (clinician approval workflow) [0][1][2]  
- **Microsoft Entra ID** (RBAC, conditional access) [0][1][2]  
- **Azure Key Vault** (secrets/keys) [0][1][2]  
- **Azure Monitor** + **Application Insights** (end-to-end tracing/observability) [0][1][2]  
- **Microsoft Purview** (data classification/governance) [0][1][2]  
- **SharePoint** (approved policy/procedure corpus, if applicable) [0][1][2]  
- Optional (recommendation based on integration needs):
  - **Azure API Management** (payer/EHR API governance) [0]
  - **Azure Functions** (non-clinical completeness rules) [2]
  - **Azure Service Bus** (work queue resiliency) [2]

## Implementation Timeline

**Recommended 12–16 weeks** (final duration depends on number of payers/specialties and data readiness):

- **Weeks 1–2: Discovery & clinical-risk mapping**
  - Process mapping, clinician approval model, risk boundaries (pattern: upfront discovery/risk mapping) [0][2]
  - Define “approved sources” corpus and ownership [0][1]
- **Weeks 3–6: Data + knowledge connections**
  - Connect FHIR read-only access; establish minimum-necessary query patterns [0][2]
  - Curate and index payer policies/procedures in Azure AI Search with metadata (payer, effective date, specialty) (pattern: metadata to avoid superseded criteria) [2]
- **Weeks 7–10: Agent workflow build + evaluations**
  - Implement bounded steps: retrieval → extraction → completeness → drafting → approval [1]
  - Establish evaluation sets by specialty/payer (pattern: specialty-specific evaluation sets) [0][2]
- **Weeks 11–12: Security validation + red-team testing**
  - Prompt-injection defenses, output validation, access checks (pattern) [2]
- **Weeks 13–16: Supervised pilot + handover**
  - Pilot with one specialty/payer slice; controlled expansion (pattern) [0][1]

## Security Considerations

- **Identity & access**: Entra ID RBAC and conditional access; separate roles for PA staff, clinicians, admins (pattern) [0][1].
- **Tenant boundary & private networking**: private endpoints / network-restricted access for Search and FHIR; keep PHI inside tenant boundary (pattern) [0][2].
- **Secrets management**: Key Vault for secrets; managed identities for service-to-service auth (pattern) [0][1][2].
- **Minimum-necessary data**: restrict FHIR queries and apply field filtering to reduce PHI exposure (pattern) [0][2].
- **Untrusted retrieval handling**: treat retrieved documents as untrusted input; implement prompt-injection defenses and output validation (pattern) [0][2].
- **Hard approval gate**: agent cannot proceed to “submit” state without authenticated clinician approval (pattern) [0][2].
- **Logging hygiene**: recommendation to exclude clinical payloads from logs and retain only required metadata/trace IDs (pattern) [1].

## Governance Controls

- **Clinical/compliance ownership of corpus & evaluations**: named owners approve the source corpus and evaluation sets (pattern) [0][2].
- **Policy freshness attestation**: content owners attest payer-policy freshness on a defined cadence (pattern: every 30 days in prior implementation) [1]. *(Recommendation to set cadence appropriate to Contoso/payer volatility.)*
- **Traceability & audit**: capture every retrieval, citation, tool call, draft, approval, and final output for audit (pattern) [0][2].
- **Versioning**: version prompts, policies, evaluations, and releases; maintain rollback criteria (pattern) [2][1].
- **Exception handling**: failed groundedness, missing evidence, or prompt-injection detections route to human-only queue (pattern) [1][0].
- **Automation boundary control**: named clinical owner approves each automation boundary; keep high-risk steps out until validated (pattern) [2][0].

## Success Metrics

Targets should be validated during discovery and measured during pilot (historical results are evidence of feasibility, not guaranteed outcomes).

- **Cycle time**: median PA preparation time (goal: approach 15 minutes; recommendation).
  - Evidence that similar workflows reduced median prep time near this range in pilots: 118→17 minutes [0], 105→19 minutes [1], 94→16 minutes [2].
- **Clinician approval compliance**: 100% of submissions have authenticated clinician approval (pattern metric achieved previously; propose as Contoso non-negotiable control) [0][2].
- **Citation coverage**: % of required statements backed by citations to approved sources (pattern metric tracked previously) [0][1][2].
- **Packet completeness / first-pass acceptance proxy**:
  - Track completeness rate and rework due to missing evidence (pattern metrics used previously) [0][1][2].
- **Privacy & safety**: count of privacy/safety incidents; track severity and near-misses (pattern: monitored in prior pilot) [0].

## Lessons Applied

- **Policy ownership > prompt tuning**: assign explicit owners for payer criteria and internal guidance; governance drives reliability (pattern) [0].
- **Use payer/specialty checklists and filters** to improve retrieval precision (pattern) [0][1].
- **Specialty-specific evaluation sets** uncover missing evidence early and prevent broad, low-precision launches (pattern) [0][1].
- **Keep urgency classification rule-based**, not delegated to the language model (pattern) [2]. *(Recommendation if Contoso needs prioritization.)*
- **Ensure policy metadata (effective dates/payer tags)** to reduce superseded criteria retrieval (pattern) [2].
- **Defer automated submission until stable**: keep portal submission outside the agent until completeness/quality thresholds are consistently met (pattern) [0].

## Future Expansion Opportunities

- **Add denial appeal drafting** with governed legal/clinical approval (pattern) [0][2][1].
- **Policy-change detection and regression tests** to proactively manage payer updates (pattern) [0][2].
- **Operational analytics**: recurring documentation gaps by facility/specialty and denial-reason insights (pattern) [0][1].
- **Expand to additional specialties** after pilot stabilization (pattern expansion path) [0][2].
- **Pre-order documentation guidance** for physicians to reduce downstream PA rework (pattern) [2].
