from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from utils.models import model_manager
from config.settings import settings
import random

app = FastAPI()

class PredictorAgent:
    def __init__(self):
        self.name = "Predictor Agent"
        self.description = "Makes predictions and forecasts based on patterns and data"
    
    def make_prediction(self, query: str) -> str:
        """Use LLM to make predictions based on the query"""
        prompt = f"""The following query requires a prediction or forecast:

Query:
{query}

Please provide a prediction or forecast based on available patterns and data."""
        
        response = model_manager.azure_llm.invoke(prompt)
        if hasattr(response, 'content'):
            return response.content
        return str(response)

predictor_agent = PredictorAgent()

@app.get("/.well-known/agent.json")
async def agent_card():
    return {
        "name": predictor_agent.name,
        "description": predictor_agent.description,
        "version": "1.0.0",
        "capabilities": ["prediction", "forecasting", "llm_analysis"],
        "endpoints": {"a2a": "/"}
    }

@app.post("/")
async def handle_a2a(request: Request):
    data = await request.json()
    method = data.get("method")
    params = data.get("params", {})
    
    if method == "sendTask":
        user_message = params.get("message", {}).get("parts", [{}])[0].get("text", "")
        result = predictor_agent.make_prediction(user_message)
        
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
    uvicorn.run(app, host="0.0.0.0", port=5107)