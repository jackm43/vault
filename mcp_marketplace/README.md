# MCP Marketplace Clients

Clients copied from [google/mcp-security](https://github.com/google/mcp-security)
limited to the following integrations:

- `hashicorpvault`
- `okta`
- `ssh`
- `zendesk`

Use `registry.register_all_tools(mcp)` to expose all tools from these clients.
Secrets are referenced via environment variables defined in `.env` and stored in
1Password.
