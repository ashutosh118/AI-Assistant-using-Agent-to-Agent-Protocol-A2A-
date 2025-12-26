import streamlit as st
import httpx
import PyPDF2
import csv
import json
import time
from datetime import datetime
from typing import List, Dict, Any
from utils.vector_store import vector_store
from utils.models import model_manager

# Configure Streamlit page
st.set_page_config(
    page_title="A2A Multi-Agent Demo",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# List of all agents following A2A protocol
agents = [
    {"name": "Web Search Agent", "url": "http://localhost:5101/"},
    {"name": "Web Scraper Agent", "url": "http://localhost:5102/"},
    {"name": "File Reader Agent", "url": "http://localhost:5103/"},
    {"name": "Summarizer Agent", "url": "http://localhost:5104/"},
    {"name": "Elaborator Agent", "url": "http://localhost:5105/"},
    {"name": "Calculator Agent", "url": "http://localhost:5106/"},
    {"name": "Predictor Agent", "url": "http://localhost:5107/"},
]

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []
if "urls" not in st.session_state:
    st.session_state.urls = []
if "vectorized_files" not in st.session_state:
    st.session_state.vectorized_files = set()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # List of {query, responses, completed}
if "current_query_responses" not in st.session_state:
    st.session_state.current_query_responses = []

# Sidebar for configuration and stats
with st.sidebar:
    st.header("🛠️ Configuration")
    st.subheader("📊 Vector Store")
    stats = vector_store.get_stats()
    st.metric("Documents", stats["total_documents"])
    st.metric("Index Size", stats["index_size"])
    if st.button("Clear Vector Store"):
        vector_store.clear()
        st.session_state.vectorized_files = set()
        st.session_state.uploaded_files = []
        st.success("Vector store cleared!")

    with st.expander("🤖 Available Agents", expanded=True):
        for agent in agents:
            st.write(f"🔹 {agent['name']}")

    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p><b>Multi-Agent A2A Protocol App</b></p>
        <p>This app demonstrates the <b>Agent to Agent Protocol (A2A)</b> for seamless, standardized communication between specialized AI agents.</p>
        <p>• Developed by Ashutosh Srivastava</p>
        <p>🤖 Powered by Azure OpenAI</p>
    </div>
    """, unsafe_allow_html=True)

# Custom CSS for better chat and UI
st.markdown("""
<style>
    /* Reduce expander width in sidebar */
    section[data-testid="stSidebar"] .st-expander {
        width: 80% !important;
        margin: 0 auto 1rem auto !important;
    }
    .main-header {
        background: linear-gradient(90deg, #4e54c8 0%, #8f94fb 100%);
        padding: 1.5rem 0;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        background: #f1f3f4;
        display: flex;
        align-items: flex-start;
    }
    .user-message {
        background: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .chat-icon {
        font-size: 2rem;
        margin-right: 0.5rem;
        margin-top: -0.2rem;
    }
    .chat-bubble {
        padding: 0.75rem 1.2rem;
        border-radius: 12px;
        max-width: 70%;
        color: #222;
        background: inherit;
    }
    .agent-response {
        background: #f8f9fa;
        border-left: 4px solid #28a745;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .agent-label {
        font-weight: bold;
        color: #28a745;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
        display: block;
    }
    .current-query {
        background: #e3f2fd;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 4px solid #2196f3;
    }
</style>
""", unsafe_allow_html=True)

# Main header with attractive background
st.markdown(
    """
    <div class="main-header">
        <h1>🤖 Multi-Agent AI Assistance</h1>
        <h3>Based on Agent to Agent Protocol</h3>
    </div>
    """,
    unsafe_allow_html=True
)

# Tabs for different functionalities
tab1, tab2, tab3 = st.tabs(["💬 Chat", "📁 File Upload", "🌐 URL Input"])

# Tab 1: Chat Interface
with tab1:
    st.header("💬 Ask Anything (A2A Orchestrator)")
    
    user_input = st.chat_input("Enter your query and press Enter or click the send icon...")
    if user_input:
        # Clear previous session completely when new query starts
        st.session_state.current_query_responses = []
        st.session_state.pop("orchestrator_task_id", None)
        st.session_state.pop("orchestrator_steps", None)
        st.session_state.pop("orchestrator_status", None)
        st.session_state.pop("orchestrator_artifacts", None)
        st.session_state.pop("current_user_query", None)
        
        # Send query to Orchestrator Agent
        params = {
            "id": "task-1",
            "sessionId": "session-1",
            "acceptedOutputModes": ["text"],
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": user_input}]
            }
        }
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "sendTask",
            "params": params
        }
        try:
            with st.spinner("Sending request to Orchestrator Agent..."):
                response = httpx.post("http://localhost:5108/", json=payload, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    task_id = data.get("result", {}).get("task_id")
                    st.session_state["orchestrator_task_id"] = task_id
                    st.session_state["orchestrator_steps"] = data.get("result", {}).get("steps", [])
                    st.session_state["orchestrator_status"] = data.get("result", {}).get("status", "pending")
                    st.session_state["orchestrator_artifacts"] = data.get("result", {}).get("artifacts", [])
                    st.session_state["current_user_query"] = user_input
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
        except Exception as e:
            st.error(f"Request failed: {e}")

    # Show orchestration workflow/progress if a task is active
    if st.session_state.get("orchestrator_task_id"):
        task_id = st.session_state["orchestrator_task_id"]
        
        # Poll for status updates
        try:
            status_response = httpx.get(f"http://localhost:5108/status/{task_id}", timeout=10)
            if status_response.status_code == 200:
                task_data = status_response.json()
                st.session_state["orchestrator_steps"] = task_data.get("steps", [])
                st.session_state["orchestrator_status"] = task_data.get("status", "pending")
                artifacts = task_data.get("artifacts", [])
                st.session_state["orchestrator_artifacts"] = artifacts
                
                # Update current query responses with new artifacts
                current_responses = []
                for artifact in artifacts:
                    if artifact.get("type") == "text":
                        current_responses.append({
                            "agent": artifact["agent"],
                            "content": artifact["content"]
                        })
                st.session_state.current_query_responses = current_responses
                
        except Exception as e:
            st.warning(f"Failed to get status update: {e}")
        
        st.subheader("Orchestration Workflow")
        steps = st.session_state.get("orchestrator_steps", [])
        status = st.session_state.get("orchestrator_status", "pending")
        st.write(f"**Task Status:** {status}")
        
        for step in steps:
            if step['status'] == 'completed':
                st.success(f"Agent: {step['agent']} | Status: ✅ {step['status']}")
            elif step['status'] == 'running':
                st.info(f"Agent: {step['agent']} | Status: 🔄 {step['status']}")
            elif step['status'] == 'pending':
                st.info(f"Agent: {step['agent']} | Status: ⏳ {step['status']}")
            else:
                st.error(f"Agent: {step['agent']} | Status: ❌ {step['status']}")
        
        # When task is completed, add to chat history
        if status == "completed" and st.session_state.get("current_user_query"):
            # Check if this query is already in history
            current_query = st.session_state["current_user_query"]
            existing_query = next((item for item in st.session_state.chat_history if item["query"] == current_query), None)
            
            if not existing_query:
                st.session_state.chat_history.append({
                    "query": current_query,
                    "responses": st.session_state.current_query_responses.copy(),
                    "completed": True
                })
                
        # Auto-refresh every 2 seconds if task is not completed
        if status not in ["completed", "failed"]:
            time.sleep(2)
            st.rerun()

    # Current Query Chat History (Always visible when there's an active query)
    if st.session_state.get("current_user_query"):
        st.subheader("Current Conversation")
        
        # Display current user query
        st.markdown(f"""
        <div class="current-query">
            <span style='font-size:1.2rem;'>🧑‍💻</span> <b>You:</b> {st.session_state["current_user_query"]}
        </div>
        """, unsafe_allow_html=True)
        
        # Display agent responses as they come in
        for response in st.session_state.current_query_responses:
            st.markdown(f"""
            <div class="agent-response">
                <span class="agent-label">🤖 {response['agent']}:</span>
                {response['content']}
            </div>
            """, unsafe_allow_html=True)

    # Previous Chat History Dropdown
    if st.session_state.chat_history:
        st.subheader("Previous Conversations")
        
        # Create dropdown with previous queries
        query_options = ["Select a previous conversation..."] + [item["query"][:80] + "..." if len(item["query"]) > 80 else item["query"] for item in reversed(st.session_state.chat_history)]
        
        selected_query = st.selectbox(
            "Choose a previous conversation to view:",
            options=query_options,
            key="previous_conversations_dropdown"
        )
        
        if selected_query != "Select a previous conversation...":
            # Find the selected conversation
            selected_conversation = None
            for item in reversed(st.session_state.chat_history):
                truncated_query = item["query"][:80] + "..." if len(item["query"]) > 80 else item["query"]
                if truncated_query == selected_query:
                    selected_conversation = item
                    break
            
            if selected_conversation:
                with st.expander(f"💬 Conversation: {selected_query}", expanded=True):
                    # Display the full query
                    st.markdown(f"""
                    <div class="current-query">
                        <span style='font-size:1.2rem;'>🧑‍💻</span> <b>You:</b> {selected_conversation['query']}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Display all agent responses
                    for response in selected_conversation['responses']:
                        st.markdown(f"""
                        <div class="agent-response">
                            <span class="agent-label">🤖 {response['agent']}:</span>
                            {response['content']}
                        </div>
                        """, unsafe_allow_html=True)

# Tab 2: File Upload
with tab2:
    st.header("📁 Upload Files for Analysis")
    uploaded_files = st.file_uploader(
        "Upload files for vectorization and analysis",
        type=["txt", "pdf", "csv", "json"],
        accept_multiple_files=True
    )
    if uploaded_files:
        st.session_state.uploaded_files = list(uploaded_files)  # Overwrite with new uploads
        st.success(f"Uploaded {len(uploaded_files)} file(s).")

    if st.session_state.uploaded_files:
        st.subheader("Uploaded Files")
        files_to_keep = []
        for file in st.session_state.uploaded_files:
            col1, col2 = st.columns([8, 1])
            with col1:
                st.write(f"📄 {file.name} ({file.size} bytes)")
            with col2:
                if st.button("Remove", key=f"remove_{file.name}"):
                    continue  # Skip adding this file to files_to_keep
            files_to_keep.append(file)
        st.session_state.uploaded_files = files_to_keep

        if st.button("Vectorize Files"):
            newly_vectorized = 0
            for file in st.session_state.uploaded_files:
                if file.name not in st.session_state.vectorized_files:
                    try:
                        docs = []
                        metas = []
                        if file.name.lower().endswith('.pdf'):
                            pdf_reader = PyPDF2.PdfReader(file)
                            for i, page in enumerate(pdf_reader.pages):
                                text = page.extract_text() or ""
                                if text.strip():
                                    docs.append(text)
                                    metas.append({"filename": file.name, "type": "pdf", "chunk": i})
                        elif file.name.lower().endswith('.csv'):
                            file.seek(0)
                            reader = csv.reader(file.read().decode("utf-8").splitlines())
                            header = next(reader)
                            for i, row in enumerate(reader):
                                row_text = ", ".join(f"{h}: {v}" for h, v in zip(header, row))
                                docs.append(row_text)
                                metas.append({"filename": file.name, "type": "csv", "row": i})
                        elif file.name.lower().endswith('.json'):
                            file.seek(0)
                            data = json.load(file)
                            docs.append(json.dumps(data, indent=2)[:2000])
                            metas.append({"filename": file.name, "type": "json"})
                        else:
                            file.seek(0)
                            text = file.read().decode("utf-8")
                            # Chunk by paragraphs
                            for i, chunk in enumerate(text.split("\n\n")):
                                if chunk.strip():
                                    docs.append(chunk)
                                    metas.append({"filename": file.name, "type": "txt", "chunk": i})
                        if docs:
                            vector_store.add_documents(docs, metas)
                            vector_store.save_index()  # Automatically save after vectorization
                            st.session_state.vectorized_files.add(file.name)
                            st.success(f"Vectorized {file.name} ({len(docs)} chunks)")
                            newly_vectorized += 1
                        else:
                            st.warning(f"No content extracted from {file.name}")
                    except Exception as e:
                        st.error(f"Failed to vectorize {file.name}: {e}")
                else:
                    st.info(f"{file.name} already vectorized. Skipping.")
            if newly_vectorized == 0:
                st.info("No new files to vectorize.")

# Tab 3: URL Input
with tab3:
    st.header("🌐 Input URLs for Scraping")
    urls_input = st.text_area(
        "Enter URLs (one per line):",
        placeholder="https://example.com\nhttps://another-site.com"
    )
    if urls_input:
        urls = [url.strip() for url in urls_input.split("\n") if url.strip()]
        st.session_state.urls = urls  # Overwrite with new URLs
        st.success(f"Added {len(urls)} URL(s).")

    if st.session_state.urls:
        st.subheader("URLs to Scrape")
        for url in st.session_state.urls:
            st.write(f"🔗 {url}")