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
