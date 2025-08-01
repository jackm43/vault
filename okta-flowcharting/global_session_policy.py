from collections import defaultdict
import asyncio
from typing import Dict

import schemdraw
from schemdraw import flow
from okta.client import Client as OktaClient

from okta_data import (
    Credentials,
    OktaCache,
    PolicyBundle,
    get_okta_client,
    get_okta_policies,
)


async def get_okta_groups_coroutine(cache: OktaCache):
    return await cache.get_groups()


async def get_okta_networks_coroutine(cache: OktaCache):
    return await cache.get_networks()


def get_okta_handler() -> OktaClient:
    return get_okta_client()

def label_format(label):
    out = ""
    start = 0
    for i in range(0, len(label), 25):
        out += label[start:i] + "-\n"
        start = i
    out += label[start:len(label)]
    return out

async def extract_rule_conditions(policy_rule, cache: OktaCache, skip_defaults=False):
    networks = await get_okta_networks_coroutine(cache)
    conditions = []
    # IP Restrictions
    if policy_rule.conditions.network.exclude:
        network_zones = policy_rule.conditions.network.exclude
        if network_zones == ["ALL_ZONES"]:
            policy_rule_condition = flow.Decision(w=5.5, h=4, N='', E='YES', S='NO').label(label_format(f"Is user NOT in Any Zone"))
        else:
            network_names = [networks[network_id].name for network_id in network_zones]
            policy_rule_condition = flow.Decision(w=5.5, h=4, N='', E='YES', S='NO').label(label_format(f"Is user NOT in Network Range {' or '.join(network_names)}"))
        conditions.append(policy_rule_condition)
    if policy_rule.conditions.network.include:
        network_zones = policy_rule.conditions.network.include
        if network_zones == ["ALL_ZONES"]:
            policy_rule_condition = flow.Decision(w=5.5, h=4, N='', E='YES', S='NO').label(label_format(f"Is user in Any Zone"))
        else:
            network_names = [networks[network_id].name for network_id in network_zones]
            policy_rule_condition = flow.Decision(w=5.5, h=4, N='', E='YES', S='NO').label(label_format(f"Is user in Network Range {' or '.join(network_names)}"))
        conditions.append(policy_rule_condition)
    # Identity Provider
    if policy_rule.conditions.identity_provider:
        identity_provider = policy_rule.conditions.identity_provider.provider
        policy_rule_condition = flow.Decision(w=5.5, h=4, N='', E='YES', S='NO').label(label_format(f"Identity Provider is {identity_provider}"))
        if identity_provider == "ANY" and skip_defaults:
            pass
        else:
            conditions.append(policy_rule_condition)
    # Authenticates via
    if policy_rule.conditions.auth_context:
        auth_type = policy_rule.conditions.auth_context.auth_type
        policy_rule_condition = flow.Decision(w=5.5, h=4, N='', E='YES', S='NO').label(label_format(f"Is authentication performed via {auth_type}"))
        if auth_type == "ANY" and skip_defaults:
            pass
        else:
            conditions.append(policy_rule_condition)
    # Behavior
    # Behavior can be None on default policies.
    if policy_rule.conditions.risk and policy_rule.conditions.risk.behaviors:
        # There is No API to list Behaviors, this is also not a documented condition type
        # https://developer.okta.com/docs/reference/api/policy/#device-condition-object
        behaviors = policy_rule.conditions.risk.behaviors
        policy_rule_condition = flow.Decision(w=5.5, h=4, N='', E='YES', S='NO').label(label_format(f"Is behavior {', '.join(behaviors)}"))
        conditions.append(policy_rule_condition)
    # Risk
    if policy_rule.conditions.risk_score and policy_rule.conditions.risk_score.level:
        risk_level = policy_rule.conditions.risk_score.level
        policy_rule_condition = flow.Decision(w=5.5, h=4, N='', E='YES', S='NO').label(label_format(f"Is Risk Score {risk_level}"))
        if risk_level == "ANY" and skip_defaults:
            pass
        else:
            conditions.append(policy_rule_condition)
    return conditions

async def extract_policy_condition(policy, cache: OktaCache):
    groups = await get_okta_groups_coroutine(cache)
    group_access = policy.conditions.people.groups.include
    group_names = [groups[group_id].profile.name for group_id in group_access]
    if len(group_names) == 1 and group_names == ["Everyone"]:
        policy_condition = flow.Decision(w=5.5, h=4, E='YES', S='NO').label("Is the user enrolled in Okta?")
    else:
        policy_condition = flow.Decision(w=5.5, h=4, E='YES', S='NO').label(label_format(f"Is user in group {' or '.join(group_names)}?"))
    return policy_condition

