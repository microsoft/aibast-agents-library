#!/usr/bin/env python3
"""
Generate a Power Platform solution ZIP for a Copilot Studio agent with
memory read/write capabilities (ContextMemory + ManageMemory agents).

The generated ZIP can be imported via:
    pac solution import --path <output.zip>

Usage:
    python utils/generate_memory_agent_solution.py \
        --function-url https://rapp-xyz.azurewebsites.net \
        [--function-key YOUR_KEY] \
        [--output CommunityRAPPMemoryAgent_1_0_0_0.zip] \
        [--solution-name CommunityRAPPMemoryAgent] \
        [--publisher-prefix crapp]
"""

import argparse
import io
import json
import sys
import uuid
import zipfile
from textwrap import dedent


# ---------------------------------------------------------------------------
# Deterministic GUID helpers
# ---------------------------------------------------------------------------

def _guid(name: str) -> uuid.UUID:
    """Deterministic UUID-5 based on component name."""
    return uuid.uuid5(uuid.NAMESPACE_DNS, name)


def guid_upper(name: str) -> str:
    """GUID string in uppercase with hyphens (for file names)."""
    return str(_guid(name)).upper()


def guid_lower(name: str) -> str:
    """GUID string in lowercase with hyphens (for XML/JSON refs)."""
    return str(_guid(name))


# ---------------------------------------------------------------------------
# XML generators
# ---------------------------------------------------------------------------

def _solution_xml(
    solution_name: str,
    display_name: str,
    prefix: str,
    workflow_guids: list[tuple[str, str]],
) -> str:
    root_components = "\n      ".join(
        f'<RootComponent type="29" id="{{{gid}}}" behavior="0" />'
        for _, gid in workflow_guids
    )
    return dedent(f"""\
    <?xml version="1.0" encoding="utf-8"?>
    <ImportExportXml version="9.2.25114.191" SolutionPackageVersion="9.2" languagecode="1033" generatedBy="CrmLive" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
      <SolutionManifest>
        <UniqueName>{solution_name}</UniqueName>
        <LocalizedNames>
          <LocalizedName description="{display_name}" languagecode="1033" />
        </LocalizedNames>
        <Descriptions />
        <Version>1.0.0.0</Version>
        <Managed>0</Managed>
        <Publisher>
          <UniqueName>CommunityRAPP</UniqueName>
          <LocalizedNames>
            <LocalizedName description="CommunityRAPP" languagecode="1033" />
          </LocalizedNames>
          <Descriptions>
            <Description description="CommunityRAPP Publisher" languagecode="1033" />
          </Descriptions>
          <EMailAddress xsi:nil="true"></EMailAddress>
          <SupportingWebsiteUrl xsi:nil="true"></SupportingWebsiteUrl>
          <CustomizationPrefix>{prefix}</CustomizationPrefix>
          <CustomizationOptionValuePrefix>55100</CustomizationOptionValuePrefix>
          <Addresses>
            <Address>
              <AddressNumber>1</AddressNumber>
              <AddressTypeCode>1</AddressTypeCode>
              <City xsi:nil="true"></City>
              <County xsi:nil="true"></County>
              <Country xsi:nil="true"></Country>
              <Fax xsi:nil="true"></Fax>
              <FreightTermsCode xsi:nil="true"></FreightTermsCode>
              <ImportSequenceNumber xsi:nil="true"></ImportSequenceNumber>
              <Latitude xsi:nil="true"></Latitude>
              <Line1 xsi:nil="true"></Line1>
              <Line2 xsi:nil="true"></Line2>
              <Line3 xsi:nil="true"></Line3>
              <Longitude xsi:nil="true"></Longitude>
              <Name xsi:nil="true"></Name>
              <PostalCode xsi:nil="true"></PostalCode>
              <PostOfficeBox xsi:nil="true"></PostOfficeBox>
              <PrimaryContactName xsi:nil="true"></PrimaryContactName>
              <ShippingMethodCode>1</ShippingMethodCode>
              <StateOrProvince xsi:nil="true"></StateOrProvince>
              <Telephone1 xsi:nil="true"></Telephone1>
              <Telephone2 xsi:nil="true"></Telephone2>
              <Telephone3 xsi:nil="true"></Telephone3>
              <TimeZoneRuleVersionNumber xsi:nil="true"></TimeZoneRuleVersionNumber>
              <UPSZone xsi:nil="true"></UPSZone>
              <UTCOffset xsi:nil="true"></UTCOffset>
              <UTCConversionTimeZoneCode xsi:nil="true"></UTCConversionTimeZoneCode>
            </Address>
            <Address>
              <AddressNumber>2</AddressNumber>
              <AddressTypeCode>1</AddressTypeCode>
              <City xsi:nil="true"></City>
              <County xsi:nil="true"></County>
              <Country xsi:nil="true"></Country>
              <Fax xsi:nil="true"></Fax>
              <FreightTermsCode xsi:nil="true"></FreightTermsCode>
              <ImportSequenceNumber xsi:nil="true"></ImportSequenceNumber>
              <Latitude xsi:nil="true"></Latitude>
              <Line1 xsi:nil="true"></Line1>
              <Line2 xsi:nil="true"></Line2>
              <Line3 xsi:nil="true"></Line3>
              <Longitude xsi:nil="true"></Longitude>
              <Name xsi:nil="true"></Name>
              <PostalCode xsi:nil="true"></PostalCode>
              <PostOfficeBox xsi:nil="true"></PostOfficeBox>
              <PrimaryContactName xsi:nil="true"></PrimaryContactName>
              <ShippingMethodCode>1</ShippingMethodCode>
              <StateOrProvince xsi:nil="true"></StateOrProvince>
              <Telephone1 xsi:nil="true"></Telephone1>
              <Telephone2 xsi:nil="true"></Telephone2>
              <Telephone3 xsi:nil="true"></Telephone3>
              <TimeZoneRuleVersionNumber xsi:nil="true"></TimeZoneRuleVersionNumber>
              <UPSZone xsi:nil="true"></UPSZone>
              <UTCOffset xsi:nil="true"></UTCOffset>
              <UTCConversionTimeZoneCode xsi:nil="true"></UTCConversionTimeZoneCode>
            </Address>
          </Addresses>
        </Publisher>
        <RootComponents>
          {root_components}
        </RootComponents>
        <MissingDependencies />
      </SolutionManifest>
    </ImportExportXml>
    """)


