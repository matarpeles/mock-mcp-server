import os
import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from anthropic import Anthropic

# Load prompts
PROMPTS_DIR = Path(__file__).parent / "prompts"

def load_prompt(vendor: str) -> str:
    prompt_file = PROMPTS_DIR / f"{vendor}.md"
    if prompt_file.exists():
        return prompt_file.read_text()
    return f"You are a {vendor} MCP server. Generate realistic responses based on the provided context."

def get_anthropic_api_key() -> str:
    """Get Anthropic API key from AWS Secrets Manager or environment variable."""
    # Try environment variable first (for local dev)
    if api_key := os.getenv("ANTHROPIC_API_KEY"):
        return api_key
    
    # Load from AWS Secrets Manager
    try:
        import boto3
        client = boto3.client("secretsmanager", region_name="eu-west-1")
        response = client.get_secret_value(SecretId="mock-mcp-server/anthropic-api-key")
        return response["SecretString"]
    except Exception as e:
        raise RuntimeError(f"Failed to get Anthropic API key: {e}")

# Initialize LLM client
llm = Anthropic(api_key=get_anthropic_api_key())

# Model configuration - use env var to allow updates without code changes
# Default to claude-haiku-4-5-20251001 (cheapest current model)
# Can be overridden via AWS App Runner env var or Secrets Manager
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")

def generate_response(vendor: str, tool_name: str, params: dict, port_context: dict) -> dict:
    """Generate a mock response using LLM."""
    system_prompt = load_prompt(vendor)
    
    user_prompt = f"""
TOOL CALLED: {tool_name}
PARAMETERS: {json.dumps(params, indent=2)}

PORT CONTEXT:
{json.dumps(port_context, indent=2)}

Generate a realistic {vendor} response. Return valid JSON only.
"""
    
    response = llm.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=1000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )
    
    raw_text = response.content[0].text
    if "```json" in raw_text:
        raw_text = raw_text.split("```json")[1].split("```")[0].strip()
    elif "```" in raw_text:
        raw_text = raw_text.split("```")[1].split("```")[0].strip()
    
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        return {"error": "Failed to parse response", "raw": raw_text[:500]}


# ============= DATADOG MCP =============
from mcp.server.transport_security import TransportSecuritySettings
# Disable DNS rebinding protection for ngrok compatibility
security_settings = TransportSecuritySettings(enable_dns_rebinding_protection=False)

datadog_mcp = FastMCP("datadog-mock", transport_security=security_settings)

@datadog_mcp.tool()
async def search_datadog_logs(query: str, port_context: dict, from_time: str = None, to_time: str = None) -> dict:
    """Search logs with pattern analysis and insights."""
    return generate_response("datadog", "search_datadog_logs", 
        {"query": query, "from_time": from_time, "to_time": to_time}, port_context)

@datadog_mcp.tool()
async def get_datadog_metrics(metric: str, service: str, port_context: dict, from_time: str = None, to_time: str = None) -> dict:
    """Query metrics with anomaly detection."""
    return generate_response("datadog", "get_datadog_metrics",
        {"metric": metric, "service": service, "from_time": from_time, "to_time": to_time}, port_context)

@datadog_mcp.tool()
async def get_datadog_service_dependencies(service: str, port_context: dict) -> dict:
    """Get service dependencies with health status."""
    return generate_response("datadog", "get_datadog_service_dependencies", {"service": service}, port_context)

@datadog_mcp.tool()
async def search_datadog_incidents(status: str, port_context: dict, severity: str = None) -> dict:
    """Search incidents with timeline and impact."""
    return generate_response("datadog", "search_datadog_incidents", {"status": status, "severity": severity}, port_context)

@datadog_mcp.tool()
async def get_datadog_monitors(port_context: dict, name: str = None, tags: list = None, status: str = None) -> dict:
    """Get monitors with their current status and alert conditions."""
    return generate_response("datadog", "get_datadog_monitors", {"name": name, "tags": tags, "status": status}, port_context)

@datadog_mcp.tool()
async def list_datadog_dashboards(port_context: dict, name: str = None, tags: list = None) -> dict:
    """List dashboards with their widgets and configurations."""
    return generate_response("datadog", "list_datadog_dashboards", {"name": name, "tags": tags}, port_context)

