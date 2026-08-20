# Presenter Guide: Opportunity Assessment Agent

This runbook presents five numbered demos as one story for Microsoft partners and system integrators. The complete presentation takes about 22 minutes.

## The story

Your company is a Microsoft systems integrator responding to a healthcare opportunity from Contoso Health.

Contoso wants to reduce prior-authorization preparation from about two hours to fifteen minutes. Staff must use approved clinical records, protected health information must remain inside the tenant, and a clinician must approve every submission.

The account team needs to answer five questions:

1. Can an agent turn the opportunity into a useful first assessment?
2. Can the assessment reuse the firm's delivery experience instead of relying only on model knowledge?
3. When should orchestration be model-directed instead of encoded as a fixed workflow?
4. Can the agent work with approved enterprise systems and explicit tool boundaries?
5. Can the resulting solution be traced and evaluated in operation?

Each demo answers one question while retaining the same customer, workflow, constraints, and human-accountability boundary.

## Consistent facts

Keep these facts consistent throughout the presentation:

| Fact | Source in the story |
| --- | --- |
| Customer is Contoso Health | Initial opportunity |
| Workflow is healthcare prior authorization | Initial opportunity |
| Current preparation time is about two hours | Initial opportunity |
| Target preparation time is fifteen minutes | Initial opportunity |
| Staff use approved clinical records containing PHI | Initial opportunity |
| Patient data remains inside the tenant | Initial opportunity |
| A clinician approves every submission | Initial opportunity |
| Opportunity ID is `OPP-1042` | Approved CRM record retrieved in Demo 4 |
| Volume is 12,000 requests per month | Approved CRM record retrieved in Demo 4 |
| Historical projects and outcomes are synthetic samples | Foundry IQ corpus used in Demo 2 |

Do not mention `OPP-1042` or 12,000 requests as known facts before Demo 4. Their appearance demonstrates that tool access can add approved enterprise context.

## Core message

Use this sentence to connect the five demos:

> We start with a useful agent, ground it in organizational experience, connect it to governed enterprise tools, and make its operation observable.

## Timing

| Segment | Time | Outcome |
| --- | ---: | --- |
| Opening | 1 minute | Establish the customer opportunity |
| Demo 1 | 3 minutes | Show a useful model-based assessment |
| Demo 2 | 90 seconds | Create a grounded proposal artifact and open its URL |
| Demo 3 | 2 minutes | Compare fixed and model-directed orchestration |
| Demo 4 | 4 minutes | Add approved enterprise tools and hosting boundary |
| Demo 5 | 3 minutes | Trace and evaluate the agent run |
| Close | 1 minute | Summarize the enterprise progression |

## Before the presentation

Run all setup from the repository root.

### 1. Prepare Python and authentication

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
az login
Copy-Item .env.example .env
```

Populate `.env` with:

- `FOUNDRY_PROJECT_ENDPOINT`
- `AZURE_AI_MODEL_DEPLOYMENT_NAME`
- `FOUNDRY_IQ_SEARCH_CONNECTION_NAME`
- `AZURE_OPENAI_EMBEDDING_ENDPOINT`
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`
- `AZURE_OPENAI_EMBEDDING_MODEL`
- Optional `AZURE_STORAGE_ACCOUNT_URL`
- Optional telemetry settings for Demo 5

Never display `.env` during the presentation.

### 2. Validate and ingest project memory

The ingestion script is setup for Demo 2, not one of the five numbered demos.

```powershell
python -B kickoffdemos\ingest_foundry_iq.py --dry-run
python -B kickoffdemos\ingest_foundry_iq.py
```

Confirm that the live command reports:

Confirm that the live command creates or updates both indexes and accepts three opportunity and three proposal documents.

The command is idempotent. It updates the same index, knowledge source, knowledge base, and three document IDs.

### 3. Prepare tracing for Demo 5

Choose one telemetry destination before the presentation:

