import unittest
from okta_flowcharting.policy_models import (
    PolicyConditionModel,
    PolicyRuleModel,
    AuthenticationPolicyModel,
    UserContext,
)


def group_cond(groups):
    cond = PolicyConditionModel("group", "include", groups)
    cond.test = lambda ctx: any(g in ctx.groups for g in groups)
    return cond


class JourneyIntegrationTest(unittest.TestCase):
    def setUp(self):
        deny_rule = PolicyRuleModel(
            id="1",
            name="DenyGuests",
            conditions=[group_cond(["guests"])],
            action="DENY",
            steps=["access denied"],
        )
        mfa_rule = PolicyRuleModel(
            id="2",
            name="Admins",
            conditions=[group_cond(["admins"])],
            action="ALLOW",
            steps=["enter password", "verify factor"],
        )
        allow_rule = PolicyRuleModel(
            id="3",
            name="Employees",
            conditions=[group_cond(["employees"])],
            action="ALLOW",
            steps=["enter password"],
        )
        self.policy = AuthenticationPolicyModel(
            name="Example", rules=[deny_rule, mfa_rule, allow_rule], default_action="DENY"
        )

    def test_guest_denied(self):
        ctx = UserContext(username="bob", groups=["guests"])
        steps = self.policy.evaluate(ctx)
        self.assertEqual(steps, ["access denied", "DENY"])

    def test_admin_mfa(self):
        ctx = UserContext(username="alice", groups=["admins"])
        steps = self.policy.evaluate(ctx)
        self.assertEqual(steps, ["enter password", "verify factor", "ALLOW"])

    def test_employee_password(self):
        ctx = UserContext(username="carol", groups=["employees"])
        steps = self.policy.evaluate(ctx)
        self.assertEqual(steps, ["enter password", "ALLOW"])

    def test_unknown_default_deny(self):
        ctx = UserContext(username="eve", groups=["unknown"])
        steps = self.policy.evaluate(ctx)
        self.assertEqual(steps, ["DENY"])


if __name__ == "__main__":
    unittest.main()
