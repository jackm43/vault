# Vault + 1Password Integration Architecture

This document describes how to integrate HashiCorp Vault with 1Password using Okta SSO and short-lived tokens for Buildkite.

## Overview
- Users authenticate to **1Password** and **Vault** using Okta SSO with phishing‑resistant MFA.
- The [1Password shell plugin](https://developer.1password.com/docs/cli/shell-plugins/hashicorp-vault/) provides secure `vault` CLI authentication.
- Vault rotates Buildkite tokens and stores them in a secret named after the user's Okta ID.
- Device certificates issued by the internal PKI authenticate laptops and DevBoxes to Vault.

## Components
1. **Okta OIDC** – central identity provider for Vault and 1Password.
2. **1Password CLI** – configured with the HashiCorp Vault shell plugin.
3. **Vault agent** – maintains renewed tokens for Buildkite.
4. **Ansible** – installs the plugin and configures the token helper on all machines.

## Flow
1. User unlocks 1Password (biometric or password).
2. `vault login` triggers the shell plugin which retrieves the user's Vault token from 1Password.
3. Vault verifies the token via Okta auth and the device certificate.
4. Vault issues a short‑lived Buildkite token which the agent stores in 1Password.
5. Buildkite CLI uses the token stored in 1Password; Vault continuously renews it via the agent.

## Security Notes
- Tokens never persist on disk; the plugin stores them in the user's 1Password vault.
- Device certificates provide additional assurance that commands originate from a trusted laptop or DevBox.
- The Vault policy restricts tokens to Buildkite usage only.
# 1Password and Hashicorp Vault Integration

This document describes the architecture for integrating the 1Password shell
plugin with Hashicorp Vault using Okta as the identity provider. The goal is to
maintain short‑lived tokens for Buildkite while avoiding local token storage.

------

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


