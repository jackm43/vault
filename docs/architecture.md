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

