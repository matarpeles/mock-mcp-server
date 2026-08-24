# Mock MCP Server for Port Demos

A mock MCP server that simulates Datadog, GitHub, NewRelic, AWS, Notion, FluxCD, ServiceNow, Confluence, and Backstage tools for Port's Agentic Engineering Platform demos.

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
| Confluence | `/confluence/mcp` | Pages, spaces, CQL search, Rovo search/fetch |
| Backstage | `/backstage/mcp` | Catalog entities, relations, overlays, search |
| Figma | `/figma/mcp` | Design context, metadata, screenshots, variables, comments |

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

## Figma Tools

The Figma mock mirrors the real [Figma Dev Mode MCP Server](https://developers.figma.com/docs/figma-mcp-server/tools-and-prompts/) (`https://mcp.figma.com/mcp`). Links are parsed for `fileKey`/`nodeId` the same way the real server does (`https://www.figma.com/design/:fileKey/:fileName?node-id=:nodeId`).

| Tool | Description |
|------|-------------|
| `get_metadata` | Sparse XML outline of a selection's layer hierarchy |
| `get_design_context` | Structured design-to-code context (React + Tailwind) for a node, aka `get_code` |
| `get_screenshot` | Visual reference image of a selection |
| `get_variable_defs` | Design tokens (color, spacing, typography) used in a selection |
| `get_figma_comments` | Review comments and open questions on a file (Port extension, not part of the real Dev Mode toolset) |

### Port workflow pattern

Use Figma as the **design context source** for engineering plan generation:

1. Register Figma MCP at `https://your-app.onrender.com/figma`
2. In a Port AI agent or workflow, call `get_metadata` then `get_design_context`/`get_variable_defs` on the design's `figma_link` to pull layout, tokens, and any unresolved `get_figma_comments` into the engineering plan's technical approach and risks sections

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
- `https://your-app.onrender.com/confluence/mcp`
- `https://your-app.onrender.com/backstage/mcp`
- `https://your-app.onrender.com/figma/mcp`

## Backstage Tools

The Backstage mock mirrors [Backstage Portal MCP tools](https://backstage.spotify.com/docs/portal/core-features-and-plugins/mcp/available-tools). Catalog lookups return deterministic data aligned with other demo vendors (`checkout-service`, `payment-gateway`, etc.).

| Tool | Description |
|------|-------------|
| `get_entity` | Get a catalog entity by reference |
| `get_catalog_entity` | Same as `get_entity` (Portal MCP naming) |
| `list_entities` | List entities by kind (Component, API, System, Resource, Group) |
| `search_entities` | Search catalog by keyword and optional kind filter |
| `search` | Broad catalog search (Portal MCP) |
| `get_entity_relations` | Get dependsOn, providesApis, owner, system relations |
| `get_entity_overlay` | Get overlay metadata (maturity, on-call, compliance) |
| `query_semantic_search_engine` | Semantic search across catalog and docs (LLM) |

### Port workflow pattern

Use Backstage as the **catalog source of truth** and Port as the **workflow engine**:

1. Register Backstage MCP at `https://your-app.onrender.com/backstage`
2. In a Port AI agent or workflow, call `get_catalog_entity` or `search_entities` to resolve service metadata, owners, and dependencies
3. Use Port workflows (`trigger_workflow_run`) to orchestrate actions (incident response, scaffolding, approvals) based on Backstage catalog data

This decouples the Port IDP catalog from the agentic engineering platform — Backstage owns entity metadata; Port owns workflow execution.

## Confluence Tools

The Confluence mock mirrors the official [Atlassian Rovo MCP Server](https://www.atlassian.com/platform/remote-mcp-server) read-only Confluence tools:

| Tool | Description |
|------|-------------|
| `getConfluencePage` | Get a page or live doc by ID with storage-format body |
| `getConfluencePageDescendants` | List descendant pages under a parent |
| `getConfluencePageFooterComments` | List footer comments on a page |
| `getConfluencePageInlineComments` | List inline comments on a page |
| `getConfluenceCommentChildren` | List reply comments for a parent comment |
| `getConfluenceSpaces` | List Confluence spaces |
| `getPagesInConfluenceSpace` | List pages in a space |
| `searchConfluenceUsingCql` | Search content using CQL |
| `searchAtlassian` | Natural-language search across Jira and Confluence (Rovo) |
| `fetchAtlassian` | Fetch content by Atlassian Resource Identifier (ARI) |
| `atlassianUserInfo` | Get current Atlassian user details |
| `getAccessibleAtlassianResources` | List accessible Atlassian cloud sites |

Demo content uses Port-style service names (`checkout-service`, `payment-gateway`) across spaces `ENGINEERING`, `PLATFORM`, and `RUNBOOKS`.

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
