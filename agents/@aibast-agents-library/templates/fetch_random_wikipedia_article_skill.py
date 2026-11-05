
from agents.basic_agent import BasicAgent
import requests
import json

class FetchRandomWikipediaArticleSkill(BasicSkill):
    def __init__(self):
        self.name = "FetchRandomWikipediaArticle"
        self.metadata = {
            "name": self.name,
            "description": "Fetches a random article from Wikipedia",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Parameter limit of type int", "default": 1}
                },
                "required": ['limit']
            }
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        """
        Fetches a random article from Wikipedia

        Args:
            limit (int = 1): Description of limit.

        Returns:
            str: The result of the skill operation.
        """
        try:
            limit = kwargs.get('limit', 1)
            limit = int(limit) if limit is not None else None
            import requests
            
            # Define the Wikipedia API endpoint for fetching a random article
            WIKIPEDIA_RANDOM_URL = "https://en.wikipedia.org/api/rest_v1/page/random/title"
            
            # Define the function to fetch a random Wikipedia article
            def fetch_random_wikipedia_article(limit: int = 1):
                results = []
                for _ in range(limit):
                    response = requests.get(WIKIPEDIA_RANDOM_URL)
                    if response.status_code == 200:
                        data = response.json()
                        title = data["items"][0]["title"]
                        results.append({"title": title, "url": f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"})
                    else:
                        results.append({"error": "Failed to fetch random article"})
                return results
        except Exception as e:
            return f"An error occurred while executing the FetchRandomWikipediaArticle skill: {str(e)}"

    
