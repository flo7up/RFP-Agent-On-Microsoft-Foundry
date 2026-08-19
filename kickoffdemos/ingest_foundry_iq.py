"""Ingest three sample healthcare projects into Azure AI Search and Foundry IQ.

Validate the sample documents without contacting Azure:
    python kickoffdemos/ingest_foundry_iq.py --dry-run

Create or update the index, knowledge source, and knowledge base:
    python kickoffdemos/ingest_foundry_iq.py

Search authentication (choose one):
    FOUNDRY_IQ_SEARCH_ENDPOINT or AZURE_SEARCH_ENDPOINT
    FOUNDRY_PROJECT_ENDPOINT and FOUNDRY_IQ_SEARCH_CONNECTION_NAME

Optional environment variables:
    FOUNDRY_IQ_OPPORTUNITY_INDEX_NAME
    FOUNDRY_IQ_OPPORTUNITY_KNOWLEDGE_SOURCE_NAME
    FOUNDRY_IQ_OPPORTUNITY_KNOWLEDGE_BASE_NAME
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any

from azure.ai.projects import AIProjectClient
from azure.core.credentials import AzureKeyCredential
from azure.identity import AzureCliCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    KnowledgeBase,
    KnowledgeSourceReference,
    SearchableField,
    SearchFieldDataType,
    SearchIndex,
    SearchIndexFieldReference,
    SearchIndexKnowledgeSource,
    SearchIndexKnowledgeSourceParameters,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    SimpleField,
)
from dotenv import load_dotenv


SEARCH_API_VERSION = "2026-05-01-preview"
DEFAULT_INDEX_NAME = "si-healthcare-opportunity-history"
DEFAULT_KNOWLEDGE_SOURCE_NAME = "si-healthcare-opportunity-history-ks"
DEFAULT_KNOWLEDGE_BASE_NAME = "si-healthcare-opportunity-assessment-kb"
SEMANTIC_CONFIGURATION_NAME = "opportunity-project-semantic-config"

SECTION_FIELDS = (
    ("executive_summary", "Executive Summary"),
    ("customer_situation", "Customer Situation"),
    ("recommended_architecture", "Recommended Architecture"),
    ("microsoft_services_used", "Microsoft Services Used"),
    ("implementation_timeline", "Implementation Timeline"),
    ("security_considerations", "Security Considerations"),
    ("governance_controls", "Governance Controls"),
    ("success_metrics", "Success Metrics"),
    ("lessons_learned", "Lessons Learned"),
    ("future_expansion_opportunities", "Future Expansion Opportunities"),
)

SAMPLE_PROJECTS = [
    {
        "id": "northwind-health-prior-authorization-agent",
        "title": "Sample Historical Project - Northwind Health Prior Authorization Agent",
        "customer": "Northwind Health Network",
        "industry": "Healthcare provider",
        "document_type": "historical-project",
        "source_path": "DemoData/Past Projects/Northwind Health Prior Authorization Agent",
        "executive_summary": (
            "Northwind Health Network implemented an AI-assisted prior-authorization workflow for "
            "cardiology and orthopedics. The solution assembled approved clinical evidence, checked "
            "payer requirements, drafted submission packets, and required a clinician to approve every "
            "packet. The pilot reduced median preparation time from 118 minutes to 17 minutes while "
            "keeping protected health information inside Northwind's Azure tenant."
        ),
        "customer_situation": (
            "Staff across fourteen hospitals manually searched the electronic health record, payer "
            "policy PDFs, and SharePoint procedure guidance before entering data into payer portals. "
            "Incomplete packets caused rework and delayed care. Northwind required source-grounded "
            "answers, tenant-contained patient data, complete audit history, and accountable clinician "
            "review before submission."
        ),
        "recommended_architecture": (
            "A Microsoft Agent Framework workflow hosted by Microsoft Foundry Agent Service orchestrated "
            "record retrieval, policy matching, evidence extraction, packet drafting, and approval. "
            "Foundry IQ used Azure AI Search to ground decisions in approved payer policies and clinical "
            "guidance. Azure Health Data Services exposed FHIR records through a read-only tool. Azure API "
            "Management governed payer integrations, and a Power Automate approval routed every packet "
            "to the responsible clinician."
        ),
        "microsoft_services_used": (
            "Microsoft Foundry, Microsoft Agent Framework, Foundry Agent Service, Foundry IQ, Azure AI "
            "Search, Azure Health Data Services FHIR service, Azure API Management, Microsoft Entra ID, "
            "Azure Key Vault, Azure Monitor, Application Insights, Microsoft Purview, SharePoint, and "
            "Power Automate."
        ),
        "implementation_timeline": (
            "Fourteen weeks: two weeks for discovery and clinical-risk mapping; four weeks for data and "
            "policy connections; four weeks for agent workflow and evaluations; two weeks for a "
            "cardiology pilot; and two weeks for controlled orthopedics rollout and handover."
        ),
        "security_considerations": (
            "Microsoft Entra ID enforced role-based access and conditional access. Managed identities, "
            "private endpoints, Key Vault, encryption in transit and at rest, and minimum-necessary FHIR "
            "queries reduced PHI exposure. Retrieved documents were treated as untrusted input, and the "
            "agent could not submit a packet without a clinician's authenticated approval."
        ),
        "governance_controls": (
            "Clinical and compliance owners approved the source corpus and evaluation set. Purview "
            "classified sensitive data. Every retrieval, citation, tool call, draft, approval, and final "
            "submission was traced. Monthly quality reviews monitored groundedness, completeness, access "
            "violations, and payer-policy freshness. High-risk exceptions entered a human work queue."
        ),
        "success_metrics": (
            "Median preparation time decreased from 118 to 17 minutes; packet completeness reached 96 "
            "percent; 100 percent of submissions retained clinician approval; citation coverage reached "
            "98 percent; and the pilot recorded no severity-one privacy or safety incident."
        ),
        "lessons_learned": (
            "Policy ownership mattered more than prompt tuning. Payer-specific checklists improved "
            "retrieval precision, and specialty-specific evaluation sets exposed missing evidence early. "
            "The team kept portal submission outside the agent until approval and completeness targets "
            "were stable for six consecutive weeks."
        ),
        "future_expansion_opportunities": (
            "Extend the pattern to oncology and diagnostic imaging, detect payer-policy changes, draft "
            "appeal packets for denied requests, and add operational analytics that identify recurring "
            "documentation gaps by facility and specialty."
        ),
    },
    {
        "id": "fabrikam-specialty-care-authorization-copilot",
        "title": "Sample Historical Project - Fabrikam Specialty Care Authorization Copilot",
        "customer": "Fabrikam Specialty Care Alliance",
        "industry": "Specialty healthcare provider",
        "document_type": "historical-project",
        "source_path": "DemoData/Past Projects/Fabrikam Specialty Care Authorization Copilot",
        "executive_summary": (
            "Fabrikam Specialty Care Alliance deployed an authorization copilot for infusion therapy and "
            "specialty medications across forty-two outpatient clinics. The copilot found approved "
            "clinical records and payer criteria, highlighted missing evidence, and prepared a reviewable "
            "draft. Pharmacists or prescribing clinicians remained responsible for every authorization."
        ),
        "customer_situation": (
            "Authorization specialists spent 105 minutes on a typical request and frequently worked from "
            "outdated payer criteria stored in email and local folders. Clinical notes were available "
            "through FHIR APIs, while formulary rules and operating procedures lived in SharePoint. The "
            "organization needed faster preparation without moving PHI outside its tenant or allowing AI "
            "to make coverage or treatment decisions."
        ),
        "recommended_architecture": (
            "A Microsoft Agent Framework workflow in Microsoft Foundry separated policy retrieval, "
            "clinical-evidence collection, completeness checking, and packet drafting into bounded steps. "
            "Foundry IQ and Azure AI Search indexed approved formulary and payer documents with source "
            "citations. Azure Health Data Services provided FHIR context. Dynamics 365 Customer Service "
            "tracked work items, and Power Automate implemented pharmacist and clinician approvals."
        ),
        "microsoft_services_used": (
            "Microsoft Foundry, Microsoft Agent Framework, Foundry Agent Service, Foundry IQ, Azure AI "
            "Search, Azure Health Data Services, Dynamics 365 Customer Service, SharePoint, Power "
            "Automate, Microsoft Entra ID, Azure Key Vault, Azure Monitor, Application Insights, and "
            "Microsoft Purview."
        ),
        "implementation_timeline": (
            "Sixteen weeks: three weeks for process mapping and governance; four weeks for FHIR, "
            "SharePoint, and Dynamics 365 connections; four weeks for agent development; three weeks for "
            "groundedness, safety, and workflow evaluation; and two weeks for a supervised clinic pilot."
        ),
        "security_considerations": (
            "Least-privilege Entra groups separated authorization specialists, pharmacists, clinicians, "
            "and administrators. Managed identities and private networking protected service-to-service "
            "calls. Logs excluded clinical payloads, secrets remained in Key Vault, and retrieval enforced "
            "document permissions. No agent step could determine coverage or approve treatment."
        ),
        "governance_controls": (
            "A clinical AI review board approved use cases, risk classification, evaluation thresholds, "
            "and rollback criteria. Content owners attested payer-policy freshness every thirty days. "
            "Application Insights traces connected each answer to citations and tool activity. Failed "
            "groundedness, missing evidence, and prompt-injection detections forced human-only handling."
        ),
        "success_metrics": (
            "Median preparation time decreased from 105 to 19 minutes; first-pass packet acceptance "
            "improved by 22 percentage points; citation coverage reached 97 percent; missing-evidence "
            "rework fell 41 percent; and 100 percent of authorization decisions remained with qualified "
            "pharmacists or clinicians."
        ),
        "lessons_learned": (
            "Combining all specialties in one launch reduced precision, so the team introduced "
            "specialty-specific retrieval filters and evaluations. Clear missing-evidence explanations "
            "built more trust than a single confidence score. Adoption increased when the copilot wrote "
            "back to the existing Dynamics 365 work queue instead of creating a separate interface."
        ),
        "future_expansion_opportunities": (
            "Add proactive renewal alerts, denial-reason analytics, policy-change impact summaries, "
            "patient-status notifications, and a governed appeal-drafting workflow with legal and "
            "clinical approval."
        ),
    },
    {
        "id": "woodgrove-medical-imaging-authorization-agent",
        "title": "Sample Historical Project - Woodgrove Medical Imaging Authorization Agent",
        "customer": "Woodgrove Medical Group",
        "industry": "Regional healthcare provider",
        "document_type": "historical-project",
        "source_path": "DemoData/Past Projects/Woodgrove Medical Imaging Authorization Agent",
        "executive_summary": (
            "Woodgrove Medical Group introduced an agent-assisted prior-authorization process for MRI, "
            "CT, and PET imaging. The solution compared orders and clinical history with approved payer "
            "criteria, assembled cited evidence, and generated a submission draft for clinician review. "
            "The implementation focused on repeatable controls that could later support other referrals."
        ),
        "customer_situation": (
            "A centralized team handled 2,600 imaging authorizations per month. Preparation averaged 94 "
            "minutes because staff navigated multiple record systems and payer websites. Urgent requests "
            "were difficult to prioritize, and leaders lacked consistent metrics for avoidable denials. "
            "Woodgrove required tenant isolation, auditable evidence, explicit clinician accountability, "
            "and safe handling of incomplete or conflicting records."
        ),
        "recommended_architecture": (
            "Microsoft Agent Framework implemented a deterministic workflow hosted on Foundry Agent "
            "Service. Foundry IQ and Azure AI Search retrieved payer criteria, imaging guidelines, and "
            "internal procedures. Azure Health Data Services normalized FHIR observations and orders. "
            "Azure Functions calculated non-clinical completeness rules, Service Bus supported resilient "
            "work queues, and Power Automate captured clinician approval before portal submission."
        ),
        "microsoft_services_used": (
            "Microsoft Foundry, Microsoft Agent Framework, Foundry Agent Service, Foundry IQ, Azure AI "
            "Search, Azure Health Data Services, Azure Functions, Azure Service Bus, Power Automate, "
            "Microsoft Entra ID, Azure Key Vault, Azure Monitor, Application Insights, Microsoft Purview, "
            "and SharePoint."
        ),
        "implementation_timeline": (
            "Twelve weeks: two weeks for discovery and baseline measurement; three weeks for data and "
            "knowledge preparation; three weeks for workflow implementation; two weeks for evaluation "
            "and red-team testing; and two weeks for a supervised imaging pilot."
        ),
        "security_considerations": (
            "Entra ID, managed identities, private endpoints, customer-managed encryption keys, and "
            "network-restricted Search and FHIR services kept data inside the approved boundary. Field "
            "filtering limited the clinical context supplied to each tool. Prompt-injection defenses and "
            "output validation prevented retrieved documents from changing workflow policy."
        ),
        "governance_controls": (
            "A named clinical owner approved every automation boundary. The team versioned prompts, "
            "policies, evaluations, and agent releases; required citations for all evidence; retained "
            "approval and override reasons; and reviewed fairness, safety, privacy, and operational "
            "metrics before expanding beyond the pilot."
        ),
        "success_metrics": (
            "Median preparation time decreased from 94 to 16 minutes; same-day completion increased from "
            "54 to 89 percent; avoidable missing-document denials fell 35 percent; citation coverage "
            "reached 99 percent; and every submitted packet had an authenticated clinician approval."
        ),
        "lessons_learned": (
            "Urgency classification needed explicit rules and could not be delegated to the language "
            "model. Source documents required effective dates and payer metadata to avoid retrieving "
            "superseded criteria. A visible evidence checklist made clinician review faster and produced "
            "better feedback for subsequent evaluations."
        ),
        "future_expansion_opportunities": (
            "Extend to specialist referrals, automate policy-change regression tests, predict staffing "
            "demand from the work queue, draft denial appeals, and provide physicians with pre-order "
            "documentation guidance before an authorization reaches the central team."
        ),
    },
]


def required_setting(*names: str) -> str:
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    raise RuntimeError(f"Set one of these environment variables: {', '.join(names)}")


def resource_names() -> tuple[str, str, str]:
    return (
        os.getenv("FOUNDRY_IQ_OPPORTUNITY_INDEX_NAME", DEFAULT_INDEX_NAME),
        os.getenv("FOUNDRY_IQ_OPPORTUNITY_KNOWLEDGE_SOURCE_NAME", DEFAULT_KNOWLEDGE_SOURCE_NAME),
        os.getenv("FOUNDRY_IQ_OPPORTUNITY_KNOWLEDGE_BASE_NAME", DEFAULT_KNOWLEDGE_BASE_NAME),
    )


def search_access(credential: AzureCliCredential) -> tuple[str, Any]:
    endpoint = os.getenv("FOUNDRY_IQ_SEARCH_ENDPOINT") or os.getenv("AZURE_SEARCH_ENDPOINT")
    if endpoint:
        return endpoint.rstrip("/"), credential

    project_client = AIProjectClient(
        endpoint=required_setting("FOUNDRY_PROJECT_ENDPOINT", "AZURE_AI_PROJECT_ENDPOINT", "project_endpoint"),
        credential=credential,
    )
    try:
        connection = project_client.connections.get(
            name=required_setting("FOUNDRY_IQ_SEARCH_CONNECTION_NAME"),
            include_credentials=True,
        )
    finally:
        project_client.close()

    if not connection.target:
        raise RuntimeError("The Foundry Azure AI Search connection has no target endpoint.")
    search_key = connection.credentials.get("key") if connection.credentials else None
    search_credential = AzureKeyCredential(search_key) if search_key else credential
    return connection.target.rstrip("/"), search_credential


def build_documents() -> list[dict[str, str]]:
    if len(SAMPLE_PROJECTS) != 3:
        raise ValueError("The ingestion demo must contain exactly three sample projects.")

    documents: list[dict[str, str]] = []
    seen_ids: set[str] = set()
    required_metadata = ("id", "title", "customer", "industry", "document_type", "source_path")
    for project in SAMPLE_PROJECTS:
        missing = [
            field
            for field in (*required_metadata, *(field for field, _ in SECTION_FIELDS))
            if not project.get(field, "").strip()
        ]
        if missing:
            raise ValueError(f"{project.get('id', 'Unknown project')} is missing: {', '.join(missing)}")
        if project["id"] in seen_ids:
            raise ValueError(f"Duplicate sample project id: {project['id']}")
        seen_ids.add(project["id"])

        document = dict(project)
        document["content"] = "\n\n".join(
            f"{heading}\n{project[field]}" for field, heading in SECTION_FIELDS
        )
        documents.append(document)
    return documents


def create_index(index_name: str) -> SearchIndex:
    section_fields = [
        SearchableField(name=field, type=SearchFieldDataType.String)
        for field, _ in SECTION_FIELDS
    ]
    return SearchIndex(
        name=index_name,
        description="Structured sample healthcare projects for SI opportunity and offer acceleration.",
        fields=[
            SimpleField(name="id", type=SearchFieldDataType.String, key=True, filterable=True),
            SearchableField(name="title", type=SearchFieldDataType.String, filterable=True),
            SearchableField(name="customer", type=SearchFieldDataType.String, filterable=True, facetable=True),
            SearchableField(name="industry", type=SearchFieldDataType.String, filterable=True, facetable=True),
            SimpleField(name="document_type", type=SearchFieldDataType.String, filterable=True, facetable=True),
            SearchableField(name="source_path", type=SearchFieldDataType.String, filterable=True),
            *section_fields,
            SearchableField(name="content", type=SearchFieldDataType.String),
        ],
        semantic_search=SemanticSearch(
            default_configuration_name=SEMANTIC_CONFIGURATION_NAME,
            configurations=[
                SemanticConfiguration(
                    name=SEMANTIC_CONFIGURATION_NAME,
                    prioritized_fields=SemanticPrioritizedFields(
                        title_field=SemanticField(field_name="title"),
                        content_fields=[SemanticField(field_name="content")],
                        keywords_fields=[
                            SemanticField(field_name="customer"),
                            SemanticField(field_name="industry"),
                        ],
                    ),
                )
            ],
        ),
    )


def create_knowledge_source(index_name: str, knowledge_source_name: str) -> SearchIndexKnowledgeSource:
    searchable_fields = [
        SearchIndexFieldReference(name=field)
        for field in ("title", "customer", "industry", "content")
    ]
    source_fields = [
        SearchIndexFieldReference(name=field)
        for field in (
            "id",
            "title",
            "customer",
            "industry",
            "document_type",
            "source_path",
            *(field for field, _ in SECTION_FIELDS),
            "content",
        )
    ]
    return SearchIndexKnowledgeSource(
        name=knowledge_source_name,
        description=(
            "Past healthcare AI projects with architectures, controls, outcomes, lessons, and expansion ideas."
        ),
        search_index_parameters=SearchIndexKnowledgeSourceParameters(
            search_index_name=index_name,
            semantic_configuration_name=SEMANTIC_CONFIGURATION_NAME,
            search_fields=searchable_fields,
            source_data_fields=source_fields,
        ),
    )


def print_dry_run(documents: list[dict[str, str]]) -> None:
    print(f"Validated {len(documents)} sample historical projects.")
    print(f"Each project contains {len(SECTION_FIELDS)} required sections:")
    print("  " + ", ".join(heading for _, heading in SECTION_FIELDS))
    for document in documents:
        print(f"  - {document['title']}")


def ingest(documents: list[dict[str, str]], credential: AzureCliCredential) -> None:
    index_name, knowledge_source_name, knowledge_base_name = resource_names()
    endpoint, search_credential = search_access(credential)
    index_client = SearchIndexClient(
        endpoint=endpoint,
        credential=search_credential,
        api_version=SEARCH_API_VERSION,
    )
    search_client = SearchClient(
        endpoint=endpoint,
        index_name=index_name,
        credential=search_credential,
        api_version=SEARCH_API_VERSION,
    )
    try:
        print("\nINGESTING SAMPLE OPPORTUNITY HISTORY")
        print(f"  [1/4] Creating or updating index: {index_name}")
        index_client.create_or_update_index(create_index(index_name))

        print(f"  [2/4] Uploading {len(documents)} structured project documents")
        results = search_client.upload_documents(documents=documents)
        failures = [result.key for result in results if not result.succeeded]
        if failures:
            raise RuntimeError(f"Failed to upload documents: {', '.join(failures)}")
        print(f"        Accepted documents: {sum(result.succeeded for result in results)}")

        print(f"  [3/4] Creating or updating knowledge source: {knowledge_source_name}")
        index_client.create_or_update_knowledge_source(
            create_knowledge_source(index_name, knowledge_source_name)
        )

        print(f"  [4/4] Creating or updating knowledge base: {knowledge_base_name}")
        index_client.create_or_update_knowledge_base(
            KnowledgeBase(
                name=knowledge_base_name,
                description="Organizational project memory for SI opportunity and offer acceleration.",
                knowledge_sources=[KnowledgeSourceReference(name=knowledge_source_name)],
            )
        )
    finally:
        search_client.close()
        index_client.close()
    print("Foundry IQ ingestion complete.\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and summarize the three documents without contacting Azure.",
    )
    args = parser.parse_args()
    documents = build_documents()
    if args.dry_run:
        print_dry_run(documents)
        return

    credential = AzureCliCredential()
    try:
        ingest(documents, credential)
    finally:
        credential.close()


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    load_dotenv()
    main()
