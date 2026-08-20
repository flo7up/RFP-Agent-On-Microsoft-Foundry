# Running the Opportunity Assessment Demos

This guide explains how to prepare the local environment and run every demo in this repository. It is the operator-focused companion to [DEMO_GUIDE.md](DEMO_GUIDE.md), which contains the presentation narrative and timing.

The demos make live calls to Microsoft Foundry. Demos 2 and 3 also use Azure AI Search and Foundry IQ, with optional Blob Storage. Demo 5 can export telemetry. The healthcare opportunity and historical projects are synthetic, but Azure model, Search, optional Storage, and telemetry usage may incur charges.

## Run order

For a complete demonstration, use this order:

1. Create the Python environment and authenticate to Azure.
2. Configure `.env`.
3. Run the offline tests and Foundry IQ dry run.
4. Ingest three synthetic opportunities and their three linked proposals for Demo 2.
5. Run Demos 1 through 5.

The shortest command sequence, after setup and configuration, is:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -B kickoffdemos\ingest_foundry_iq.py --dry-run
.\.venv\Scripts\python.exe -B kickoffdemos\ingest_foundry_iq.py
.\.venv\Scripts\python.exe -B kickoffdemos\01_intro.py
.\.venv\Scripts\python.exe -B kickoffdemos\02_patterns.py
.\.venv\Scripts\python.exe -B kickoffdemos\03_harness.py
.\.venv\Scripts\python.exe -B kickoffdemos\04_hosted_tools.py
.\.venv\Scripts\python.exe -B kickoffdemos\05_observability.py
```

Run every command from the repository root, the directory containing [README.md](README.md) and [requirements.txt](requirements.txt).

## 1. Check prerequisites

The validated runtime is Python 3.12. You also need Azure CLI and access to:

- A Microsoft Foundry project.
- A model deployment in that project.
- Permission to create prompt-agent versions and invoke agents in the Foundry project.
- An Azure AI Search service for Demo 2.
- A Search connection in the Foundry project, or a direct Search endpoint with RBAC access.
- An Azure Storage account for Demo 2 proposal output.
- Optionally, Application Insights, an OTLP endpoint, or the Foundry Toolkit trace viewer for exported Demo 5 traces.

Check the local tools in PowerShell:

```powershell
py -3.12 --version
az --version
```

If the Python launcher is unavailable but `python` is Python 3.12, use `python --version` and substitute `python` for `py -3.12` in the environment-creation command below.

## 2. Create the Python environment

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Using the virtual environment's Python executable directly avoids PowerShell execution-policy problems. Activation is optional. To activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

### macOS or Linux

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The rest of this guide uses PowerShell commands. On macOS or Linux, replace `.\.venv\Scripts\python.exe` with `.venv/bin/python` and use `/` in paths.

## 3. Authenticate to Azure

All live demos use an Azure identity. The local scripts obtain that identity through `AzureCliCredential`.

```powershell
az login
az account show
```

Verify that `az account show` reports the tenant and subscription containing, or authorized to access, the Foundry project and Search service. If your account can access multiple tenants or subscriptions, select the intended context before continuing.

The signed-in identity needs permission to invoke the Foundry model deployment. For direct or keyless Search access, it also needs the Search data and service permissions required to manage the index, upload documents, create knowledge resources, and retrieve from the knowledge base. For proposal upload and a private read URL, assign Azure Storage Blob Data Contributor at the storage-account scope. Azure role changes can take several minutes to propagate.

## 4. Configure `.env`

Create a local configuration file from the safe template:

```powershell
Copy-Item .env.example .env
```

Edit `.env` privately. Do not paste credentials into source files, display `.env` during a presentation, or commit it. The repository's `.gitignore` excludes `.env` files other than the template.

Every numbered demo needs these values:

```dotenv
FOUNDRY_PROJECT_ENDPOINT=https://your-resource.services.ai.azure.com/api/projects/your-project
AZURE_AI_MODEL_DEPLOYMENT_NAME=your-model-deployment-name
```

Use the project endpoint, not the Foundry portal URL or the base resource endpoint. The deployment value is the deployment name configured in the project, which may differ from the underlying model family name.

### Choose one Search access mode for Demo 2

**Foundry project connection, recommended:**

```dotenv
FOUNDRY_IQ_SEARCH_CONNECTION_NAME=your-search-connection-name
```

The ingestion and retrieval scripts resolve the Search endpoint from this project connection. A key-based connection uses the connection's key in memory. A keyless connection uses the signed-in Azure CLI identity.

**Direct Search endpoint:**

```dotenv
FOUNDRY_IQ_SEARCH_ENDPOINT=https://your-search-service.search.windows.net
```

With this mode, the scripts use the signed-in Azure CLI identity. Remove or comment out the placeholder connection-name setting so the file does not imply that both modes are required. `AZURE_SEARCH_ENDPOINT` is also supported as an alias.

The default persistent resource names are:

| Resource | Default name |
| --- | --- |
| Search index | `si-healthcare-opportunity-history` |
| Foundry IQ knowledge source | `si-healthcare-opportunity-history-ks` |
| Foundry IQ knowledge base | `si-healthcare-opportunity-assessment-kb` |

Usually these names should remain unchanged. To share a Search service with another isolated copy of the demo, set all three optional overrides shown in [.env.example](.env.example). Ingestion and retrieval must use the same knowledge-source and knowledge-base names.

### Configure proposal storage for Demo 2

```dotenv
AZURE_STORAGE_ACCOUNT_URL=https://your-storage-account.blob.core.windows.net
# AZURE_STORAGE_PROPOSAL_CONTAINER_NAME=opportunity-proposals
```

The script creates a missing container as private. It returns a one-hour, read-only user-delegation SAS URL for a private container. If an existing container already has anonymous blob or container access, it returns the direct URL. The script does not change public-access policy.

### Optional telemetry for Demo 5

Configure at most one preferred export destination:

```dotenv
# APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=replace-me
# OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
```

Destination precedence is Application Insights, then an explicit OTLP endpoint, then a running Foundry Toolkit trace viewer on `localhost:4317`. If none is available, Demo 5 still runs and computes its score, but it reports local spans only.

## 5. Run offline preflight checks

Run the regression suite. It imports all scripts but does not call Azure:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

Expected result:

```text
OK
```

Next, validate the three synthetic Foundry IQ records without contacting Azure:

```powershell
.\.venv\Scripts\python.exe -B kickoffdemos\ingest_foundry_iq.py --dry-run
```

The output should report three validated projects and list Northwind, Fabrikam, and Woodgrove. A dry run verifies local data shape only; it does not validate Azure access or create resources.

You can also inspect every command-line option without making live calls:

```powershell
.\.venv\Scripts\python.exe -B kickoffdemos\01_intro.py --help
.\.venv\Scripts\python.exe -B kickoffdemos\02_patterns.py --help
.\.venv\Scripts\python.exe -B kickoffdemos\03_harness.py --help
.\.venv\Scripts\python.exe -B kickoffdemos\04_hosted_tools.py --help
.\.venv\Scripts\python.exe -B kickoffdemos\05_observability.py --help
```

## 6. Ingest Foundry IQ project memory

Demo 2 requires one successful ingestion before it can retrieve opportunity and linked-proposal evidence:

```powershell
.\.venv\Scripts\python.exe -B kickoffdemos\ingest_foundry_iq.py
```

A successful run reports:

The successful run creates or updates both vectorized indexes, accepts three documents in each, and updates both planner-backed knowledge bases.

The operation is idempotent. Rerunning it updates the same two indexes, knowledge sources, knowledge bases, and document IDs. The Azure resources persist after the process exits.

## 7. Run Demo 1: baseline assessment

```powershell
.\.venv\Scripts\python.exe -B kickoffdemos\01_intro.py
```

The script publishes a new version of `partner-solution-assessment-intro` with an `opportunity_tool` declaration, then binds that tool's local implementation to `FoundryAgent`. The run prompt contains no customer facts, so the agent must call the no-argument tool to read [data/default_opportunity.txt](data/default_opportunity.txt) before assessing it. A successful response contains these exact headings:

- `AI Opportunities`
- `Architecture Proposal`
- `Delivery Risks`
- `Executive Summary`

To assess a different opportunity, edit [data/default_opportunity.txt](data/default_opportunity.txt), then rerun the script. Model wording varies between runs. Validate the headings, assumptions, human oversight, and tenant boundary instead of exact prose.

## 8. Run Demo 2: grounded proposal artifact

```powershell
.\.venv\Scripts\python.exe -B kickoffdemos\02_patterns.py
```

The command retrieves the three synthetic project records, generates one cited Markdown proposal, uploads it as `draft-opportunity-proposal-<UTC timestamp>.md` with overwrite disabled, and prints only its URL. Open that URL to inspect the proposal.

You may pass a custom opportunity:

```powershell
.\.venv\Scripts\python.exe -B kickoffdemos\02_patterns.py "A hospital wants to streamline imaging referrals with clinician review."
```

Use an opportunity reasonably similar to the three healthcare records. An unrelated opportunity can retrieve weak evidence, which is expected for this small corpus. A private-container URL includes a temporary SAS query string; do not publish that live credential in a recording. Use an approved public container for a clean direct URL, redact the query, or publish the video only after the one-hour SAS expires.

## 9. Run Demo 3: Harness orchestration

Run the full comparison with visible progress:

```powershell
.\.venv\Scripts\python.exe -B kickoffdemos\03_harness.py --verbose
```

The Harness receives bounded opportunity retrieval, linked-proposal retrieval, and publication tools. It plans the work through its built-in todo and mode providers instead of using the fixed `WorkflowBuilder` graph from Demo 2. A successful run completes its todos, validates citations, publishes a timestamped proposal, and prints the output URL or path.

For the observable pixel-art experience, launch Harness Office and open `http://127.0.0.1:8090`:

