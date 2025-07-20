import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

@dataclass
class Config:
    tavily_api_key: str
    deepseek_api_key: Optional[str] = None
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"
    max_search_results: int = 10
    max_conversation_history: int = 20

def load_config() -> Config:
    """Load configuration from environment variables"""
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Tavily API key (required)
    tavily_key = os.getenv("TAVILY_API_KEY")
    if not tavily_key:
        raise ValueError(
            "TAVILY_API_KEY not found in environment variables. "
            "Please copy .env.example to .env and fill in your API keys."
        )
    
    # DeepSeek API key (required)
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    if not deepseek_key:
        raise ValueError(
            "DEEPSEEK_API_KEY not found in environment variables. "
            "Please copy .env.example to .env and fill in your API keys."
        )
    
    return Config(
        tavily_api_key=tavily_key,
        deepseek_api_key=deepseek_key,
        deepseek_base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        deepseek_model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        max_search_results=int(os.getenv("MAX_SEARCH_RESULTS", "10")),
        max_conversation_history=int(os.getenv("MAX_CONVERSATION_HISTORY", "20"))
    )