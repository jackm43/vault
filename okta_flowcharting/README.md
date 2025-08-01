# okta-flowcharting
A set of scripts designed to generate flowcharts to visually show Okta OIE Global Session Policies and Authentication Policies

# FAQ

Q: Why are you pickling results.

A: This is mostly a proof of concept and on large Okta tenants downloading this data can take a long time. As a reminder pickle is unsafe when accepting pickle files from untrusted sources (see https://davidhamann.de/2020/04/05/exploiting-python-pickle/)


Q: Why are you reading creds in from a file

A: Again, quick and dirty -- it didn't help that the Okta Python SDK was broken


Q: What is the cred file format?

A: A file named okta.creds with the following content.
```
{
    "orgUrl": "https://mydomain.okta.com",
    "token": "API key"
}
```


## Data Model

The updated scripts use dataclasses to model Okta resources and cached policy information. `okta_data.py` defines:

- `Credentials` – loads API credentials from `okta.creds`.
- `PolicyBundle` – pairs an Okta policy with its rules.
- `OktaCache` – lazily fetches and stores groups, networks, users, and user types to reduce API calls.

These abstractions are shared between the policy scripts to keep the logic consistent.

### Assurance Models

`policy_models.py` introduces generic dataclasses that describe policy rules and assurance requirements. They can be used to validate Okta policies or to model new ones before deployment.

- `PolicyConditionModel` – represents a single condition such as a device or zone restriction and exposes a `test` method.
- `PolicyRuleModel` – groups conditions, a resulting action, and the user interaction `steps` into a rule object.
- `AuthenticationPolicyModel` – collection of rules that can be evaluated for a given user context.
- `UserContext` – minimal user information (username and groups) used when evaluating sample policies.
- `AssuranceRequirement` – a collection of callable tests that must succeed for a rule.
- `AssuranceLevel` – links a descriptive name with its assurance requirements.

These abstractions let you develop testable policy designs and integrate assurance levels directly into the flowcharting tools or standalone unit tests.