@datadog_mcp.tool()
async def list_datadog_traces(query: str, port_context: dict, service: str = None, from_time: str = None, to_time: str = None) -> dict:
    """List APM traces with span details and timing."""
    return generate_response("datadog", "list_datadog_traces", {"query": query, "service": service, "from_time": from_time, "to_time": to_time}, port_context)

@datadog_mcp.tool()
async def list_datadog_hosts(port_context: dict, filter: str = None, sort_field: str = None) -> dict:
    """List infrastructure hosts with their metadata and status."""
    return generate_response("datadog", "list_datadog_hosts", {"filter": filter, "sort_field": sort_field}, port_context)


# ============= GITHUB MCP =============
github_mcp = FastMCP("github-mock", transport_security=security_settings)

@github_mcp.tool()
async def list_pull_requests(owner: str, repo: str, port_context: dict, state: str = "all") -> dict:
    """List pull requests with details."""
    return generate_response("github", "list_pull_requests", {"owner": owner, "repo": repo, "state": state}, port_context)

@github_mcp.tool()
async def get_file_content(owner: str, repo: str, path: str, port_context: dict) -> dict:
    """Get file content from repository."""
    return generate_response("github", "get_file_content", {"owner": owner, "repo": repo, "path": path}, port_context)

@github_mcp.tool()
async def list_commits(owner: str, repo: str, port_context: dict, sha: str = None) -> dict:
    """List commits with details."""
    return generate_response("github", "list_commits", {"owner": owner, "repo": repo, "sha": sha}, port_context)

@github_mcp.tool()
async def search_code(query: str, port_context: dict) -> dict:
    """Search code across repositories."""
    return generate_response("github", "search_code", {"query": query}, port_context)

@github_mcp.tool()
async def search_issues(query: str, port_context: dict, state: str = "open") -> dict:
    """Search issues and pull requests across repositories."""
    return generate_response("github", "search_issues", {"query": query, "state": state}, port_context)

@github_mcp.tool()
async def get_repository(owner: str, repo: str, port_context: dict) -> dict:
    """Get repository details including stats, languages, and metadata."""
    return generate_response("github", "get_repository", {"owner": owner, "repo": repo}, port_context)

@github_mcp.tool()
async def list_branches(owner: str, repo: str, port_context: dict) -> dict:
    """List branches in a repository."""
    return generate_response("github", "list_branches", {"owner": owner, "repo": repo}, port_context)

@github_mcp.tool()
async def get_workflow_runs(owner: str, repo: str, port_context: dict, workflow_id: str = None, status: str = None) -> dict:
    """Get GitHub Actions workflow runs for a repository."""
    return generate_response("github", "get_workflow_runs", {"owner": owner, "repo": repo, "workflow_id": workflow_id, "status": status}, port_context)

@github_mcp.tool()
async def list_dependabot_alerts(owner: str, repo: str, port_context: dict, state: str = "open", severity: str = None) -> dict:
    """List Dependabot security alerts for a repository."""
    return generate_response("github", "list_dependabot_alerts", {"owner": owner, "repo": repo, "state": state, "severity": severity}, port_context)


# ============= NEW RELIC MCP =============
newrelic_mcp = FastMCP("newrelic-mock", transport_security=security_settings)

@newrelic_mcp.tool()
async def get_newrelic_entity(port_context: dict, guid: str = None, name: str = None) -> dict:
    """Get entity by GUID or name."""
    return generate_response("newrelic", "get_newrelic_entity", {"guid": guid, "name": name}, port_context)

@newrelic_mcp.tool()
async def execute_nrql_query(query: str, account_id: int, port_context: dict) -> dict:
    """Execute NRQL query."""
    return generate_response("newrelic", "execute_nrql_query", {"query": query, "account_id": account_id}, port_context)

@newrelic_mcp.tool()
async def list_newrelic_error_groups(entity_guid: str, port_context: dict, time_window: str = "1h") -> dict:
    """Get error groups from Errors Inbox."""
    return generate_response("newrelic", "list_newrelic_error_groups", {"entity_guid": entity_guid, "time_window": time_window}, port_context)

@newrelic_mcp.tool()
async def list_newrelic_alerts(port_context: dict, policy_id: str = None, status: str = None) -> dict:
    """List alert conditions and their current status."""
    return generate_response("newrelic", "list_newrelic_alerts", {"policy_id": policy_id, "status": status}, port_context)

