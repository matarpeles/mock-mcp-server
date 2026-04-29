# Mock MCP Server for Port Demos

A mock MCP server that simulates Datadog, GitHub, NewRelic, AWS, Notion, FluxCD, and ServiceNow tools for Port's Agentic Engineering Platform demos.

## Endpoints

| Vendor | URL Path | Description |
|--------|----------|-------------|
| Datadog | `/datadog/mcp` | Logs, metrics, APM, monitors |
| GitHub | `/github/mcp` | PRs, commits, code search, workflows |
| NewRelic | `/newrelic/mcp` | Entities, NRQL, error groups, alerts |
| AWS | `/aws/mcp` | CloudWatch, CloudTrail, EC2, Lambda |
| Notion | `/notion/mcp` | Pages, databases, search |
| FluxCD | `/fluxcd/mcp` | Flux resources, K8s logs, reconciliation |
| ServiceNow | `/servicenow/mcp` | Incidents, changes, CMDB, catalog, approvals |

## FluxCD Tools

The FluxCD mock mirrors the real [Flux Operator MCP Server](https://fluxcd.control-plane.io/mcp/tools):

| Tool | Description |
|------|-------------|
| `get_flux_instance` | Flux installation status, version, components |
| `get_kubernetes_resources` | HelmRelease, Kustomization, GitRepository status |
| `get_kubernetes_logs` | Pod container logs with timestamps |
| `get_kubernetes_metrics` | CPU/Memory usage for pods |
| `reconcile_flux_helmrelease` | Trigger HelmRelease reconciliation |
| `reconcile_flux_kustomization` | Trigger Kustomization reconciliation |
| `reconcile_flux_source` | Trigger source reconciliation |
| `suspend_flux_reconciliation` | Suspend Flux resource |
| `resume_flux_reconciliation` | Resume Flux resource |
| `search_flux_docs` | Search Flux documentation |

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key
export ANTHROPIC_API_KEY=your_key_here

# Run server
python -m uvicorn src.main:create_app --factory --host 0.0.0.0 --port 8000
```

## Deploy to Render

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo
4. Add environment variable: `ANTHROPIC_API_KEY`
5. Deploy

Your MCP URLs will be:
- `https://your-app.onrender.com/datadog/mcp`
- `https://your-app.onrender.com/github/mcp`
- `https://your-app.onrender.com/newrelic/mcp`
- `https://your-app.onrender.com/aws/mcp`
- `https://your-app.onrender.com/notion/mcp`
- `https://your-app.onrender.com/fluxcd/mcp`
- `https://your-app.onrender.com/servicenow/mcp`

## ServiceNow Tools

The ServiceNow mock provides ITSM/ITOM tools based on common community implementations:

| Tool | Description |
|------|-------------|
| `search_incidents` | Search incidents with filters (state, priority, assigned_to) |
| `get_incident` | Get incident details by number (INC0001234) |
| `create_incident` | Create new incident |
| `update_incident` | Update incident, add work notes/comments |
| `resolve_incident` | Resolve incident with resolution code |
| `search_change_requests` | Search change requests |
| `get_change_request` | Get change request details (CHG0001234) |
| `create_change_request` | Create normal/standard/emergency change |
| `search_cmdb_ci` | Search CMDB configuration items |
| `get_cmdb_ci` | Get CI details |
| `get_ci_relationships` | Get CI upstream/downstream dependencies |
| `search_knowledge_base` | Search KB articles |
| `get_catalog_items` | List service catalog items |
| `order_catalog_item` | Submit catalog request |
| `get_user` | Get user by ID, email, or username |
| `search_problems` | Search problem records |
| `get_my_approvals` | Get pending approvals |
| `approve_request` | Approve a request |
| `reject_request` | Reject a request |

## Connect to Port

1. Go to Port → Settings → MCP Connectors
2. Add connector with URL: `https://your-app.onrender.com/fluxcd`
3. Repeat for other vendors
