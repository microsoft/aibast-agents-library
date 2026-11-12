from agents.basic_agent import BasicAgent
import json
import requests
import os
from typing import Optional, Dict, List, Any

class ServiceNowAgent(BasicAgent):
    def __init__(self):
        self.name = "ServiceNow"
        self.metadata = {
            "name": self.name,
            "description": "Performs CRUD (Create, Read, Update, Delete) operations on a ServiceNow instance.",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "description": "The operation to perform on ServiceNow: 'create', 'read', 'update', or 'delete'.",
                        "enum": ["create", "read", "update", "delete"]
                    },
                    "table": {
                        "type": "string",
                        "description": "The ServiceNow table to operate on (e.g., 'incident', 'problem', 'change_request', etc.)."
                    },
                    "record_id": {
                        "type": "string",
                        "description": "For read, update, and delete operations, the sys_id of the record to operate on."
                    },
                    "query_params": {
                        "type": "object",
                        "description": "For read operations, query parameters to filter results (e.g., {'active': 'true', 'priority': '1'})."
                    },
                    "fields": {
                        "type": "object",
                        "description": "For create and update operations, the fields to set on the record."
                    },
                    "limit": {
                        "type": "integer",
                        "description": "For read operations, the maximum number of records to return."
                    }
                },
                "required": ["operation", "table"]
            }
        }
        
        # Get ServiceNow credentials from environment variables
        self.instance_url = os.environ.get('SERVICENOW_INSTANCE_URL', '')
        self.username = os.environ.get('SERVICENOW_USERNAME', '')
        self.password = os.environ.get('SERVICENOW_PASSWORD', '')
        
        if not all([self.instance_url, self.username, self.password]):
            self.credentials_available = False
        else:
            self.credentials_available = True
            
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        """
        Performs CRUD operations on a ServiceNow instance.
        
        Args:
            operation: The operation to perform (create, read, update, delete)
            table: The ServiceNow table to operate on
            record_id: For read, update, and delete operations, the sys_id of the record
            query_params: For read operations, query parameters to filter results
            fields: For create and update operations, the fields to set on the record
            limit: For read operations, the maximum number of records to return
            
        Returns:
            str: JSON string with the result of the operation
        """
        operation = kwargs.get('operation')
        table = kwargs.get('table')
        record_id = kwargs.get('record_id', '')
        query_params = kwargs.get('query_params', {})
        fields = kwargs.get('fields', {})
        limit = kwargs.get('limit', 10)
        
        if not self.credentials_available:
            return json.dumps({
                "status": "error",
                "message": "ServiceNow credentials not configured. Please set SERVICENOW_INSTANCE_URL, SERVICENOW_USERNAME, and SERVICENOW_PASSWORD environment variables."
            })
        
        if not operation:
            return json.dumps({
                "status": "error",
                "message": "Operation parameter is required. Use 'create', 'read', 'update', or 'delete'."
            })
            
        if not table:
            return json.dumps({
                "status": "error",
                "message": "Table parameter is required."
            })
        
        # Basic validation for required parameters based on operation
        if operation in ['update', 'delete'] and not record_id:
            return json.dumps({
                "status": "error",
                "message": f"record_id parameter is required for {operation} operations."
            })
            
        if operation == 'create' and not fields:
            return json.dumps({
                "status": "error",
                "message": "fields parameter is required for create operations."
            })
            
        if operation == 'update' and not fields:
            return json.dumps({
                "status": "error",
                "message": "fields parameter is required for update operations."
            })
        
        try:
            if operation == 'create':
                return self._create_record(table, fields)
            elif operation == 'read':
                return self._read_records(table, record_id, query_params, limit)
            elif operation == 'update':
                return self._update_record(table, record_id, fields)
            elif operation == 'delete':
                return self._delete_record(table, record_id)
            else:
                return json.dumps({
                    "status": "error",
                    "message": f"Unsupported operation: {operation}. Use 'create', 'read', 'update', or 'delete'."
                })
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": f"An error occurred: {str(e)}"
            })
    
    def _get_headers(self):
        """Returns the headers required for ServiceNow REST API calls"""
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def _create_record(self, table, fields):
        """Creates a record in the specified ServiceNow table"""
        url = f"{self.instance_url}/api/now/table/{table}"
        
        response = requests.post(
            url,
            auth=(self.username, self.password),
            headers=self._get_headers(),
            json=fields
        )
        
        if response.status_code == 201:
            return json.dumps({
                "status": "success",
                "message": f"Record created successfully in table '{table}'",
                "data": response.json()
            })
        else:
            return json.dumps({
                "status": "error",
                "message": f"Failed to create record. Status code: {response.status_code}",
                "response": response.text[:1000]
            })
    
    def _read_records(self, table, record_id, query_params, limit):
        """Reads records from the specified ServiceNow table"""
        if record_id:
            # Get a specific record by sys_id
            url = f"{self.instance_url}/api/now/table/{table}/{record_id}"
            
            response = requests.get(
                url,
                auth=(self.username, self.password),
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                return json.dumps({
                    "status": "success",
                    "message": f"Record retrieved successfully from table '{table}'",
                    "data": response.json()
                })
            else:
                return json.dumps({
                    "status": "error",
                    "message": f"Failed to retrieve record. Status code: {response.status_code}",
                    "response": response.text[:1000]
                })
        else:
            # Query for records based on query parameters
            url = f"{self.instance_url}/api/now/table/{table}"
            
            # Convert query_params to sysparm_query format
            query_string = ""
            if query_params:
                query_parts = []
                for key, value in query_params.items():
                    query_parts.append(f"{key}={value}")
                query_string = "^".join(query_parts)
            
            params = {
                "sysparm_limit": limit
            }
            
            if query_string:
                params["sysparm_query"] = query_string
            
            response = requests.get(
                url,
                auth=(self.username, self.password),
                headers=self._get_headers(),
                params=params
            )
            
            if response.status_code == 200:
                results = response.json().get('result', [])
                return json.dumps({
                    "status": "success",
                    "message": f"Retrieved {len(results)} records from table '{table}'",
                    "data": response.json()
                })
            else:
                return json.dumps({
                    "status": "error",
                    "message": f"Failed to query records. Status code: {response.status_code}",
                    "response": response.text[:1000]
                })
    
    def _update_record(self, table, record_id, fields):
        """Updates a record in the specified ServiceNow table"""
        url = f"{self.instance_url}/api/now/table/{table}/{record_id}"
        
        response = requests.patch(
            url,
            auth=(self.username, self.password),
            headers=self._get_headers(),
            json=fields
        )
        
        if response.status_code == 200:
            return json.dumps({
                "status": "success",
                "message": f"Record updated successfully in table '{table}'",
                "data": response.json()
            })
        else:
            return json.dumps({
                "status": "error",
                "message": f"Failed to update record. Status code: {response.status_code}",
                "response": response.text[:1000]
            })
    
    def _delete_record(self, table, record_id):
        """Deletes a record from the specified ServiceNow table"""
        url = f"{self.instance_url}/api/now/table/{table}/{record_id}"
        
        response = requests.delete(
            url,
            auth=(self.username, self.password),
            headers=self._get_headers()
        )
        
        if response.status_code == 204:
            return json.dumps({
                "status": "success",
                "message": f"Record deleted successfully from table '{table}'"
            })
        else:
            return json.dumps({
                "status": "error",
                "message": f"Failed to delete record. Status code: {response.status_code}",
                "response": response.text[:1000]
            })