@newrelic_mcp.tool()
async def get_newrelic_dashboard(dashboard_guid: str, port_context: dict) -> dict:
    """Get dashboard with widgets and visualizations."""
    return generate_response("newrelic", "get_newrelic_dashboard", {"dashboard_guid": dashboard_guid}, port_context)

@newrelic_mcp.tool()
async def list_newrelic_services(port_context: dict, tags: dict = None) -> dict:
    """List APM services with their health status and key metrics."""
    return generate_response("newrelic", "list_newrelic_services", {"tags": tags}, port_context)


# ============= AWS MCP =============
aws_mcp = FastMCP("aws-mock", transport_security=security_settings)

@aws_mcp.tool()
async def get_cloudwatch_metrics(namespace: str, metric_name: str, port_context: dict, dimensions: dict = None) -> dict:
    """Get CloudWatch metrics."""
    return generate_response("aws", "get_cloudwatch_metrics", {"namespace": namespace, "metric_name": metric_name, "dimensions": dimensions}, port_context)

@aws_mcp.tool()
async def get_cloudwatch_logs(log_group: str, port_context: dict, start_time: str = None, end_time: str = None) -> dict:
    """Get log events from CloudWatch."""
    return generate_response("aws", "get_cloudwatch_logs", {"log_group": log_group, "start_time": start_time, "end_time": end_time}, port_context)

@aws_mcp.tool()
async def get_cloudtrail_events(port_context: dict, lookup_attributes: dict = None, start_time: str = None, end_time: str = None) -> dict:
    """Get CloudTrail events."""
    return generate_response("aws", "get_cloudtrail_events", {"lookup_attributes": lookup_attributes, "start_time": start_time, "end_time": end_time}, port_context)

@aws_mcp.tool()
async def describe_ec2_instances(port_context: dict, instance_ids: list = None, filters: dict = None) -> dict:
    """Describe EC2 instances with their state, type, and metadata."""
    return generate_response("aws", "describe_ec2_instances", {"instance_ids": instance_ids, "filters": filters}, port_context)

@aws_mcp.tool()
async def list_lambda_functions(port_context: dict, function_name: str = None) -> dict:
    """List Lambda functions with their configuration and runtime."""
    return generate_response("aws", "list_lambda_functions", {"function_name": function_name}, port_context)

@aws_mcp.tool()
async def describe_cloudwatch_alarms(port_context: dict, alarm_names: list = None, state: str = None) -> dict:
    """Describe CloudWatch alarms with their status and thresholds."""
    return generate_response("aws", "describe_cloudwatch_alarms", {"alarm_names": alarm_names, "state": state}, port_context)


# ============= NOTION MCP =============
notion_mcp = FastMCP("notion-mock", transport_security=security_settings)

@notion_mcp.tool()
async def search_notion(query: str, port_context: dict, filter_type: str = None) -> dict:
    """Search across Notion workspace for pages, databases, and content."""
    return generate_response("notion", "search_notion", {"query": query, "filter_type": filter_type}, port_context)

@notion_mcp.tool()
async def query_notion_database(database_id: str, port_context: dict, filter: dict = None, sorts: list = None) -> dict:
    """Query a Notion database with optional filters and sorting."""
    return generate_response("notion", "query_notion_database", {"database_id": database_id, "filter": filter, "sorts": sorts}, port_context)

@notion_mcp.tool()
async def get_notion_page(page_id: str, port_context: dict) -> dict:
    """Get a Notion page with its properties and content blocks."""
    return generate_response("notion", "get_notion_page", {"page_id": page_id}, port_context)

@notion_mcp.tool()
async def list_notion_databases(port_context: dict) -> dict:
    """List all databases in the Notion workspace."""
    return generate_response("notion", "list_notion_databases", {}, port_context)


# ============= FLUXCD MCP =============
# Mirrors the real Flux Operator MCP Server tools: https://fluxcd.control-plane.io/mcp/tools
fluxcd_mcp = FastMCP("fluxcd-mock", transport_security=security_settings)

@fluxcd_mcp.tool()
async def get_flux_instance(port_context: dict) -> dict:
    """Retrieves detailed information about the Flux installation including distribution version, component status and health, cluster sync statistics."""
    return generate_response("fluxcd", "get_flux_instance", {}, port_context)