def _customizations_xml(
    prefix: str,
    workflows: list[dict],
) -> str:
    """Generate customizations.xml listing workflows and connection references."""
    wf_entries = []
    for wf in workflows:
        desc_elem = ""
        if wf.get("description"):
            desc_elem = (
                f'\n      <Descriptions>\n'
                f'        <Description languagecode="1033" description="{wf["description"]}" />\n'
                f'      </Descriptions>'
            )
        wf_entries.append(dedent(f"""\
            <Workflow WorkflowId="{{{wf['id']}}}" Name="{wf['name']}" Description="{wf.get('description', '')}">
              <JsonFileName>{wf['json_path']}</JsonFileName>
              <Type>1</Type>
              <Subprocess>0</Subprocess>
              <Category>5</Category>
              <Mode>0</Mode>
              <Scope>4</Scope>
              <OnDemand>0</OnDemand>
              <TriggerOnCreate>0</TriggerOnCreate>
              <TriggerOnDelete>0</TriggerOnDelete>
              <AsyncAutodelete>0</AsyncAutodelete>
              <SyncWorkflowLogOnFailure>0</SyncWorkflowLogOnFailure>
              <StateCode>1</StateCode>
              <StatusCode>2</StatusCode>
              <RunAs>1</RunAs>
              <IsTransacted>1</IsTransacted>
              <IntroducedVersion>1.0.0.0</IntroducedVersion>
              <IsCustomizable>1</IsCustomizable>
              <IsCustomProcessingStepAllowedForOtherPublishers>1</IsCustomProcessingStepAllowedForOtherPublishers>
              <ModernFlowType>0</ModernFlowType>
              <PrimaryEntity>none</PrimaryEntity>
              <LocalizedNames>
                <LocalizedName languagecode="1033" description="{wf['name']}" />
              </LocalizedNames>{desc_elem}
            </Workflow>"""))

    wf_block = "\n    ".join(wf_entries)
    conn_ref_name = f"{prefix}_sharedoffice365users_memoryagent"

    return dedent(f"""\
    <?xml version="1.0" encoding="utf-8"?>
    <ImportExportXml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
      <Entities></Entities>
      <Roles></Roles>
      <Workflows>
        {wf_block}
      </Workflows>
      <FieldSecurityProfiles></FieldSecurityProfiles>
      <Templates />
      <EntityMaps />
      <EntityRelationships />
      <OrganizationSettings />
      <optionsets />
      <CustomControls />
      <EntityDataProviders />
      <connectionreferences>
        <connectionreference connectionreferencelogicalname="{conn_ref_name}">
          <connectionreferencedisplayname>Office 365 Users - Memory Agent</connectionreferencedisplayname>
          <connectorid>/providers/Microsoft.PowerApps/apis/shared_office365users</connectorid>
          <iscustomizable>1</iscustomizable>
          <promptingbehavior>0</promptingbehavior>
          <statecode>0</statecode>
          <statuscode>1</statuscode>
        </connectionreference>
      </connectionreferences>
      <Languages>
        <Language>1033</Language>
      </Languages>
    </ImportExportXml>
    """)


def _content_types_xml(data_parts: list[str]) -> str:
    overrides = "".join(
        f'<Override PartName="/{p}" ContentType="application/octet-stream" />'
        for p in data_parts
    )
    return (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="xml" ContentType="application/octet-stream" />'
        '<Default Extension="json" ContentType="application/octet-stream" />'
        f'{overrides}'
        '</Types>'
    )


def _botcomponent_xml(schema_name: str, display_name: str, bot_schema: str, component_type: int = 9) -> str:
    return dedent(f"""\
    <botcomponent schemaname="{schema_name}">
      <componenttype>{component_type}</componenttype>
      <iscustomizable>0</iscustomizable>
      <name>{display_name}</name>
      <parentbotid>
        <schemaname>{bot_schema}</schemaname>
      </parentbotid>
      <statecode>0</statecode>
      <statuscode>1</statuscode>
    </botcomponent>
    """)


def _bot_xml(bot_schema: str) -> str:
    return dedent(f"""\
    <bot schemaname="{bot_schema}">
      <authenticationmode>2</authenticationmode>
      <authenticationtrigger>1</authenticationtrigger>
      <iscustomizable>0</iscustomizable>
      <language>1033</language>
      <name>Memory Agent</name>
      <runtimeprovider>0</runtimeprovider>
      <synchronizationstatus>{{"$kind":"BotSynchronizationDetails","contentVersion":1}}</synchronizationstatus>
      <template>default-2.1.0</template>
      <timezoneruleversionnumber>4</timezoneruleversionnumber>
    </bot>
    """)


# ---------------------------------------------------------------------------
# Flow JSON generators
# ---------------------------------------------------------------------------

