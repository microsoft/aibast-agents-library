"""
SharePoint Document Extractor Agent

Searches SharePoint document libraries, extracts URLs, enriches metadata,
and validates document links for accessibility.

Where a real deployment would connect to SharePoint APIs, this agent uses
a synthetic data layer so it runs anywhere without credentials.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))

from basic_agent import BasicAgent

# ═══════════════════════════════════════════════════════════════
# RAPP AGENT MANIFEST
# ═══════════════════════════════════════════════════════════════
__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/sharepoint-document-extractor",
    "version": "1.0.0",
    "display_name": "SharePoint Document Extractor",
    "description": "SharePoint document search, URL extraction, metadata enrichment, and link validation.",
    "author": "AIBAST",
    "tags": ["sharepoint", "documents", "url-extraction", "metadata", "search"],
    "category": "general",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ═══════════════════════════════════════════════════════════════
# SYNTHETIC DATA LAYER
# ═══════════════════════════════════════════════════════════════

_DOCUMENT_LIBRARY = {
    "DOC-001": {"id": "DOC-001", "title": "Enterprise Platform - Product Brief", "file_name": "Enterprise_Platform_Brief_v3.pdf", "library": "Sales Collateral", "folder": "/Products/Platform", "size_kb": 2450, "type": "PDF", "modified": "2025-10-28", "modified_by": "Marketing Team", "url": "https://contoso.sharepoint.com/sites/sales/Shared%20Documents/Products/Platform/Enterprise_Platform_Brief_v3.pdf", "tags": ["product", "platform", "enterprise", "brief"]},
    "DOC-002": {"id": "DOC-002", "title": "Q3 2025 Sales Playbook", "file_name": "Q3_2025_Sales_Playbook.pptx", "library": "Sales Enablement", "folder": "/Playbooks/2025", "size_kb": 8900, "type": "PowerPoint", "modified": "2025-09-15", "modified_by": "Sales Ops", "url": "https://contoso.sharepoint.com/sites/sales/Shared%20Documents/Playbooks/2025/Q3_2025_Sales_Playbook.pptx", "tags": ["playbook", "sales", "q3", "2025"]},
    "DOC-003": {"id": "DOC-003", "title": "Competitive Analysis - Competitor B", "file_name": "Competitive_Analysis_CompB_2025.xlsx", "library": "Competitive Intel", "folder": "/Competitors", "size_kb": 1200, "type": "Excel", "modified": "2025-11-05", "modified_by": "Product Marketing", "url": "https://contoso.sharepoint.com/sites/sales/Shared%20Documents/Competitors/Competitive_Analysis_CompB_2025.xlsx", "tags": ["competitive", "analysis", "competitor-b"]},
    "DOC-004": {"id": "DOC-004", "title": "ROI Calculator Template", "file_name": "ROI_Calculator_Template_v2.xlsx", "library": "Sales Tools", "folder": "/Calculators", "size_kb": 350, "type": "Excel", "modified": "2025-08-20", "modified_by": "Finance Team", "url": "https://contoso.sharepoint.com/sites/sales/Shared%20Documents/Calculators/ROI_Calculator_Template_v2.xlsx", "tags": ["roi", "calculator", "template", "pricing"]},
    "DOC-005": {"id": "DOC-005", "title": "Customer Reference - Meridian Corp Case Study", "file_name": "Meridian_Corp_Case_Study.pdf", "library": "Customer Success", "folder": "/Case Studies/Technology", "size_kb": 1800, "type": "PDF", "modified": "2025-10-10", "modified_by": "Customer Success", "url": "https://contoso.sharepoint.com/sites/sales/Shared%20Documents/Case%20Studies/Technology/Meridian_Corp_Case_Study.pdf", "tags": ["case-study", "meridian", "technology", "reference"]},
    "DOC-006": {"id": "DOC-006", "title": "MSA Template - Enterprise Agreement", "file_name": "MSA_Enterprise_Template_2025.docx", "library": "Legal Templates", "folder": "/Contracts/Templates", "size_kb": 420, "type": "Word", "modified": "2025-07-01", "modified_by": "Legal Team", "url": "https://contoso.sharepoint.com/sites/legal/Shared%20Documents/Contracts/Templates/MSA_Enterprise_Template_2025.docx", "tags": ["contract", "msa", "enterprise", "template", "legal"]},
    "DOC-007": {"id": "DOC-007", "title": "HIPAA Compliance Whitepaper", "file_name": "HIPAA_Compliance_Whitepaper.pdf", "library": "Compliance", "folder": "/Healthcare", "size_kb": 3200, "type": "PDF", "modified": "2025-09-20", "modified_by": "Compliance Team", "url": "https://contoso.sharepoint.com/sites/compliance/Shared%20Documents/Healthcare/HIPAA_Compliance_Whitepaper.pdf", "tags": ["hipaa", "compliance", "healthcare", "whitepaper"]},
}

_METADATA_FIELDS = {
    "standard": ["Title", "File Name", "Modified", "Modified By", "File Size", "Content Type"],
    "custom": ["Document Category", "Target Audience", "Approval Status", "Expiration Date", "Confidentiality Level"],
    "search": ["Tags", "Full Text Index", "Associated Account", "Deal Stage"],
}

_URL_PATTERNS = {
    "direct_download": "https://{tenant}.sharepoint.com/sites/{site}/_layouts/15/download.aspx?SourceUrl={encoded_path}",
    "web_view": "https://{tenant}.sharepoint.com/sites/{site}/_layouts/15/Doc.aspx?sourcedoc={doc_id}",
    "sharing_link": "https://{tenant}.sharepoint.com/:b:/s/{site}/{share_id}",
    "embed": "https://{tenant}.sharepoint.com/sites/{site}/_layouts/15/embed.aspx?UniqueId={doc_id}",
}

_LINK_VALIDATION_RESULTS = [
    {"doc_id": "DOC-001", "status": "Valid", "http_code": 200, "accessible": True, "permissions": "Organization", "last_checked": "2025-11-14T10:00:00Z"},
    {"doc_id": "DOC-002", "status": "Valid", "http_code": 200, "accessible": True, "permissions": "Sales Team", "last_checked": "2025-11-14T10:00:01Z"},
    {"doc_id": "DOC-003", "status": "Valid", "http_code": 200, "accessible": True, "permissions": "Sales Team", "last_checked": "2025-11-14T10:00:02Z"},
    {"doc_id": "DOC-004", "status": "Valid", "http_code": 200, "accessible": True, "permissions": "Organization", "last_checked": "2025-11-14T10:00:03Z"},
    {"doc_id": "DOC-005", "status": "Valid", "http_code": 200, "accessible": True, "permissions": "Organization", "last_checked": "2025-11-14T10:00:04Z"},
    {"doc_id": "DOC-006", "status": "Restricted", "http_code": 403, "accessible": False, "permissions": "Legal Team Only", "last_checked": "2025-11-14T10:00:05Z"},
    {"doc_id": "DOC-007", "status": "Valid", "http_code": 200, "accessible": True, "permissions": "Organization", "last_checked": "2025-11-14T10:00:06Z"},
]


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _search_documents(query):
    if not query:
        return list(_DOCUMENT_LIBRARY.values())
    q = query.lower()
    results = []
    for doc in _DOCUMENT_LIBRARY.values():
        if (q in doc["title"].lower() or q in doc["file_name"].lower() or
                any(q in tag for tag in doc["tags"])):
            results.append(doc)
    return results if results else list(_DOCUMENT_LIBRARY.values())[:3]


def _get_validation_status(doc_id):
    for v in _LINK_VALIDATION_RESULTS:
        if v["doc_id"] == doc_id:
            return v
    return {"status": "Unknown", "http_code": 0, "accessible": False, "permissions": "Unknown"}


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

class SharePointDocumentExtractorAgent(BasicAgent):
    """
    SharePoint document search and URL extraction agent.

    Operations:
        document_search      - search SharePoint for documents
        url_extraction       - extract shareable URLs for documents
        metadata_enrichment  - enrich document metadata
        link_validation      - validate document link accessibility
    """

    def __init__(self):
        self.name = "SharePointDocumentExtractorAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "document_search", "url_extraction",
                            "metadata_enrichment", "link_validation",
                        ],
                        "description": "The SharePoint operation to perform",
                    },
                    "search_query": {
                        "type": "string",
                        "description": "Search query for documents",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "document_search")
        query = kwargs.get("search_query", "")
        dispatch = {
            "document_search": self._document_search,
            "url_extraction": self._url_extraction,
            "metadata_enrichment": self._metadata_enrichment,
            "link_validation": self._link_validation,
        }
        handler = dispatch.get(op)
        if not handler:
            return f"Unknown operation: {op}"
        return handler(query)

    def _document_search(self, query):
        results = _search_documents(query)
        rows = ""
        for doc in results:
            rows += f"| {doc['id']} | {doc['title'][:35]} | {doc['type']} | {doc['library']} | {doc['modified']} | {doc['size_kb']:,} KB |\n"
        return (
            f"**SharePoint Document Search**\n"
            f"Query: \"{query or 'all documents'}\"\n\n"
            f"| ID | Title | Type | Library | Modified | Size |\n|---|---|---|---|---|---|\n"
            f"{rows}\n"
            f"**Results:** {len(results)} document(s) found\n\n"
            f"Source: [SharePoint Search API]\nAgents: SharePointDocumentExtractorAgent"
        )

    def _url_extraction(self, query):
        results = _search_documents(query)
        url_rows = ""
        for doc in results:
            url_rows += f"| {doc['id']} | {doc['title'][:30]} | [Link]({doc['url']}) |\n"
        pattern_rows = ""
        for pattern_name, template in _URL_PATTERNS.items():
            pattern_rows += f"| {pattern_name.replace('_', ' ').title()} | `{template[:60]}...` |\n"
        return (
            f"**URL Extraction Results**\n\n"
            f"| ID | Document | URL |\n|---|---|---|\n"
            f"{url_rows}\n"
            f"**URL Patterns Available:**\n\n"
            f"| Type | Pattern |\n|---|---|\n"
            f"{pattern_rows}\n\n"
            f"Source: [SharePoint Document Library]\nAgents: SharePointDocumentExtractorAgent"
        )

    def _metadata_enrichment(self, query):
        results = _search_documents(query)
        if results:
            doc = results[0]
            meta_rows = ""
            meta_rows += f"| Title | {doc['title']} |\n"
            meta_rows += f"| File Name | {doc['file_name']} |\n"
            meta_rows += f"| Library | {doc['library']} |\n"
            meta_rows += f"| Folder | {doc['folder']} |\n"
            meta_rows += f"| Type | {doc['type']} |\n"
            meta_rows += f"| Size | {doc['size_kb']:,} KB |\n"
            meta_rows += f"| Modified | {doc['modified']} |\n"
            meta_rows += f"| Modified By | {doc['modified_by']} |\n"
            meta_rows += f"| Tags | {', '.join(doc['tags'])} |\n"
        else:
            meta_rows = "| No document found | - |\n"
        field_rows = ""
        for cat, fields in _METADATA_FIELDS.items():
            field_rows += f"| {cat.title()} | {', '.join(fields)} |\n"
        return (
            f"**Metadata Enrichment**\n\n"
            f"**Document Metadata:**\n\n"
            f"| Field | Value |\n|---|---|\n"
            f"{meta_rows}\n"
            f"**Available Metadata Fields:**\n\n"
            f"| Category | Fields |\n|---|---|\n"
            f"{field_rows}\n\n"
            f"Source: [SharePoint Metadata API]\nAgents: SharePointDocumentExtractorAgent"
        )

    def _link_validation(self, query):
        rows = ""
        valid_count = 0
        for v in _LINK_VALIDATION_RESULTS:
            doc = _DOCUMENT_LIBRARY.get(v["doc_id"], {})
            status_icon = "Pass" if v["accessible"] else "Fail"
            rows += f"| {v['doc_id']} | {doc.get('title', 'Unknown')[:30]} | {v['status']} | {v['http_code']} | {status_icon} | {v['permissions']} |\n"
            if v["accessible"]:
                valid_count += 1
        total = len(_LINK_VALIDATION_RESULTS)
        return (
            f"**Link Validation Report**\n\n"
            f"| Metric | Value |\n|---|---|\n"
            f"| Total Links | {total} |\n"
            f"| Valid | {valid_count} |\n"
            f"| Invalid/Restricted | {total - valid_count} |\n\n"
            f"**Validation Results:**\n\n"
            f"| ID | Document | Status | HTTP | Accessible | Permissions |\n|---|---|---|---|---|---|\n"
            f"{rows}\n"
            f"**Alerts:**\n"
            f"- DOC-006 (MSA Template) is restricted to Legal Team Only - request access if needed\n\n"
            f"Source: [SharePoint Link Validator]\nAgents: SharePointDocumentExtractorAgent"
        )


if __name__ == "__main__":
    agent = SharePointDocumentExtractorAgent()
    for op in ["document_search", "url_extraction", "metadata_enrichment", "link_validation"]:
        print("=" * 60)
        print(agent.perform(operation=op, search_query="product"))
        print()