@fluxcd_mcp.tool()
async def get_kubernetes_resources(apiVersion: str, kind: str, port_context: dict, name: str = None, namespace: str = None, selector: str = None, limit: int = None) -> dict:
    """Retrieves Kubernetes resources from the cluster, including Flux custom resources, their status, and associated events. Returns YAML format with spec, status conditions, related events, and metadata."""
    return generate_response("fluxcd", "get_kubernetes_resources", {
        "apiVersion": apiVersion, "kind": kind, "name": name, 
        "namespace": namespace, "selector": selector, "limit": limit
    }, port_context)

@fluxcd_mcp.tool()
async def get_kubernetes_logs(pod_name: str, pod_namespace: str, container_name: str, port_context: dict, limit: int = 100, previous: bool = False) -> dict:
    """Retrieves logs from Kubernetes pods for analyzing application behavior and troubleshooting issues. Returns log lines with timestamps and log levels preserved."""
    return generate_response("fluxcd", "get_kubernetes_logs", {
        "pod_name": pod_name, "pod_namespace": pod_namespace, 
        "container_name": container_name, "limit": limit, "previous": previous
    }, port_context)

@fluxcd_mcp.tool()
async def get_kubernetes_metrics(pod_namespace: str, port_context: dict, pod_name: str = None, pod_selector: str = None, limit: int = 100) -> dict:
    """Retrieves CPU and Memory usage for Kubernetes pods. Returns metrics for each container in YAML format."""
    return generate_response("fluxcd", "get_kubernetes_metrics", {
        "pod_namespace": pod_namespace, "pod_name": pod_name,
        "pod_selector": pod_selector, "limit": limit
    }, port_context)

@fluxcd_mcp.tool()
async def get_kubernetes_api_versions(port_context: dict) -> dict:
    """Retrieves the Kubernetes CRDs registered on the cluster and returns the preferred apiVersion for each kind."""
    return generate_response("fluxcd", "get_kubernetes_api_versions", {}, port_context)

@fluxcd_mcp.tool()
async def get_kubeconfig_contexts(port_context: dict) -> dict:
    """Retrieves the available Kubernetes cluster contexts from the kubeconfig."""
    return generate_response("fluxcd", "get_kubeconfig_contexts", {}, port_context)

@fluxcd_mcp.tool()
async def set_kubeconfig_context(name: str, port_context: dict) -> dict:
    """Switches the current session to use a specific Kubernetes cluster context."""
    return generate_response("fluxcd", "set_kubeconfig_context", {"name": name}, port_context)

@fluxcd_mcp.tool()
async def reconcile_flux_helmrelease(name: str, namespace: str, port_context: dict, with_source: bool = False) -> dict:
    """Triggers the reconciliation of a Flux HelmRelease."""
    return generate_response("fluxcd", "reconcile_flux_helmrelease", {
        "name": name, "namespace": namespace, "with_source": with_source
    }, port_context)

@fluxcd_mcp.tool()
async def reconcile_flux_kustomization(name: str, namespace: str, port_context: dict, with_source: bool = False) -> dict:
    """Triggers the reconciliation of a Flux Kustomization."""
    return generate_response("fluxcd", "reconcile_flux_kustomization", {
        "name": name, "namespace": namespace, "with_source": with_source
    }, port_context)

@fluxcd_mcp.tool()
async def reconcile_flux_source(kind: str, name: str, namespace: str, port_context: dict) -> dict:
    """Triggers the reconciliation of Flux sources (GitRepository, OCIRepository, HelmRepository, HelmChart, Bucket)."""
    return generate_response("fluxcd", "reconcile_flux_source", {
        "kind": kind, "name": name, "namespace": namespace
    }, port_context)

@fluxcd_mcp.tool()
async def suspend_flux_reconciliation(apiVersion: str, kind: str, name: str, namespace: str, port_context: dict) -> dict:
    """Suspends the reconciliation of a Flux resource."""
    return generate_response("fluxcd", "suspend_flux_reconciliation", {
        "apiVersion": apiVersion, "kind": kind, "name": name, "namespace": namespace
    }, port_context)

