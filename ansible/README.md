# Ansible Setup

This directory contains an example playbook and role for configuring the
1Password shell plugin for Hashicorp Vault.

Run the playbook with:

```bash
ansible-playbook -i inventory ansible/site.yml
```

The role installs the required CLI tools and copies the `vault_sync.sh` script
that synchronizes Buildkite tokens from Vault into 1Password.
