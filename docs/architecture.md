# 1Password and Hashicorp Vault Integration

This document describes the architecture for integrating the 1Password shell
plugin with Hashicorp Vault using Okta as the identity provider. The goal is to
maintain short‑lived tokens for Buildkite while avoiding local token storage.

## Overview

1. **Authentication**
   - Users authenticate to 1Password via Okta SSO. MFA is enforced by Okta.
   - Hashicorp Vault is configured with Okta OIDC auth and TLS client
     certificates issued by the internal PKI.
   - Device certificates are installed on macOS laptops via Kandji and on Linux
     DevBoxes at provisioning time.

2. **1Password Shell Plugin**
   - The 1Password shell plugin for Hashicorp Vault is initialized with the
     command:
     ```bash
     op plugin init hashicorp-vault
     ```
   - During initialization the plugin stores the Vault address and required
     TLS parameters so that it can log in on demand.
   - The plugin authenticates using the user’s Okta account and the device
     certificate, retrieving a short-lived Vault token.

3. **Vault Item Naming**
   - Buildkite tokens are stored in Vault at a path derived from the user’s
     Okta user ID, for example:
     `secret/data/buildkite/<okta_user_id>`.
   - The plugin syncs this Vault item into a 1Password item with the same name
     so that it can be used by the Buildkite CLI.

4. **Token Rotation**
   - Vault rotates Buildkite tokens periodically using the `vault agent` with an
     auto-auth block. Users never store the token locally.
   - When a token is rotated, the plugin syncs the new value into 1Password.

5. **Usage with Buildkite**
   - Users run the Buildkite CLI through `op run` to inject the token
     automatically:
     ```bash
     op run --env BK_TOKEN -- buildkite-agent pipeline upload
     ```
   - The environment variable `BK_TOKEN` is populated from the 1Password item.

6. **Coder DevBoxes**
   - DevBoxes use the same configuration and rely on the device certificate for
     mutual TLS. Coder sessions are short lived and use the Vault token helper
     configured by the plugin.

## Security Considerations

- All tokens are short lived and retrieved on demand.
- Device certificates ensure that only registered machines can access Vault.
- Users authenticate via Okta with MFA for both 1Password and Vault.

