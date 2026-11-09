from skills.basic_agent import BasicSkill
import requests
import json

class MotivationalQuoteSkill(BasicSkill):
    def __init__(self):
        self.name = "MotivationalQuote"
        self.metadata = {
            "name": self.name,
            "description": "Fetches a motivational quote from the Forismatic API, formats it, and returns the information.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
        super().__init__(name=self.name, metadata=self.metadata)
        self.last_quote = None

    def perform(self, **kwargs):
        """
        Fetches a motivational quote from the Forismatic API.

        Returns:
            str: A formatted string containing the quote and its author.
        """
        try:
            response = requests.get("https://api.forismatic.com/api/1.0/?method=getQuote&lang=en&format=jsonp&jsonp=?")
            data = json.loads(response.text[2:-1])  # Remove the (? and ?)
            quote = data['quoteText'].strip()
            author = data['quoteAuthor'].strip() or "Unknown"
            formatted_quote = f"Quote: {quote}\nAuthor: {author}"
            self.last_quote = formatted_quote
            return formatted_quote

        except Exception as e:
            return f"An error occurred while executing the MotivationalQuote skill: {str(e)}"