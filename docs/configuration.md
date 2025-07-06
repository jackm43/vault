# Configuration Requirements

## Okta
- Enable the Okta OIDC application for Vault and 1Password.
- Device Trust: require valid device certificates from the PKI for login.
- Assign users to the application with MFA enforced.

## Vault
- Enable the [Okta auth method](https://developer.hashicorp.com/vault/docs/auth/okta).
- Configure a role for Buildkite with short-lived tokens (e.g., TTL 15m, max TTL 1h).
- Configure `vault agent` with [generate-config](https://developer.hashicorp.com/vault/docs/commands/agent/generate-config) to renew tokens and place them in the 1Password item.

## 1Password CLI
- Install the shell plugin for Vault and create an item named after the user's Okta ID.
- Use biometric unlock where supported.

## Coder
- Integrate Vault following [Coder's Vault guide](https://coder.com/docs/admin/integrations/vault).
- Use short-lived session tokens as described in [Coder docs](https://coder.com/docs/admin/users/sessions-tokens#short-lived-tokens-sessions).

