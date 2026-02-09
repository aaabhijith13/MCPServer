from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv

load_dotenv()
class NewsConfig(BaseModel):
    api_token: str

class NEWSAPI(NewsConfig):
    query: str = ""  # default empty

    @property
    def top_stories(self) -> str:
        return f"https://api.thenewsapi.com/v1/news/top?api_token={self.api_token}&locale=us&search={self.query}"

    @property
    def all_news(self) -> str:
        return f"https://api.thenewsapi.com/v1/news/all?api_token={self.api_token}&search={self.query}"

    def search_news(self, endpoint: str, query: str) -> dict:
        self.query = query  # update query for URL
        req = requests.get(endpoint)
        req.raise_for_status()  # optional: raise error if request fails
        return req.json()


if __name__ == "__main__":
    news_api = NEWSAPI(api_token=os.getenv("NEWS_API_KEY"))
    
    result = news_api.search_news(news_api.top_stories, "MU stock price")
    print(result)
    print(news_api.top_stories)