@fluxcd_mcp.tool()
async def resume_flux_reconciliation(apiVersion: str, kind: str, name: str, namespace: str, port_context: dict) -> dict:
    """Resumes the reconciliation of a previously suspended Flux resource."""
    return generate_response("fluxcd", "resume_flux_reconciliation", {
        "apiVersion": apiVersion, "kind": kind, "name": name, "namespace": namespace
    }, port_context)

@fluxcd_mcp.tool()
async def search_flux_docs(query: str, port_context: dict, limit: int = 1) -> dict:
    """Searches the Flux documentation for specific information."""
    return generate_response("fluxcd", "search_flux_docs", {"query": query, "limit": limit}, port_context)


# ============= SERVICENOW MCP =============
# Mirrors common ServiceNow ITSM/ITOM tools based on community implementations
servicenow_mcp = FastMCP("servicenow-mock", transport_security=security_settings)

@servicenow_mcp.tool()
async def search_incidents(port_context: dict, query: str = None, state: str = None, priority: str = None, assigned_to: str = None, limit: int = 10) -> dict:
    """Search incidents with optional filters for state, priority, and assignment."""
    return generate_response("servicenow", "search_incidents", {
        "query": query, "state": state, "priority": priority, "assigned_to": assigned_to, "limit": limit
    }, port_context)

@servicenow_mcp.tool()
async def get_incident(number: str, port_context: dict) -> dict:
    """Get detailed information about a specific incident by number (e.g., INC0001234)."""
    return generate_response("servicenow", "get_incident", {"number": number}, port_context)

@servicenow_mcp.tool()
async def create_incident(short_description: str, port_context: dict, description: str = None, priority: str = None, category: str = None, assignment_group: str = None, caller_id: str = None) -> dict:
    """Create a new incident with the specified details."""
    return generate_response("servicenow", "create_incident", {
        "short_description": short_description, "description": description, "priority": priority,
        "category": category, "assignment_group": assignment_group, "caller_id": caller_id
    }, port_context)

@servicenow_mcp.tool()
async def update_incident(number: str, port_context: dict, state: str = None, priority: str = None, assigned_to: str = None, work_notes: str = None, comments: str = None) -> dict:
    """Update an existing incident with new values or add work notes/comments."""
    return generate_response("servicenow", "update_incident", {
        "number": number, "state": state, "priority": priority, "assigned_to": assigned_to,
        "work_notes": work_notes, "comments": comments
    }, port_context)

@servicenow_mcp.tool()
async def resolve_incident(number: str, resolution_code: str, resolution_notes: str, port_context: dict) -> dict:
    """Resolve an incident with a resolution code and notes."""
    return generate_response("servicenow", "resolve_incident", {
        "number": number, "resolution_code": resolution_code, "resolution_notes": resolution_notes
    }, port_context)

@servicenow_mcp.tool()
async def search_change_requests(port_context: dict, query: str = None, state: str = None, type: str = None, risk: str = None, limit: int = 10) -> dict:
    """Search change requests with optional filters."""
    return generate_response("servicenow", "search_change_requests", {
        "query": query, "state": state, "type": type, "risk": risk, "limit": limit
    }, port_context)

@servicenow_mcp.tool()
async def get_change_request(number: str, port_context: dict) -> dict:
    """Get detailed information about a specific change request by number (e.g., CHG0001234)."""
    return generate_response("servicenow", "get_change_request", {"number": number}, port_context)

@servicenow_mcp.tool()
async def create_change_request(short_description: str, type: str, port_context: dict, description: str = None, risk: str = None, impact: str = None, assignment_group: str = None, start_date: str = None, end_date: str = None) -> dict:
    """Create a new change request (normal, standard, or emergency)."""
    return generate_response("servicenow", "create_change_request", {
        "short_description": short_description, "type": type, "description": description,
        "risk": risk, "impact": impact, "assignment_group": assignment_group,
        "start_date": start_date, "end_date": end_date
    }, port_context)

@servicenow_mcp.tool()
async def search_cmdb_ci(port_context: dict, query: str = None, ci_class: str = None, operational_status: str = None, environment: str = None, limit: int = 10) -> dict:
    """Search CMDB configuration items with optional filters for class, status, and environment."""
    return generate_response("servicenow", "search_cmdb_ci", {
        "query": query, "ci_class": ci_class, "operational_status": operational_status,
        "environment": environment, "limit": limit
    }, port_context)

