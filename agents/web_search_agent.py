from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
from typing import Dict, Any
from utils.models import model_manager
from config.settings import settings

app = FastAPI()

class WebSearchAgent:
    def __init__(self):
        self.name = "Web Search Agent"
        self.description = "Searches the web for information using DuckDuckGo and LLM analysis"
    
    async def search_web(self, query: str) -> str:
        """Perform web search using DuckDuckGo API and LLM synthesis"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.duckduckgo.com/",
                    params={"q": query, "format": "json", "no_html": "1", "skip_disambig": "1"}
                )
                data = response.json()
                
                # Collect search results
                results = []
                if data.get("Abstract"):
                    results.append(f"Abstract: {data['Abstract']}")
                if data.get("Answer"):
                    results.append(f"Answer: {data['Answer']}")
                
                # Get related topics
                for topic in data.get("RelatedTopics", [])[:3]:
                    if isinstance(topic, dict) and topic.get("Text"):
                        results.append(f"Related: {topic['Text']}")
                
                if results:
                    # Use LLM to synthesize the search results
                    context = "\n".join(results)
                    prompt = f"""Based on the following search results, provide a comprehensive answer to the query: "{query}"

Search Results:
{context}

Please synthesize this information into a clear, informative response that addresses the user's query."""

                    response = model_manager.azure_llm.invoke(prompt)
                    if hasattr(response, 'content'):
                        return response.content
                    return str(response)
                else:
                    # No search results - do not use LLM fallback
                    return "No results found for your query."
                
        except Exception as e:
            return f"Search failed: {str(e)}"

web_search_agent = WebSearchAgent()

@app.get("/.well-known/agent.json")
async def agent_card():
    return {
        "name": web_search_agent.name,
        "description": web_search_agent.description,
        "version": "1.0.0",
        "capabilities": ["web_search", "information_retrieval", "llm_synthesis"],
        "endpoints": {"a2a": "/"}
    }

@app.post("/")
async def handle_a2a(request: Request):
    data = await request.json()
    method = data.get("method")
    params = data.get("params", {})
    
    if method == "sendTask":
        user_message = params.get("message", {}).get("parts", [{}])[0].get("text", "")
        result = await web_search_agent.search_web(user_message)
        
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
    uvicorn.run(app, host="0.0.0.0", port=5101)