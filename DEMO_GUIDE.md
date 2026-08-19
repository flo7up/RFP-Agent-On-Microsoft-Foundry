# Presenter Guide: Opportunity Assessment Agent

This runbook presents the four demo files as one story for Microsoft partners and system integrators. The complete presentation takes about 20 minutes.

## The story

Your company is a Microsoft systems integrator responding to a healthcare opportunity from Contoso Health.

Contoso wants to reduce prior-authorization preparation from about two hours to fifteen minutes. Staff must use approved clinical records, protected health information must remain inside the tenant, and a clinician must approve every submission.

The account team needs to answer four questions:

1. Can an agent turn the opportunity into a useful first assessment?
2. Can the assessment reuse the firm's delivery experience instead of relying only on model knowledge?
3. Can the agent work with approved enterprise systems and explicit tool boundaries?
4. Can the resulting solution be traced and evaluated in operation?

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
| Opportunity ID is `OPP-1042` | Approved CRM record retrieved in Demo 3 |
| Volume is 12,000 requests per month | Approved CRM record retrieved in Demo 3 |
| Historical projects and outcomes are synthetic samples | Foundry IQ corpus used in Demo 2 |

Do not mention `OPP-1042` or 12,000 requests as known facts before Demo 3. Their appearance demonstrates that tool access can add approved enterprise context.

## Core message

Use this sentence to connect the four demos:

> We start with a useful agent, ground it in organizational experience, connect it to governed enterprise tools, and make its operation observable.

## Timing

| Segment | Time | Outcome |
| --- | ---: | --- |
| Opening | 1 minute | Establish the customer opportunity |
| Demo 1 | 3 minutes | Show a useful model-based assessment |
| Demo 2 | 8 minutes | Improve the offer with Foundry IQ project memory |
| Demo 3 | 4 minutes | Add approved enterprise tools and hosting boundary |
| Demo 4 | 3 minutes | Trace and evaluate the agent run |
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
- Optional telemetry settings for Demo 4

Never display `.env` during the presentation.

### 2. Validate and ingest project memory

The ingestion script is setup for Demo 2, not one of the four numbered demos.

```powershell
python -B kickoffdemos\ingest_foundry_iq.py --dry-run
python -B kickoffdemos\ingest_foundry_iq.py
```

Confirm that the live command reports:

```text
[1/4] Creating or updating index
[2/4] Uploading 3 structured project documents
        Accepted documents: 3
[3/4] Creating or updating knowledge source
[4/4] Creating or updating knowledge base
Foundry IQ ingestion complete.
```

The command is idempotent. It updates the same index, knowledge source, knowledge base, and three document IDs.

### 3. Prepare tracing for Demo 4

Choose one telemetry destination before the presentation:

- Configure `APPLICATIONINSIGHTS_CONNECTION_STRING` in `.env`.
- Configure `OTEL_EXPORTER_OTLP_ENDPOINT` in `.env`.
- Open the Foundry Toolkit trace viewer so it listens on `localhost:4317`.

Do not use `--include-content` in a customer setting. The included scenario is synthetic, but leaving content capture off demonstrates the safer production default.

### 4. Preflight all four commands

Run the offline regression suite, then run all four demos once before the audience arrives:

```powershell
python -B -m unittest discover -s tests -v
python -B kickoffdemos\01_intro.py
python -B kickoffdemos\02_patterns.py
python -B kickoffdemos\03_hosted_tools.py
python -B kickoffdemos\04_observability.py
```

Keep one terminal at the repository root, increase its font size, and clear previous output before starting.

## Opening

Say:

> Contoso Health has a concrete operational problem. Prior-authorization preparation takes about two hours, and the target is fifteen minutes. The workflow uses protected clinical data, data must remain in the tenant, and every submission needs clinician approval. We will build confidence in the solution through four increasingly enterprise-ready capabilities.

Do not show architecture slides first. Start with the opportunity and let each demo earn the next layer of architecture.

## Demo 1: Useful first assessment

**File:** `kickoffdemos/01_intro.py`

**Question answered:** Can one agent turn an opportunity into a useful first assessment?

### Run

```powershell
python -B kickoffdemos\01_intro.py
```

### Say before running

> We begin with the smallest useful Agent Framework application: one agent, one Foundry-hosted model, and a clear role. It receives the customer opportunity and produces an architecture-ready brief.

### Point out in the output

The response should contain these four headings:

- `AI Opportunities`
- `Architecture Proposal`
- `Delivery Risks`
- `Executive Summary`

Call attention to:

- The output is concise and immediately useful to an account team.
- Human oversight and tenant boundaries appear in the recommendation.
- Assumptions and risks are visible instead of hidden.
- The assessment is still based on the opportunity and model reasoning only.

### Do not claim

Do not say that this response uses prior projects, CRM facts, or authoritative customer data. It does not.

### Transition

Say:

> This is a credible first draft, but a systems integrator has something more valuable than a generic first draft: experience from prior deliveries. The next step turns that experience into governed organizational memory.

## Demo 2: Ground the offer in delivery experience

**File:** `kickoffdemos/02_patterns.py`

**Question answered:** Can the assessment reuse similar delivery experience and cite it?

### Run

For a controlled presentation, use pauses without the open-ended audience loop:

```powershell
python -B kickoffdemos\02_patterns.py --pause
```

Press Enter after explaining each step.

Use `--interactive` only when you intentionally want audience questions after the scripted flow:

```powershell
python -B kickoffdemos\02_patterns.py --pause --interactive
```

Type `exit` to end the interactive loop.

### Step 1: Assess the opportunity

Say:

> This first step establishes the control: the same new opportunity is assessed without organizational project memory. It gives us a direct before-and-after comparison.

Point out the line:

```text
WITHOUT FOUNDRY IQ: model reasoning only
```

This step intentionally overlaps with Demo 1. Move through it quickly; its purpose here is comparison, not introducing the basic agent again.

### Step 2: Retrieve similar projects

Say:

> Foundry IQ now searches a governed Azure AI Search corpus containing three synthetic historical projects. The retrieval layer returns evidence and native reference IDs before the model prepares the comparison.

Point out:

- Retrieval activity names the knowledge source and match count.
- Exactly three project titles are displayed.
- Native references `[0]`, `[1]`, and `[2]` identify the evidence supplied to the agent.
- Northwind, Fabrikam, and Woodgrove are synthetic historical examples.

Do not describe the three projects as customer references or real deployments.

### Step 3: Build the offer

Say:

> The agent now converts retrieved project experience into a reusable SI offer structure. Historical facts carry citations; new design choices remain recommendations.

Point out the offer sections:

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

Call attention to citations beside historical architectures, lessons, timelines, or metrics. Explicitly state that historical outcomes are evidence, not guarantees for Contoso.

### Step 4: Executive recommendation

Say:

> The final step distills the grounded offer for the account team. It preserves the clinician as the accountable decision-maker and proposes a controlled first phase.

End on these two lines:

```text
Without Foundry IQ: The agent proposes a plausible solution from model knowledge.
With Foundry IQ: The agent accelerates offer creation using organizational delivery experience.
```

### Optional follow-up question

If interactive mode is enabled, use this prepared question:

```text
Which controls and evaluation gates should we require before expanding from one specialty to the full health system?
```

Point out that the follow-up performs a new retrieval and cites project evidence again.

### Transition

Say:

> We now have an evidence-grounded offer. Delivery still requires current enterprise facts, governed actions, and cost context. Those should enter through explicit tools, not through prompt text or model memory.

## Demo 3: Connect approved enterprise tools

**File:** `kickoffdemos/03_hosted_tools.py`

**Question answered:** Can the agent retrieve approved business context through bounded tools?

### Run

```powershell
python -B kickoffdemos\03_hosted_tools.py
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

## Demo 4: Observe and evaluate the run

**File:** `kickoffdemos/04_observability.py`

**Question answered:** Can operators trace the agent and attach evaluation evidence to the same run?

### Run

```powershell
python -B kickoffdemos\04_observability.py
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

Finish with four short takeaways:

1. Start with a narrow, useful agent.
2. Ground historical claims in governed organizational evidence.
3. Put enterprise access behind explicit tools and identities.
4. Attach observability and evaluation before scaling the workflow.

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
| Demo 3 omits a tool | Rerun once; use the visible tool messages as the success criterion |
| Demo 4 reports local spans only | Open the Foundry Toolkit trace viewer before rerunning or configure an exporter |
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
- [ ] Demo 3 invokes CRM, guidance, and cost tools.
- [ ] A telemetry destination is ready for Demo 4.
- [ ] Content capture remains disabled.
- [ ] Terminal font size and window layout are readable.
- [ ] Backup screenshots contain no secrets or sensitive content.
