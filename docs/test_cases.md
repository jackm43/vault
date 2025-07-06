# Test Cases

These test cases can be executed in an isolated environment without access to
production services.

## 1. Verify Scripts

```bash
shellcheck scripts/vault_sync.sh
```

## 2. Run Ansible Lint

```bash
ansible-lint ansible/roles
```

## 3. Simulated Vault Server

Start a development Vault server and verify that `vault_sync.sh` retrieves a
secret.

```bash
vault server -dev -dev-root-token-id=root &
export VAULT_ADDR=http://127.0.0.1:8200
export VAULT_TOKEN=root
export OKTA_USER_ID=test-user
vault kv put secret/buildkite/test-user token=dummy
./scripts/vault_sync.sh
```

The script should create a 1Password item locally (requires mock `op`). In this
isolated test you can set `op` to a wrapper script that echoes the arguments.

