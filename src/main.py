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
        model="claude-3-haiku-20240307",  # Cheapest model that definitely works
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


# ============= SECURITY =============
from starlette.responses import JSONResponse, RedirectResponse, Response
from starlette.requests import Request
from starlette.middleware.base import BaseHTTPMiddleware
from urllib.parse import urlencode
import secrets
import time
from collections import defaultdict

# Secret key for additional validation (set in environment)
MCP_SECRET = os.getenv("MCP_SECRET", "")  # Optional: set this for extra security

# Rate limiting: max requests per minute per IP
RATE_LIMIT = int(os.getenv("RATE_LIMIT", "60"))
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

# Port's egress IPs (EU region) - only these can access the server
PORT_ALLOWED_IPS = {
    "35.156.37.90",
    "3.71.36.69",
    "52.58.133.79",
}

# Set to True to enforce IP whitelist (disable for local dev)
ENFORCE_IP_WHITELIST = os.getenv("ENFORCE_IP_WHITELIST", "true").lower() == "true"

class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware to validate requests and enforce rate limits + IP whitelist."""
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "unknown")
        if "," in client_ip:
            client_ip = client_ip.split(",")[0].strip()
        
        # Enforce Port IP whitelist (skip for health checks)
        if ENFORCE_IP_WHITELIST and request.url.path != "/health":
            if client_ip not in PORT_ALLOWED_IPS and client_ip not in ("127.0.0.1", "localhost"):
                return Response(f"Forbidden - IP {client_ip} not allowed", status_code=403)
        
        # Skip further security for OAuth endpoints (needed for initial connection)
        if request.url.path.startswith("/.well-known") or \
           request.url.path == "/authorize" or \
           request.url.path == "/token":
            return await call_next(request)
        
        # Rate limiting
        if not check_rate_limit(client_ip):
            return Response("Rate limit exceeded", status_code=429)
        
        # Optional: Validate secret header (if MCP_SECRET is set)
        if MCP_SECRET:
            auth_header = request.headers.get("authorization", "")
            # Allow if it's a valid OAuth token OR if it matches our secret
            if not auth_header.startswith("Bearer ") and \
               request.headers.get("x-mcp-secret") != MCP_SECRET:
                return Response("Unauthorized", status_code=401)
        
        return await call_next(request)

# Store authorization codes temporarily
auth_codes = {}

async def oauth_metadata(request: Request):
    """OAuth 2.0 Authorization Server Metadata - tells Port how to authenticate."""
    base_url = str(request.base_url).rstrip('/')
    return JSONResponse({
        "issuer": base_url,
        "authorization_endpoint": f"{base_url}/authorize",
        "token_endpoint": f"{base_url}/token",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code"],
        "code_challenge_methods_supported": ["S256", "plain"],
        "token_endpoint_auth_methods_supported": ["client_secret_post", "client_secret_basic"]
    })

async def authorize(request: Request):
    """OAuth authorize endpoint - auto-approves and redirects back to Port."""
    redirect_uri = request.query_params.get("redirect_uri", "")
    state = request.query_params.get("state", "")
    code_challenge = request.query_params.get("code_challenge", "")
    
    # Generate auth code
    code = secrets.token_urlsafe(32)
    auth_codes[code] = {"code_challenge": code_challenge, "redirect_uri": redirect_uri}
    
    # Redirect back to Port with the code
    params = urlencode({"code": code, "state": state})
    return RedirectResponse(f"{redirect_uri}?{params}", status_code=302)

async def token(request: Request):
    """OAuth token endpoint - exchanges code for access token."""
    try:
        # Handle both form data and JSON
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type:
            data = await request.json()
        else:
            form = await request.form()
            data = dict(form)
        
        code = data.get("code", "")
        
        # Validate code exists (basic check)
        if code and code in auth_codes:
            del auth_codes[code]  # Use once
        
        # Return access token
        return JSONResponse({
            "access_token": secrets.token_urlsafe(32),
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": secrets.token_urlsafe(32)
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


# ============= ROUTER =============
def create_app():
    """Create ASGI app with Streamable HTTP transport and OAuth support."""
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
                        yield
    
    # Get the streamable HTTP apps - they handle /mcp internally
    datadog_http = datadog_mcp.streamable_http_app()
    github_http = github_mcp.streamable_http_app()
    newrelic_http = newrelic_mcp.streamable_http_app()
    aws_http = aws_mcp.streamable_http_app()
    
    # Health check endpoint (bypasses IP whitelist)
    async def health(request):
        return JSONResponse({"status": "healthy", "service": "mock-mcp-server"})
    
    app = Starlette(
        routes=[
            # Health check (for App Runner / load balancers)
            Route("/health", health, methods=["GET"]),
            
            # OAuth endpoints at root (for discovery)
            Route("/.well-known/oauth-authorization-server", oauth_metadata, methods=["GET"]),
            Route("/authorize", authorize, methods=["GET"]),
            Route("/token", token, methods=["POST"]),
            
            # OAuth endpoints for each vendor path (Port looks here based on MCP URL)
            Route("/datadog/.well-known/oauth-authorization-server", oauth_metadata, methods=["GET"]),
            Route("/github/.well-known/oauth-authorization-server", oauth_metadata, methods=["GET"]),
            Route("/newrelic/.well-known/oauth-authorization-server", oauth_metadata, methods=["GET"]),
            Route("/aws/.well-known/oauth-authorization-server", oauth_metadata, methods=["GET"]),
            
            # MCP endpoints - Port expects POST/GET directly at /datadog, /github, etc.
            # The streamable_http_app handles /mcp subpath, so we mount it
            Mount("/datadog", app=datadog_http),
            Mount("/github", app=github_http),
            Mount("/newrelic", app=newrelic_http),
            Mount("/aws", app=aws_http),
        ],
        middleware=[
            Middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]),
            Middleware(SecurityMiddleware),  # Rate limiting + optional secret validation
        ],
        lifespan=lifespan
    )
    
    return app


if __name__ == "__main__":
    import uvicorn
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
