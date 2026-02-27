# Mock MCP Server for Port Demos

A mock MCP server that simulates Datadog, GitHub, NewRelic, and AWS observability tools for Port's Agentic Engineering Platform demos.

## Endpoints

| Vendor | URL Path |
|--------|----------|
| Datadog | `/datadog/sse` |
| GitHub | `/github/sse` |
| NewRelic | `/newrelic/sse` |
| AWS | `/aws/sse` |

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
- `https://your-app.onrender.com/datadog/sse`
- `https://your-app.onrender.com/github/sse`
- `https://your-app.onrender.com/newrelic/sse`
- `https://your-app.onrender.com/aws/sse`

## Connect to Port

1. Go to Port → Settings → MCP Connectors
2. Add connector with URL: `https://your-app.onrender.com/datadog`
3. Repeat for other vendors
