from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
from bs4 import BeautifulSoup
from utils.models import model_manager
from config.settings import settings
import re

app = FastAPI()

class WebScraperAgent:
    def __init__(self):
        self.name = "Web Scraper Agent"
        self.description = "Scrapes content from web pages and extracts meaningful information"
    
    def extract_url(self, text: str) -> str:
        # Find the first URL in the text
        match = re.search(r'(https?://\S+)', text)
        return match.group(1) if match else None

    async def scrape_url(self, url: str) -> str:
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"}
            async with httpx.AsyncClient(headers=headers) as client:
                response = await client.get(url, timeout=60)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Get text content
                text = soup.get_text()
                text = ' '.join(text.split())  # Clean up whitespace
                
                # Instead, just return the scraped text (up to 2000 chars)
                return text[:2000] if text else "No content found on the page."
                
        except httpx.TimeoutException:
            return f"Request to {url} timed out. Please try again later or check the site."
        except Exception as e:
            return f"Failed to scrape {url}: {str(e)}"
    
    async def scrape_and_answer(self, url: str, query: str = None) -> str:
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"}
            async with httpx.AsyncClient(headers=headers) as client:
                response = await client.get(url, timeout=60)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                for script in soup(["script", "style"]):
                    script.decompose()
                text = soup.get_text()
                text = ' '.join(text.split())
                if not text:
                    return "No content found on the page."
                if query:
                    prompt = f"""You are given the following web page content scraped from {url}:

{text[:2000]}

User request: {query}

Based on the content above, please provide a comprehensive response that addresses the user's request. If the user is asking for a summary, provide a concise summary of the key information. If they want specific information, extract and present the relevant details. Focus on the actual content from the webpage and ignore any error messages or irrelevant context."""
                    response = model_manager.azure_llm.invoke(prompt)
                    if hasattr(response, 'content'):
                        return response.content
                    return str(response)
                return text[:2000]
        except httpx.TimeoutException:
            return f"Request to {url} timed out. Please try again later or check the site."
        except Exception as e:
            return f"Failed to scrape {url}: {str(e)}"

web_scraper_agent = WebScraperAgent()

@app.get("/.well-known/agent.json")
async def agent_card():
    return {
        "name": web_scraper_agent.name,
        "description": web_scraper_agent.description,
        "version": "1.0.0",
        "capabilities": ["web_scraping", "content_extraction", "llm_analysis"],
        "endpoints": {"a2a": "/"}
    }

@app.post("/")
async def handle_a2a(request: Request):
    data = await request.json()
    method = data.get("method")
    params = data.get("params", {})
    
    if method == "sendTask":
        # Prefer direct URL param if present
        url = params.get("url")
        user_message = params.get("message", {}).get("parts", [{}])[0].get("text", "")
        
        # Get original query from orchestrator context
        original_query = params.get("originalQuery", user_message)
        
        if not url:
            url = web_scraper_agent.extract_url(user_message)
        if not url and original_query != user_message:
            # Try extracting from original query if current message has no URL
            url = web_scraper_agent.extract_url(original_query)
            print(f"[WebScraper] Extracted URL from original query: {url}")
            
        if not url:
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": data.get("id"),
                "result": {
                    "message": {
                        "role": "agent",
                        "parts": [{"type": "text", "text": "No valid URL found in your request. Please provide a URL in the URL field or in your message."}]
                    }
                }
            })
        
        # Use original query for context when available, otherwise fall back to user_message
        query_for_context = original_query if original_query != user_message else user_message
        result = await web_scraper_agent.scrape_and_answer(url, query_for_context)
        
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": data.get("id"),
            "result": {
                "message": {
                    "role": "agent",
                    "parts": [{"type": "text", "text": result}]
                }
            }
        })
    
    return JSONResponse({"error": "Invalid method"}, status_code=400)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5102)