def _talk_to_memory_agent_flow(
    function_url: str,
    function_key: str,
    prefix: str,
) -> dict:
    """Main flow: Copilot Studio Skills trigger → Office 365 profile → HTTP → parse → respond."""
    conn_ref = f"{prefix}_sharedoffice365users_memoryagent"
    api_endpoint = f"{function_url}/api/businessinsightbot_function"

    return {
        "properties": {
            "connectionReferences": {
                "shared_office365users": {
                    "runtimeSource": "invoker",
                    "connection": {
                        "connectionReferenceLogicalName": conn_ref
                    },
                    "api": {"name": "shared_office365users"}
                }
            },
            "definition": {
                "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
                "contentVersion": "1.0.0.0",
                "parameters": {
                    "$connections": {"defaultValue": {}, "type": "Object"},
                    "$authentication": {"defaultValue": {}, "type": "SecureObject"}
                },
                "triggers": {
                    "manual": {
                        "metadata": {
                            "operationMetadataId": guid_lower("trigger.talk_to_memory_agent")
                        },
                        "type": "Request",
                        "kind": "Skills",
                        "inputs": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "text": {
                                        "title": "user_input",
                                        "type": "string",
                                        "x-ms-dynamically-added": True,
                                        "description": "The user message",
                                        "x-ms-content-hint": "TEXT"
                                    },
                                    "text_1": {
                                        "title": "conversation_history",
                                        "type": "string",
                                        "x-ms-dynamically-added": True,
                                        "description": "JSON conversation history",
                                        "x-ms-content-hint": "TEXT"
                                    }
                                },
                                "required": ["text", "text_1"]
                            }
                        }
                    }
                },
                "actions": {
                    "Original_String": {
                        "runAfter": {},
                        "metadata": {"operationMetadataId": guid_lower("action.original_string")},
                        "type": "Compose",
                        "inputs": "@triggerBody()['text']"
                    },
                    "Parsed_JSON": {
                        "runAfter": {"Original_String": ["Succeeded"]},
                        "metadata": {"operationMetadataId": guid_lower("action.parsed_json")},
                        "type": "Compose",
                        "inputs": "@trim(replace(outputs('Original_String'), 'BODY:,', ''))"
                    },
                    "Compose_Conversation_History": {
                        "runAfter": {"Parsed_JSON": ["Succeeded"]},
                        "metadata": {"operationMetadataId": guid_lower("action.compose_history")},
                        "type": "Compose",
                        "inputs": "@triggerBody()['text_1']"
                    },
                    "Compose_Format_JSON": {
                        "runAfter": {"Compose_Conversation_History": ["Succeeded"]},
                        "metadata": {"operationMetadataId": guid_lower("action.format_json")},
                        "type": "Compose",
                        "inputs": (
                            "@if(\n"
                            "  or(\n"
                            "    equals(outputs('Compose_Conversation_History'), '[]'),\n"
                            "    equals(outputs('Compose_Conversation_History'), '[, ]'),\n"
                            "    startsWith(outputs('Compose_Conversation_History'), '[\\\"[]\\\"]'),\n"
                            "    equals(outputs('Compose_Conversation_History'), null)\n"
                            "  ),\n"
                            "  json('[]'),\n"
                            "  json(\n"
                            "    concat(\n"
                            "      '[',\n"
                            "      substring(\n"
                            "        outputs('Compose_Conversation_History'), \n"
                            "        indexOf(outputs('Compose_Conversation_History'), '{'), \n"
                            "        sub(length(outputs('Compose_Conversation_History')), indexOf(outputs('Compose_Conversation_History'), '{'))\n"
                            "      )\n"
                            "    )\n"
                            "  )\n"
                            ")"
                        )
                    },
                    "Parse_JSON_History": {
                        "runAfter": {"Compose_Format_JSON": ["Succeeded"]},
                        "metadata": {"operationMetadataId": guid_lower("action.parse_history")},
                        "type": "ParseJson",
                        "inputs": {
                            "content": "@outputs('Compose_Format_JSON')",
                            "schema": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "role": {"type": "string"},
                                        "content": {"type": "string"}
                                    },
                                    "required": ["role", "content"]
                                }
                            }
                        }
                    },
                    "Get_my_profile_(V2)": {
                        "runAfter": {"Parse_JSON_History": ["Succeeded"]},
                        "metadata": {"operationMetadataId": guid_lower("action.get_profile")},
                        "type": "OpenApiConnection",
                        "inputs": {
                            "host": {
                                "connectionName": "shared_office365users",
                                "operationId": "MyProfile_V2",
                                "apiId": "/providers/Microsoft.PowerApps/apis/shared_office365users"
                            },
                            "parameters": {},
                            "authentication": "@parameters('$authentication')"
                        }
                    },
                    "jsonForAZFCall": {
                        "runAfter": {"Get_my_profile_(V2)": ["Succeeded"]},
                        "metadata": {"operationMetadataId": guid_lower("action.json_for_call")},
                        "type": "InitializeVariable",
                        "inputs": {
                            "variables": [{
                                "name": "jsonForAZFCall",
                                "type": "object",
                                "value": {
                                    "user_input": "@{triggerBody()['text']}",
                                    "conversation_history": "@outputs('Compose_Format_JSON')",
                                    "user_guid": "@{outputs('Get_my_profile_(V2)')?['body/id']}"
                                }
                            }]
                        }
                    },
                    "functionKey": {
                        "runAfter": {"jsonForAZFCall": ["Succeeded"]},
                        "metadata": {"operationMetadataId": guid_lower("action.function_key")},
                        "type": "InitializeVariable",
                        "inputs": {
                            "variables": [{
                                "name": "functionKey",
                                "type": "string",
                                "value": function_key
                            }]
                        }
                    },
                    "Initialize_FunctionURL": {
                        "runAfter": {"functionKey": ["Succeeded"]},
                        "metadata": {"operationMetadataId": guid_lower("action.function_url")},
                        "type": "InitializeVariable",
                        "inputs": {
                            "variables": [{
                                "name": "RAPPFunctionURL",
                                "type": "string",
                                "value": api_endpoint
                            }]
                        }
                    },
                    "HTTP": {
                        "runAfter": {"Initialize_FunctionURL": ["Succeeded"]},
                        "metadata": {"operationMetadataId": guid_lower("action.http_main")},
                        "type": "Http",
                        "inputs": {
                            "method": "POST",
                            "uri": "@{variables('RAPPFunctionURL')}?code=@{variables('functionKey')}",
                            "headers": {
                                "Content-Type": "application/json",
                                "x-functions-key": "@{variables('functionKey')}"
                            },
                            "body": "@variables('jsonForAZFCall')"
                        }
                    },
                    "Compose_Response": {
                        "runAfter": {"HTTP": ["Succeeded"]},
                        "metadata": {"operationMetadataId": guid_lower("action.compose_response")},
                        "type": "Compose",
                        "inputs": "@body('HTTP')"
                    },
                    "Parse_JSON": {
                        "runAfter": {"Compose_Response": ["Succeeded"]},
                        "metadata": {"operationMetadataId": guid_lower("action.parse_json")},
                        "type": "ParseJson",
                        "inputs": {
                            "content": "@body('HTTP')",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "assistant_response": {"type": "string"},
                                    "voice_response": {"type": "string"},
                                    "agent_logs": {"type": "string"},
                                    "user_guid": {"type": "string"}
                                }
                            }
                        }
                    },
                    "Respond_to_Copilot": {
                        "runAfter": {"Parse_JSON": ["Succeeded"]},
                        "metadata": {"operationMetadataId": guid_lower("action.respond_copilot")},
                        "type": "Response",
                        "kind": "Skills",
                        "inputs": {
                            "statusCode": 200,
                            "body": {
                                "output": "@body('Parse_JSON')?['assistant_response']",
                                "output_1": "@body('Parse_JSON')?['agent_logs']",
                                "output_2": "@body('Parse_JSON')?['user_guid']",
                                "voice_response": "@body('Parse_JSON')?['voice_response']"
                            },
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "output": {
                                        "title": "output",
                                        "x-ms-dynamically-added": True,
                                        "type": "string"
                                    },
                                    "output_1": {
                                        "title": "output_1",
                                        "x-ms-dynamically-added": True,
                                        "type": "string"
                                    },
                                    "output_2": {
                                        "title": "output_2",
                                        "x-ms-dynamically-added": True,
                                        "type": "string"
                                    },
                                    "voice_response": {
                                        "title": "voice_response",
                                        "x-ms-dynamically-added": True,
                                        "type": "string"
                                    }
                                }
                            }
                        }
                    }
                },
                "outputs": {}
            },
            "templateName": ""
        },
        "schemaVersion": "1.0.0.0"
    }


