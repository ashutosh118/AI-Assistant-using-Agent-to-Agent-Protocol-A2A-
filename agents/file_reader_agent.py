from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from utils.vector_store import vector_store

app = FastAPI()

class FileReaderAgent:
    def __init__(self):
        self.name = "File Reader Agent"
        self.description = "Reads and extracts content from vector store"
    
    async def query_vector_store(self, query: str) -> str:
        # Always reload the latest vector store index/metadata before querying
        vector_store.load_index()
        stats = vector_store.get_stats()
        print(f"[FileReaderAgent] Loaded vector store: {stats}")
        print(f"[FileReaderAgent] First 3 docs: {vector_store.documents[:3]}")
        print(f"[FileReaderAgent] First 3 metadata: {vector_store.metadata[:3]}")
        # Always use vector search to fetch relevant chunks, then use LLM to answer the query based on those chunks
        results = vector_store.similarity_search(query, k=5)
        if results:
            from utils.models import model_manager
            # Compose a context from the top chunks
            context = "\n---\n".join(doc for doc, _, _ in results)
            prompt = (
                f"You are a helpful assistant. The user asked: '{query}'.\n"
                f"Here are the most relevant excerpts from the uploaded files:\n\n{context}\n\n"
                "Based on this information, provide a concise, direct answer to the user's question. "
                "If the answer is not present, say 'The answer is not found in the provided documents.'"
            )
            try:
                summary = model_manager.azure_llm.invoke(prompt)
                if hasattr(summary, 'content'):
                    return summary.content
                return str(summary)
            except Exception as e:
                return f"No relevant content found in the vector store. (LLM summary failed: {e})"
        # If no results, fallback to LLM summary over all docs
        if vector_store.documents:
            from utils.models import model_manager
            all_context = "\n---\n".join(vector_store.documents[:10])
            prompt = (
                f"You are a helpful assistant. The user asked: '{query}'.\n"
                f"Here are some excerpts from the uploaded files:\n\n{all_context}\n\n"
                "Based on this information, provide a concise, direct answer to the user's question. "
                "If the answer is not present, say 'The answer is not found in the provided documents.'"
            )
            try:
                summary = model_manager.azure_llm.invoke(prompt)
                if hasattr(summary, 'content'):
                    return summary.content
                return str(summary)
            except Exception as e:
                return f"No relevant content found in the vector store. (LLM summary failed: {e})"
        return "No relevant content found in the vector store."

file_reader_agent = FileReaderAgent()

@app.get("/.well-known/agent.json")
async def agent_card():
    return {
        "name": file_reader_agent.name,
        "description": file_reader_agent.description,
        "version": "1.0.0",
        "capabilities": ["file_reading", "vector_search"],
        "endpoints": {"a2a": "/"}
    }

@app.post("/")
async def handle_a2a(request: Request):
    data = await request.json()
    method = data.get("method")
    params = data.get("params", {})
    
    if method == "sendTask":
        user_message = params.get("message", {}).get("parts", [{}])[0].get("text", "")
        result = await file_reader_agent.query_vector_store(user_message)
        
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
    uvicorn.run(app, host="0.0.0.0", port=5103)