from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from utils.models import model_manager
from config.settings import settings

app = FastAPI()

class SummarizerAgent:
    def __init__(self):
        self.name = "Summarizer Agent"
        self.description = "Summarizes long text content into concise summaries"
    
    def summarize_text(self, text: str) -> str:
        """Use LLM to summarize the given text"""
        prompt = f"""The following text needs to be summarized:

        Text:
        {text[:2000]}  # Limit to 2000 characters

        Please provide a concise summary that captures the key points."""
        
        response = model_manager.azure_llm.invoke(prompt)
        if hasattr(response, 'content'):
            return response.content
        return str(response)

summarizer_agent = SummarizerAgent()

@app.get("/.well-known/agent.json")
async def agent_card():
    return {
        "name": summarizer_agent.name,
        "description": summarizer_agent.description,
        "version": "1.0.0",
        "capabilities": ["text_summarization", "llm_analysis"],
        "endpoints": {"a2a": "/"}
    }

@app.post("/")
async def handle_a2a(request: Request):
    data = await request.json()
    method = data.get("method")
    params = data.get("params", {})
    
    if method == "sendTask":
        user_message = params.get("message", {}).get("parts", [{}])[0].get("text", "")
        result = summarizer_agent.summarize_text(user_message)
        
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
    uvicorn.run(app, host="0.0.0.0", port=5104)