def _read_memory_flow(function_url: str, function_key: str) -> dict:
    """Dedicated Read Memory flow using the copilot-studio trigger endpoint."""
    api_endpoint = f"{function_url}/api/trigger/copilot-studio"

    return {
        "properties": {
            "connectionReferences": {},
            "definition": {
                "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
                "contentVersion": "1.0.0.0",
                "parameters": {
                    "$connections": {"defaultValue": {}, "type": "Object"},
                    "$authentication": {"defaultValue": {}, "type": "SecureObject"}
                },
                "triggers": {
                    "manual": {
                        "metadata": {"operationMetadataId": guid_lower("trigger.read_memory")},
                        "type": "Request",
                        "kind": "Skills",
                        "inputs": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "text": {
                                        "title": "keywords",
                                        "type": "string",
                                        "x-ms-dynamically-added": True,
                                        "description": "Optional comma-separated keywords to filter memories",
                                        "x-ms-content-hint": "TEXT"
                                    },
                                    "text_1": {
                                        "title": "max_messages",
                                        "type": "string",
                                        "x-ms-dynamically-added": True,
                                        "description": "Optional max number of messages to return",
                                        "x-ms-content-hint": "TEXT"
                                    }
                                },
                                "required": []
                            }
                        }
                    }
                },
                "actions": {
                    "Build_Keywords_Array": {
                        "runAfter": {},
                        "metadata": {"operationMetadataId": guid_lower("action.build_keywords")},
                        "type": "Compose",
                        "inputs": "@if(equals(triggerBody()?['text'], null), json('[]'), split(triggerBody()?['text'], ','))"
                    },
                    "Build_Max_Messages": {
                        "runAfter": {"Build_Keywords_Array": ["Succeeded"]},
                        "metadata": {"operationMetadataId": guid_lower("action.build_max_messages")},
                        "type": "Compose",
                        "inputs": "@if(equals(triggerBody()?['text_1'], null), 10, int(triggerBody()?['text_1']))"
                    },
                    "functionKey": {
                        "runAfter": {"Build_Max_Messages": ["Succeeded"]},
                        "metadata": {"operationMetadataId": guid_lower("action.read_function_key")},
                        "type": "InitializeVariable",
                        "inputs": {
                            "variables": [{
                                "name": "functionKey",
                                "type": "string",
                                "value": function_key
                            }]
                        }
                    },
                    "HTTP_Read_Memory": {
                        "runAfter": {"functionKey": ["Succeeded"]},
                        "metadata": {"operationMetadataId": guid_lower("action.http_read_memory")},
                        "type": "Http",
                        "inputs": {
                            "method": "POST",
                            "uri": f"{api_endpoint}?code=@{{variables('functionKey')}}",
                            "headers": {
                                "Content-Type": "application/json",
                                "x-functions-key": "@{variables('functionKey')}"
                            },
                            "body": {
                                "agent": "ContextMemory",
                                "action": "recall_context",
                                "parameters": {
                                    "keywords": "@outputs('Build_Keywords_Array')",
                                    "max_messages": "@outputs('Build_Max_Messages')",
                                    "full_recall": True
                                }
                            }
                        }
                    },
                    "Parse_Read_Response": {
                        "runAfter": {"HTTP_Read_Memory": ["Succeeded"]},
                        "metadata": {"operationMetadataId": guid_lower("action.parse_read_response")},
                        "type": "ParseJson",
                        "inputs": {
                            "content": "@body('HTTP_Read_Memory')",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "status": {"type": "string"},
                                    "response": {"type": "string"},
                                    "copilot_studio_format": {"type": "object"}
                                }
                            }
                        }
                    },
                    "Respond_to_Copilot": {
                        "runAfter": {"Parse_Read_Response": ["Succeeded"]},
                        "metadata": {"operationMetadataId": guid_lower("action.respond_read")},
                        "type": "Response",
                        "kind": "Skills",
                        "inputs": {
                            "statusCode": 200,
                            "body": {
                                "memory_response": "@body('Parse_Read_Response')?['response']"
                            },
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "memory_response": {
                                        "title": "memory_response",
                                        "x-ms-dynamically-added": True,
                                        "type": "string"
                                    }
                                }
                            }
                        }
                    }
                },
                "outputs": {}
            },
            "templateName": ""
        },
        "schemaVersion": "1.0.0.0"
    }


