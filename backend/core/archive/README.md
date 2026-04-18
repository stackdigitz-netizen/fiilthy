# Archived Backend Stacks

These route stacks are intentionally archived because they are not part of the live production surface.

Canonical production stacks:
- Campaigns: `core/routes_product_launch.py` via `/api/products/{product_id}/launch-campaign`
- Branding: `core/routes_product_launch.py` via `/api/products/{product_id}/branding`
- Gumroad publishing: `core/routes_product_launch.py` via `/api/products/{product_id}/publish` with an explicit manual Gumroad dashboard handoff
- Autonomous execution: `core/routes_agents.py` plus `server.py` `/api/autonomous/*` and `/api/v5/*`

Archived here:
- `routes_v4_production.py`
- `routes_campaigns.py`
- `routes_branding.py`

Deleted outright because they were superseded duplicates with stale dependencies:
- `routes_v2.py`
- `routes_v3.py`
- `autonomous_engine_v2.py`