```powershell
.\.venv\Scripts\python.exe -B kickoffdemos\03_harness.py --playground
```

The live work plan comes from actual `TodoProvider` add, complete, and remove calls; it has no fixed
step count. Structured middleware and bounded-tool events move the character between the desk,
Foundry IQ shelves, notebook, and printer. The journey keeps repeated visits, so weak retrieval or a
failed validation visibly sends the agent back. Timeline messages summarize observable actions and
results; they do not expose private chain-of-thought. If needed, choose another loopback port with
`--playground-port <port>`. In idle and after completion, the character returns to its nap nook. Each
run starts with a visitor ringing the doorbell and handing over the opportunity, which wakes the
character and plays a short stretch before the first workstation visit.

For the smallest possible one-tool Harness example, run:

```powershell
.\.venv\Scripts\python.exe -B kickoffdemos\03_harness_simple.py
```

That companion uses one synthetic weather tool and does not access the opportunity scenario, Search, or Storage.

## 10. Run Demo 4: enterprise tools

Run the tool-grounded agent locally:

```powershell
.\.venv\Scripts\python.exe -B kickoffdemos\04_hosted_tools.py
```

The model receives only opportunity ID `OPP-1042` in the default prompt. A successful run normally displays all three bounded tool calls:

```text
[tool] CRM lookup: OPP-1042
[tool] Knowledge search:
[tool] Cost profile: OPP-1042 -> 12,000 requests/month
```

