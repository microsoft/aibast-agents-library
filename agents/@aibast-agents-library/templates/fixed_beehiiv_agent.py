from agents.basic_agent import BasicAgent
import requests
import xml.etree.ElementTree as ET

class BeehiivRSSNewsAgent(BasicAgent):
    def __init__(self):
        self.name = "BeehiivRSSNews"
        self.metadata = {
            "name": self.name,
            "description": "Fetches and parses recent news from the beehiiv RSS feed at https://rss.beehiiv.com/feeds/bbrRpKlcfI.xml. Returns the N latest news items as a summary with title and link.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of news items to fetch (up to 10 recommended)"
                    }
                },
                "required": ["limit"]
            }
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, limit):
        url = "https://rss.beehiiv.com/feeds/bbrRpKlcfI.xml"
        resp = requests.get(url)
        if resp.status_code != 200:
            return f"Failed to fetch RSS feed: {resp.status_code}"
        
        try:
            xmlroot = ET.fromstring(resp.content)
            items = xmlroot.findall("./channel/item")
            out = []
            
            for i, item in enumerate(items[:int(limit)]):
                title = item.find("title").text if item.find("title") is not None else "No Title"
                link = item.find("link").text if item.find("link") is not None else "No Link"
                out.append(f"{i+1}. {title}\n{link}")
            
            return "\n\n".join(out)
            
        except ET.ParseError as e:
            return f"Failed to parse RSS feed: {str(e)}"
        except Exception as e:
            return f"An error occurred: {str(e)}"