def _write_memory_flow(function_url: str, function_key: str) -> dict:
    """Dedicated Write Memory flow using the copilot-studio trigger endpoint."""
    api_endpoint = f"{function_url}/api/trigger/copilot-studio"

    return {
        "properties": {
            "connectionReferences": {},
            "definition": {
                "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
                "contentVersion": "1.0.0.0",
                "parameters": {
                    "$connections": {"defaultValue": {}, "type": "Object"},
                    "$authentication": {"defaultValue": {}, "type": "SecureObject"}
                },
                "triggers": {
                    "manual": {
                        "metadata": {"operationMetadataId": guid_lower("trigger.write_memory")},
                        "type": "Request",
                        "kind": "Skills",
                        "inputs": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "text": {
                                        "title": "memory_type",
                                        "type": "string",
                                        "x-ms-dynamically-added": True,
                                        "description": "Memory type: fact, preference, insight, or task",
                                        "x-ms-content-hint": "TEXT"
                                    },
                                    "text_1": {
                                        "title": "content",
                                        "type": "string",
                                        "x-ms-dynamically-added": True,
                                        "description": "The content to store in memory",
                                        "x-ms-content-hint": "TEXT"
                                    },
                                    "text_2": {
                                        "title": "importance",
                                        "type": "string",
                                        "x-ms-dynamically-added": True,
                                        "description": "Importance 1-5 (optional, default 3)",
                                        "x-ms-content-hint": "TEXT"
                                    }
                                },
                                "required": ["text", "text_1"]
                            }
                        }
                    }
                },
                "actions": {
                    "Build_Importance": {
                        "runAfter": {},
                        "metadata": {"operationMetadataId": guid_lower("action.build_importance")},
                        "type": "Compose",
                        "inputs": "@if(equals(triggerBody()?['text_2'], null), 3, int(triggerBody()?['text_2']))"
                    },
                    "functionKey": {
                        "runAfter": {"Build_Importance": ["Succeeded"]},
                        "metadata": {"operationMetadataId": guid_lower("action.write_function_key")},
                        "type": "InitializeVariable",
                        "inputs": {
                            "variables": [{
                                "name": "functionKey",
                                "type": "string",
                                "value": function_key
                            }]
                        }
                    },
                    "HTTP_Write_Memory": {
                        "runAfter": {"functionKey": ["Succeeded"]},
                        "metadata": {"operationMetadataId": guid_lower("action.http_write_memory")},
                        "type": "Http",
                        "inputs": {
                            "method": "POST",
                            "uri": f"{api_endpoint}?code=@{{variables('functionKey')}}",
                            "headers": {
                                "Content-Type": "application/json",
                                "x-functions-key": "@{variables('functionKey')}"
                            },
                            "body": {
                                "agent": "ManageMemory",
                                "action": "store_memory",
                                "parameters": {
                                    "memory_type": "@triggerBody()['text']",
                                    "content": "@triggerBody()['text_1']",
                                    "importance": "@outputs('Build_Importance')"
                                }
                            }
                        }
                    },
                    "Parse_Write_Response": {
                        "runAfter": {"HTTP_Write_Memory": ["Succeeded"]},
                        "metadata": {"operationMetadataId": guid_lower("action.parse_write_response")},
                        "type": "ParseJson",
                        "inputs": {
                            "content": "@body('HTTP_Write_Memory')",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "status": {"type": "string"},
                                    "response": {"type": "string"},
                                    "copilot_studio_format": {"type": "object"}
                                }
                            }
                        }
                    },
                    "Respond_to_Copilot": {
                        "runAfter": {"Parse_Write_Response": ["Succeeded"]},
                        "metadata": {"operationMetadataId": guid_lower("action.respond_write")},
                        "type": "Response",
                        "kind": "Skills",
                        "inputs": {
                            "statusCode": 200,
                            "body": {
                                "result": "@body('Parse_Write_Response')?['response']"
                            },
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "result": {
                                        "title": "result",
                                        "x-ms-dynamically-added": True,
                                        "type": "string"
                                    }
                                }
                            }
                        }
                    }
                },
                "outputs": {}
            },
            "templateName": ""
        },
        "schemaVersion": "1.0.0.0"
    }


# ---------------------------------------------------------------------------
# Bot component YAML data generators
# ---------------------------------------------------------------------------

def _topic_main_yaml(bot_schema: str, flow_id: str) -> str:
    """MAIN topic — handles all user messages, invokes Talk to Memory Agent flow."""
    return dedent(f"""\
    kind: AdaptiveDialog
    inputs:
      - kind: AutomaticTaskInput
        propertyName: Var1
        entity: StringPrebuiltEntity
        shouldPromptUser: true
        modelDescription: This should call the assistant. Always trigger this when a user has a message.

    beginDialog:
      kind: OnActivity
      id: main
      type: Message
      actions:
        - kind: ConditionGroup
          id: conditionGroup_clearChat
          conditions:
            - id: conditionItem_clearChat
              condition: =System.LastMessage.Text in "Clear Chat"
              actions:
                - kind: SetVariable
                  id: setVariable_clearHistory
                  variable: Global.VarConversationHistory
                  value:

                - kind: SendActivity
                  id: sendActivity_cleared
                  activity: "Chat context has been cleared. \\U0001f9f9"

        - kind: SetVariable
          id: setVariable_userInput
          variable: Topic.user_input
          value: =System.LastMessage.Text

        - kind: SetVariable
          id: setVariable_escapedInput
          variable: Topic.varEscapedInput
          value: =Substitute(Topic.user_input, "\\"", "\\\\\\"")

        - kind: SetVariable
          id: setVariable_buildHistory
          variable: Global.VarConversationHistory
          value: |-
            =If(
              Or(Global.VarConversationHistory = "", Global.VarConversationHistory = "[]"),
              Concatenate("{{\\"role\\": \\"user\\", \\"content\\": \\"", Topic.varEscapedInput, "\\"}}"),
              Concatenate(Global.VarConversationHistory, ", {{\\"role\\": \\"user\\", \\"content\\": \\"", Topic.varEscapedInput, "\\"}}")
            )

        - kind: InvokeFlowAction
          id: invokeFlowAction_talkToMemory
          input:
            binding:
              text: =Topic.user_input
              text_1: =Global.VarConversationHistory
          output:
            binding:
              output: Topic.Var1
              output_1: Topic.AgentLogs
              output_2: Topic.UserGuid
          flowId: {flow_id}

        - kind: SetVariable
          id: setVariable_escapeResponse
          variable: Topic.varEscapedInput
          value: =Substitute(Topic.Var1, "\\"", "\\\\\\"")

        - kind: SetVariable
          id: setVariable_appendAssistant
          variable: Global.VarConversationHistory
          value: "=Concatenate(Global.VarConversationHistory, \\", {{\\\\\\"role\\\\\\": \\\\\\"assistant\\\\\\", \\\\\\"content\\\\\\": \\\\\\"\\", Topic.varEscapedInput, \\\"\\\\\\"}}\\\")"

        - kind: ConditionGroup
          id: conditionGroup_appendLogs
          conditions:
            - id: conditionItem_hasLogs
              condition: =And(Not(IsBlank(Topic.AgentLogs)), Len(Topic.AgentLogs) > 0)
              actions:
                - kind: SetVariable
                  id: setVariable_appendLogs
                  variable: Global.VarConversationHistory
                  value: "=Concatenate(Global.VarConversationHistory, \\", {{\\\\\\"role\\\\\\": \\\\\\"system\\\\\\", \\\\\\"content\\\\\\": \\\\\\"\\", Substitute(Topic.AgentLogs, \\"\\\\\\"\\", \\"\\\\\\\\\\\\\\"\\"), \\\"\\\\\\"}}\\\")"

        - kind: ConditionGroup
          id: conditionGroup_display
          conditions:
            - id: conditionItem_hasAgentLogs
              condition: =And(Not(IsBlank(Topic.AgentLogs)), Len(Topic.AgentLogs) > 0)
              actions:
                - kind: SendActivity
                  id: sendActivity_withLogs
                  activity: |-
                    {{Topic.Var1}}

                    ---
                    \\U0001f527 **Agent Calls:** {{Topic.AgentLogs}}

          elseActions:
            - kind: SendActivity
              id: sendActivity_noLogs
              activity: "{{Topic.Var1}}"
    """)


