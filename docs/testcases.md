# Test Cases

These tests can run locally without external systems.

1. **Token helper presence**
   - Verify that the `VAULT_TOKEN_HELPER` environment variable is set to `op-vault`.
2. **1Password CLI available**
   - Run `op --version` and confirm the command returns a version string.
3. **Ansible role execution**
   - Use `ansible-playbook --check playbook.yml` to perform a dry-run and confirm tasks complete.