- Configure `APPLICATIONINSIGHTS_CONNECTION_STRING` in `.env`.
- Configure `OTEL_EXPORTER_OTLP_ENDPOINT` in `.env`.
- Open the Foundry Toolkit trace viewer so it listens on `localhost:4317`.

Do not use `--include-content` in a customer setting. The included scenario is synthetic, but leaving content capture off demonstrates the safer production default.

### 4. Preflight all five commands

Run the offline regression suite, then run all five demos once before the audience arrives:

```powershell
python -B -m unittest discover -s tests -v
python -B kickoffdemos\01_intro.py
python -B kickoffdemos\02_patterns.py
python -B kickoffdemos\03_harness.py
python -B kickoffdemos\04_hosted_tools.py
python -B kickoffdemos\05_observability.py
```

Keep one terminal at the repository root, increase its font size, and clear previous output before starting.

## Opening

Say:

> Contoso Health has a concrete operational problem. Prior-authorization preparation takes about two hours, and the target is fifteen minutes. The workflow uses protected clinical data, data must remain in the tenant, and every submission needs clinician approval. We will build confidence in the solution through five increasingly enterprise-ready capabilities.

Do not show architecture slides first. Start with the opportunity and let each demo earn the next layer of architecture.

## Demo 1: Useful first assessment

**File:** `kickoffdemos/01_intro.py`

**Question answered:** Can one agent turn an opportunity into a useful first assessment?

### Run

```powershell
python -B kickoffdemos\01_intro.py
```

### Say before running

> We begin with one prompt agent, one Foundry-hosted model, and one bounded Agent Framework tool. The run prompt contains no customer facts, so the agent calls `opportunity_tool` to read the approved opportunity before producing an architecture-ready brief.

### Point out in the output

The response should contain these four headings:

- `AI Opportunities`
- `Architecture Proposal`
- `Delivery Risks`
- `Executive Summary`

Call attention to:

- The `@tool` declaration has no arguments and reads the shared opportunity file.
- The same tool schema is published with the prompt agent and its callable is bound to `FoundryAgent`.
- The output is concise and immediately useful to an account team.
- Human oversight and tenant boundaries appear in the recommendation.
- Assumptions and risks are visible instead of hidden.
- The assessment is still based on the opportunity and model reasoning only.

### Do not claim

Do not say that this response uses prior projects, CRM facts, or authoritative customer data. It does not.

### Transition

Say:

> This is a credible first draft, but a systems integrator has something more valuable than a generic first draft: experience from prior deliveries. The next step turns that experience into governed organizational memory.

## Demo 2: Publish a grounded proposal

**File:** `kickoffdemos/02_patterns.py`

**Question answered:** Can the agent reuse similar delivery experience and deliver a proposal artifact?

### Run

```powershell
python -B kickoffdemos\02_patterns.py
```

### Say before running

> Demo 1 produced a useful assessment from the opportunity alone. Here, Foundry IQ first matches similar synthetic calls for offer, then retrieves their linked proposals with hybrid agentic search and creates a cited draft.

### Point out in the output

The terminal prints only one URL. Open it and point out these proposal sections:

- Executive Summary
- Customer Situation
- Recommended Architecture
- Microsoft Services Used
- Implementation Timeline
- Security Considerations
- Governance Controls
- Success Metrics
- Lessons Applied
- Future Expansion Opportunities

Call attention to cited historical claims, labeled recommendations, clinician approval, and the synthetic-content warning. The blob name contains a UTC timestamp and uploads use `overwrite=False`.

For an existing public container, the output is a direct blob URL. For a private container, it is a one-hour read-only SAS URL. Do not expose an active SAS query in a published recording.

### Transition

Say:

> We now have an evidence-grounded proposal delivered as a usable artifact through a fixed workflow. Before adding more systems, compare that deterministic graph with an agent that can plan the same job dynamically.

## Demo 3: Compare Harness orchestration

**File:** `kickoffdemos/03_harness.py`

**Question answered:** When should orchestration be model-directed instead of encoded as a fixed workflow?

### Run

