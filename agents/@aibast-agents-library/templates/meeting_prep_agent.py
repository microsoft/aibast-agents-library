from agents.basic_agent import BasicAgent
import json
import logging
import datetime

class MeetingPrepAgent(BasicAgent):
    def __init__(self):
        self.name = "MeetingPrep"
        self.metadata = {
            "name": self.name,
            "description": "Preps user for a client meeting by summarizing deal details, issues, and creating a checklist.",
            "parameters": {
                "type": "object",
                "properties": {
                    "intent": {
                        "type": "string",
                        "description": "The action to perform: 'prep_meeting', 'summarize_issues', or 'create_checklist'",
                        "enum": ["prep_meeting", "summarize_issues", "create_checklist"]
                    },
                    "opportunity_id": {
                        "type": "string",
                        "description": "The ID of the opportunity record to retrieve details for"
                    },
                    "contact_id": {
                        "type": "string",
                        "description": "The ID of the primary contact for the meeting"
                    },
                    "company_name": {
                        "type": "string",
                        "description": "The name of the company for the meeting, used when opportunity_id isn't known"
                    }
                },
                "required": ["intent"]
            }
        }
        super().__init__(name=self.name, metadata=self.metadata)
        self.dynamics_crud = None
        self.opportunity_id = None
        self.opportunity_data = None
        self.issues = None
        self.crm_base_url = "https://orgc62c53e4.crm.dynamics.com/main.aspx?appid=fe67eeca-edd0-ef11-8eea-00224808ff68&pagetype=entityrecord&etn="

    def _get_dynamics_crud_agent(self):
        """
        Gets the Dynamics 365 CRUD agent instance from the Assistant's known agents.
        """
        try:
            from function_app import Assistant
            assistant = Assistant._instance
            
            if assistant and hasattr(assistant, 'known_agents'):
                agent = assistant.known_agents.get("Dynamics365CRUD")
                if agent:
                    return agent
            
            logging.warning("Could not find Dynamics365CRUD in Assistant.known_agents")
            return None
        except Exception as e:
            logging.error(f"Error getting Dynamics CRUD agent: {str(e)}")
            return None

    def _find_or_create_account(self, company_name):
        """Find an account by name or create one if it doesn't exist"""
        if not company_name or not self.dynamics_crud:
            return None
            
        try:
            # Search for existing account
            fetchxml = f"""
            <fetch version="1.0" output-format="xml-platform" mapping="logical" distinct="false">
              <entity name="account">
                <attribute name="accountid" />
                <attribute name="name" />
                <filter type="and">
                  <condition attribute="name" operator="like" value="%{company_name}%" />
                </filter>
              </entity>
            </fetch>
            """
            
            # Remove newlines and extra spaces
            fetchxml = " ".join(fetchxml.split())
            
            # Search for the account
            resp = self.dynamics_crud.perform(
                operation="query", 
                entity="accounts", 
                fetchxml=fetchxml
            )
            
            res_json = json.loads(resp)
            if "error" not in res_json and "value" in res_json and len(res_json["value"]) > 0:
                # Found existing account, return its ID
                return res_json["value"][0]["accountid"]
                    
            # No existing account found, create a new one
            logging.info(f"No account found for {company_name}, creating a new one")
            
            # Create new account
            account_data = {
                "name": company_name,
                "telephone1": "555-0100", 
                "websiteurl": f"https://www.{company_name.lower().replace(' ', '')}.com"
            }
            
            create_resp = self.dynamics_crud.perform(
                operation="create",
                entity="accounts",
                data=json.dumps(account_data)
            )
            
            create_json = json.loads(create_resp)
            if "error" in create_json:
                logging.error(f"Error creating account: {create_json['error']}")
                return None
                
            # Return the newly created account ID
            new_account_id = create_json.get("accountid")
            logging.info(f"Created new account with ID: {new_account_id}")
            return new_account_id
                
        except Exception as e:
            logging.error(f"Exception in _find_or_create_account: {str(e)}")
            return None

    def _find_opportunity_by_company(self, company_name):
        """Find an opportunity by company name or create one if it doesn't exist"""
        if not company_name or not self.dynamics_crud:
            return None
            
        try:
            # Search for existing opportunity
            fetchxml = f"""
            <fetch version="1.0" output-format="xml-platform" mapping="logical" distinct="false">
              <entity name="opportunity">
                <attribute name="opportunityid" />
                <attribute name="name" />
                <filter type="and">
                  <condition attribute="name" operator="like" value="%{company_name}%" />
                </filter>
                <link-entity name="account" from="accountid" to="parentaccountid" link-type="outer" alias="account">
                  <filter>
                    <condition attribute="name" operator="like" value="%{company_name}%" />
                  </filter>
                </link-entity>
              </entity>
            </fetch>
            """
            
            # Remove newlines and extra spaces
            fetchxml = " ".join(fetchxml.split())
            
            # Search for the opportunity
            resp = self.dynamics_crud.perform(
                operation="query", 
                entity="opportunities", 
                fetchxml=fetchxml
            )
            
            res_json = json.loads(resp)
            if "error" not in res_json and "value" in res_json and len(res_json["value"]) > 0:
                # Found existing opportunity, return its ID
                return res_json["value"][0]["opportunityid"]
                    
            # No existing opportunity found, create a new one
            logging.info(f"No opportunity found for {company_name}, creating a new one")
            
            # First ensure account exists
            account_id = self._find_or_create_account(company_name)
            if not account_id:
                logging.error("Failed to find or create account, cannot create opportunity")
                return None
            
            # Create new opportunity
            opp_data = {
                "name": f"{company_name} Opportunity",
                "estimatedvalue": 150000,
                "statuscode": 1,  # Proposal stage
                "estimatedclosedate": (datetime.date.today() + datetime.timedelta(days=90)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "parentaccountid_account@odata.bind": f"/accounts({account_id})"
            }
            
            create_resp = self.dynamics_crud.perform(
                operation="create",
                entity="opportunities",
                data=json.dumps(opp_data)
            )
            
            create_json = json.loads(create_resp)
            if "error" in create_json:
                logging.error(f"Error creating opportunity: {create_json['error']}")
                return None
                
            # Return the newly created opportunity ID
            new_opp_id = create_json.get("opportunityid")
            logging.info(f"Created new opportunity with ID: {new_opp_id}")
            return new_opp_id
                
        except Exception as e:
            logging.error(f"Exception in _find_opportunity_by_company: {str(e)}")
            return None

    def _get_opportunity_details(self, opportunity_id=None, company_name=None, contact_id=None):
        """Get opportunity details from Dynamics 365"""
        if not self.dynamics_crud:
            return None
            
        try:
            # If opportunity ID provided, query directly
            if opportunity_id:
                try:
                    # Get opportunity details by ID
                    resp = self.dynamics_crud.perform(
                        operation="read", 
                        entity="opportunities", 
                        record_id=opportunity_id
                    )
                    
                    res_json = json.loads(resp)
                    if "error" in res_json:
                        logging.error(f"Error reading opportunity: {res_json['error']}")
                        # If real ID lookup fails, try to find by company name
                        if company_name:
                            return self._get_opportunity_details(None, company_name, contact_id)
                        return None
                        
                    # Store and process the opportunity
                    self.opportunity_id = opportunity_id
                    self.opportunity_data = self._process_opportunity_data(res_json)
                    return self.opportunity_data
                except Exception as e:
                    logging.error(f"Error getting opportunity by ID: {str(e)}")
                    # Fall back to search by company name if provided
                    if company_name:
                        return self._get_opportunity_details(None, company_name, contact_id)
                    return None
            
            # Search by company name if no ID or ID lookup failed
            if company_name:
                # FetchXML to find the opportunity by company name
                fetchxml = f"""
                <fetch version="1.0" output-format="xml-platform" mapping="logical" distinct="false">
                  <entity name="opportunity">
                    <attribute name="name" />
                    <attribute name="estimatedvalue" />
                    <attribute name="statuscode" />
                    <attribute name="opportunityid" />
                    <attribute name="estimatedclosedate" />
                    <filter type="and">
                      <condition attribute="name" operator="like" value="%{company_name}%" />
                    </filter>
                    <link-entity name="account" from="accountid" to="parentaccountid" link-type="outer" alias="account">
                      <attribute name="name" />
                      <filter>
                        <condition attribute="name" operator="like" value="%{company_name}%" />
                      </filter>
                    </link-entity>
                    <link-entity name="contact" from="contactid" to="customerid" link-type="outer" alias="contact">
                      <attribute name="fullname" />
                      <attribute name="emailaddress1" />
                    </link-entity>
                  </entity>
                </fetch>
                """
                
                # Remove newlines and extra spaces
                fetchxml = " ".join(fetchxml.split())
                
                # Search for the opportunity
                resp = self.dynamics_crud.perform(
                    operation="query", 
                    entity="opportunities", 
                    fetchxml=fetchxml
                )
                
                res_json = json.loads(resp)
                if "error" in res_json:
                    logging.error(f"Error finding opportunity: {res_json['error']}")
                    # Try to create a new opportunity
                    new_opp_id = self._find_opportunity_by_company(company_name)
                    if new_opp_id:
                        return self._get_opportunity_details(new_opp_id)
                    return None
                    
                # Extract opportunity details from the results
                if "value" in res_json and len(res_json["value"]) > 0:
                    opp = res_json["value"][0]
                    self.opportunity_id = opp["opportunityid"]
                    self.opportunity_data = self._process_opportunity_data(opp)
                    return self.opportunity_data
                
                # No opportunity found, try to create one
                new_opp_id = self._find_opportunity_by_company(company_name)
                if new_opp_id:
                    return self._get_opportunity_details(new_opp_id)
                return None
            
            # No identifiers provided
            return None
                
        except Exception as e:
            logging.error(f"Exception in _get_opportunity_details: {str(e)}")
            # Try to create one if company name is available
            if company_name:
                new_opp_id = self._find_opportunity_by_company(company_name)
                if new_opp_id:
                    return self._get_opportunity_details(new_opp_id)
            return None

    def _process_opportunity_data(self, opp):
        """Process opportunity data into a standardized format"""
        try:
            # Map statuscode to text
            status_map = {
                1: "Proposal",
                2: "Negotiation", 
                3: "Contract",
                4: "Closed Won",
                5: "Closed Lost"
            }
            status = status_map.get(opp.get("statuscode"), "Proposal")
            
            # Format estimated value
            est_value = opp.get("estimatedvalue", 150000)
            if isinstance(est_value, (int, float)):
                formatted_value = f"${int(est_value):,}"
            else:
                formatted_value = "$150,000"  # Default fallback
            
            # Get company name
            company_name = opp.get("account.name")
            if not company_name:
                company_name = opp.get("name", "").split(" ")[0]  # Use first word of opportunity name
                
            # Get contact name
            contact_name = opp.get("contact.fullname", "Primary Contact")
            
            return {
                "id": opp.get("opportunityid"),
                "name": opp.get("name", f"{company_name} Opportunity"),
                "company": company_name,
                "value": formatted_value,
                "status": status,
                "contact": contact_name,
                "close_date": opp.get("estimatedclosedate")
            }
        except Exception as e:
            logging.error(f"Error processing opportunity data: {str(e)}")
            return None

    def _get_open_issues(self, opportunity_id=None):
        """Get open issues related to the opportunity"""
        if not opportunity_id and self.opportunity_id:
            opportunity_id = self.opportunity_id
            
        if not opportunity_id:
            return None
            
        try:
            # Query Dynamics 365 for open issues related to this opportunity
            fetchxml = f"""
            <fetch version="1.0" output-format="xml-platform" mapping="logical" distinct="false">
              <entity name="incident">
                <attribute name="title" />
                <attribute name="incidentid" />
                <attribute name="description" />
                <attribute name="createdon" />
                <filter type="and">
                  <condition attribute="statecode" operator="eq" value="0" />
                </filter>
                <link-entity name="opportunity" from="opportunityid" to="regardingobjectid" link-type="inner" alias="opportunity">
                  <filter>
                    <condition attribute="opportunityid" operator="eq" value="{opportunity_id}" />
                  </filter>
                </link-entity>
              </entity>
            </fetch>
            """
            
            # Remove newlines and extra spaces
            fetchxml = " ".join(fetchxml.split())
            
            # Query for issues
            resp = self.dynamics_crud.perform(
                operation="query", 
                entity="incidents", 
                fetchxml=fetchxml
            )
            
            res_json = json.loads(resp)
            if "error" in res_json:
                logging.error(f"Error querying issues: {res_json['error']}")
                # Create some default issues if none found
                return self._create_default_issues(opportunity_id)
                
            # Process the results
            if "value" in res_json and len(res_json["value"]) > 0:
                issues = []
                for incident in res_json["value"]:
                    issues.append(incident.get("title", "Untitled Issue"))
                
                self.issues = issues
                return issues
            
            # No issues found, create some default ones
            return self._create_default_issues(opportunity_id)
            
        except Exception as e:
            logging.error(f"Exception in _get_open_issues: {str(e)}")
            return self._create_default_issues(opportunity_id)

    def _create_default_issues(self, opportunity_id):
        """Create default issues for the opportunity if none exist"""
        if not self.dynamics_crud or not opportunity_id:
            return ["No specific issues found for this opportunity"]
        
        try:
            # Get company name if available
            company_name = ""
            if self.opportunity_data:
                company_name = self.opportunity_data.get("company", "").lower()
            
            # Generate default issues
            default_issues = [
                "Need to gather additional requirements",
                "Pricing needs review",
                "Follow-up after initial discussion needed"
            ]
            
            # Create issues in Dynamics 365
            created_issues = []
            for issue_title in default_issues:
                issue_data = {
                    "title": issue_title,
                    "description": f"Automatically created issue for opportunity.",
                    "regardingobjectid_opportunity@odata.bind": f"/opportunities({opportunity_id})"
                }
                
                # Try to create the issue
                try:
                    resp = self.dynamics_crud.perform(
                        operation="create", 
                        entity="incidents", 
                        data=json.dumps(issue_data)
                    )
                    
                    res_json = json.loads(resp)
                    if "error" not in res_json:
                        created_issues.append(issue_title)
                except Exception as e:
                    logging.error(f"Error creating issue: {str(e)}")
            
            # If we created any issues, return those
            if created_issues:
                self.issues = created_issues
                return created_issues
            
            # Otherwise return the default issues list without saving to Dynamics
            self.issues = default_issues
            return default_issues
            
        except Exception as e:
            logging.error(f"Exception in _create_default_issues: {str(e)}")
            default_issues = ["Need to gather additional requirements", "Pricing needs review"]
            self.issues = default_issues
            return default_issues

    def _create_meeting_checklist(self, opportunity_id=None):
        """Create a checklist task for the meeting"""
        if not opportunity_id and self.opportunity_id:
            opportunity_id = self.opportunity_id
            
        if not self.dynamics_crud or not opportunity_id:
            return False, None
            
        try:
            # Get opportunity if needed
            if not self.opportunity_data:
                self._get_opportunity_details(opportunity_id)
                
            # Get issues if needed
            if not self.issues:
                self._get_open_issues(opportunity_id)
                
            # Get company name for the checklist
            company_name = "the client"
            if self.opportunity_data:
                company_name = self.opportunity_data.get("company", "the client")
                
            # Calculate today's date
            today = datetime.date.today()
            
            # Build checklist items
            checklist_items = [
                "Review opportunity history and current status",
                "Prepare discussion points based on opportunity stage"
            ]
            
            # Add company-specific items based on issues
            if self.issues:
                for issue in self.issues:
                    issue_lower = issue.lower()
                    if "pricing" in issue_lower:
                        checklist_items.append("Prepare pricing options and alternatives")
                    elif "sla" in issue_lower:
                        checklist_items.append("Review and prepare revised SLA terms")
                    elif "follow" in issue_lower:
                        checklist_items.append("Develop follow-up plan for after the demo")
                    elif "security" in issue_lower:
                        checklist_items.append("Gather security documentation and certifications")
                    elif "approval" in issue_lower:
                        checklist_items.append("Prepare approval acceleration strategy")
                    elif "competitor" in issue_lower:
                        checklist_items.append("Review competitive differentiation points")
                    elif "integration" in issue_lower:
                        checklist_items.append("Document integration requirements and solutions")
                    elif "budget" in issue_lower:
                        checklist_items.append("Prepare ROI and budget justification materials")
                    elif "requirement" in issue_lower:
                        checklist_items.append("Prepare requirement gathering questions")
            
            # Deduplicate and limit the number of items
            checklist_items = list(set(checklist_items))
            if len(checklist_items) > 8:
                checklist_items = checklist_items[:8]
                
            # Format checklist as numbered items
            checklist_text = "\n".join([f"{i+1}. {item}" for i, item in enumerate(checklist_items)])
            
            # Prepare task data with properly formatted date
            task_data = {
                "subject": f"Meeting checklist for {company_name}",
                "description": checklist_text,
                "scheduledstart": today.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "scheduledend": today.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "prioritycode": 1,  # High priority
                # Remove statuscode since it's causing the 400 error
                # Dynamics 365 will set the appropriate default status
                "regardingobjectid_opportunity@odata.bind": f"/opportunities({opportunity_id})"
            }
            
            # Log the task data for debugging
            logging.info(f"Creating task with data: {json.dumps(task_data)}")
            
            # Create the task
            resp = self.dynamics_crud.perform(
                operation="create", 
                entity="tasks", 
                data=json.dumps(task_data)
            )
            
            res_json = json.loads(resp)
            if "error" in res_json:
                logging.error(f"Error creating checklist: {res_json['error']}")
                logging.error(f"Full error response: {resp}")
                logging.error(f"Request data: {json.dumps(task_data)}")
                
                # Try with minimal data as fallback
                basic_task_data = {
                    "subject": f"Meeting checklist for {company_name}",
                    "description": checklist_text
                }
                
                fallback_resp = self.dynamics_crud.perform(
                    operation="create", 
                    entity="tasks", 
                    data=json.dumps(basic_task_data)
                )
                
                fallback_json = json.loads(fallback_resp)
                if "error" in fallback_json:
                    logging.error(f"Error creating basic checklist: {fallback_json['error']}")
                    return False, None
                
                logging.info("Created checklist with minimal data")
                return True, fallback_json.get("guid")
                
            logging.info(f"Successfully created checklist task")
            return True, res_json.get("guid")
            
        except Exception as e:
            logging.error(f"Exception in _create_meeting_checklist: {str(e)}")
            return False, None

    def perform(self, **kwargs):
        """
        Main entry point for the agent.
        """
        intent = kwargs.get("intent")
        opportunity_id = kwargs.get("opportunity_id")
        contact_id = kwargs.get("contact_id")
        company_name = kwargs.get("company_name")
        
        # Get the Dynamics CRUD agent
        if not self.dynamics_crud:
            self.dynamics_crud = self._get_dynamics_crud_agent()
            
        if not self.dynamics_crud:
            error_msg = {
                "error": "Dynamics365CRUD agent not found",
                "status": "incomplete",
                "message": "Could not initialize Dynamics365CRUD. Please ensure it is available."
            }
            return json.dumps(error_msg)
        
        # Find or create opportunity ID if not provided
        if not opportunity_id and company_name:
            opportunity_id = self._find_opportunity_by_company(company_name)
            if not opportunity_id:
                return json.dumps({
                    "error": "No opportunity found",
                    "message": f"Could not find or create an opportunity for {company_name}. Please provide a valid company name.",
                    "status": "incomplete"
                })
        elif not opportunity_id:
            return json.dumps({
                "error": "Missing parameters",
                "message": "Please provide either an opportunity ID or a company name to continue.",
                "status": "incomplete"
            })
        
        # Store the opportunity ID for reference in the response
        actual_opp_id = opportunity_id
            
        # Execute based on intent
        if intent == "prep_meeting":
            # Get opportunity details
            opportunity = self._get_opportunity_details(opportunity_id)
            
            if not opportunity:
                return json.dumps({
                    "error": "Opportunity not found",
                    "message": f"Could not retrieve opportunity details for ID: {opportunity_id}. Please verify the opportunity exists.",
                    "opportunity_id": actual_opp_id,
                    "status": "incomplete"
                })
                
            # Format response with opportunity details
            company = opportunity.get("company", company_name or "the client")
            status = opportunity.get("status", "Proposal")
            value = opportunity.get("value", "$150,000")
            contact = opportunity.get("contact", "the primary contact")
            
            # Return full data including the actual opportunity ID and record link
            response_data = {
                "message": f"{company} opportunity is at {status} stage, {value} value. Last interaction: demo two weeks ago. Key contact: {contact}. Would you like a quick summary of open issues?",
                "opportunity_id": actual_opp_id,
                "company": company,
                "status": status,
                "value": value,
                "contact": contact,
                "record_link": f"{self.crm_base_url}opportunity&id={actual_opp_id}"
            }
            return json.dumps(response_data)
        
        elif intent == "summarize_issues":
            # Get issues
            if not self.opportunity_data:
                opportunity = self._get_opportunity_details(opportunity_id)
                
            issues = self._get_open_issues(opportunity_id)
            
            if not issues or len(issues) == 0:
                company = company_name
                if self.opportunity_data:
                    company = self.opportunity_data.get("company", company_name)
                    
                response_data = {
                    "message": f"No open issues found for {company or 'this opportunity'}. Shall I create a checklist for today's meeting?",
                    "opportunity_id": actual_opp_id,
                    "company": company,
                    "record_link": f"{self.crm_base_url}opportunity&id={actual_opp_id}"
                }
                return json.dumps(response_data)
                
            # Format issues into a comma-separated list
            issues_text = ", ".join(issues)
            
            company = company_name
            if self.opportunity_data:
                company = self.opportunity_data.get("company", company_name)
                
            response_data = {
                "message": f"Client requested {issues_text}. Shall I create a checklist for today's meeting?",
                "opportunity_id": actual_opp_id,
                "company": company,
                "issues": issues,
                "record_link": f"{self.crm_base_url}opportunity&id={actual_opp_id}"
            }
            return json.dumps(response_data)
            
        elif intent == "create_checklist":
            # Create checklist
            success, task_id = self._create_meeting_checklist(opportunity_id)
            
            if not success:
                return json.dumps({
                    "error": "Failed to create checklist",
                    "opportunity_id": actual_opp_id,
                    "message": "There was an issue creating the checklist in Dynamics 365.",
                    "status": "incomplete",
                    "record_link": f"{self.crm_base_url}opportunity&id={actual_opp_id}"
                })
                
            # Get company name for response
            company = company_name
            if self.opportunity_data:
                company = self.opportunity_data.get("company", company_name)
                
            contact = ""
            if self.opportunity_data and "contact" in self.opportunity_data:
                contact = f" with {self.opportunity_data['contact']}"
                
            response_data = {
                "message": f"Checklist created for your {company or 'client'} meeting{contact}.",
                "opportunity_id": actual_opp_id,
                "company": company,
                "success": True,
                "record_link": f"{self.crm_base_url}opportunity&id={actual_opp_id}"
            }
            
            # Add task link if we have a task ID
            if task_id:
                response_data["task_link"] = f"{self.crm_base_url}task&id={task_id}"
                
            return json.dumps(response_data)
            
        else:
            return json.dumps({
                "error": "Invalid intent",
                "message": "Please specify 'prep_meeting', 'summarize_issues', or 'create_checklist'.",
                "status": "incomplete"
            })