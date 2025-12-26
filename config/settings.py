from typing import Dict, Any
import os

class Settings:
    """Application settings and configuration"""
    
    # Agent Configuration
    MAX_SEARCH_RESULTS: int = 5
    MAX_SCRAPING_PAGES: int = 5
    
    # UI Configuration
    PAGE_TITLE: str = "A2A Multi-Agent Demo"
    PAGE_ICON: str = "🤖"
    
    @classmethod
    def get_agent_prompts(cls) -> Dict[str, str]:
        """Return agent-specific prompts"""
        return {
            "web_search": """You are a web search specialist. Your task is to search for relevant information on the web based on user queries. 
            Provide accurate, up-to-date information with proper citations.""",
            
            "web_scraper": """You are a web scraping expert. Extract meaningful content from web pages, focusing on the most relevant information. 
            Structure the extracted data clearly and remove unnecessary elements.""",
            
            "file_reader": """You are a file processing expert. Read and analyze various file formats, extract key information, 
            and present it in a structured manner.""",
            
            "summarizer": """You are a summarization expert. Create concise, informative summaries that capture the essential points 
            while maintaining context and clarity.""",
            
            "elaborator": """You are an elaboration specialist. Expand on topics with detailed explanations, examples, and additional context 
            to provide comprehensive understanding.""",
            
            "calculator": """You are a mathematical computation expert. Perform accurate calculations, solve mathematical problems, 
            and provide step-by-step solutions when needed.""",
            
            "predictor": """You are a prediction and analysis expert. Analyze data patterns, make informed predictions, 
            and provide insights based on available information."""
        }

settings = Settings()