"""Deterministic Backstage catalog data for Port demos.

Entity refs and service names align with other mock MCP vendors
(checkout-service, payment-gateway, auth-service, etc.).
"""

from __future__ import annotations

from typing import Any

MOCK_ENTITIES: dict[str, dict[str, Any]] = {
    "component:default/checkout-service": {
        "apiVersion": "backstage.io/v1alpha1",
        "kind": "Component",
        "metadata": {
            "name": "checkout-service",
            "namespace": "default",
            "title": "Checkout Service",
            "description": "Handles cart checkout and order placement",
            "labels": {"team": "checkout", "language": "nodejs", "tier": "critical"},
            "tags": ["checkout", "critical", "tier-1"],
            "annotations": {
                "github.com/project-slug": "port-labs/checkout-service",
                "backstage.io/source-location": "url:https://github.com/port-labs/checkout-service",
            },
        },
        "spec": {
            "type": "service",
            "lifecycle": "production",
            "owner": "group:default/checkout-team",
            "system": "system:default/commerce",
            "providesApis": ["api:default/checkout-api"],
            "dependsOn": [
                "resource:default/orders-db",
                "component:default/payment-gateway",
                "component:default/auth-service",
            ],
        },
    },
    "component:default/payment-gateway": {
        "apiVersion": "backstage.io/v1alpha1",
        "kind": "Component",
        "metadata": {
            "name": "payment-gateway",
            "namespace": "default",
            "title": "Payment Gateway",
            "description": "Payment processing gateway for order transactions",
            "labels": {"team": "payments", "language": "go", "tier": "critical"},
            "tags": ["payment", "critical", "pci"],
            "annotations": {
                "github.com/project-slug": "port-labs/payment-gateway",
            },
        },
        "spec": {
            "type": "service",
            "lifecycle": "production",
            "owner": "group:default/payments-team",
            "system": "system:default/commerce",
            "providesApis": ["api:default/payment-api"],
            "dependsOn": ["resource:default/orders-db"],
        },
    },
    "component:default/auth-service": {
        "apiVersion": "backstage.io/v1alpha1",
        "kind": "Component",
        "metadata": {
            "name": "auth-service",
            "namespace": "default",
            "title": "Auth Service",
            "description": "Authentication and authorization service",
            "labels": {"team": "platform", "language": "typescript", "tier": "critical"},
            "tags": ["auth", "security"],
        },
        "spec": {
            "type": "service",
            "lifecycle": "production",
            "owner": "group:default/platform-team",
            "system": "system:default/platform",
            "providesApis": ["api:default/auth-api"],
            "dependsOn": ["resource:default/redis-cache"],
        },
    },
    "component:default/api-server": {
        "apiVersion": "backstage.io/v1alpha1",
        "kind": "Component",
        "metadata": {
            "name": "api-server",
            "namespace": "default",
            "title": "API Server",
            "description": "Core API gateway and routing layer",
            "labels": {"team": "platform", "language": "go"},
            "tags": ["api", "gateway"],
        },
        "spec": {
            "type": "service",
            "lifecycle": "production",
            "owner": "group:default/platform-team",
            "system": "system:default/platform",
            "dependsOn": ["component:default/auth-service"],
        },
    },
    "api:default/checkout-api": {
        "apiVersion": "backstage.io/v1alpha1",
        "kind": "API",
        "metadata": {
            "name": "checkout-api",
            "namespace": "default",
            "description": "REST API for checkout operations",
        },
        "spec": {
            "type": "openapi",
            "lifecycle": "production",
            "owner": "group:default/checkout-team",
            "definition": '{"openapi":"3.0.0","info":{"title":"Checkout API","version":"1.0.0"}}',
        },
    },
    "api:default/payment-api": {
        "apiVersion": "backstage.io/v1alpha1",
        "kind": "API",
        "metadata": {
            "name": "payment-api",
            "namespace": "default",
            "description": "REST API for payment processing",
        },
        "spec": {
            "type": "openapi",
            "lifecycle": "production",
            "owner": "group:default/payments-team",
        },
    },
    "api:default/auth-api": {
        "apiVersion": "backstage.io/v1alpha1",
        "kind": "API",
        "metadata": {
            "name": "auth-api",
            "namespace": "default",
            "description": "Authentication and authorization API",
        },
        "spec": {
            "type": "openapi",
            "lifecycle": "production",
            "owner": "group:default/platform-team",
        },
    },
    "system:default/commerce": {
        "apiVersion": "backstage.io/v1alpha1",
        "kind": "System",
        "metadata": {
            "name": "commerce",
            "namespace": "default",
            "description": "Commerce and checkout domain",
            "labels": {"domain": "commerce"},
        },
        "spec": {"owner": "group:default/checkout-team"},
    },
    "system:default/platform": {
        "apiVersion": "backstage.io/v1alpha1",
        "kind": "System",
        "metadata": {
            "name": "platform",
            "namespace": "default",
            "description": "Platform and identity services",
            "labels": {"domain": "platform"},
        },
        "spec": {"owner": "group:default/platform-team"},
    },
    "resource:default/orders-db": {
        "apiVersion": "backstage.io/v1alpha1",
        "kind": "Resource",
        "metadata": {
            "name": "orders-db",
            "namespace": "default",
            "description": "PostgreSQL database for orders",
            "labels": {"type": "database", "env": "production"},
        },
        "spec": {"type": "database", "owner": "group:default/platform-team"},
    },
    "resource:default/redis-cache": {
        "apiVersion": "backstage.io/v1alpha1",
        "kind": "Resource",
        "metadata": {
            "name": "redis-cache",
            "namespace": "default",
            "description": "Redis cache cluster for sessions",
            "labels": {"type": "cache", "env": "production"},
        },
        "spec": {"type": "cache", "owner": "group:default/platform-team"},
    },
    "group:default/checkout-team": {
        "apiVersion": "backstage.io/v1alpha1",
        "kind": "Group",
        "metadata": {
            "name": "checkout-team",
            "namespace": "default",
            "description": "Checkout domain team",
        },
        "spec": {"type": "team", "children": []},
    },
    "group:default/payments-team": {
        "apiVersion": "backstage.io/v1alpha1",
        "kind": "Group",
        "metadata": {
            "name": "payments-team",
            "namespace": "default",
            "description": "Payments domain team",
        },
        "spec": {"type": "team", "children": []},
    },
    "group:default/platform-team": {
        "apiVersion": "backstage.io/v1alpha1",
        "kind": "Group",
        "metadata": {
            "name": "platform-team",
            "namespace": "default",
            "description": "Platform engineering team",
        },
        "spec": {"type": "team", "children": []},
    },
}

