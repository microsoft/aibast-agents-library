from agents.basic_agent import BasicAgent
import json
import datetime
import logging
import importlib
import sys

class Dynamics365DemoDataSeederAgent(BasicAgent):
    def __init__(self):
        self.name = "Dynamics365DemoDataSeeder"  # Removed "Agent" suffix to match naming convention
        self.metadata = {
            "name": self.name,
            "description": (
                "Seeds all required demo entities into Dynamics 365 (accounts, contacts, opportunities/leads, tasks) "
                "for consistent repeatable demo runs. Uses Dynamics365CRUD agent as backend."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "dynamics_crud_agent_name": {
                        "type": "string",
                        "description": "Name of the Dynamics 365 CRUD agent to use. Defaults to 'Dynamics365CRUD'."
                    }
                },
                "required": []
            }
        }
        super().__init__(name=self.name, metadata=self.metadata)
        self.dynamics_crud = None

    def _get_dynamics_crud_agent(self, agent_name="Dynamics365CRUD"):
        """
        Attempts to get the Dynamics 365 CRUD agent instance from the Assistant's known agents.
        
        Based on the application structure in function_app.py, this method accesses the Assistant
        singleton instance to retrieve the agent from its known_agents dictionary.
        
        Returns None if the agent cannot be found.
        """
        try:
            # Import the Assistant class from the parent module
            # Relative import to avoid full path dependency
            from function_app import Assistant
            
            # Get the singleton instance of Assistant
            # Since Assistant uses the singleton pattern with _instance class variable
            assistant = Assistant._instance
            
            # If we have a valid Assistant instance, access its known_agents
            if assistant and hasattr(assistant, 'known_agents'):
                agent = assistant.known_agents.get(agent_name)
                if agent:
                    logging.info(f"Successfully retrieved {agent_name} from Assistant.known_agents")
                    return agent
            
            logging.warning(f"Could not find {agent_name} in Assistant.known_agents")
            return None
        except Exception as e:
            logging.error(f"Error getting Dynamics CRUD agent: {str(e)}")
            return None

    def perform(self, **kwargs):
        """
        Seeds demo data into Dynamics 365 by calling the CRUD agent.
        
        Args:
            dynamics_crud_agent_name (str, optional): Name of the Dynamics 365 CRUD agent to use.
                Defaults to "Dynamics365CRUD".
                
        Returns:
            str: JSON string with IDs of created entities or error message
        """
        # Get the Dynamics CRUD agent
        dynamics_crud_agent_name = kwargs.get("dynamics_crud_agent_name", "Dynamics365CRUD")
        self.dynamics_crud = self._get_dynamics_crud_agent(dynamics_crud_agent_name)
        
        if not self.dynamics_crud:
            # Return a structured JSON response with error information
            error_msg = {
                "error": f"Agent '{dynamics_crud_agent_name}' not found",
                "status": "incomplete",
                "message": f"Could not find or initialize {dynamics_crud_agent_name}. Please ensure it is available in the system before running this agent.",
                "required_agent": dynamics_crud_agent_name
            }
            return json.dumps(error_msg)
        
        try:
            # 1. Create Accounts (or ensure they exist)
            accounts = [
                {"name": "Relecloud"},
                {"name": "Alpine Ski House"},
                {"name": "Proseware"},
                {"name": "Tailwind Traders"},
            ]
            account_ids = {}
            for acc in accounts:
                resp = self.dynamics_crud.perform(operation="create", entity="accounts", data=json.dumps(acc))
                res_json = json.loads(resp)
                account_ids[acc['name']] = res_json.get('guid', None)

            # 2. Create Contacts/Decision Makers (for Alpine, Relecloud)
            contacts = [
                {"firstname": "Priya", "lastname": "Patel", "emailaddress1": "priya.patel@relecloud.com", "parentcustomerid_account@odata.bind": f"/accounts({account_ids['Relecloud']})"},
                {"firstname": "Alpine", "lastname": "DecisionMaker", "emailaddress1": "decision@alpineski.com", "parentcustomerid_account@odata.bind": f"/accounts({account_ids['Alpine Ski House']})"},
                {"firstname": "Alex", "lastname": "Baker", "emailaddress1": "alex.baker@tailwind.com", "parentcustomerid_account@odata.bind": f"/accounts({account_ids['Tailwind Traders']})"},
            ]
            contact_ids = {}
            for con in contacts:
                resp = self.dynamics_crud.perform(operation="create", entity="contacts", data=json.dumps(con))
                res_json = json.loads(resp)
                contact_ids[con['emailaddress1']] = res_json.get('guid', None)

            # 3. Create Opportunities with proper field names and error handling
            today = datetime.date.today()
            ops = [
                {
                    "name": "Relecloud Opportunity",
                    "parentaccountid@odata.bind": f"/accounts({account_ids['Relecloud']})",
                    "customerid_contact@odata.bind": f"/contacts({contact_ids['priya.patel@relecloud.com']})",
                    "estimatedvalue": 150000,
                    "estimatedclosedate": today.strftime("%Y-%m-%d"),  # Format date correctly
                    "statuscode": 1,  # Use numeric status code instead of text
                    "opportunityratingcode": 1  # Common required field
                },
                {
                    "name": "Alpine Ski House Opportunity",
                    "parentaccountid@odata.bind": f"/accounts({account_ids['Alpine Ski House']})",
                    "customerid_contact@odata.bind": f"/contacts({contact_ids['decision@alpineski.com']})",
                    "estimatedvalue": 75000,
                    "estimatedclosedate": (today + datetime.timedelta(days=10)).strftime("%Y-%m-%d"),
                    "statuscode": 1,
                    "opportunityratingcode": 2
                },
                {
                    "name": "Proseware Opportunity",
                    "parentaccountid@odata.bind": f"/accounts({account_ids['Proseware']})",
                    "estimatedvalue": 50000,
                    "estimatedclosedate": (today - datetime.timedelta(days=3)).strftime("%Y-%m-%d"),
                    "statuscode": 2,  # Different status
                    "opportunityratingcode": 3
                }
            ]
            op_ids = []
            opportunity_errors = []

            for op in ops:
                try:
                    logging.info(f"Creating opportunity: {op['name']}")
                    resp = self.dynamics_crud.perform(operation="create", entity="opportunities", data=json.dumps(op))
                    logging.info(f"Response from CRUD agent: {resp}")
                    
                    res_json = json.loads(resp)
                    if "error" in res_json:
                        logging.error(f"Error creating opportunity {op['name']}: {res_json['error']}")
                        opportunity_errors.append({
                            "name": op['name'],
                            "error": res_json.get('error', 'Unknown error'),
                            "details": res_json.get('details', '')
                        })
                        op_ids.append(None)
                    else:
                        guid = res_json.get('guid')
                        logging.info(f"Successfully created opportunity {op['name']} with GUID: {guid}")
                        op_ids.append(guid)
                except Exception as e:
                    logging.error(f"Exception creating opportunity {op['name']}: {str(e)}")
                    opportunity_errors.append({
                        "name": op['name'],
                        "error": str(e)
                    })
                    op_ids.append(None)

            # Include errors in the result for debugging
            result = {
                "accounts": account_ids,
                "contacts": contact_ids,
                "opportunities": op_ids
            }

            if opportunity_errors:
                result["opportunity_errors"] = opportunity_errors
                
            return json.dumps(result)
            
        except Exception as e:
            logging.error(f"Error in Dynamics365DemoDataSeederAgent: {str(e)}")
            return f"Error occurred while seeding Dynamics 365 data: {str(e)}"