@servicenow_mcp.tool()
async def get_cmdb_ci(sys_id: str, port_context: dict) -> dict:
    """Get detailed information about a specific configuration item including relationships."""
    return generate_response("servicenow", "get_cmdb_ci", {"sys_id": sys_id}, port_context)

@servicenow_mcp.tool()
async def get_ci_relationships(sys_id: str, port_context: dict, relationship_type: str = None) -> dict:
    """Get relationships for a configuration item (upstream/downstream dependencies)."""
    return generate_response("servicenow", "get_ci_relationships", {
        "sys_id": sys_id, "relationship_type": relationship_type
    }, port_context)

@servicenow_mcp.tool()
async def search_knowledge_base(query: str, port_context: dict, category: str = None, limit: int = 10) -> dict:
    """Search knowledge base articles."""
    return generate_response("servicenow", "search_knowledge_base", {
        "query": query, "category": category, "limit": limit
    }, port_context)

@servicenow_mcp.tool()
async def get_catalog_items(port_context: dict, category: str = None, query: str = None, limit: int = 20) -> dict:
    """List available service catalog items with optional filtering."""
    return generate_response("servicenow", "get_catalog_items", {
        "category": category, "query": query, "limit": limit
    }, port_context)

@servicenow_mcp.tool()
async def order_catalog_item(item_sys_id: str, port_context: dict, variables: dict = None, requested_for: str = None, quantity: int = 1) -> dict:
    """Submit a service catalog request for an item."""
    return generate_response("servicenow", "order_catalog_item", {
        "item_sys_id": item_sys_id, "variables": variables, "requested_for": requested_for, "quantity": quantity
    }, port_context)

@servicenow_mcp.tool()
async def get_user(port_context: dict, user_id: str = None, email: str = None, username: str = None) -> dict:
    """Get user details by sys_id, email, or username."""
    return generate_response("servicenow", "get_user", {
        "user_id": user_id, "email": email, "username": username
    }, port_context)

@servicenow_mcp.tool()
async def search_problems(port_context: dict, query: str = None, state: str = None, priority: str = None, limit: int = 10) -> dict:
    """Search problem records with optional filters."""
    return generate_response("servicenow", "search_problems", {
        "query": query, "state": state, "priority": priority, "limit": limit
    }, port_context)

@servicenow_mcp.tool()
async def get_my_approvals(port_context: dict, state: str = "requested") -> dict:
    """Get pending approvals for the current user."""
    return generate_response("servicenow", "get_my_approvals", {"state": state}, port_context)

@servicenow_mcp.tool()
async def approve_request(approval_sys_id: str, port_context: dict, comments: str = None) -> dict:
    """Approve a pending approval request."""
    return generate_response("servicenow", "approve_request", {
        "approval_sys_id": approval_sys_id, "comments": comments
    }, port_context)

@servicenow_mcp.tool()
async def reject_request(approval_sys_id: str, port_context: dict, comments: str = None) -> dict:
    """Reject a pending approval request."""
    return generate_response("servicenow", "reject_request", {
        "approval_sys_id": approval_sys_id, "comments": comments
    }, port_context)


# ============= CONFLUENCE MCP =============
# Dummy mock — same pattern as Notion (snake_case tools, LLM-generated responses, no auth)
confluence_mcp = FastMCP("confluence-mock", transport_security=security_settings)

@confluence_mcp.tool()
async def search_confluence(query: str, port_context: dict, space_key: str = None) -> dict:
    """Search across Confluence for pages, runbooks, and documentation."""
    return generate_response("confluence", "search_confluence", {"query": query, "space_key": space_key}, port_context)

@confluence_mcp.tool()
async def get_confluence_page(page_id: str, port_context: dict) -> dict:
    """Get a Confluence page with content preview."""
    return generate_response("confluence", "get_confluence_page", {"page_id": page_id}, port_context)

@confluence_mcp.tool()
async def list_confluence_spaces(port_context: dict) -> dict:
    """List Confluence spaces in the wiki."""
    return generate_response("confluence", "list_confluence_spaces", {}, port_context)

@confluence_mcp.tool()
async def get_confluence_page_children(page_id: str, port_context: dict) -> dict:
    """List child pages under a parent page."""
    return generate_response("confluence", "get_confluence_page_children", {"page_id": page_id}, port_context)