ENTITY_OVERLAYS: dict[str, dict[str, Any]] = {
    "component:default/checkout-service": {
        "entityRef": "component:default/checkout-service",
        "overlay": {
            "maturity": {"score": 82, "level": "gold"},
            "oncall": {"pagerduty": "checkout-oncall", "slack": "#checkout-alerts"},
            "compliance": {"pci": False, "soc2": True},
        },
    },
    "component:default/payment-gateway": {
        "entityRef": "component:default/payment-gateway",
        "overlay": {
            "maturity": {"score": 91, "level": "platinum"},
            "oncall": {"pagerduty": "payments-oncall", "slack": "#payments-alerts"},
            "compliance": {"pci": True, "soc2": True},
        },
    },
    "component:default/auth-service": {
        "entityRef": "component:default/auth-service",
        "overlay": {
            "maturity": {"score": 88, "level": "gold"},
            "oncall": {"pagerduty": "platform-oncall", "slack": "#platform-alerts"},
            "compliance": {"pci": False, "soc2": True},
        },
    },
}


def _normalize_ref(entity_ref: str) -> str:
    """Accept 'checkout-service' or 'component:default/checkout-service'."""
    if ":" in entity_ref:
        return entity_ref
    for ref in MOCK_ENTITIES:
        if ref.endswith(f"/{entity_ref}"):
            return ref
    return entity_ref


def _entity_matches_query(ref: str, entity: dict[str, Any], query: str) -> bool:
    query_lower = query.lower()
    metadata = entity.get("metadata", {})
    haystack = " ".join(
        [
            ref,
            metadata.get("name", ""),
            metadata.get("title", ""),
            metadata.get("description", ""),
            " ".join(metadata.get("tags", [])),
            str(metadata.get("labels", {})),
        ]
    ).lower()
    return query_lower in haystack


def search_entities(query: str, kind: str | None = None, limit: int = 10) -> list[dict[str, Any]]:
    results = []
    for ref, entity in MOCK_ENTITIES.items():
        if kind and ref.split(":")[0].lower() != kind.lower():
            continue
        if _entity_matches_query(ref, entity, query):
            results.append({"entityRef": ref, **entity})
    return results[:limit]


def get_entity(entity_ref: str) -> dict[str, Any] | None:
    ref = _normalize_ref(entity_ref)
    entity = MOCK_ENTITIES.get(ref)
    if not entity:
        return None
    return {"entityRef": ref, **entity}


def list_entities(kind: str, limit: int = 20) -> list[dict[str, Any]]:
    results = []
    for ref, entity in MOCK_ENTITIES.items():
        if ref.split(":")[0].lower() == kind.lower():
            results.append({"entityRef": ref, **entity})
    return results[:limit]


def get_entity_relations(entity_ref: str, relation_type: str | None = None) -> dict[str, Any]:
    ref = _normalize_ref(entity_ref)
    entity = MOCK_ENTITIES.get(ref)
    if not entity:
        return {"error": f"Entity not found: {entity_ref}"}

    spec = entity.get("spec", {})
    relations: dict[str, Any] = {}

    relation_map = {
        "dependsOn": spec.get("dependsOn", []),
        "providesApis": spec.get("providesApis", []),
        "consumesApis": spec.get("consumesApis", []),
        "ownedBy": spec.get("owner"),
        "system": spec.get("system"),
    }

    if relation_type:
        if relation_type in relation_map:
            relations[relation_type] = relation_map[relation_type]
        else:
            relations[relation_type] = []
    else:
        relations = {k: v for k, v in relation_map.items() if v}

    return {"entityRef": ref, "relations": relations}


def get_entity_overlay(entity_ref: str) -> dict[str, Any]:
    ref = _normalize_ref(entity_ref)
    overlay = ENTITY_OVERLAYS.get(ref)
    if overlay:
        return overlay
    return {
        "entityRef": ref,
        "overlay": {},
        "message": "No overlay metadata configured for this entity",
    }


def search(query: str, limit: int = 10) -> dict[str, Any]:
    """Broad catalog search (Backstage Portal 'search' tool)."""
    catalog_results = search_entities(query, limit=limit)
    return {
        "query": query,
        "results": [
            {
                "type": "catalog",
                "title": r.get("metadata", {}).get("title") or r.get("metadata", {}).get("name"),
                "entityRef": r.get("entityRef"),
                "snippet": r.get("metadata", {}).get("description", ""),
            }
            for r in catalog_results
        ],
        "total": len(catalog_results),
    }
