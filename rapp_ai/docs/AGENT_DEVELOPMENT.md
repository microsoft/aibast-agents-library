# Agent Development Guide

Learn how to create custom AI agents for CommunityRAPP.

## Table of Contents

- [Overview](#overview)
- [Agent Basics](#agent-basics)
- [Creating Your First Agent](#creating-your-first-agent)
- [Agent Examples](#agent-examples)
- [Best Practices](#best-practices)
- [Testing & Debugging](#testing--debugging)
- [Deployment](#deployment)

## Overview

Agents are modular components that extend your AI assistant's capabilities. Each agent:
- Inherits from `BasicAgent`
- Defines its own function metadata (JSON schema)
- Implements custom logic in the `perform()` method
- Can access Azure storage, APIs, and other services

### When to Create an Agent

Create a custom agent when you need to:
- ✅ Access external APIs or services
- ✅ Perform specialized processing (data analysis, formatting)
- ✅ Integrate with enterprise systems (CRM, ERP, databases)
- ✅ Implement business logic specific to your organization
- ✅ Provide domain-specific knowledge or operations

## Agent Basics

### Agent Structure

```python
from agents.basic_agent import BasicAgent

class MyAgent(BasicAgent):
    def __init__(self):
        self.name = 'MyAgent'  # Function name for OpenAI
        self.metadata = {
            "name": self.name,
            "description": "What this agent does",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "string",
                        "description": "Description of parameter"
                    }
                },
                "required": ["param1"]
            }
        }
        super().__init__(self.name, self.metadata)

    def perform(self, **kwargs):
        """Execute agent logic."""
        param1 = kwargs.get('param1', '')
        # Your logic here
        return "Result as string"
```

### Metadata Schema

The metadata follows OpenAI function calling format:

```python
{
    "name": "agent_function_name",  # Must match self.name
    "description": "Clear description of what the agent does",
    "parameters": {
        "type": "object",
        "properties": {
            "parameter_name": {
                "type": "string|number|boolean|array|object",
                "description": "What this parameter does",
                "enum": ["option1", "option2"]  # Optional: restrict values
            }
        },
        "required": ["param1", "param2"]  # List of required parameters
    }
}
```

**Supported Types:**
- `string` - Text data
- `number` - Integers or floats
- `boolean` - True/False
- `array` - Lists
- `object` - Nested objects

## Creating Your First Agent

### Example: Weather Agent

Let's create an agent that fetches weather information:

**Step 1: Create file `agents/weather_agent.py`**

```python
from agents.basic_agent import BasicAgent
import requests
import os

class WeatherAgent(BasicAgent):
    def __init__(self):
        self.name = 'WeatherAgent'
        self.metadata = {
            "name": self.name,
            "description": "Get current weather information for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name (e.g., 'Seattle', 'London')"
                    },
                    "units": {
                        "type": "string",
                        "description": "Temperature units",
                        "enum": ["celsius", "fahrenheit"]
                    }
                },
                "required": ["city"]
            }
        }
        super().__init__(self.name, self.metadata)

    def perform(self, city="", units="celsius", **kwargs):
        """
        Fetch weather data from OpenWeatherMap API.

        Args:
            city (str): City name
            units (str): Temperature units (celsius or fahrenheit)

        Returns:
            str: Weather description
        """
        try:
            # Get API key from environment variable
            api_key = os.environ.get('OPENWEATHER_API_KEY')
            if not api_key:
                return "Error: OpenWeatherMap API key not configured"

            # Convert units for API
            api_units = "metric" if units == "celsius" else "imperial"

            # Make API request
            url = f"https://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": city,
                "appid": api_key,
                "units": api_units
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Extract relevant information
            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            description = data['weather'][0]['description']
            humidity = data['main']['humidity']

            unit_symbol = "°C" if units == "celsius" else "°F"

            result = f"""
Weather in {city}:
- Temperature: {temp}{unit_symbol} (feels like {feels_like}{unit_symbol})
- Conditions: {description}
- Humidity: {humidity}%
            """

            return result.strip()

        except requests.exceptions.RequestException as e:
            return f"Error fetching weather data: {str(e)}"
        except KeyError as e:
            return f"Error parsing weather data: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
```

**Step 2: Add API key to configuration**

In `local.settings.json`:
```json
{
  "Values": {
    ...
    "OPENWEATHER_API_KEY": "your-api-key-here"
  }
}
```

And in Azure Portal → Function App → Configuration → Application Settings.

**Step 3: Install dependencies**

Add to `requirements.txt`:
```
requests==2.31.0
```

Run:
```bash
pip install -r requirements.txt
```

**Step 4: Test**

Restart your function app and ask:
> "What's the weather in Seattle?"

The AI will automatically call your WeatherAgent!

## Agent Examples

### Example 1: Database Query Agent

```python
from agents.basic_agent import BasicAgent
import pyodbc
import os

class DatabaseAgent(BasicAgent):
    def __init__(self):
        self.name = 'DatabaseAgent'
        self.metadata = {
            "name": self.name,
            "description": "Query the company database for customer information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query_type": {
                        "type": "string",
                        "description": "Type of query",
                        "enum": ["customer_info", "order_history", "product_search"]
                    },
                    "search_term": {
                        "type": "string",
                        "description": "Search term (customer ID, order ID, product name)"
                    }
                },
                "required": ["query_type", "search_term"]
            }
        }
        super().__init__(self.name, self.metadata)

    def perform(self, query_type="", search_term="", **kwargs):
        try:
            # Get connection string from environment
            conn_str = os.environ.get('SQL_CONNECTION_STRING')

            # Connect to database
            with pyodbc.connect(conn_str) as conn:
                cursor = conn.cursor()

                if query_type == "customer_info":
                    query = """
                    SELECT CustomerID, Name, Email, Phone
                    FROM Customers
                    WHERE CustomerID = ? OR Name LIKE ?
                    """
                    cursor.execute(query, (search_term, f"%{search_term}%"))

                elif query_type == "order_history":
                    query = """
                    SELECT OrderID, OrderDate, TotalAmount, Status
                    FROM Orders
                    WHERE CustomerID = ?
                    ORDER BY OrderDate DESC
                    """
                    cursor.execute(query, (search_term,))

                elif query_type == "product_search":
                    query = """
                    SELECT ProductID, ProductName, Price, StockQuantity
                    FROM Products
                    WHERE ProductName LIKE ?
                    """
                    cursor.execute(query, (f"%{search_term}%",))

                # Fetch results
                rows = cursor.fetchall()

                if not rows:
                    return f"No results found for {search_term}"

                # Format results
                result = []
                for row in rows:
                    result.append(" | ".join(str(col) for col in row))

                return "\n".join(result)

        except Exception as e:
            return f"Database error: {str(e)}"
```

### Example 2: File Analysis Agent

```python
from agents.basic_agent import BasicAgent
from utils.azure_file_storage import AzureFileStorageManager
import json
import csv
from io import StringIO

class FileAnalysisAgent(BasicAgent):
    def __init__(self):
        self.name = 'FileAnalysisAgent'
        self.metadata = {
            "name": self.name,
            "description": "Analyze CSV or JSON files from Azure storage",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_name": {
                        "type": "string",
                        "description": "Name of the file to analyze"
                    },
                    "analysis_type": {
                        "type": "string",
                        "description": "Type of analysis to perform",
                        "enum": ["summary", "statistics", "preview"]
                    }
                },
                "required": ["file_name", "analysis_type"]
            }
        }
        super().__init__(self.name, self.metadata)
        self.storage = AzureFileStorageManager()

    def perform(self, file_name="", analysis_type="", **kwargs):
        try:
            # Read file from Azure storage
            content = self.storage.read_file('data', file_name)
            if not content:
                return f"File '{file_name}' not found"

            # Determine file type and parse
            if file_name.endswith('.json'):
                data = json.loads(content)
                return self._analyze_json(data, analysis_type)
            elif file_name.endswith('.csv'):
                return self._analyze_csv(content, analysis_type)
            else:
                return "Unsupported file type. Only JSON and CSV are supported."

        except Exception as e:
            return f"Error analyzing file: {str(e)}"

    def _analyze_json(self, data, analysis_type):
        if analysis_type == "summary":
            if isinstance(data, list):
                return f"JSON array with {len(data)} items"
            elif isinstance(data, dict):
                return f"JSON object with {len(data)} keys: {', '.join(data.keys())}"
            else:
                return f"JSON value: {type(data).__name__}"

        elif analysis_type == "preview":
            return json.dumps(data, indent=2)[:500] + "..."

        # Add more analysis types as needed

    def _analyze_csv(self, content, analysis_type):
        reader = csv.DictReader(StringIO(content))
        rows = list(reader)

        if analysis_type == "summary":
            return f"CSV file with {len(rows)} rows and {len(rows[0])} columns: {', '.join(rows[0].keys())}"

        elif analysis_type == "preview":
            preview = "\n".join([str(row) for row in rows[:5]])
            return f"First 5 rows:\n{preview}"

        elif analysis_type == "statistics":
            # Calculate basic statistics for numeric columns
            stats = {}
            for column in rows[0].keys():
                try:
                    values = [float(row[column]) for row in rows if row[column]]
                    stats[column] = {
                        "min": min(values),
                        "max": max(values),
                        "avg": sum(values) / len(values)
                    }
                except ValueError:
                    stats[column] = "Non-numeric"

            return json.dumps(stats, indent=2)
```

### Example 3: Notification Agent

```python
from agents.basic_agent import BasicAgent
import requests
import os

class NotificationAgent(BasicAgent):
    def __init__(self):
        self.name = 'NotificationAgent'
        self.metadata = {
            "name": self.name,
            "description": "Send notifications via email or Teams",
            "parameters": {
                "type": "object",
                "properties": {
                    "channel": {
                        "type": "string",
                        "description": "Notification channel",
                        "enum": ["email", "teams", "sms"]
                    },
                    "recipient": {
                        "type": "string",
                        "description": "Recipient email, Teams webhook URL, or phone number"
                    },
                    "message": {
                        "type": "string",
                        "description": "Message content"
                    },
                    "priority": {
                        "type": "string",
                        "description": "Message priority",
                        "enum": ["low", "medium", "high"],
                        "default": "medium"
                    }
                },
                "required": ["channel", "recipient", "message"]
            }
        }
        super().__init__(self.name, self.metadata)

    def perform(self, channel="", recipient="", message="", priority="medium", **kwargs):
        try:
            if channel == "email":
                return self._send_email(recipient, message, priority)
            elif channel == "teams":
                return self._send_teams(recipient, message, priority)
            elif channel == "sms":
                return self._send_sms(recipient, message, priority)
            else:
                return f"Unsupported channel: {channel}"

        except Exception as e:
            return f"Error sending notification: {str(e)}"

    def _send_email(self, recipient, message, priority):
        # Use SendGrid, Azure Communication Services, or Office 365
        api_key = os.environ.get('SENDGRID_API_KEY')
        # Implementation here
        return f"Email sent to {recipient}"

    def _send_teams(self, webhook_url, message, priority):
        # Send to Teams webhook
        payload = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "summary": "Notification from Copilot Agent",
            "themeColor": "0078D4" if priority != "high" else "FF0000",
            "sections": [{
                "activityTitle": f"Priority: {priority.upper()}",
                "text": message
            }]
        }

        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()

        return "Teams notification sent successfully"

    def _send_sms(self, phone, message, priority):
        # Use Twilio or Azure Communication Services
        # Implementation here
        return f"SMS sent to {phone}"
```

## Best Practices

### 1. Error Handling

Always handle errors gracefully:

```python
def perform(self, **kwargs):
    try:
        # Your logic
        result = do_something()
        return result
    except SpecificException as e:
        return f"Specific error occurred: {str(e)}"
    except Exception as e:
        logging.error(f"Unexpected error in {self.name}: {str(e)}")
        return f"An error occurred. Please try again later."
```

### 2. Input Validation

Validate inputs before processing:

```python
def perform(self, email="", **kwargs):
    # Validate email format
    import re
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(email_pattern, email):
        return "Invalid email format"

    # Continue with logic
    ...
```

### 3. Timeouts

Set timeouts for external calls:

```python
import requests

response = requests.get(url, timeout=10)  # 10 second timeout
```

### 4. Logging

Use logging for debugging:

```python
import logging

def perform(self, **kwargs):
    logging.info(f"{self.name} called with: {kwargs}")
    # Your logic
    logging.debug(f"Processing completed successfully")
    return result
```

### 5. Documentation

Document your agent thoroughly:

```python
class MyAgent(BasicAgent):
    """
    MyAgent provides X functionality for Y use case.

    This agent connects to Z service and performs ABC operations.

    Environment Variables Required:
        - API_KEY: Service API key
        - ENDPOINT_URL: Service endpoint

    Example Usage:
        User: "Do X with Y"
        Agent: Calls MyAgent with parameters
    """

    def perform(self, param1="", param2="", **kwargs):
        """
        Execute the agent logic.

        Args:
            param1 (str): Description of param1
            param2 (int): Description of param2
            **kwargs: Additional parameters

        Returns:
            str: Result description

        Raises:
            ValueError: If parameters are invalid
            RequestException: If API call fails
        """
```

### 6. Security

- Never hardcode credentials
- Use environment variables or Azure Key Vault
- Validate and sanitize all inputs
- Implement rate limiting for external APIs

```python
import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

def get_secret(secret_name):
    """Retrieve secret from Azure Key Vault."""
    vault_url = os.environ.get('KEY_VAULT_URL')
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=vault_url, credential=credential)
    return client.get_secret(secret_name).value
```

## Testing & Debugging

### Local Testing

**Option 1: Direct Testing**

Create a test file `test_my_agent.py`:

```python
from agents.my_agent import MyAgent

# Initialize agent
agent = MyAgent()

# Test with sample data
result = agent.perform(
    param1="test value",
    param2=123
)

print(result)
```

Run:
```bash
python test_my_agent.py
```

**Option 2: Integration Testing**

Test with the full function app:

```bash
# Start function app
func start

# In another terminal, send test request
curl -X POST http://localhost:7071/api/businessinsightbot_function \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Test my agent with X", "conversation_history": []}'
```

### Debugging

**Enable Debug Logging:**

In `local.settings.json`:
```json
{
  "Values": {
    "LOGGING_LEVEL": "DEBUG"
  }
}
```

**Add Debug Statements:**

```python
import logging

def perform(self, **kwargs):
    logging.debug(f"Agent {self.name} called")
    logging.debug(f"Parameters: {kwargs}")

    # Your logic
    result = process_data()

    logging.debug(f"Result: {result}")
    return result
```

**Test in Azure Portal:**

1. Go to Function App → Functions → businessinsightbot_function
2. Click "Code + Test"
3. Use "Test/Run" to send test requests
4. View logs in "Logs" panel

## Deployment

### Deploy to Local Development

1. **Create agent file**: `agents/my_agent.py`
2. **Restart function**: `func start`
3. **Test**: Agent auto-loads on startup

### Deploy to Azure Storage

For dynamic agent updates without redeployment:

```python
from utils.azure_file_storage import AzureFileStorageManager

# Upload agent to Azure storage
storage = AzureFileStorageManager()

with open('agents/my_agent.py', 'r') as f:
    content = f.read()

storage.write_file('agents', 'my_agent.py', content)
```

Or use Azure Portal:
1. Storage Account → File shares → `agents`
2. Upload `my_agent.py`
3. Restart Function App

### Deploy with Function App

To include in function app deployment:

```bash
# Ensure agent is in agents/ folder
ls agents/my_agent.py

# Deploy to Azure
func azure functionapp publish YOUR-FUNCTION-APP-NAME
```

## Next Steps

- **[Architecture Guide](ARCHITECTURE.md)** - Understand the system
- **[API Reference](API_REFERENCE.md)** - API documentation
- **[Troubleshooting](TROUBLESHOOTING.md)** - Common issues

---

**Need help?** [Join the discussion](https://github.com/kody-w/CommunityRAPP/discussions)