# ============= BACKSTAGE MCP =============
# Mirrors Backstage Portal MCP tools: https://backstage.spotify.com/docs/portal/core-features-and-plugins/mcp/available-tools
# Catalog lookups use deterministic data; semantic search uses LLM for doc-style results.
from .backstage_catalog import (
    get_entity as catalog_get_entity,
    get_entity_overlay as catalog_get_entity_overlay,
    get_entity_relations as catalog_get_entity_relations,
    list_entities as catalog_list_entities,
    search as catalog_search,
    search_entities as catalog_search_entities,
)

backstage_mcp = FastMCP("backstage-mock", transport_security=security_settings)

@backstage_mcp.tool()
async def search_entities(query: str, port_context: dict, kind: str = None, limit: int = 10) -> dict:
    """Search for entities in the Backstage software catalog."""
    entities = catalog_search_entities(query, kind, limit)
    return {"entities": entities, "total": len(entities), "query": query}

@backstage_mcp.tool()
async def get_entity(entity_ref: str, port_context: dict) -> dict:
    """Get a specific catalog entity by reference (e.g. component:default/checkout-service)."""
    entity = catalog_get_entity(entity_ref)
    if not entity:
        return {"error": f"Entity not found: {entity_ref}"}
    return entity

@backstage_mcp.tool()
async def get_catalog_entity(entity_ref: str, port_context: dict) -> dict:
    """Retrieve detailed information about a specific entity in the software catalog (Backstage Portal MCP)."""
    return await get_entity(entity_ref, port_context)

@backstage_mcp.tool()
async def list_entities(kind: str, port_context: dict, limit: int = 20) -> dict:
    """List all catalog entities of a specific kind (Component, API, System, Resource, Group)."""
    entities = catalog_list_entities(kind, limit)
    return {"entities": entities, "kind": kind, "total": len(entities)}

@backstage_mcp.tool()
async def get_entity_relations(entity_ref: str, port_context: dict, relation_type: str = None) -> dict:
    """Get relations for a catalog entity (dependsOn, providesApis, owner, system)."""
    return catalog_get_entity_relations(entity_ref, relation_type)

@backstage_mcp.tool()
async def get_entity_overlay(entity_ref: str, port_context: dict) -> dict:
    """Retrieve overlay metadata for a catalog entity (maturity, on-call, compliance)."""
    return catalog_get_entity_overlay(entity_ref)

@backstage_mcp.tool()
async def search(query: str, port_context: dict, limit: int = 10) -> dict:
    """Search for information across the software catalog (Backstage Portal MCP)."""
    return catalog_search(query, limit)

@backstage_mcp.tool()
async def query_semantic_search_engine(query: str, port_context: dict, limit: int = 5) -> dict:
    """Perform semantic search across indexed knowledge sources and the software catalog."""
    return generate_response("backstage", "query_semantic_search_engine",
        {"query": query, "limit": limit}, port_context)


# ============= FIGMA MCP =============
# Mirrors Figma's real Dev Mode MCP Server: https://developers.figma.com/docs/figma-mcp-server/tools-and-prompts/
figma_mcp = FastMCP("figma-mock", transport_security=security_settings)

@figma_mcp.tool()
async def get_metadata(fileKey: str, nodeId: str, port_context: dict) -> dict:
    """Returns a sparse XML representation of a Figma selection: layer IDs, names, types, position, and sizes. Use this to navigate large files before calling get_design_context on specific child nodes."""
    return generate_response("figma", "get_metadata", {"fileKey": fileKey, "nodeId": nodeId}, port_context)

@figma_mcp.tool()
async def get_design_context(fileKey: str, nodeId: str, port_context: dict) -> dict:
    """Returns structured design-to-code context (React + Tailwind by default) for a Figma node. Also known as get_code."""
    return generate_response("figma", "get_design_context", {"fileKey": fileKey, "nodeId": nodeId}, port_context)

@figma_mcp.tool()
async def get_screenshot(fileKey: str, nodeId: str, port_context: dict) -> dict:
    """Takes a screenshot of a Figma selection for visual reference and layout fidelity checks."""
    return generate_response("figma", "get_screenshot", {"fileKey": fileKey, "nodeId": nodeId}, port_context)

