from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse
import httpx
import uuid
import asyncio
import traceback

app = FastAPI()

tasks = {}

# List of agent endpoints (excluding orchestrator itself)
AGENT_ENDPOINTS = [
    {"name": "Web Search Agent", "url": "http://localhost:5101/"},
    {"name": "Web Scraper Agent", "url": "http://localhost:5102/"},
    {"name": "File Reader Agent", "url": "http://localhost:5103/"},
    {"name": "Summarizer Agent", "url": "http://localhost:5104/"},
    {"name": "Elaborator Agent", "url": "http://localhost:5105/"},
    {"name": "Calculator Agent", "url": "http://localhost:5106/"},
    {"name": "Predictor Agent", "url": "http://localhost:5107/"},
]

async def fetch_agent_cards():
    cards = []
    print(f"[Orchestrator] Fetching agent cards from {len(AGENT_ENDPOINTS)} endpoints...")
    async with httpx.AsyncClient() as client:
        for agent in AGENT_ENDPOINTS:
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    url = agent["url"] + ".well-known/agent.json"
                    print(f"[Orchestrator] Fetching agent card from: {url} (attempt {attempt + 1})")
                    resp = await client.get(url, timeout=10)
                    print(f"[Orchestrator] Response from {agent['name']}: {resp.status_code}")
                    if resp.status_code == 200:
                        card = resp.json()
                        card["url"] = agent["url"]
                        cards.append(card)
                        print(f"[Orchestrator] Successfully added card for {agent['name']}")
                        break
                    else:
                        print(f"[Orchestrator] Failed to get card for {agent['name']}: {resp.status_code}")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(2)
                except Exception as e:
                    print(f"[Orchestrator] Exception fetching card for {agent['name']} (attempt {attempt + 1}): {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2)
                    continue
    print(f"[Orchestrator] Total cards fetched: {len(cards)}")
    return cards

def match_agents(query, agent_cards):
    # Enhanced keyword-based matching for multi-agent orchestration
    query_lower = query.lower()
    selected = []
    print(f"[Orchestrator] Matching query '{query}' against {len(agent_cards)} agent cards")
    
    for card in agent_cards:
        print(f"[Orchestrator] Checking agent: {card.get('name', 'Unknown')}")
        # Handle both string and dict capabilities
        caps_raw = card.get("capabilities", [])
        caps = []
        for c in caps_raw:
            if isinstance(c, str):
                caps.append(c)
            elif isinstance(c, dict):
                caps.extend([str(v).lower() for v in c.values()])
        desc = card.get("description", "").lower()
        caps_desc = " ".join(caps) + " " + desc
        print(f"[Orchestrator] Agent capabilities/desc: {caps_desc}")
        
        # Check for File Reader Agent
        if (any(word in query_lower for word in ["uploaded", "documents", "files", "pdf", "csv", "document", "file"]) and 
            any(cap in caps_desc for cap in ["file_reading", "vector_search", "file reading"])):
            selected.append(card)
            print(f"[Orchestrator] Selected {card['name']} for file reading")
        # Check for Summarizer Agent  
        elif (any(word in query_lower for word in ["summarize", "summary", "summarization"]) and 
              any(cap in caps_desc for cap in ["text_summarization", "summarization", "summarize"])):
            selected.append(card)
            print(f"[Orchestrator] Selected {card['name']} for summarization")
        # Check for Elaborator Agent
        elif (any(word in query_lower for word in ["elaborate", "explain", "detailed", "detail", "explanation"]) and 
              any(cap in caps_desc for cap in ["topic_elaboration", "detailed_explanation", "elaboration", "elaborate"])):
            selected.append(card)
            print(f"[Orchestrator] Selected {card['name']} for elaboration")
        # Check for Predictor Agent
        elif (any(word in query_lower for word in ["predict", "forecast", "future", "trends"]) and 
              any(cap in caps_desc for cap in ["prediction", "forecasting", "predict"])):
            selected.append(card)
            print(f"[Orchestrator] Selected {card['name']} for prediction")
        # Check for Calculator Agent  
        elif (any(word in query_lower for word in ["calculate", "result", "math", "percentage", "compute"]) and 
              any(cap in caps_desc for cap in ["mathematical_calculations", "calculation", "calculate"])):
            selected.append(card)
            print(f"[Orchestrator] Selected {card['name']} for calculation")
        # Check for Web Search Agent
        elif (any(word in query_lower for word in ["search", "news", "find"]) and 
              any(cap in caps_desc for cap in ["web_search", "search", "information_retrieval"])):
            selected.append(card)
            print(f"[Orchestrator] Selected {card['name']} for search")
        # Check for Web Scraper Agent
        elif (any(word in query_lower for word in ["scrape", "extract", "url", "http"]) and 
              any(cap in caps_desc for cap in ["web_scraping", "scraping", "content_extraction"])):
            selected.append(card)
            print(f"[Orchestrator] Selected {card['name']} for scraping")
    
    print(f"[Orchestrator] Initial selection: {len(selected)} agents")
    
    # Fallback: if nothing matched, use Web Scraper Agent as default
    if not selected:
        print(f"[Orchestrator] No agents matched, looking for fallback...")
        for card in agent_cards:
            if "web scraper" in card["name"].lower():
                selected.append(card)
                print(f"[Orchestrator] Selected fallback: {card['name']}")
                break
        # If still nothing, select the first available agent
        if not selected and agent_cards:
            selected.append(agent_cards[0])
            print(f"[Orchestrator] Selected first available: {agent_cards[0]['name']}")
    
    print(f"[Orchestrator] Final selection: {[card['name'] for card in selected]}")
    return selected

@app.get("/.well-known/agent.json")
async def agent_card():
    return {
        "name": "Orchestrator Agent",
        "description": "Orchestrates multi-agent workflows, delegates tasks, and manages lifecycle.",
        "version": "1.0.0",
        "capabilities": ["orchestration", "agent_discovery", "delegation", "user_input_handling"],
        "endpoints": {"a2a": "/"}
    }

async def delegate_to_agents(task_id, user_message):
    # Wait for agents to be ready
    print(f"[Orchestrator] Waiting for agents to be ready...")
    await asyncio.sleep(15)  # Give agents more time to start if they just launched
    
    agent_cards = await fetch_agent_cards()
    selected_agents = match_agents(user_message, agent_cards)
    print(f"[Orchestrator] Selected agents: {[agent['name'] for agent in selected_agents]}")
    steps = [{"agent": card["name"], "status": "pending"} for card in selected_agents]
    artifacts = []
    input_text = user_message
    accumulated_content = []  # Store substantial content from all agents
    
    for idx, card in enumerate(selected_agents):
        print(f"[Orchestrator] Delegating to {card['name']} at {card['url']}")
        steps[idx]["status"] = "running"
        tasks[task_id]["status"] = f"{card['name']} running"
        tasks[task_id]["steps"] = steps  # Update steps in real-time
        
        # For Summarizer Agent, use accumulated substantial content instead of just previous agent output
        if "summarizer" in card["name"].lower() and accumulated_content:
            # Find the most substantial content for summarization
            substantial_content = max(accumulated_content, key=len) if accumulated_content else input_text
            actual_input = substantial_content
        else:
            actual_input = input_text
            
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "sendTask",
                "params": {
                    "id": f"subtask-{idx}",
                    "sessionId": task_id,
                    "acceptedOutputModes": ["text"],
                    "originalQuery": user_message,  # Include original query for context
                    "message": {
                        "role": "user",
                        "parts": [{"type": "text", "text": actual_input}]
                    }
                }
            }
            
            # Retry mechanism for failed requests
            max_retries = 3
            resp = None
            for attempt in range(max_retries):
                try:
                    async with httpx.AsyncClient() as client:
                        print(f"[Orchestrator] About to POST to {card['name']} at {card['url']} (attempt {attempt + 1})")
                        resp = await client.post(card["url"], json=payload, timeout=30)
                        print(f"[Orchestrator] Finished POST to {card['name']} at {card['url']}")
                        print(f"[Orchestrator] {card['name']} response status: {resp.status_code}")
                        break  # Success, exit retry loop
                except httpx.ReadTimeout:
                    if attempt < max_retries - 1:
                        print(f"[Orchestrator] Timeout for {card['name']}, retrying in 5 seconds...")
                        await asyncio.sleep(5)
                        continue
                    else:
                        raise  # Re-raise the exception if all retries failed
            
            # Process response outside the retry loop
            if resp and resp.status_code == 200:
                try:
                    data = resp.json()
                    print(f"[Orchestrator] {card['name']} response data: {data}")
                    agent_message = data.get("result", {}).get("message", {}).get("parts", [{}])[0].get("text", "")
                    print(f"[Orchestrator] {card['name']} extracted message: '{agent_message}'")
                    
                    if agent_message:  # Only proceed if we got a valid message
                        artifacts.append({
                            "agent": card["name"],
                            "type": "text",
                            "content": agent_message
                        })
                        steps[idx]["status"] = "completed"
                        
                        # Add substantial content (>50 chars and not error messages) to accumulated content
                        if (len(agent_message) > 50 and 
                            "no results found" not in agent_message.lower() and 
                            "no relevant content" not in agent_message.lower() and
                            "failed to" not in agent_message.lower()):
                            accumulated_content.append(agent_message)
                        
                        input_text = agent_message  # Pass result to next agent
                        print(f"[Orchestrator] {card['name']} marked as completed")
                    else:
                        print(f"[Orchestrator] {card['name']} returned empty message, marking as failed")
                        steps[idx]["status"] = "failed (empty response)"
                        artifacts.append({
                            "agent": card["name"],
                            "type": "error",
                            "content": "Agent returned empty response"
                        })
                        break
                    
                    # Update task status in real-time
                    tasks[task_id]["steps"] = steps
                    tasks[task_id]["artifacts"] = artifacts
                    tasks[task_id]["status"] = f"Processing... ({idx + 1}/{len(selected_agents)} agents completed)"
                except Exception as json_exc:
                    print(f"[Orchestrator] JSON decode error for {card['name']}: {json_exc}")
                    print(f"[Orchestrator] Response text: {resp.text}")
                    traceback.print_exc()
                    steps[idx]["status"] = "failed (json decode error)"
                    artifacts.append({
                        "agent": card["name"],
                        "type": "error",
                        "content": f"JSON decode error: {json_exc}\nResponse: {resp.text}"
                    })
                    break
            elif resp:
                print(f"[Orchestrator] {card['name']} non-200 response body: {resp.text}")
                steps[idx]["status"] = f"failed ({resp.status_code})"
                artifacts.append({
                    "agent": card["name"],
                    "type": "error",
                    "content": resp.text
                })
                break
            else:
                print(f"[Orchestrator] No response received from {card['name']}")
                steps[idx]["status"] = "failed (no response)"
                artifacts.append({
                    "agent": card["name"],
                    "type": "error",
                    "content": "No response received"
                })
                break
        except Exception as e:
            print(f"[Orchestrator] Exception for {card['name']}: {e}")
            traceback.print_exc()
            steps[idx]["status"] = "failed (exception)"
            artifacts.append({
                "agent": card["name"],
                "type": "error",
                "content": str(e) + "\n" + traceback.format_exc()
            })
            break
        tasks[task_id]["artifacts"] = artifacts
    
    # Final status update
    final_status = "completed" if all(s["status"] == "completed" for s in steps) else "failed"
    tasks[task_id]["status"] = final_status
    tasks[task_id]["steps"] = steps
    tasks[task_id]["artifacts"] = artifacts
    
    print(f"[Orchestrator] Workflow {final_status} for task {task_id}")
    print(f"[Orchestrator] Final artifacts count: {len(artifacts)}")
    print(f"[Orchestrator] Final steps: {[s['status'] for s in steps]}")

@app.post("/")
async def handle_a2a(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    method = data.get("method")
    params = data.get("params", {})
    if method == "sendTask":
        user_message = params.get("message", {}).get("parts", [{}])[0].get("text", "")
        task_id = str(uuid.uuid4())
        # Fetch agent cards and match agents for this query
        agent_cards = await fetch_agent_cards()
        selected_agents = match_agents(user_message, agent_cards)
        steps = [{"agent": card["name"], "status": "pending"} for card in selected_agents]
        tasks[task_id] = {
            "status": "pending",
            "steps": steps,
            "artifacts": [],
            "user_message": user_message
        }
        background_tasks.add_task(delegate_to_agents, task_id, user_message)
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": data.get("id"),
            "result": {
                "task_id": task_id,
                "status": "pending",
                "message": {"role": "orchestrator", "parts": [{"type": "text", "text": "Task received. Orchestrating agents..."}]},
                "steps": steps,
                "artifacts": []
            }
        })
    return JSONResponse({"error": "Invalid method"}, status_code=400)

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    task = tasks.get(task_id)
    if not task:
        return JSONResponse({"error": "Task not found"}, status_code=404)
    return JSONResponse(task)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5108)
