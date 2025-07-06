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