def _topic_read_memory_yaml(bot_schema: str, flow_id: str) -> str:
    return dedent(f"""\
    kind: AdaptiveDialog
    beginDialog:
      kind: OnRecognizedIntent
      id: main
      intent:
        displayName: Read Memory
        includeInOnSelectIntent: false
        triggerQueries:
          - what do you remember
          - recall memory
          - show memories
          - what have you stored
          - recall context
          - show stored memories
          - memory recall
          - what's in memory
          - read memory
          - retrieve memories

      actions:
        - kind: Question
          id: question_keywords
          variable: Topic.Keywords
          prompt: Would you like to filter by specific keywords? (leave blank for all memories)
          entity: StringPrebuiltEntity

        - kind: InvokeFlowAction
          id: invokeFlowAction_readMemory
          input:
            binding:
              text: =Topic.Keywords
              text_1: "10"
          output:
            binding:
              memory_response: Topic.MemoryResponse
          flowId: {flow_id}

        - kind: SendActivity
          id: sendActivity_memories
          activity: |-
            \\U0001f4da **Stored Memories:**

            {{Topic.MemoryResponse}}
    """)


def _topic_write_memory_yaml(bot_schema: str, flow_id: str) -> str:
    return dedent(f"""\
    kind: AdaptiveDialog
    beginDialog:
      kind: OnRecognizedIntent
      id: main
      intent:
        displayName: Write Memory
        includeInOnSelectIntent: false
        triggerQueries:
          - remember this
          - save memory
          - store this
          - save this to memory
          - write memory
          - remember that
          - store memory
          - save this information
          - keep this in mind
          - remember for later

      actions:
        - kind: Question
          id: question_memoryType
          variable: Topic.MemoryType
          prompt: "What type of memory is this? Choose one: **fact**, **preference**, **insight**, or **task**"
          entity: StringPrebuiltEntity

        - kind: Question
          id: question_content
          variable: Topic.Content
          prompt: What would you like me to remember?
          entity: StringPrebuiltEntity

        - kind: Question
          id: question_importance
          variable: Topic.Importance
          prompt: "How important is this? (1-5, where 5 is most important. Default: 3)"
          entity: StringPrebuiltEntity

        - kind: InvokeFlowAction
          id: invokeFlowAction_writeMemory
          input:
            binding:
              text: =Topic.MemoryType
              text_1: =Topic.Content
              text_2: =Topic.Importance
          output:
            binding:
              result: Topic.Result
          flowId: {flow_id}

        - kind: SendActivity
          id: sendActivity_saved
          activity: |-
            \\u2705 **Memory Saved!**

            {{Topic.Result}}
    """)


def _topic_conversation_start_yaml(bot_schema: str) -> str:
    return dedent("""\
    kind: AdaptiveDialog
    beginDialog:
      kind: OnConversationStart
      id: main
      actions:
        - kind: SendActivity
          id: sendMessage_welcome
          activity:
            text:
              - Hello, I'm {System.Bot.Name}. I can remember things across our conversations! Try asking me to remember something or recall stored memories.
            speak:
              - Hello, I'm {System.Bot.Name}. I have persistent memory capabilities. How can I help you today?
    """)


def _topic_fallback_yaml(bot_schema: str) -> str:
    return dedent(f"""\
    kind: AdaptiveDialog
    beginDialog:
      kind: OnUnknownIntent
      id: main
      actions:
        - kind: ConditionGroup
          id: conditionGroup_fallback
          conditions:
            - id: conditionItem_retry
              condition: =System.FallbackCount < 3
              actions:
                - kind: SendActivity
                  id: sendMessage_retry
                  activity: I'm sorry, I'm not sure how to help with that. Can you try rephrasing?

          elseActions:
            - kind: BeginDialog
              id: beginDialog_escalate
              dialog: {bot_schema}.topic.Escalate
    """)


def _topic_escalate_yaml(bot_schema: str) -> str:
    return dedent("""\
    kind: AdaptiveDialog
    startBehavior: CancelOtherTopics
    beginDialog:
      kind: OnEscalate
      id: main
      intent:
        displayName: Escalate
        includeInOnSelectIntent: false
        triggerQueries:
          - Talk to agent
          - Talk to a person
          - Talk to someone
          - Connect me to a live agent
          - I need help from a person
          - Customer service
          - I want to speak with a representative

      actions:
        - kind: SendActivity
          id: sendMessage_escalate
          activity:
            text:
              - I understand you'd like to speak with someone. Let me transfer you.
            speak:
              - I'll transfer you to an agent now.

        - kind: EndConversation
          id: endConversation_transfer
    """)


def _topic_on_error_yaml(bot_schema: str) -> str:
    return dedent("""\
    kind: AdaptiveDialog
    startBehavior: UseLatestPublishedContentAndCancelOtherTopics
    beginDialog:
      kind: OnError
      id: main
      actions:
        - kind: SetVariable
          id: setVariable_timestamp
          variable: init:Topic.CurrentTime
          value: =Text(Now(), DateTimeFormat.UTC)

        - kind: ConditionGroup
          id: condition_testMode
          conditions:
            - id: conditionItem_test
              condition: =System.Conversation.InTestMode = true
              actions:
                - kind: SendActivity
                  id: sendMessage_testError
                  activity: |-
                    Error Message: {System.Error.Message}
                    Error Code: {System.Error.Code}
                    Conversation Id: {System.Conversation.Id}
                    Time (UTC): {Topic.CurrentTime}

          elseActions:
            - kind: SendActivity
              id: sendMessage_prodError
              activity:
                text:
                  - |-
                    An error has occurred.
                    Error code: {System.Error.Code}
                    Conversation Id: {System.Conversation.Id}
                    Time (UTC): {Topic.CurrentTime}.
                speak:
                  - An error has occurred, please try again.

        - kind: LogCustomTelemetryEvent
          id: logTelemetry_error
          eventName: OnErrorLog
          properties: "={ErrorMessage: System.Error.Message, ErrorCode: System.Error.Code, TimeUTC: Topic.CurrentTime, ConversationId: System.Conversation.Id}"

        - kind: CancelAllDialogs
          id: cancelDialogs_error
    """)


