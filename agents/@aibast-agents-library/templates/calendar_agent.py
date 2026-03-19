from agents.basic_agent import BasicAgent

class CalendarAgent(BasicAgent):
    def __init__(self):
        self.name = "Calendar"
        self.metadata = {
            "name": self.name,
            "description": "DEMO SCRIPT: When Taylor says 'Perfect. Set up a meeting with Sarah for this week' - call this agent to schedule the meeting. Handles meeting scheduling with intelligent time suggestions and conflict resolution. Returns confirmation of meeting request sent with proposed times based on attendee availability.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        return """📅 **Meeting Request Sent Successfully**

✉️ **Meeting Invitation:**
• **To:** Sarah Chen (sarah.chen@contoso.com)
• **From:** Taylor (You)
• **Subject:** Q1 Product Launch Legal Review
• **Status:** ✅ Sent - Awaiting response

⏰ **Proposed Time Options:**
```
Option 1: Tuesday, March 19 at 2:00 PM (60 minutes)
├── Your calendar: ✅ Available
├── Sarah's calendar: ✅ Available  
└── Conference room: "Legal Conference Room B" reserved

Option 2: Thursday, March 21 at 10:00 AM (60 minutes)  
├── Your calendar: ✅ Available
├── Sarah's calendar: ✅ Available
└── Conference room: "Executive Meeting Room 3" reserved
```

📋 **Meeting Agenda (Auto-generated):**
• Review Q1 product launch legal requirements
• Discuss timeline and regulatory compliance needs
• Identify potential roadblocks and mitigation strategies
• Define next steps and deliverables

🔗 **Meeting Details:**
• **Teams Link:** [Join Microsoft Teams Meeting](https://teams.microsoft.com/l/meetup-join/legal-review-q1)
• **Location:** Hybrid (Conference room + Teams)
• **Attachments:** 
  - [Q1 Product Launch Overview.pdf](https://contoso.sharepoint.com/sites/ProductTeam/Q1-overview.pdf)
  - [Previous Legal Review Notes.docx](https://contoso.sharepoint.com/legal/previous-notes.docx)

📊 **Smart Scheduling Insights:**
• Sarah typically prefers Tuesday afternoons for project reviews
• Both attendees are most productive during these time slots
• Legal conference room has whiteboard for collaborative planning
• No competing priorities detected for either time option

🔔 **Next Steps:**
• Sarah will receive calendar invite with both options
• Auto-reminder set for 24 hours before confirmed meeting
• Meeting materials will be shared automatically once confirmed
• Follow-up tasks will be tracked in your project management system

💡 **Pro Tip:** Based on past patterns, Sarah usually responds to meeting requests within 4 hours during business days."""