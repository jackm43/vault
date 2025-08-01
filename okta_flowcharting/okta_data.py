from __future__ import annotations

import os
import json
import pickle
from dataclasses import dataclass, asdict, field
from typing import Any, Callable, Coroutine, Dict, List

from okta.client import Client as OktaClient


@dataclass
class Credentials:
    orgUrl: str
    token: str

    @staticmethod
    def from_file(service: str) -> "Credentials":
        filename = f"{service}.creds"
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Unable to open {service} credentials")
        with open(filename, "r") as fh:
            data = json.load(fh)
        return Credentials(**data)

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


@dataclass
class PolicyBundle:
    policy: Any
    rules: List[Any]


@dataclass
class OktaCache:
    client: OktaClient
    cache_dir: str = "."
    groups: Dict[str, Any] = field(default_factory=dict)
    networks: Dict[str, Any] = field(default_factory=dict)
    users: Dict[str, Any] = field(default_factory=dict)
    user_types: Dict[str, Any] = field(default_factory=dict)

    async def _load_cached(self, filename: str, loader: Callable[[], Coroutine[Any, Any, List[Any]]]) -> Dict[str, Any]:
        path = os.path.join(self.cache_dir, filename)
        if os.path.exists(path):
            items = pickle.load(open(path, "rb"))
        else:
            items = await loader()
            pickle.dump(items, open(path, "wb"))
        return {item.id: item for item in items}

    async def get_groups(self) -> Dict[str, Any]:
        if not self.groups:
            async def loader():
                return await fetch_groups(self.client)

            self.groups = await self._load_cached("okta_groups.pickle", loader)
        return self.groups

    async def get_networks(self) -> Dict[str, Any]:
        if not self.networks:
            async def loader():
                networks, _, _ = await self.client.list_network_zones()
                return networks

            self.networks = await self._load_cached("okta_networks.pickle", loader)
        return self.networks

    async def get_users(self) -> Dict[str, Any]:
        if not self.users:
            async def loader():
                users, _, _ = await self.client.list_users()
                return users

            self.users = await self._load_cached("okta_users.pickle", loader)
        return self.users

    async def get_user_types(self) -> Dict[str, Any]:
        if not self.user_types:
            async def loader():
                types, _, _ = await self.client.list_user_types()
                return types

            self.user_types = await self._load_cached("okta_user_types.pickle", loader)
        return self.user_types


async def fetch_groups(client: OktaClient) -> List[Any]:
    query_parameters = {"limit": 500}
    output_groups, resp, err = await client.list_groups(query_parameters)
    while resp.has_next():
        groups, err = await resp.next()
        output_groups += groups
    return output_groups


async def get_okta_policies(client: OktaClient, policy_type: str) -> Dict[str, PolicyBundle]:
    cache_file = f"okta_{policy_type.lower()}.pickle"
    if os.path.exists(cache_file):
        raw = pickle.load(open(cache_file, "rb"))
        return {
            pid: PolicyBundle(policy=entry["Policy"], rules=entry["Rules"]) for pid, entry in raw.items()
        }

    policies, _, _ = await client.list_policies({"type": policy_type})
    bundles: Dict[str, PolicyBundle] = {}
    for policy in policies:
        rules, _, _ = await client.list_policy_rules(policy.id)
        bundles[policy.id] = PolicyBundle(policy=policy, rules=rules)
    pickle.dump({pid: {"Policy": pb.policy, "Rules": pb.rules} for pid, pb in bundles.items()}, open(cache_file, "wb"))
    return bundles


def get_okta_client() -> OktaClient:
    creds = Credentials.from_file("okta")
    return OktaClient(creds.to_dict())
