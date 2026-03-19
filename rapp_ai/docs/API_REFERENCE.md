# API Reference

Complete REST API documentation for CommunityRAPP.

## Base URL

**Local Development:**
```
http://localhost:7071/api
```

**Azure Production:**
```
https://YOUR-FUNCTION-APP.azurewebsites.net/api
```

## Authentication

### Function Key Authentication

Include function key in one of two ways:

**Option 1: Query Parameter**
```
POST https://your-app.azurewebsites.net/api/businessinsightbot_function?code=YOUR_FUNCTION_KEY
```

**Option 2: Header**
```bash
curl -X POST https://your-app.azurewebsites.net/api/businessinsightbot_function \
  -H "x-functions-key: YOUR_FUNCTION_KEY" \
  -H "Content-Type: application/json"
```

### Get Function Key

1. Azure Portal → Function App → Functions
2. Click `businessinsightbot_function`
3. Click "Function Keys"
4. Copy "default" key

## Endpoints

### POST /businessinsightbot_function

Send a message to the AI assistant and receive a response.

#### Request

**Headers:**
```
Content-Type: application/json
x-functions-key: YOUR_FUNCTION_KEY (optional if using query param)
```

**Body:**
```json
{
  "user_input": "string (required)",
  "conversation_history": "array (optional)",
  "user_guid": "string (optional)",
  "user_context": "object (optional)"
}
```

**Parameters:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `user_input` | string | Yes | - | User's message or query |
| `conversation_history` | array | No | `[]` | Previous conversation messages |
| `user_guid` | string | No | `c0p110t0-aaaa-bbbb-cccc-123456789abc` | Unique user identifier for memory |
| `user_context` | object | No | `null` | User profile information from Office 365 |

**conversation_history format:**
```json
[
  {
    "role": "user|assistant|system|function",
    "content": "message content",
    "name": "function_name (for role=function only)"
  }
]
```

**user_context format:**
```json
{
  "email": "user@company.com",
  "name": "John Doe",
  "department": "Engineering",
  "jobTitle": "Senior Engineer"
}
```

#### Response

**Success (200 OK):**
```json
{
  "assistant_response": "string",
  "voice_response": "string",
  "agent_logs": "string",
  "user_guid": "string"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `assistant_response` | string | Formatted markdown response for display |
| `voice_response` | string | Concise response suitable for voice synthesis |
| `agent_logs` | string | Execution details and agent activity (for debugging) |
| `user_guid` | string | User GUID used in this session |

**Error Responses:**

| Status Code | Description |
|-------------|-------------|
| 400 Bad Request | Invalid JSON or missing required fields |
| 401 Unauthorized | Invalid or missing function key |
| 500 Internal Server Error | Server error during processing |
| 503 Service Unavailable | Azure OpenAI service unavailable |

#### Examples

**Example 1: Simple Query**

```bash
curl -X POST http://localhost:7071/api/businessinsightbot_function \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "What can you help me with?"
  }'
```

Response:
```json
{
  "assistant_response": "I can help you with:\n- Answering questions\n- Drafting emails\n- Managing your notes\n- And much more!",
  "voice_response": "I can help with questions, emails, notes, and more!",
  "agent_logs": "Session initialized. No agents called.",
  "user_guid": "c0p110t0-aaaa-bbbb-cccc-123456789abc"
}
```

**Example 2: With Conversation History**

```bash
curl -X POST http://localhost:7071/api/businessinsightbot_function \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "Can you remind me what we discussed?",
    "conversation_history": [
      {"role": "user", "content": "Hello"},
      {"role": "assistant", "content": "Hi! How can I help?"},
      {"role": "user", "content": "Tell me about project X"},
      {"role": "assistant", "content": "Project X is a new initiative..."}
    ]
  }'
