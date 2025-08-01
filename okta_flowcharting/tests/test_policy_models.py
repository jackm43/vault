import unittest
from okta_flowcharting.policy_models import (
    PolicyConditionModel,
    PolicyRuleModel,
    AssuranceRequirement,
    AssuranceLevel,
    AuthenticationPolicyModel,
    UserContext,
)


class PolicyModelTests(unittest.TestCase):
    def test_condition_default(self):
        cond = PolicyConditionModel("group", "in", ["admins"])
        self.assertTrue(cond.test(None))

    def test_rule_compliance(self):
        rule = PolicyRuleModel(id="1", name="r1")
        req = AssuranceRequirement(name="anything", tests=[lambda r: True])
        self.assertTrue(rule.is_compliant(req))


class AuthenticationPolicyTests(unittest.TestCase):
    def test_evaluate_policy(self):
        def is_admin(context):
            return "admins" in context.groups

        cond = PolicyConditionModel("group", "include", ["admins"])
        cond.test = is_admin
        rule = PolicyRuleModel(
            id="1",
            name="Admins",
            conditions=[cond],
            action="ALLOW",
            steps=["enter password", "verify factor"],
        )
        policy = AuthenticationPolicyModel(name="Test", rules=[rule])
        ctx = UserContext(username="alice", groups=["admins"])
        steps = policy.evaluate(ctx)
        self.assertEqual(steps, ["enter password", "verify factor", "ALLOW"])


if __name__ == "__main__":
    unittest.main()
