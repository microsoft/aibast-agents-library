import json
import os
import requests
import time
from urllib.parse import quote_plus
from agents.basic_agent import BasicAgent

class Dynamics365CRUDAgent(BasicAgent):
    def __init__(self):
        self.name = "Dynamics365CRUD"
        self.metadata = {
            "name": self.name,
            "description": "Performs CRUD operations with Dynamics 365 Web API.",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "description": "The CRUD operation to perform. Must be one of: create, read, update, delete, query.",
                        "enum": ["create", "read", "update", "delete", "query"]
                    },
                    "entity": {
                        "type": "string",
                        "description": "The entity to perform the operation on. Examples: accounts, contacts, leads, or custom entities. Use plural form (e.g., 'contacts' not 'contact')."
                    },
                    "data": {
                        "type": "string",
                        "description": "JSON string containing data for create and update operations. For create, include all required fields. For update, include only fields to be updated."
                    },
                    "record_id": {
                        "type": "string",
                        "description": "The unique identifier (GUID) of the record for read, update, or delete operations. Required for these operations."
                    },
                    "fetchxml": {
                        "type": "string",
                        "description": "The FetchXML query string for complex read or query operations. Required for 'query' operation. Must be a single-line string without newlines or extra spaces."
                    },
                    "select": {
                        "type": "string",
                        "description": "Comma-separated list of attributes to return in the query results. Use with read or query operations to limit returned fields."
                    }
                },
                "required": ["operation", "entity"]
            }
        }
        super().__init__(name=self.name, metadata=self.metadata)

        # Load configuration from environment variables
        self.client_id = os.environ.get('DYNAMICS_365_CLIENT_ID')
        self.client_secret = os.environ.get('DYNAMICS_365_CLIENT_SECRET')
        self.tenant_id = os.environ.get('DYNAMICS_365_TENANT_ID')
        self.resource = os.environ.get('DYNAMICS_365_RESOURCE')

        self.token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        self.access_token = None
        self.max_retries = 3
        self.retry_delay = 5

    def authenticate(self):
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': f'{self.resource}/.default',
            'grant_type': 'client_credentials'
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        response = requests.post(self.token_url, data=data, headers=headers)
        response.raise_for_status()
        self.access_token = response.json().get('access_token')

    def construct_headers(self):
        if not self.access_token:
            self.authenticate()
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'OData-MaxVersion': '4.0',
            'OData-Version': '4.0',
            'Accept': 'application/json'
        }

    def perform(self, **kwargs):
        operation = kwargs.get('operation')
        entity = kwargs.get('entity')
        data = kwargs.get('data')
        record_id = kwargs.get('record_id')
        fetchxml = kwargs.get('fetchxml')
        select = kwargs.get('select')

        retries = 0
        while retries <= self.max_retries:
            try:
                return self._perform_operation(operation, entity, data, record_id, fetchxml, select)
            except requests.exceptions.RequestException as e:
                if retries == self.max_retries:
                    return json.dumps({"error": str(e)})
                else:
                    time.sleep(self.retry_delay)
                    retries += 1
            except Exception as e:
                return json.dumps({"error": str(e)})

    def _perform_operation(self, operation, entity, data=None, record_id=None, fetchxml=None, select=None):
        base_url = f"{self.resource}/api/data/v9.2/"
        headers = self.construct_headers()

        if operation == "create":
            url = f"{base_url}{entity}"
            response = requests.post(url, headers=headers, data=data)
            
            if response.status_code == 204:
                entity_url = response.headers.get('OData-EntityId')
                if entity_url:
                    guid = entity_url.split('(')[1].split(')')[0]
                    return json.dumps({"message": "Record created successfully", "guid": guid})
                else:
                    return json.dumps({"message": "Record created successfully, but GUID could not be extracted"})
        elif operation == "read":
            if not record_id:
                return json.dumps({"error": "Record ID is required for read operations"})
            url = f"{base_url}{entity}({record_id})"
            if select:
                url += f"?$select={select}"
            response = requests.get(url, headers=headers)
        elif operation == "update":
            if not record_id:
                return json.dumps({"error": "Record ID is required for update operations"})
            url = f"{base_url}{entity}({record_id})"
            response = requests.patch(url, headers=headers, data=data)
        elif operation == "delete":
            if not record_id:
                return json.dumps({"error": "Record ID is required for delete operations"})
            url = f"{base_url}{entity}({record_id})"
            response = requests.delete(url, headers=headers)
        elif operation == "query":
            if not fetchxml:
                return json.dumps({"error": "FetchXML is required for query operations"})
            encoded_fetchxml = quote_plus(fetchxml)
            url = f"{base_url}{entity}?fetchXml={encoded_fetchxml}"
            if select:
                url += f"&$select={select}"
            response = requests.get(url, headers=headers)
        else:
            return json.dumps({"error": "Unsupported operation"})

        if response.status_code not in [200, 204]:
            return json.dumps({"error": f"Request failed with status code {response.status_code}", "details": response.text})

        result = response.json() if response.content else {"message": "Operation successful."}
        result_str = json.dumps(result)
        
        if len(result_str) > 20000:
            return json.dumps({"message": "Response too large. Please use a more specific query or fewer fields."})
        else:
            return result_str