```

**Example 3: With User Context (Power Platform)**

```bash
curl -X POST https://your-app.azurewebsites.net/api/businessinsightbot_function \
  -H "Content-Type: application/json" \
  -H "x-functions-key: YOUR_KEY" \
  -d '{
    "user_input": "Show me my recent activity",
    "user_guid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "user_context": {
      "email": "john.doe@company.com",
      "name": "John Doe",
      "department": "Engineering",
      "jobTitle": "Senior Engineer"
    }
  }'
```

**Example 4: PowerShell (Windows)**

```powershell
$body = @{
    user_input = "Hello, what's the weather?"
    conversation_history = @()
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri "http://localhost:7071/api/businessinsightbot_function" `
  -Method Post `
  -Body $body `
  -ContentType "application/json"
```

**Example 5: Python**

```python
import requests
import json

url = "http://localhost:7071/api/businessinsightbot_function"
headers = {"Content-Type": "application/json"}
data = {
    "user_input": "Help me draft an email",
    "conversation_history": []
}

response = requests.post(url, headers=headers, json=data)
result = response.json()

print(result["assistant_response"])
```

**Example 6: JavaScript (Node.js)**

```javascript
const fetch = require('node-fetch');

async function callAssistant(message) {
  const response = await fetch('http://localhost:7071/api/businessinsightbot_function', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      user_input: message,
      conversation_history: []
    })
  });

  const data = await response.json();
  return data.assistant_response;
}

callAssistant('Hello!').then(console.log);
```

## Rate Limits

### Local Development
- No rate limits

### Azure Production (Consumption Plan)
- **Default**: 200 concurrent requests
- **Timeout**: 230 seconds per request
- **Daily Executions**: 1,000,000 (free tier)

### Azure OpenAI Limits
- **Tokens per minute**: Depends on your deployment quota
- **Requests per minute**: Typically 60-120 RPM
- Monitor usage in Azure Portal → OpenAI → Quotas

## Response Codes

| Code | Status | Description |
|------|--------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid request format or parameters |
| 401 | Unauthorized | Missing or invalid function key |
| 403 | Forbidden | IP restricted or function disabled |
| 404 | Not Found | Invalid endpoint URL |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server-side error |
| 503 | Service Unavailable | OpenAI or storage service down |

## Error Handling

### Error Response Format

```json
{
  "error": "Error message",
  "details": "Additional error details (optional)",
  "code": "ERROR_CODE"
}
```

### Common Errors

**Invalid JSON:**
```json
{
  "error": "Invalid JSON in request body",
  "code": "INVALID_JSON"
}
```

**Missing user_input:**
```json
{
  "error": "user_input is required",
  "code": "MISSING_PARAMETER"
}
```

**OpenAI Service Error:**
```json
{
  "error": "Azure OpenAI service error",
  "details": "Quota exceeded for model deployment",
  "code": "OPENAI_ERROR"
}
```

### Retry Logic

Implement exponential backoff for transient errors:

```python
import time
import requests

def call_assistant_with_retry(data, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=data, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Retry {attempt + 1}/{max_retries} after {wait_time}s")
                time.sleep(wait_time)
            else:
                raise e
```

## CORS Configuration

CORS is enabled for all origins by default.

**Allowed Methods:**
- POST
- OPTIONS

**Allowed Headers:**
- Content-Type
- x-functions-key
- Authorization

**Exposed Headers:**
- Content-Type

To restrict origins, update `function_app.py`:

```python
ALLOWED_ORIGINS = ['https://yourapp.com', 'https://teams.microsoft.com']

def build_cors_response(response):
    origin = request.headers.get('Origin')
    if origin in ALLOWED_ORIGINS:
        response.headers['Access-Control-Allow-Origin'] = origin
    # ...
```

## Webhooks

### Incoming Webhooks

Not currently supported. Use HTTP endpoint instead.

### Outgoing Webhooks

To send data to external services from agents, use the HTTP connector in agents:

```python
import requests

def perform(self, webhook_url="", data="", **kwargs):
    payload = {"message": data}
    response = requests.post(webhook_url, json=payload)
    return f"Webhook sent: {response.status_code}"
```

## SDK Examples

### Python SDK Example

```python
class CopilotAgent365Client:
    def __init__(self, base_url, function_key=None):
        self.base_url = base_url
        self.function_key = function_key
        self.conversation_history = []

    def send_message(self, message, user_guid=None):
        """Send a message to the assistant."""
        url = f"{self.base_url}/api/businessinsightbot_function"
        headers = {"Content-Type": "application/json"}

        if self.function_key:
            headers["x-functions-key"] = self.function_key

        data = {
            "user_input": message,
            "conversation_history": self.conversation_history
        }

        if user_guid:
            data["user_guid"] = user_guid

        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        result = response.json()

        # Update conversation history
        self.conversation_history.append({
            "role": "user",
            "content": message
        })
        self.conversation_history.append({
            "role": "assistant",
            "content": result["assistant_response"]
        })

        return result

    def reset_conversation(self):
        """Clear conversation history."""
        self.conversation_history = []


# Usage
client = CopilotAgent365Client(
    base_url="http://localhost:7071",
    function_key="YOUR_KEY"
)

response = client.send_message("Hello!")
print(response["assistant_response"])

response = client.send_message("What did I just say?")
print(response["assistant_response"])
```

### TypeScript SDK Example

```typescript
interface Message {
  role: 'user' | 'assistant' | 'system' | 'function';
  content: string;
  name?: string;
}

interface AssistantResponse {
  assistant_response: string;
  voice_response: string;
  agent_logs: string;
  user_guid: string;
}

class CopilotAgent365Client {
  private baseUrl: string;
  private functionKey?: string;
  private conversationHistory: Message[] = [];

  constructor(baseUrl: string, functionKey?: string) {
    this.baseUrl = baseUrl;
    this.functionKey = functionKey;
  }

  async sendMessage(
    message: string,
    userGuid?: string
  ): Promise<AssistantResponse> {
    const url = `${this.baseUrl}/api/businessinsightbot_function`;
    const headers: HeadersInit = {
      'Content-Type': 'application/json'
    };

    if (this.functionKey) {
      headers['x-functions-key'] = this.functionKey;
    }

    const data = {
      user_input: message,
      conversation_history: this.conversationHistory,
      user_guid: userGuid
    };

    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result: AssistantResponse = await response.json();

    // Update conversation history
    this.conversationHistory.push({
      role: 'user',
      content: message
    });
    this.conversationHistory.push({
      role: 'assistant',
      content: result.assistant_response
    });

    return result;
  }

  resetConversation(): void {
    this.conversationHistory = [];
  }
}

// Usage
const client = new CopilotAgent365Client(
  'http://localhost:7071',
  'YOUR_KEY'
);

(async () => {
  const response = await client.sendMessage('Hello!');
  console.log(response.assistant_response);
})();
```

## Monitoring & Analytics

### Track API Usage

Query Application Insights:

```kusto
requests
| where name == "businessinsightbot_function"
| summarize
    RequestCount = count(),
    AvgDuration = avg(duration),
    P95Duration = percentile(duration, 95)
    by bin(timestamp, 1h)
| render timechart
```

### Monitor Error Rate

```kusto
requests
| where name == "businessinsightbot_function"
| summarize
    TotalRequests = count(),
    FailedRequests = countif(success == false),
    ErrorRate = 100.0 * countif(success == false) / count()
    by bin(timestamp, 5m)
| render timechart
```

## Next Steps

- **[Agent Development Guide](AGENT_DEVELOPMENT.md)** - Create custom agents
- **[Architecture Overview](ARCHITECTURE.md)** - Understand the system
- **[Troubleshooting](TROUBLESHOOTING.md)** - Common issues

---

**Questions?** [Open an issue](https://github.com/kody-w/CommunityRAPP/issues)
