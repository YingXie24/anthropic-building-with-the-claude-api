# Official Python SDK to buil MCP servers. The SDK writes JSON schemas for tools for us.
from mcp.server.fastmcp import FastMCP
from pydantic import Field

#  Initialise MCP server
mcp = FastMCP("DocumentMCP", log_level="ERROR")

# Key: document ID, Value: document content
docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}

# TOOLS
# Write a tool to read a doc
# The @mcp.tool decorator generates the JSON schema that Claude needs
@mcp.tool(
    name="read_doc_contents",
    description="Read the contents of a document and return it as a string."
)
def read_document(
    # The Field class from Pydantic provides parameter descriptions that help Claude understand what each argument expects.
    doc_id: str = Field(description="Id of the document to read.")
):
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    
    return docs[doc_id]

# Write a tool to edit a doc
@mcp.tool(
    name='edit_document',
    description='Edit a document by replacing a string in the documents content with a new string'
)
def edit_document(
    doc_id: str = Field(description='Id of the document that will be edited'),
    old_str: str = Field(description='The text to replace. Must match exactly, including whitespaces'),
    new_str: str = Field(description='The new text to insert in place of the old text')
):
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")

    docs[doc_id] = docs[doc_id].replace(old_str, new_str)

# RESOURCES (Resources fetch data, tools perform actions)
# Write a DIRECT resource to return all doc id's. URIs in direct resources do not contain any params.
@mcp.resource(
    "docs://documents",
    mime_type="application/json" #MIME type helps cliensts understand response format
)
def list_docs() -> list[str]:
    return list(docs.keys()) #The MCP Python SDK automatically serialises the return values. There is no need to manually convert to JSON strings

# Write a TEMPLATED resource to return the contents of a particular doc. URIs in templated resources contain one or more params,
@mcp.resource(
    "docs://documents/{doc_id}",
    mime_type="text/plain"
)
def fetch_doc(doc_id: str) -> str:
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    return docs[doc_id]

# TODO: Write a prompt to rewrite a doc in markdown format
# TODO: Write a prompt to summarize a doc

# To test that the server works as expected, run in terminal `mcp dev mcp_server.py`

if __name__ == "__main__":
    mcp.run(transport="stdio")