The final recommendation should distinguish approved facts from assumptions, retain human approval, and label costs as illustrative. The tools are local simulations; they are not live CRM or pricing integrations.

To supply another instruction while retaining the same approved sample record:

```powershell
.\.venv\Scripts\python.exe -B kickoffdemos\04_hosted_tools.py --prompt "Assess OPP-1042 and emphasize governance and delivery risks."
```

The simulated CRM only recognizes `OPP-1042`. Other IDs intentionally return no approved record.

### Optional hosted mode

Hosted mode is separate from the standard local presentation. Install its prerelease dependency with:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-hosted.txt
```

The entry point is:

```powershell
.\.venv\Scripts\python.exe -B kickoffdemos\04_hosted_tools.py --serve
```

Use `--serve` only in a configured Foundry Hosted Agent environment that supplies the platform-managed Responses endpoint and identity. Installing the additional package alone does not provision or deploy a Hosted Agent. For the normal demo, use local mode.

## 11. Run Demo 5: observability and evaluation

Open or configure the intended telemetry destination first, then run:

```powershell
.\.venv\Scripts\python.exe -B kickoffdemos\05_observability.py
```

The terminal reports:

- The selected telemetry destination.
- A Trace ID, or an unavailable message when no exporter is active.
- The enterprise coverage score.
- Any missing criteria.

The score checks whether the model response mentions architecture, security, cost, executive summary, human approval, and observability. It is an illustrative phrase-based check, not a clinical, safety, groundedness, or production-readiness evaluation.

When a valid Trace ID is shown, use it to find the run in the configured destination. Inspect agent and model spans, latency, token usage when available, errors, scenario attributes, and the `evaluation.completed` event.

Content capture is disabled by default. The demo records operational attributes without exporting prompt and completion bodies. For approved, non-sensitive test data only, content capture can be enabled explicitly:

```powershell
.\.venv\Scripts\python.exe -B kickoffdemos\05_observability.py --include-content
```

Do not use `--include-content` with PHI, credentials, customer data, or an unapproved telemetry destination.

## Stopping and rerunning

- Press Ctrl+C to stop a local demo.
- Demo 1 creates a persistent prompt-agent version named `partner-solution-assessment-intro` on each run.
- Demos 4 and 5 do not create persistent application data in this repository.
- All agents set `default_options={"store": False}` so their Responses API calls do not store model responses.
- Foundry IQ ingestion creates persistent Search resources and documents. Rerunning ingestion updates them; it does not duplicate the three fixed document IDs.
- Every full Demo 2 or Demo 3 run creates a new timestamped proposal blob. The container and blobs persist.
- This repository has no cleanup command. Delete unneeded Demo 1 agent versions and Demo 2 Search and Blob resources through your normal Azure resource-management process only when they are no longer shared or needed.

## Troubleshooting

| Symptom | Check and recovery |
| --- | --- |
| `python` cannot open a demo file | Return to the repository root and rerun the command. |
| PowerShell blocks `Activate.ps1` | Skip activation and use `.\.venv\Scripts\python.exe` as shown in this guide. |
| `ModuleNotFoundError` | Confirm the command uses `.venv`, then reinstall `requirements.txt` with that same Python executable. |
| Azure credential or login error | Run `az login`, then `az account show` and verify the tenant and subscription. |
| HTTP 401 or 403 | Verify model and Search role assignments for the signed-in identity. Allow time for recent RBAC changes to propagate. |
| Missing project endpoint or model | Check the two required values in `.env`. Use the Foundry project endpoint and the deployment name. |
| Search connection is missing | Set `FOUNDRY_IQ_SEARCH_CONNECTION_NAME`, or configure `FOUNDRY_IQ_SEARCH_ENDPOINT` for direct RBAC access. |
| Ingestion fails before document upload | Verify Search endpoint resolution, Search API compatibility, network access, and service-level permissions. |
| Demo 2 returns no project evidence | Confirm ingestion accepted three documents and that ingestion and retrieval use the same knowledge-base overrides. Rerun ingestion, then retry retrieval after indexing completes. |
| Demo 2 reports a Storage 403 | Verify `AZURE_STORAGE_ACCOUNT_URL` and assign Azure Storage Blob Data Contributor at the account scope; allow RBAC propagation time. |
| Demo 2 cannot create a user-delegation key | Move the Blob role assignment to storage-account scope, or use an existing approved public container. |
| The proposal URL has a query string | The container is private, so the URL contains a one-hour read-only SAS. This is expected. |
| Demo 2 proposal wording differs | Model output is nondeterministic. Open the file and validate its sections, citations, recommendations, and clinician approval boundary. |
| Demo 3 does not complete its todo list | Rerun with `--verbose`; confirm retrieval completed before publication. |
| Demo 4 omits a tool message | Rerun once. The visible CRM, knowledge, and cost tool messages are the success criterion. |
| `--serve` cannot import the hosting package | Install `requirements-hosted.txt`; also verify that the process is running in a configured Hosted Agent environment. |
| Demo 5 reports `local spans only` | Open the Foundry Toolkit trace viewer before rerunning, or configure Application Insights or an OTLP endpoint in `.env`. |
| Demo 5 score is below 100% | Review the reported missing criteria. This is a visible evaluation result, not a script failure. |
| Trace ID is unavailable | No active exporter produced a valid trace context. Configure the destination, restart the script, and use the new Trace ID. |

## Final pre-demo checklist

- [ ] Python 3.12 environment is installed and selected.
- [ ] Base dependencies are installed.
- [ ] Azure CLI is signed in to the intended tenant and subscription.
- [ ] `.env` contains the project endpoint and model deployment name.
- [ ] One Search access mode is configured.
- [ ] Embedding endpoint, deployment, model, and required managed-identity roles are configured.
- [ ] Offline tests pass.
- [ ] Foundry IQ dry run validates three opportunities and three proposals.
- [ ] Live ingestion accepts three documents in each index.
- [ ] Demo 2 prints one output path or URL and the proposal opens.
- [ ] Demo 3 completes its Harness todo list and publishes a cited proposal.
- [ ] Demo 4 calls CRM, knowledge, and cost tools.
- [ ] Demo 5 has the intended telemetry destination.
- [ ] Prompt and completion content capture remains disabled.
- [ ] No credentials, `.env` values, or sensitive traces are visible to the audience.