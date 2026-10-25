from agents.basic_agent import BasicAgent
import requests

class HackerNewsAgent(BasicAgent):
    def __init__(self):
        self.name = "HackerNewsAgent"
        self.metadata = {
            "name": self.name,
            "description": "Fetches the latest top posts from Hacker News",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "The number of top posts to fetch"
                    },
                },
                "required": ["limit"]
            }
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, limit):
        top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        item_url = "https://hacker-news.firebaseio.com/v0/item/{}.json"
        
        # Fetch the top stories IDs
        response = requests.get(top_stories_url)
        top_story_ids = response.json()[:limit]
        
        top_posts = []
        
        # Fetch details of each top story
        for story_id in top_story_ids:
            response = requests.get(item_url.format(story_id))
            top_posts.append(response.json())
        
        return str(top_posts)