```powershell
python -B kickoffdemos\03_harness.py --playground
```

The pixel-art Harness Office opens at `http://127.0.0.1:8090`. Use `--playground-port <port>` if needed. The
terminal-only comparison remains available with `python -B kickoffdemos\03_harness.py --verbose`.

### Say before running

> Demo 2 encoded retrieval, drafting, citation assembly, and publication as a fixed graph. Demo 3 gives the Harness bounded tools for the same job and lets the model manage its todo list and execution mode.

### Point out in the output

- The Harness creates and completes its own todo list.
- Plan length is chosen at runtime through `TodoProvider`; new or obsolete work can be added or removed.
- The character moves only when real todo, retrieval, drafting, or publication events occur.
- The journey preserves returns to earlier workstations for refined searches and validation retries.
- Every run opens at the door: a visitor rings the doorbell and hands over the opportunity brief.
- Idle is visible too: the character sleeps between runs, then wakes and stretches on the first event.
- Speech bubbles summarize observable actions and results, not private chain-of-thought.
- Retrieval and publication remain bounded by application tools.
- `default_options={"store": False}` remains enforced.
- The resulting proposal still requires resolvable citations and a Sources section.
- `03_harness_simple.py` is the minimal one-tool hello-world companion when the full comparison is more detail than the audience needs.

### Transition

Say:

> Harness makes orchestration adaptive, while bounded tools still define what the agent can retrieve or publish. Next, we apply that same tool boundary to current enterprise facts and hosting.

## Demo 4: Connect approved enterprise tools

**File:** `kickoffdemos/04_hosted_tools.py`

**Question answered:** Can the agent retrieve approved business context through bounded tools?

### Run

```powershell
python -B kickoffdemos\04_hosted_tools.py
```

### Say before running

> The opportunity now enters delivery qualification. The agent receives only an opportunity ID and must use approved tools to retrieve customer facts, architecture guidance, and an indicative Azure service profile.

### Point out in the output

Watch for these tool messages:

```text
[tool] CRM lookup: OPP-1042
[tool] Knowledge search:
[tool] Cost profile: OPP-1042 -> 12,000 requests/month
```

Explain the newly retrieved facts:

- `OPP-1042` is the approved CRM identifier.
- The volume of 12,000 requests per month comes from the CRM tool.
- The cost tool receives the opportunity ID and resolves the same approved CRM volume; it does not accept a model-invented request count.
- Architecture guidance comes from a bounded knowledge tool.
- Cost information is an illustrative service profile, not a quote.

Point out that `default_options={"store": False}` avoids storing the local tool-grounded response through the model API.

### Hosting message

Say:

> The tool and agent boundary is independent of where it runs. We are invoking it locally for a predictable presentation, while the same factory can be exposed through the Foundry Responses host in a configured Hosted Agent environment.

Do not run `--serve` during the standard presentation. Hosted mode is an optional deployment demonstration and requires the prerelease dependency plus a configured Hosted Agent environment.

### Do not claim

- The sample tools are simulated functions, not live CRM or pricing integrations.
- The cost profile is not an Azure quote.
- The agent does not submit an authorization or make a clinical decision.

### Transition

Say:

> We have moved from reasoning to evidence and then to governed action. The final enterprise question is operational: can we inspect what happened and measure whether the response met our expectations?

## Demo 5: Observe and evaluate the run

**File:** `kickoffdemos/05_observability.py`

**Question answered:** Can operators trace the agent and attach evaluation evidence to the same run?

### Run

```powershell
python -B kickoffdemos\05_observability.py
```

### Say before running

> This is the same Contoso prior-authorization solution entering operational assurance. Agent Framework emits the model and agent telemetry, and the application adds a business-specific evaluation to the trace.

### Point out in the terminal

The command reports:

- Telemetry destination
- Trace ID, or an explicit unavailable message when no telemetry exporter is active
- Enterprise coverage score
- Any missing criteria

The custom score checks whether the response covers:

