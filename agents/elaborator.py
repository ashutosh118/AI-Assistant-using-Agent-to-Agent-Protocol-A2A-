from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from utils.models import model_manager
from config.settings import settings

app = FastAPI()

class ElaboratorAgent:
    def __init__(self):
        self.name = "Elaborator Agent"
        self.description = "Provides detailed explanations for given topics"
    
    def elaborate_topic(self, topic: str) -> str:
        """Use LLM to elaborate on the given topic"""
        prompt = f"""The following topic needs to be elaborated on:

Topic:
{topic}

Please provide a detailed explanation, including examples and additional context."""
        
        response = model_manager.azure_llm.invoke(prompt)
        if hasattr(response, 'content'):
            return response.content
        return str(response)

elaborator_agent = ElaboratorAgent()

@app.get("/.well-known/agent.json")
async def agent_card():
    return {
        "name": elaborator_agent.name,
        "description": elaborator_agent.description,
        "version": "1.0.0",
        "capabilities": ["topic_elaboration", "detailed_explanation", "llm_analysis"],
        "endpoints": {"a2a": "/"}
    }

@app.post("/")
async def handle_a2a(request: Request):
    data = await request.json()
    method = data.get("method")
    params = data.get("params", {})
    
    if method == "sendTask":
        user_message = params.get("message", {}).get("parts", [{}])[0].get("text", "")
        result = elaborator_agent.elaborate_topic(user_message)
        
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
    uvicorn.run(app, host="0.0.0.0", port=5105)