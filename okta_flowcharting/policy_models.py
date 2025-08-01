from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Any


@dataclass
class PolicyConditionModel:
    """Represents a single condition inside an authentication rule."""

    condition_type: str
    operator: str
    values: List[str]

    def test(self, rule: Any) -> bool:
        """Evaluate this condition against an Okta rule.

        The default implementation simply returns True. Custom logic can be
        injected to check real Okta rule objects when available.
        """
        return True


@dataclass
class PolicyRuleModel:
    """High level representation of an Okta policy rule."""

    id: str
    name: str
    conditions: List[PolicyConditionModel] = field(default_factory=list)
    action: str = ""
    steps: List[str] = field(default_factory=list)

    def is_compliant(self, requirement: "AssuranceRequirement") -> bool:
        """Check if this rule satisfies an assurance requirement."""
        return all(test(self) for test in requirement.tests)


@dataclass
class AssuranceRequirement:
    """Collection of checks that define an assurance level."""

    name: str
    tests: List[Callable[[PolicyRuleModel], bool]] = field(default_factory=list)
    description: str = ""


@dataclass
class AssuranceLevel:
    """Link a name with a set of assurance requirements."""

    name: str
    requirement: AssuranceRequirement


@dataclass
class AuthenticationPolicyModel:
    """Collection of rules representing a complete policy."""

    name: str
    rules: List[PolicyRuleModel] = field(default_factory=list)
    default_action: str = "DENY"

    def evaluate(self, context: Any) -> List[str]:
        """Evaluate the policy and return the user's journey steps."""
        for rule in self.rules:
            if all(cond.test(context) for cond in rule.conditions):
                return rule.steps + [rule.action]
        return [self.default_action]


@dataclass
class UserContext:
    """Simple user representation for testing policy flows."""

    username: str
    groups: List[str] = field(default_factory=list)