@figma_mcp.tool()
async def get_variable_defs(fileKey: str, nodeId: str, port_context: dict) -> dict:
    """Returns the variables and styles (colors, spacing, typography) used in a Figma selection."""
    return generate_response("figma", "get_variable_defs", {"fileKey": fileKey, "nodeId": nodeId}, port_context)

@figma_mcp.tool()
async def get_figma_comments(fileKey: str, port_context: dict) -> dict:
    """Lists review comments left on a Figma file, including unresolved open questions. Port extension, not part of Figma's real Dev Mode MCP tool set."""
    return generate_response("figma", "get_figma_comments", {"fileKey": fileKey}, port_context)


# ============= RATE LIMITING =============
from starlette.responses import JSONResponse, Response
from starlette.requests import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
from collections import defaultdict

# Rate limiting: max requests per minute per IP
# Set high for demo - multiple users, 4 tools each, parallel usage
RATE_LIMIT = int(os.getenv("RATE_LIMIT", "1000"))
rate_limit_store = defaultdict(list)

def check_rate_limit(ip: str) -> bool:
    """Check if IP has exceeded rate limit."""
    now = time.time()
    minute_ago = now - 60
    # Clean old entries
    rate_limit_store[ip] = [t for t in rate_limit_store[ip] if t > minute_ago]
    # Check limit
    if len(rate_limit_store[ip]) >= RATE_LIMIT:
        return False
    rate_limit_store[ip].append(now)
    return True

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting only."""
    
    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/health":
            return await call_next(request)

        client_ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "unknown")
        if "," in client_ip:
            client_ip = client_ip.split(",")[0].strip()

        if not check_rate_limit(client_ip):
            return Response("Rate limit exceeded", status_code=429)

        return await call_next(request)


# ============= ROUTER =============
def create_app():
    """Create ASGI app with Streamable HTTP transport (no client auth)."""
    from starlette.applications import Starlette
    from starlette.routing import Mount, Route
    from starlette.middleware import Middleware
    from starlette.middleware.cors import CORSMiddleware
    from contextlib import asynccontextmanager
    
    @asynccontextmanager
    async def lifespan(app):
        # Initialize all MCP servers
        async with datadog_mcp.session_manager.run():
            async with github_mcp.session_manager.run():
                async with newrelic_mcp.session_manager.run():
                    async with aws_mcp.session_manager.run():
                        async with notion_mcp.session_manager.run():
                            async with fluxcd_mcp.session_manager.run():
                                async with servicenow_mcp.session_manager.run():
                                    async with confluence_mcp.session_manager.run():
                                        async with backstage_mcp.session_manager.run():
                                            async with figma_mcp.session_manager.run():
                                                yield
    
    # Get the streamable HTTP apps
    datadog_http = datadog_mcp.streamable_http_app()
    github_http = github_mcp.streamable_http_app()
    newrelic_http = newrelic_mcp.streamable_http_app()
    aws_http = aws_mcp.streamable_http_app()
    notion_http = notion_mcp.streamable_http_app()
    fluxcd_http = fluxcd_mcp.streamable_http_app()
    servicenow_http = servicenow_mcp.streamable_http_app()
    confluence_http = confluence_mcp.streamable_http_app()
    backstage_http = backstage_mcp.streamable_http_app()
    figma_http = figma_mcp.streamable_http_app()
    
    async def health(request):
        return JSONResponse({"status": "healthy", "service": "mock-mcp-server"})
    
    app = Starlette(
        routes=[
            Route("/health", health, methods=["GET"]),

            # MCP endpoints - Port expects POST/GET directly at /datadog, /github, etc.
            # The streamable_http_app handles /mcp subpath, so we mount it
            Mount("/datadog", app=datadog_http),
            Mount("/github", app=github_http),
            Mount("/newrelic", app=newrelic_http),
            Mount("/aws", app=aws_http),
            Mount("/notion", app=notion_http),
            Mount("/fluxcd", app=fluxcd_http),
            Mount("/servicenow", app=servicenow_http),
            Mount("/confluence", app=confluence_http),
            Mount("/backstage", app=backstage_http),
            Mount("/figma", app=figma_http),
        ],
        middleware=[
            Middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]),
            Middleware(RateLimitMiddleware),
        ],
        lifespan=lifespan
    )
    
    return app


if __name__ == "__main__":
    import uvicorn
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))