- Architecture
- Security
- Cost
- Executive summary
- Human approval
- Observability

### Show in the trace destination

When the displayed Trace ID is valid, search for it in the configured destination and point out:

- Agent and model spans
- End-to-end latency
- Token usage when available
- Errors or status
- `demo.scenario_id`
- `demo.customer_industry=healthcare`
- `demo.content_capture_enabled=false`
- `evaluation.enterprise_coverage`
- `evaluation.missing_criteria`
- The `evaluation.completed` event

If the Trace ID is unavailable, do not claim that a trace was exported. Open or configure the intended telemetry destination, rerun the demo, and then use the valid Trace ID.

### Explain the score correctly

Say:

> This lightweight score demonstrates how application-specific evidence can travel with operational telemetry. It is not a clinical, safety, groundedness, or production-quality evaluation. A production program would add representative datasets, calibrated evaluators, thresholds, and release gates.

If the score is below 100%, treat that as a useful observation. Show the missing criteria in the trace and explain that evaluations expose gaps instead of hiding them.

### Privacy message

Point out that content capture is disabled by default. Do not use `--include-content` unless the scenario contains only approved non-sensitive data and the telemetry destination is approved.

## Close

Say:

> The progression is the product story. Agent Framework gives us a useful agent boundary. Foundry IQ grounds the offer in organizational experience. Tools add approved enterprise facts and controlled actions. Tracing and evaluation make the result operable. Tenant containment remains an explicit architecture requirement, and clinicians remain accountable for every submission.

Finish with five short takeaways:

1. Start with a narrow, useful agent.
2. Ground historical claims in governed organizational evidence.
3. Choose fixed or model-directed orchestration based on the required control boundary.
4. Put enterprise access behind explicit tools and identities.
5. Attach observability and evaluation before scaling the workflow.

## Claims to avoid

Do not make these claims during the presentation:

- The synthetic projects are real customer deployments.
- Historical time reductions are guaranteed Contoso outcomes.
- The sample performs medical-necessity, coverage, or treatment decisions.
- The agent autonomously submits payer authorizations.
- The illustrative service profile is a customer price quote.
- The phrase-based coverage score proves safety or production readiness.
- Preview Foundry IQ APIs carry production service-level commitments.

## Recovery guide

| Symptom | Presenter action |
| --- | --- |
| Azure authentication error | Run `az login`, confirm the intended subscription/tenant, then retry |
| Missing model or endpoint setting | Check `.env` privately; do not display it |
| Ingestion reports missing Search connection | Set `FOUNDRY_IQ_SEARCH_CONNECTION_NAME` or a direct Search endpoint |
| Demo 2 returns no evidence | Rerun `ingest_foundry_iq.py`, confirm three accepted documents, then retry |
| A model response varies in wording | Anchor the narration on headings, citations, tool calls, and controls rather than exact prose |
| Demo 4 omits a tool | Rerun once; use the visible tool messages as the success criterion |
| Demo 5 reports local spans only | Open the Foundry Toolkit trace viewer before rerunning or configure an exporter |
| Coverage score is below 100% | Show the missing criteria and explain how evaluation reveals a release gap |
| Network or service latency interrupts the flow | Use screenshots or saved non-sensitive output from a successful preflight; never expose `.env` |

## Presenter checklist

Before going on stage, confirm:

- [ ] The terminal is in the repository root.
- [ ] The virtual environment is active.
- [ ] Azure CLI authentication works.
- [ ] `.env` is populated and hidden from the audience.
- [ ] Ingestion accepts all three documents.
- [ ] Demo 2 retrieves `[0]`, `[1]`, and `[2]`.
- [ ] Demo 3 completes its Harness todo list and publishes a cited proposal.
- [ ] Demo 4 invokes CRM, guidance, and cost tools.
- [ ] A telemetry destination is ready for Demo 5.
- [ ] Content capture remains disabled.
- [ ] Terminal font size and window layout are readable.
- [ ] Backup screenshots contain no secrets or sensitive content.