async def make_policies(d, global_session_policies, cache: OktaCache):
    default_skip = True
    policy_conditions = {}
    rule_conditions = defaultdict(lambda: [])
    # Generate Policy Nodes
    for policy_id, policy_struct in global_session_policies.items():
        policy_condition = await extract_policy_condition(policy_struct['Policy'], cache)
        # We actually need to specify the length for the policy BEFORE because
        # this is the distance to the current policy
        all_policies = list(global_session_policies.keys())
        previous_policy_index = all_policies.index(policy_id)-1
        if previous_policy_index == -1:
            number_of_units = d.unit
        else:
            previous_policy_id = all_policies[previous_policy_index]
            previous_policy = global_session_policies[previous_policy_id]
            # Each line is d.unit/2 length and there will be n -1 of them
            line_length = d.unit/2 * (len(previous_policy['Rules']) -1)
            # each decision is 4 and there N of them
            object_length = 4 * len(previous_policy['Rules'])
            number_of_units = (line_length + object_length)
        d.add(flow.Arrow().down(number_of_units))
        policy_conditions[policy_id] = d.add(policy_condition)
    # Generate First Rule Nodes
    for policy_id, policy_struct in global_session_policies.items():
        print(policy_struct['Policy'].name)
        policy_object = policy_conditions[policy_id]
        # If we're at the end of a rule, we'll next to direct to the next policy
        all_policies = list(global_session_policies.keys())
        next_policy_index = all_policies.index(policy_id)+1
        if next_policy_index < len(global_session_policies):
            next_policy_id = list(global_session_policies)[next_policy_index]
            next_policy_object = policy_conditions[next_policy_id]
        else:
            next_policy_id = None
            next_policy_object = None
        for row_depth, policy_rule in enumerate(policy_struct['Rules']):
            # If this is the first row, move out from the policy object
            if row_depth == 0:
                d.add(flow.Arrow().right(d.unit/2).at(policy_object.E))
            # If its not the first row, make a down arrow to the previous row
            else:
                d.add(flow.Arrow().down(d.unit/2).at(first_row_condition.S))
            conditions = await extract_rule_conditions(policy_rule, cache, skip_defaults=default_skip)
            # This will only happen if everything is default, which is really ANY user
            if not conditions:
                first_row_condition = d.add(flow.Decision(w=5.5, h=4, E='YES', S='NO').label("Is the user valid in Okta?"))
            else:
                # At the end there is a Default Allow, we make it more readable
                if policy_rule.system == True:
                    first_row_condition = d.add(flow.Decision(w=5.5, h=4, E='YES', S='NO').label("Is the user valid in Okta?"))
                else:
                    first_row_condition = d.add(conditions[0])

            rule_conditions[policy_rule.id] = [first_row_condition]
            print(f"\t{policy_rule.id} - {policy_rule.name}")
        # Make all the rest of the rules
        for row_depth, policy_rule in enumerate(policy_struct['Rules']):
            # There is another rule and failures go to it
            if row_depth+1 < len(policy_struct['Rules']):
                next_row_policy_id = policy_struct['Rules'][row_depth+1].id
                next_row_object = rule_conditions[next_row_policy_id]
            # There isn't another rule so failures go to next policy
            else:
                policy_conditions[policy_id]
                next_row_object = None
            most_recent_rule = rule_conditions[policy_rule.id][0]
            conditions = await extract_rule_conditions(policy_rule, cache, skip_defaults=default_skip)

            # If there are no conditions (all conditions are default) then draw a line from our 'default' box
            if not conditions:
                # Push each rule option to the next policy
                if not next_row_object and next_policy_object:
                    first_rule_object = rule_conditions[policy_rule.id][0]
                    d.add(flow.Wire('-', arrow='->').at(first_rule_object.S).to(next_policy_object.N))
            else:
                for condition_index, condition in enumerate(conditions):
                    # We have already created these first indexes so we skip
                    # but we still wanna create the line
                    if condition_index != 0:
                        d.add(flow.Arrow().right(d.unit/2).at(most_recent_rule.E))
                        most_recent_rule = d.add(condition)
                    # If there is another rule, we need to set failure conditions to go to it
                    if next_row_object:
                        d.add(flow.Wire('-', arrow='->').at(most_recent_rule.S).to(next_row_object[0].N))
                    # If there is not another rule, then we need to set failure conditions to go to the next policy
                    else:
                        if next_policy_object:
                            # push the first rule to the next policy, we'll end up redrawing this a few times
                            first_rule_object = rule_conditions[policy_rule.id][0]
                            d.add(flow.Wire('-', arrow='->').at(first_rule_object.S).to(next_policy_object.N))
                            # Push each rule option to the next policy
                            d.add(flow.Wire('-', arrow='->').at(most_recent_rule.S).to(next_policy_object.N))
            # Add ending condition
            d.add(flow.Arrow().right(d.unit/2).at(most_recent_rule.E))
            if policy_rule.actions.signon.access == "ALLOW":
                d.add(flow.Box(w=3.5, h=4).label('Access is Allowed.'))
            else:
                d.add(flow.Box(w=3.5, h=4).label('Access is denied.'))
    all_policies = list(global_session_policies.keys())
    last_policy = policy_conditions[all_policies[-1]]
    d.add(flow.Arrow().down(d.unit/2).at(last_policy.S))
    d.add(flow.Box(w=3.5, h=4).label('Access is denied.'))

def main():
    okta_client = get_okta_handler()
    cache = OktaCache(okta_client)
    global_session_policies = asyncio.run(get_okta_policies(okta_client, "OKTA_SIGN_ON"))
    d = schemdraw.Drawing()
    start = flow.Start().label('Start Login')
    d.add(start)
    asyncio.run(make_policies(d, global_session_policies, cache))
    d.save('out.svg')

if __name__ == "__main__":
    main()
