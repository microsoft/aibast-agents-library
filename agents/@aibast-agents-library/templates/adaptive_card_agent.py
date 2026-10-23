import json
import requests
import logging
from agents.basic_agent import BasicAgent

class AdaptiveCardPowerAutomateAgent(BasicAgent):
    def __init__(self):
        self.name = "AdaptiveCardPowerAutomate"
        self.metadata = {
            "name": self.name,
            "description": "Sends fully formed adaptive cards to Power Automate HTTP endpoints. The caller provides the complete adaptive card JSON and all necessary parameters for posting.",
            "parameters": {
                "type": "object",
                "properties": {
                    "adaptive_card_json": {
                        "type": "string",
                        "description": "Complete adaptive card JSON as a string. This should be the full adaptive card object including schema, body, actions, etc. Must be valid adaptive card schema v1.4 or compatible."
                    },
                    "recipient": {
                        "type": "string",
                        "description": "Email address or identifier of the person who should receive the adaptive card. This will be used in the 'Recipient' field of the Power Automate action."
                    },
                    "post_as": {
                        "type": "string",
                        "description": "How the card should be posted (e.g., 'Power Virtual Agents (Preview)', 'Flow bot', 'Custom Bot'). This determines the sender identity in Teams/channels.",
                        "default": "Power Virtual Agents (Preview)"
                    },
                    "post_in": {
                        "type": "string", 
                        "description": "Where to post the card (e.g., 'Chat with bot', 'Channel', 'Group chat'). This determines the posting location/context.",
                        "default": "Chat with bot"
                    },
                    "update_message": {
                        "type": "string",
                        "description": "Message to show after the card is posted or when it's updated (e.g., 'Thanks for your response!', 'Approval request sent'). This appears as a status message."
                    },
                    "bot_name": {
                        "type": "string",
                        "description": "Name/identifier of the bot that should handle this card (e.g., 'Agent', 'ApprovalBot', 'NotificationBot'). Used for routing and context.",
                        "default": "Agent"
                    },
                    "wait_for_response": {
                        "type": "boolean",
                        "description": "Whether Power Automate should wait for a user response to this adaptive card. Set to true for approval cards, false for notifications. Determines if the flow pauses for user interaction.",
                        "default": False
                    },
                    "card_title": {
                        "type": "string",
                        "description": "Optional title/subject for the card for logging and tracking purposes. This helps identify the card type/purpose in Power Automate runs."
                    },
                    "card_category": {
                        "type": "string",
                        "description": "Optional category for the card (e.g., 'approval', 'notification', 'task', 'alert'). Used for analytics and routing logic in Power Automate."
                    },
                    "priority_level": {
                        "type": "string",
                        "description": "Priority level for the card: 'low', 'medium', 'high', 'urgent'. Used for conditional formatting and routing urgency.",
                        "enum": ["low", "medium", "high", "urgent"],
                        "default": "medium"
                    },
                    "expires_at": {
                        "type": "string",
                        "description": "Optional expiration date/time for the card in ISO format (e.g., '2024-01-15T10:00:00Z'). After this time, the card may be auto-processed or marked expired."
                    },
                    "reference_id": {
                        "type": "string",
                        "description": "Optional unique reference ID for tracking this card across systems (e.g., 'REQ-2024-001', 'TASK-456'). Used for correlation and follow-up."
                    },
                    "additional_metadata": {
                        "type": "string",
                        "description": "Optional additional JSON metadata as a string. This can include any extra context data needed by your Power Automate flow for business logic (e.g., department, amounts, IDs)."
                    }
                },
                "required": ["adaptive_card_json", "recipient"]
            }
        }
        # Power Automate endpoint URL
        self.power_automate_url = "https://2ecf0a25a2e7eb6a9aec43400e2b67.02.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/074e71740d454fab9bbce0da490bc142/triggers/manual/paths/invoke/?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=euNuozUXGdmpHD4sVRdoxoJy2B0x_vhDFfGzhFnbG7g"
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        """
        Sends a fully formed adaptive card to Power Automate.
        
        Args:
            adaptive_card_json (str): Complete adaptive card JSON as string
            recipient (str): Email/ID of recipient
            post_as (str): Sender identity (default: Power Virtual Agents (Preview))
            post_in (str): Posting location (default: Chat with bot)
            update_message (str): Status message after posting
            bot_name (str): Bot identifier (default: Agent)
            wait_for_response (bool): Whether to wait for user response (default: False)
            card_title (str): Optional title for tracking
            card_category (str): Optional category for routing
            priority_level (str): Priority level (default: medium)
            expires_at (str): Optional expiration datetime
            reference_id (str): Optional tracking ID
            additional_metadata (str): Optional extra metadata as JSON string
            
        Returns:
            str: Success/error message describing the result
        """
        
        # Extract parameters with defaults
        adaptive_card_json = kwargs.get('adaptive_card_json')
        recipient = kwargs.get('recipient')
        post_as = kwargs.get('post_as', 'Power Virtual Agents (Preview)')
        post_in = kwargs.get('post_in', 'Chat with bot')
        update_message = kwargs.get('update_message', 'Card sent successfully')
        bot_name = kwargs.get('bot_name', 'Agent')
        wait_for_response = kwargs.get('wait_for_response', False)
        card_title = kwargs.get('card_title')
        card_category = kwargs.get('card_category')
        priority_level = kwargs.get('priority_level', 'medium')
        expires_at = kwargs.get('expires_at')
        reference_id = kwargs.get('reference_id')
        additional_metadata = kwargs.get('additional_metadata')

        # Validate required parameters
        if not adaptive_card_json:
            return "Error: adaptive_card_json is required - must provide the complete adaptive card JSON as a string"
        
        if not recipient:
            return "Error: recipient is required - must provide email address or identifier for card recipient"

        try:
            # Parse and validate the adaptive card JSON
            try:
                adaptive_card = json.loads(adaptive_card_json)
            except json.JSONDecodeError as e:
                return f"Error: Invalid JSON in adaptive_card_json - {str(e)}. Please ensure the adaptive card JSON is properly formatted."
            
            # Basic validation of adaptive card structure
            if not isinstance(adaptive_card, dict):
                return "Error: adaptive_card_json must be a JSON object, not an array or primitive value"
                
            if adaptive_card.get('type') != 'AdaptiveCard':
                return "Error: adaptive_card_json must have 'type': 'AdaptiveCard' property"
                
            if 'body' not in adaptive_card:
                return "Error: adaptive_card_json must have a 'body' property with card content"

            # Ensure the adaptive card has basic required properties
            if '$schema' not in adaptive_card:
                adaptive_card['$schema'] = 'http://adaptivecards.io/schemas/adaptive-card.json'
            
            if 'version' not in adaptive_card:
                adaptive_card['version'] = '1.4'

            # Build the payload for Power Automate
            payload = {
                "adaptiveCard": adaptive_card,  # Pass the card as-is since schema is flexible
                "recipient": recipient,
                "postAs": post_as,
                "postIn": post_in,
                "updateMessage": update_message,
                "bot": bot_name,
                "waitForResponse": wait_for_response
            }
            
            # Add optional fields if provided
            if card_title:
                payload["cardTitle"] = card_title
            if card_category:
                payload["cardCategory"] = card_category
            if priority_level:
                payload["priorityLevel"] = priority_level
            if expires_at:
                payload["expiresAt"] = expires_at
            if reference_id:
                payload["referenceId"] = reference_id
                
            # Add additional metadata if provided
            if additional_metadata:
                try:
                    metadata_obj = json.loads(additional_metadata)
                    payload["additionalMetadata"] = metadata_obj
                except json.JSONDecodeError:
                    # If it's not valid JSON, store as raw string
                    payload["additionalMetadata"] = {"rawData": additional_metadata}

            # Send to Power Automate
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }

            logging.info(f"Sending adaptive card to Power Automate. Recipient: {recipient}, Category: {card_category}, Wait for response: {wait_for_response}")
            logging.debug(f"Full payload: {json.dumps(payload, indent=2)}")

            response = requests.post(
                self.power_automate_url,
                json=payload,
                headers=headers,
                timeout=30
            )

            # Handle response
            if response.status_code in [200, 202]:
                success_msg = f"Successfully sent adaptive card to Power Automate"
                if card_title:
                    success_msg += f" - {card_title}"
                if reference_id:
                    success_msg += f" (Reference: {reference_id})"
                success_msg += f". Recipient: {recipient}. HTTP Status: {response.status_code}"
                
                if wait_for_response:
                    success_msg += ". Flow is waiting for user response."
                
                # Log successful response
                logging.info(success_msg)
                if response.text:
                    logging.debug(f"Response body: {response.text}")
                
                return success_msg
            else:
                error_msg = f"Failed to send adaptive card. HTTP Status: {response.status_code}"
                if response.text:
                    error_msg += f". Response: {response.text[:500]}..."
                    logging.error(f"Full error response: {response.text}")
                return error_msg

        except requests.exceptions.Timeout:
            return "Error: Request to Power Automate timed out after 30 seconds. Please check endpoint availability and try again."
        except requests.exceptions.ConnectionError:
            return "Error: Could not connect to Power Automate endpoint. Please verify the endpoint URL and network connectivity."
        except requests.exceptions.RequestException as e:
            return f"Error: HTTP request failed - {str(e)}"
        except Exception as e:
            logging.error(f"Unexpected error in AdaptiveCardPowerAutomateAgent: {str(e)}", exc_info=True)
            return f"Error: Unexpected error occurred while sending adaptive card - {str(e)}"