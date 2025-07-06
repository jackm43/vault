
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
=======
# Configuration Steps

This guide lists the configuration required in Okta, Vault and 1Password to
enable the integration.

## Okta

1. Configure a new OIDC application for Hashicorp Vault.
2. Grant access to users and enable phishing‑resistant MFA policies.
3. Expose the Okta user ID as a claim so Vault can determine the secret path.

## Hashicorp Vault

1. Enable the `oidc` auth method at `auth/okta`.
2. Configure allowed client IDs and groups from Okta.
3. Map the Okta user ID claim to policies that permit access to
   `secret/data/buildkite/<user_id>`.
4. Configure `vault agent` with auto-auth to handle token rotation for Buildkite.

## 1Password

1. Enable SSO with Okta and enforce MFA.
2. Install the 1Password CLI and initialize the Vault shell plugin:
   ```bash
   op plugin init hashicorp-vault --vault-url https://vault.example.com
   ```
3. Login to 1Password using `op signin` which redirects to Okta for
   authentication.