def _topic_goodbye_yaml(bot_schema: str) -> str:
    return dedent(f"""\
    kind: AdaptiveDialog
    startBehavior: CancelOtherTopics
    beginDialog:
      kind: OnRecognizedIntent
      id: main
      intent:
        displayName: Goodbye
        includeInOnSelectIntent: false
        triggerQueries:
          - Bye
          - Bye for now
          - Good bye
          - See you later
          - Goodbye

      actions:
        - kind: Question
          id: question_endConvo
          variable: Topic.EndConversation
          prompt: Would you like to end our conversation?
          entity: BooleanPrebuiltEntity

        - kind: ConditionGroup
          id: condition_end
          conditions:
            - id: conditionItem_yes
              condition: =Topic.EndConversation = true
              actions:
                - kind: SendActivity
                  id: sendMessage_bye
                  activity: Goodbye! Your memories are safely stored for next time. \\U0001f44b

                - kind: EndConversation
                  id: endConversation_bye

            - id: conditionItem_no
              condition: =Topic.EndConversation = false
              actions:
                - kind: SendActivity
                  id: sendMessage_continue
                  activity: Go ahead. I'm listening.
    """)


def _topic_thankyou_yaml() -> str:
    return dedent("""\
    kind: AdaptiveDialog
    beginDialog:
      kind: OnRecognizedIntent
      id: main
      intent:
        displayName: Thank you
        includeInOnSelectIntent: false
        triggerQueries:
          - thanks
          - thank you
          - thanks so much
          - ty

      actions:
        - kind: SendActivity
          id: sendMessage_welcome
          activity: You're welcome! Let me know if you need anything else.
    """)


def _gpt_default_yaml(bot_schema: str) -> str:
    return dedent(f"""\
    kind: GptComponentMetadata
    displayName: Memory Agent
    responseInstructions:
    gptCapabilities:
      webBrowsing: false
      codeInterpreter: false

    aISettings:
      model: {{}}
      extensionData:
        lastUsedCustomModel: {{}}
    """)


def _gpt_default_instructions_yaml() -> str:
    """The Gpt component data file (componenttype 12)."""
    return dedent("""\
    kind: Gpt
    settings:
      modelConfiguration:
        instructions: >
          You are a Memory Agent for the CommunityRAPP platform. You help users store and recall
          important information like facts, preferences, insights, and tasks. You have persistent
          memory that carries across conversations. When users share information worth remembering,
          proactively offer to save it. When context is relevant, recall stored memories to provide
          personalized assistance. You support both shared memory (accessible to all users) and
          user-specific memory (private to each user).
    """)


def _bot_configuration_json() -> str:
    return json.dumps({
        "$kind": "BotConfiguration",
        "channels": [
            {"$kind": "ChannelDefinition", "channelId": "MsTeams"},
            {"$kind": "ChannelDefinition", "channelId": "Microsoft365Copilot"}
        ],
        "settings": {"GenerativeActionsEnabled": False},
        "publishOnImport": True,
        "gPTSettings": {
            "$kind": "GPTSettings",
            "defaultSchemaName": "crapp_memoryagent.gpt.default"
        },
        "aISettings": {
            "$kind": "AISettings",
            "useModelKnowledge": True,
            "isSemanticSearchEnabled": True,
            "contentModeration": "High"
        }
    }, indent=2)


# ---------------------------------------------------------------------------
# Main generation logic
# ---------------------------------------------------------------------------

