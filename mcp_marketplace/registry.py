from mcp.server.fastmcp import FastMCP

from . import hashicorpvault, okta, ssh, zendesk

CLIENT_MODULES = [
    hashicorpvault,
    okta,
    ssh,
    zendesk,
]

def register_all_tools(mcp: FastMCP) -> None:
    """Register tools from all included clients."""
    for module in CLIENT_MODULES:
        if hasattr(module, "register_tools"):
            module.register_tools(mcp)
