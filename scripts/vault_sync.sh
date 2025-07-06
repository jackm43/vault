#!/usr/bin/env bash
# Synchronise Buildkite token from Hashicorp Vault into 1Password.
# This script expects the 1Password shell plugin for Vault to be initialized.

set -euo pipefail

if [ -z "${OKTA_USER_ID:-}" ]; then
  echo "ERROR: OKTA_USER_ID environment variable must be set" >&2
  exit 1
fi

VAULT_PATH="secret/data/buildkite/$OKTA_USER_ID"

# Fetch token from Vault using the shell plugin
BK_TOKEN=$(op plugin run hashicorp-vault read -field=data "$VAULT_PATH" | jq -r '.data.token')

# Update 1Password item named after the Okta user ID
op item create --category=credential --title="buildkite-$OKTA_USER_ID" BK_TOKEN="$BK_TOKEN" >/dev/null

echo "Buildkite token synced for $OKTA_USER_ID"