def generate_solution(
    function_url: str,
    function_key: str,
    output_path: str,
    solution_name: str,
    prefix: str,
) -> None:
    """Build the Power Platform solution ZIP."""

    function_url = function_url.rstrip("/")
    bot_schema = f"{prefix}_memoryagent"

    # Deterministic workflow GUIDs
    wf_main_id = guid_lower(f"{solution_name}.workflow.TalkToMemoryAgent")
    wf_read_id = guid_lower(f"{solution_name}.workflow.ReadMemory")
    wf_write_id = guid_lower(f"{solution_name}.workflow.WriteMemory")
    wf_main_upper = guid_upper(f"{solution_name}.workflow.TalkToMemoryAgent")
    wf_read_upper = guid_upper(f"{solution_name}.workflow.ReadMemory")
    wf_write_upper = guid_upper(f"{solution_name}.workflow.WriteMemory")

    workflow_guids = [
        ("Talk to Memory Agent", wf_main_id),
        ("Read Memory", wf_read_id),
        ("Write Memory", wf_write_id),
    ]

    workflows_meta = [
        {
            "name": "Talk to Memory Agent",
            "description": "Main flow: Copilot Studio Skills trigger to Memory Agent Azure Function.",
            "id": wf_main_id,
            "json_path": f"/Workflows/TalkToMemoryAgent-{wf_main_upper}.json",
        },
        {
            "name": "Read Memory",
            "description": "Read stored memories via ContextMemory agent.",
            "id": wf_read_id,
            "json_path": f"/Workflows/ReadMemory-{wf_read_upper}.json",
        },
        {
            "name": "Write Memory",
            "description": "Store new memories via ManageMemory agent.",
            "id": wf_write_id,
            "json_path": f"/Workflows/WriteMemory-{wf_write_upper}.json",
        },
    ]

    # Bot component definitions: (suffix, display_name, yaml_func, component_type)
    topic_defs = [
        ("topic.MAIN", "MAIN", lambda: _topic_main_yaml(bot_schema, wf_main_id), 9),
        ("topic.ReadMemory", "ReadMemory", lambda: _topic_read_memory_yaml(bot_schema, wf_read_id), 9),
        ("topic.WriteMemory", "WriteMemory", lambda: _topic_write_memory_yaml(bot_schema, wf_write_id), 9),
        ("topic.ConversationStart", "ConversationStart", lambda: _topic_conversation_start_yaml(bot_schema), 9),
        ("topic.Fallback", "Fallback", lambda: _topic_fallback_yaml(bot_schema), 9),
        ("topic.Escalate", "Escalate", lambda: _topic_escalate_yaml(bot_schema), 9),
        ("topic.OnError", "OnError", lambda: _topic_on_error_yaml(bot_schema), 9),
        ("topic.Goodbye", "Goodbye", lambda: _topic_goodbye_yaml(bot_schema), 9),
        ("topic.ThankYou", "ThankYou", lambda: _topic_thankyou_yaml, 9),
        ("gpt.default", "GPT Default", lambda: _gpt_default_yaml(bot_schema), 12),
    ]

    # Collect all data file paths for [Content_Types].xml
    data_parts = []
    files: dict[str, str | bytes] = {}

    # --- solution.xml ---
    files["solution.xml"] = _solution_xml(
        solution_name,
        "CommunityRAPP Memory Agent",
        prefix,
        workflow_guids,
    )

    # --- customizations.xml ---
    files["customizations.xml"] = _customizations_xml(prefix, workflows_meta)

    # --- Workflow JSON files ---
    files[f"Workflows/TalkToMemoryAgent-{wf_main_upper}.json"] = json.dumps(
        _talk_to_memory_agent_flow(function_url, function_key, prefix), indent=2
    )
    files[f"Workflows/ReadMemory-{wf_read_upper}.json"] = json.dumps(
        _read_memory_flow(function_url, function_key), indent=2
    )
    files[f"Workflows/WriteMemory-{wf_write_upper}.json"] = json.dumps(
        _write_memory_flow(function_url, function_key), indent=2
    )

    # --- Bot definition ---
    files[f"bots/{bot_schema}/bot.xml"] = _bot_xml(bot_schema)
    files[f"bots/{bot_schema}/configuration.json"] = _bot_configuration_json()

    # --- Bot components ---
    for suffix, display, yaml_fn, comp_type in topic_defs:
        schema = f"{bot_schema}.{suffix}"
        comp_dir = f"botcomponents/{schema}"

        files[f"{comp_dir}/botcomponent.xml"] = _botcomponent_xml(
            schema, display, bot_schema, comp_type
        )

        yaml_content = yaml_fn() if callable(yaml_fn) else yaml_fn
        if callable(yaml_content):
            yaml_content = yaml_content()
        files[f"{comp_dir}/data"] = yaml_content
        data_parts.append(f"botcomponents/{schema}/data")

    # --- [Content_Types].xml ---
    files["[Content_Types].xml"] = _content_types_xml(data_parts)

    # Build ZIP with fixed timestamps for deterministic output
    fixed_date = (2025, 1, 1, 0, 0, 0)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for path, content in sorted(files.items()):
            if isinstance(content, str):
                content = content.encode("utf-8")
            info = zipfile.ZipInfo(filename=path, date_time=fixed_date)
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, content)

    with open(output_path, "wb") as f:
        f.write(buf.getvalue())

    # --- Summary ---
    print(f"\n{'='*60}")
    print(f"  Power Platform Solution Generated Successfully!")
    print(f"{'='*60}")
    print(f"\n  Output:   {output_path}")
    print(f"  Solution: {solution_name}")
    print(f"  Version:  1.0.0.0")
    print(f"  Managed:  No (unmanaged)")
    print(f"\n  Flows:")
    for wf in workflows_meta:
        print(f"    - {wf['name']} ({wf['id']})")
    print(f"\n  Bot: Memory Agent ({bot_schema})")
    print(f"  Channels: Microsoft Teams, Microsoft 365 Copilot")
    print(f"\n  Topics:")
    for suffix, display, _, _ in topic_defs:
        print(f"    - {display} ({bot_schema}.{suffix})")
    print(f"\n  Function URL: {function_url}")
    if function_key and function_key != "YOUR_FUNCTION_KEY_HERE":
        print(f"  Function Key: {'*' * 8}...{function_key[-4:]}")
    else:
        print(f"  Function Key: (not set — update in Power Automate after import)")

    print(f"\n{'='*60}")
    print(f"  Import Instructions:")
    print(f"{'='*60}")
    print(f"\n  Option 1 — PAC CLI:")
    print(f"    pac auth create --environment <your-env-url>")
    print(f"    pac solution import --path {output_path}")
    print(f"\n  Option 2 — Power Apps Portal:")
    print(f"    1. Go to https://make.powerapps.com")
    print(f"    2. Solutions → Import solution")
    print(f"    3. Upload {output_path}")
    print(f"    4. Configure connection references when prompted")
    print(f"\n  Post-Import Steps:")
    print(f"    1. Open the imported solution")
    print(f"    2. Configure the Office 365 Users connection reference")
    if not function_key or function_key == "YOUR_FUNCTION_KEY_HERE":
        print(f"    3. Edit each flow and update the functionKey variable")
    print(f"    4. Turn on all three Power Automate flows")
    print(f"    5. Publish the Memory Agent bot in Copilot Studio")
    print(f"    6. Deploy to Teams / M365 Copilot channels")
    print()


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a Power Platform solution ZIP for a Copilot Studio Memory Agent.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent("""\
        Examples:
          python utils/generate_memory_agent_solution.py \\
              --function-url https://rapp-xyz.azurewebsites.net

          python utils/generate_memory_agent_solution.py \\
              --function-url https://rapp-xyz.azurewebsites.net \\
              --function-key abc123== \\
              --output MyAgent.zip
        """),
    )
    parser.add_argument(
        "--function-url",
        required=True,
        help="Azure Function base URL (e.g., https://rapp-xyz.azurewebsites.net)",
    )
    parser.add_argument(
        "--function-key",
        default="YOUR_FUNCTION_KEY_HERE",
        help="Function key for auth (can update in Power Automate later)",
    )
    parser.add_argument(
        "--output",
        default="CommunityRAPPMemoryAgent_1_0_0_0.zip",
        help="Output ZIP path (default: CommunityRAPPMemoryAgent_1_0_0_0.zip)",
    )
    parser.add_argument(
        "--solution-name",
        default="CommunityRAPPMemoryAgent",
        help="Solution unique name (default: CommunityRAPPMemoryAgent)",
    )
    parser.add_argument(
        "--publisher-prefix",
        default="crapp",
        help="Publisher customization prefix (default: crapp)",
    )

    args = parser.parse_args()

    try:
        generate_solution(
            function_url=args.function_url,
            function_key=args.function_key,
            output_path=args.output,
            solution_name=args.solution_name,
            prefix=args.publisher_prefix,
        )
    except Exception as exc:
        print(f"\nError: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
