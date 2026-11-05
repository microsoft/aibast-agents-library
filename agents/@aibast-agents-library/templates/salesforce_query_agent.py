from agents.basic_agent import BasicAgent
import json
import requests
import logging
import os

class SalesforceQueryAgent(BasicAgent):
    def __init__(self):
        self.name = "SalesforceQuery"
        self.metadata = {
            "name": self.name,
            "description": "Executes a SOQL query in Salesforce to retrieve data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "soql": {
                        "type": "string",
                        "description": "The SOQL query to execute (e.g., 'SELECT Id, Name FROM Account LIMIT 5')"
                    }
                },
                "required": ["soql"]
            }
        }
        super().__init__(name=self.name, metadata=self.metadata)
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Get the flow URL from environment variables or use a default
        self.flow_url = os.environ.get(
            'SALESFORCE_FLOW_URL', 
            "https://prod-90.westus.logic.azure.com:443/workflows/e6a4ec203d3542dda8391c6778c4b42d/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=rKbMzTF7TfAcILp5lh1fzNSpoQJpaMzWsqxH-3P8klo"
        )

    def perform(self, soql):
        try:
            if not soql:
                self.logger.error("No SOQL query provided")
                return "Error: SOQL query is required"
                
            self.logger.info(f"Executing SOQL query: {soql}")
            
            # Send the SOQL query to the Power Automate flow
            payload = {
                "soql": soql
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            self.logger.info(f"Sending request to Power Automate flow with payload: {json.dumps(payload)}")
            response = requests.post(
                self.flow_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            self.logger.info(f"Power Automate response status: {response.status_code}")
            
            if response.status_code != 200:
                error_message = f"Power Automate flow execution failed with status code {response.status_code}"
                self.logger.error(error_message)
                return error_message
            
            try:
                result = response.json()
                
                # Check if it's an error response from Salesforce
                if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
                    if "errorCode" in result[0]:
                        error_message = f"Salesforce error: {result[0].get('message', 'Unknown error')} (Error code: {result[0].get('errorCode')})"
                        self.logger.error(error_message)
                        return error_message
                
                # Format the results in a readable string
                if isinstance(result, list) and len(result) > 0:
                    record_count = len(result)
                    formatted_result = f"Query returned {record_count} records. "
                    
                    # Add sample of results (first few records)
                    sample_size = min(3, record_count)
                    if sample_size > 0:
                        sample_records = result[:sample_size]
                        formatted_result += "Sample records:\n"
                        for i, record in enumerate(sample_records):
                            formatted_result += f"Record {i+1}: {json.dumps(record)}\n"
                    
                    # If there are more records than shown in the sample
                    if record_count > sample_size:
                        formatted_result += f"...and {record_count - sample_size} more records."
                    
                    # Add full JSON for the assistant to parse
                    formatted_result += f"\n\nFull result: {json.dumps(result)}"
                    return formatted_result
                elif isinstance(result, dict):
                    return f"Query result: {json.dumps(result)}"
                else:
                    return f"Query executed successfully. Result: {json.dumps(result)}"
                
            except json.JSONDecodeError as e:
                error_message = f"Invalid JSON response from Power Automate: {str(e)}"
                self.logger.error(error_message)
                return error_message
            
        except requests.exceptions.RequestException as e:
            error_message = f"Failed to communicate with Power Automate flow: {str(e)}"
            self.logger.error(error_message)
            return error_message
            
        except Exception as e:
            error_message = f"Unexpected error occurred: {str(e)}"
            self.logger.error(error_message)
            return error_message
