# Multi-Agent A2A Protocol Streamlit App

This project demonstrates an advanced multi-agent system built on the **Agent to Agent (A2A) Protocol**, featuring intelligent orchestration, real-time collaboration, and sophisticated task delegation. The system consists of 8 specialized FastAPI-based agents that work together seamlessly to handle complex queries through standardized communication protocols.

## What is the App About?

### **Core Concept**
This application showcases a distributed AI ecosystem where multiple specialized agents collaborate to solve complex problems that would be difficult for a single AI system to handle efficiently. Each agent is a self-contained microservice with specific expertise, and they communicate through the standardized A2A Protocol to ensure seamless interoperability.

### **Key Features**
- **🤖 Intelligent Multi-Agent Orchestration**: Smart agent selection and workflow management
- **🔄 Real-time Collaborative Processing**: Agents work together in coordinated sequences
- **📊 Advanced Data Sharing**: Context-aware information passing between agents
- **🎯 Specialized Agent Capabilities**: Each agent optimized for specific tasks
- **💬 Interactive Chat Interface**: Real-time progress tracking and conversation history
- **📁 Document Processing Pipeline**: Upload, vectorize, and analyze documents
- **🌐 Web Integration**: Scraping and search capabilities with content analysis
- **🔍 Semantic Search**: Vector-based document retrieval and analysis

### **Agent Ecosystem**

#### **🎯 Orchestrator Agent (Port 5108)**
- **Primary Role**: Master coordinator and workflow manager
- **Responsibilities**:
  - Discovers and registers all available agents
  - Analyzes user queries to determine optimal agent workflow
  - Manages sequential task delegation with intelligent data passing
  - Monitors execution progress and handles error recovery
  - Aggregates responses and maintains session state
- **Intelligence**: Uses sophisticated keyword matching and capability analysis to select the right agents for each task

#### **🔍 Web Search Agent (Port 5101)**
- **Primary Role**: Information discovery and retrieval
- **Responsibilities**:
  - Performs intelligent web searches using search engines
  - Retrieves relevant information based on user queries
  - Provides structured search results for further processing
- **Use Cases**: News discovery, research initiation, trend analysis

#### **🌐 Web Scraper Agent (Port 5102)**
- **Primary Role**: Content extraction and web data harvesting
- **Responsibilities**:
  - Extracts content from specific URLs using advanced scraping techniques
  - Cleans and structures web content for analysis
  - Handles dynamic content and various web formats
  - Integrates with LLM for intelligent content analysis
- **Use Cases**: Article extraction, data collection, website analysis

#### **📁 File Reader Agent (Port 5103)**
- **Primary Role**: Document processing and vector-based retrieval
- **Responsibilities**:
  - Processes uploaded documents (PDF, CSV, TXT, JSON)
  - Maintains vector store for semantic document search
  - Provides context-aware responses using RAG (Retrieval Augmented Generation)
  - Leverages chunked document analysis for comprehensive insights
- **Advanced Features**: Uses embeddings for semantic similarity and LLM integration for intelligent querying

#### **📝 Summarizer Agent (Port 5104)**
- **Primary Role**: Content condensation and key insight extraction
- **Responsibilities**:
  - Creates concise summaries from large text content
  - Identifies and highlights key points and findings
  - Maintains context while reducing information volume
  - Uses advanced LLM techniques for quality summarization
- **Intelligence**: Receives substantial content from multiple sources for comprehensive summarization

#### **🎓 Elaborator Agent (Port 5105)**
- **Primary Role**: Detailed explanation and concept expansion
- **Responsibilities**:
  - Provides comprehensive explanations of topics and concepts
  - Expands on abbreviated information with context and examples
  - Offers educational insights and detailed analysis
  - Creates informative content for complex subjects
- **Use Cases**: Educational content, detailed analysis, concept clarification

#### **🧮 Calculator Agent (Port 5106)**
- **Primary Role**: Mathematical computation and statistical analysis
- **Responsibilities**:
  - Performs complex mathematical calculations and statistical operations
  - Analyzes numerical data and trends using numpy integration
  - Extracts numbers from text content intelligently
  - Provides statistical insights including mean, median, standard deviation
  - Conducts trend analysis and data correlation studies
- **Advanced Features**: Enhanced with LLM integration for intelligent data analysis and interpretation

#### **🔮 Predictor Agent (Port 5107)**
- **Primary Role**: Forecasting and trend prediction
- **Responsibilities**:
  - Makes predictions based on patterns and available data
  - Provides forecasting for various domains (business, technology, trends)
  - Analyzes historical data to project future outcomes
  - Offers strategic insights and scenario planning
- **Use Cases**: Market forecasting, trend analysis, strategic planning

## How is it Agent to Agent Protocol?

### **A2A Protocol Compliance Overview**
The application strictly adheres to the **Agent to Agent (A2A) Protocol** specification, ensuring standardized, interoperable communication between all agents in the ecosystem. This compliance enables seamless integration, dynamic discovery, and reliable inter-agent collaboration.

### **1. Agent Cards & Discovery (/.well-known/agent.json)**
Every agent implements the A2A discovery mechanism through standardized Agent Cards:

```json
{
  "name": "Agent Name",
  "description": "Detailed agent purpose and functionality",
  "version": "1.0.0",
  "capabilities": ["capability1", "capability2", "specific_functions"],
  "endpoints": {"a2a": "/"}
}
```

**Implementation Details**:
- **Endpoint**: Each agent exposes `GET /.well-known/agent.json`
- **Purpose**: Enables dynamic agent discovery and capability assessment
- **Usage**: Orchestrator fetches all agent cards to build the available agent registry
- **Benefits**: Allows runtime discovery without hard-coded agent knowledge

### **2. JSON-RPC 2.0 Communication Protocol**
All inter-agent communication follows the JSON-RPC 2.0 standard over HTTP(S):

**Request Format**:
```json
{
  "jsonrpc": "2.0",
  "id": "unique-request-id",
  "method": "sendTask",
  "params": {
    "id": "task-identifier",
    "sessionId": "session-identifier", 
    "acceptedOutputModes": ["text"],
    "originalQuery": "user's original request context",
    "message": {
      "role": "user",
      "parts": [{"type": "text", "text": "processed input from previous agent"}]
    }
  }
}
```

**Response Format**:
```json
{
  "jsonrpc": "2.0",
  "id": "matching-request-id",
  "result": {
    "message": {
      "role": "agent",
      "parts": [{"type": "text", "text": "agent's processed output"}]
    }
  }
}
```

### **3. Standardized Task Communication**
- **Method**: All agents implement the `sendTask` method as the primary communication interface
- **Consistency**: Uniform request/response structure across all agents
- **Reliability**: Built-in error handling and timeout management
- **Context Preservation**: Original query context maintained throughout the workflow

### **4. Interoperability & Dynamic Integration**
- **Agent Independence**: Each agent operates as a standalone microservice
- **Platform Agnostic**: Agents can be implemented in different technologies while maintaining A2A compliance
- **Scalability**: New agents can be added dynamically without modifying existing agents
- **Version Management**: Agent cards include version information for compatibility tracking

### **5. Session Management**
- **Session Continuity**: SessionId parameter ensures task correlation across agents
- **State Tracking**: Orchestrator maintains session state and progress tracking
- **Task Identification**: Unique task IDs enable precise workflow management

### **6. Error Handling & Resilience**
- **Retry Mechanisms**: Built-in retry logic for failed communications
- **Graceful Degradation**: System continues operation even if individual agents fail
- **Status Reporting**: Real-time status updates following A2A guidelines

## How the App Works

### **System Architecture & Workflow**

#### **1. Multi-Layered Architecture**
```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit UI Layer                      │
│            (Real-time Chat & File Management)              │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP/JSON-RPC 2.0
┌─────────────────────▼───────────────────────────────────────┐
│                 Orchestrator Agent                         │
│        (Intelligent Workflow Management)                   │
│   • Dynamic Agent Discovery & Selection                    │
│   • Sequential Task Delegation                             │
│   • Smart Data Passing & Context Management                │
└─┬─────────┬─────────┬─────────┬─────────┬─────────┬─────────┘
  │         │         │         │         │         │
  ▼         ▼         ▼         ▼         ▼         ▼
┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐
│Web    │ │Web    │ │File   │ │Summ.  │ │Elab.  │ │Calc.  │
│Search │ │Scraper│ │Reader │ │Agent  │ │Agent  │ │Agent  │
│5101   │ │5102   │ │5103   │ │5104   │ │5105   │ │5106   │
└───┬───┘ └───┬───┘ └───┬───┘ └───┬───┘ └───┬───┘ └───┬───┘
    │         │         │         │         │         │
    │    ┌────┴─────────┼─────────┼─────────┼─────────┼────┐
    │    │              │         │         │         │    │
    └────┼──────────────┼─────────┴─────────┴─────────┼────┘
         │              │                             │
    ┌────▼───┐     ┌────▼───┐                    ┌────▼───┐
    │Predictor│     │Vector  │                    │External│
    │Agent   │     │Store & │                    │APIs &  │
    │5107    │     │Embeddings│                  │Services│
    └────────┘     └────────┘                    └────────┘

Dynamic Multi-Agent Communication Patterns:

📋 File Analysis Workflows:
   File Reader → Summarizer → Elaborator
   File Reader → Calculator → Predictor

🌐 Web Research Workflows:
   Web Search → Web Scraper → Summarizer → Elaborator
   Web Scraper → Calculator → Predictor

🔄 Cross-Agent Data Flow Examples:
   Query: "Analyze uploaded docs and predict trends"
   Flow: File Reader ──data──> Summarizer ──insights──> Predictor

   Query: "Scrape URL, calculate metrics, explain implications"
   Flow: Web Scraper ──content──> Calculator ──stats──> Elaborator

   Query: "Find news, summarize, and predict impact"
   Flow: Web Search ──urls──> Web Scraper ──content──> 
         Summarizer ──summary──> Predictor

🎯 Intelligent Orchestration Features:
   • Context-aware agent selection based on query analysis
   • Sequential data passing with content optimization
   • Parallel capability when agents work independently
   • Fallback mechanisms for failed agent communications
   • Real-time progress tracking and status updates
```

#### **2. Intelligent Agent Discovery & Registration**
- **Dynamic Discovery**: Orchestrator automatically discovers available agents
- **Capability Assessment**: Fetches agent cards to understand each agent's abilities
- **Health Monitoring**: Continuous monitoring of agent availability and responsiveness
- **Registry Management**: Maintains real-time registry of active agents

#### **3. Smart Query Analysis & Agent Selection**
```python
# Enhanced Multi-Keyword Matching Algorithm
def match_agents(query, agent_cards):
    # Analyzes query for:
    # - File operations (uploaded, documents, PDF, CSV)
    # - Web operations (scrape, extract, URL, search)
    # - Analysis operations (summarize, elaborate, calculate, predict)
    # - Sequential workflow requirements
```

**Selection Logic**:
- **Keyword Analysis**: Scans query for operation-specific keywords
- **Capability Matching**: Maps keywords to agent capabilities
- **Workflow Sequencing**: Determines optimal agent execution order
- **Context Awareness**: Considers available data sources (uploaded files, URLs)

#### **4. Sequential Task Delegation & Data Pipeline**

**Workflow Execution Process**:
1. **Query Reception**: User submits query through Streamlit interface
2. **Agent Selection**: Orchestrator analyzes query and selects appropriate agents
3. **Sequential Processing**: Agents execute in optimized order with data passing
4. **Real-time Updates**: Progress tracking and status updates
5. **Response Aggregation**: Final results compilation and presentation

**Data Passing Mechanism**:
```python
# Sequential Data Flow
input_text = user_message  # Initial input
for agent in selected_agents:
    response = await delegate_to_agent(agent, input_text)
    input_text = response  # Output becomes input for next agent
    # Smart content aggregation for Summarizer
    if agent.name == "Summarizer":
        input_text = max(accumulated_content, key=len)
```

#### **5. Advanced Content Management**
- **Context Preservation**: Original query maintained throughout workflow
- **Substantial Content Selection**: Summarizer receives most comprehensive content
- **Error Recovery**: Graceful handling of agent failures
- **Retry Logic**: Automatic retry for failed communications

#### **6. Real-time Progress Tracking**
- **Live Status Updates**: Real-time agent execution monitoring
- **Step-by-Step Progress**: Visual progress indicator for each agent
- **Artifact Collection**: Continuous collection of agent outputs
- **Session Management**: Persistent conversation history

#### **7. User Interface Features**
- **Chat Interface**: Modern conversational UI with real-time updates
- **File Upload System**: Document vectorization and analysis pipeline
- **Progress Visualization**: Live workflow execution display
- **History Management**: Organized conversation history with dropdown navigation
- **Vector Store Integration**: Automatic document indexing and retrieval

## Getting Started

### **Prerequisites**
- Python 3.8 or higher
- pip package manager
- Internet connection for Azure OpenAI services

### **Installation & Setup**

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   - Set up Azure OpenAI credentials in your environment
   - Ensure all required API keys are properly configured

3. **Launch the Multi-Agent System**:
   
   **Option A: Launch All Agents Simultaneously**
   ```bash
   python run_all_agents.py
   ```
   This script automatically starts all 8 agents in separate terminal windows:
   - Web Search Agent (Port 5101)
   - Web Scraper Agent (Port 5102) 
   - File Reader Agent (Port 5103)
   - Summarizer Agent (Port 5104)
   - Elaborator Agent (Port 5105)
   - Calculator Agent (Port 5106)
   - Predictor Agent (Port 5107)
   - Orchestrator Agent (Port 5108)

   **Option B: Manual Agent Launch**
   ```bash
   # Launch each agent individually
   uvicorn agents.orchestrator_agent:app --port 5108 --reload
   uvicorn agents.web_search_agent:app --port 5101 --reload
   uvicorn agents.web_scraper_agent:app --port 5102 --reload
   # ... (continue for all agents)
   ```

4. **Start the Streamlit Application**:
   ```bash
   streamlit run app.py
   ```

5. **Access the Application**:
   - Open your browser to `http://localhost:8501`
   - The application will automatically discover and register all running agents
   - Begin interacting through the chat interface

### **System Verification**
- Check that all 8 agents are running and accessible
- Verify agent discovery through the sidebar agent list
- Test basic functionality with simple queries
- Monitor the orchestrator logs for proper agent communication

## Example Queries to Test

Here are some example queries you can test with different agents:

### **Multi-Agent Workflow Queries (Recommended)**
These queries will trigger multiple agents working together in sequence:

#### **News Analysis & Summarization**
- "Scrape the latest news from https://newsroom.ibm.com/Accelerating-our-future-and-growth-strategy and provide a concise summary."
  - _Uses: Web Search → Web Scraper → File Reader → Summarizer_

- "Find recent news about artificial intelligence, extract the content, and give me a detailed summary with key insights."
  - _Uses: Web Search → Web Scraper → Summarizer → Elaborator_

#### **PDF Document Analysis Queries (Test with Uploaded PDFs)**
- "Analyze the uploaded documents and provide a comprehensive summary of the key findings."
  - _Should use: File Reader → Summarizer (only 2 agents)_

- "Extract key insights from the uploaded PDFs and provide detailed explanations of the main concepts."
  - _Should use: File Reader → Elaborator (only 2 agents)_

- "Read the uploaded documents, summarize the content, and then elaborate on the most important points."
  - _Should use: File Reader → Summarizer → Elaborator (only 3 agents)_

- "Analyze the uploaded financial reports and calculate the percentage changes in revenue."
  - _Should use: File Reader → Calculator (only 2 agents)_

- "Review the uploaded market research documents and predict future trends based on the data."
  - _Should use: File Reader → Predictor (only 2 agents)_

- "Examine the uploaded documents, summarize key trends, and predict future market developments."
  - _Should use: File Reader → Summarizer → Predictor (only 3 agents)_

#### **Web Scraping Only Queries (No PDF Required)**
- "Scrape https://example.com and extract the main content."
  - _Should use: Web Scraper (only 1 agent)_

- "Extract content from https://newsroom.ibm.com/news and provide a summary."
  - _Should use: Web Scraper → Summarizer (only 2 agents)_

- "Scrape https://blog.openai.com and elaborate on the technical concepts mentioned."
  - _Should use: Web Scraper → Elaborator (only 2 agents)_

#### **Pure Analysis Queries (No Web/File Access)**
- "Summarize this text: 'Artificial intelligence is revolutionizing industries by enabling automated decision-making, predictive analytics, and intelligent process optimization.'"
  - _Should use: Summarizer (only 1 agent)_

- "Explain in detail the concept of machine learning and its applications in modern business."
  - _Should use: Elaborator (only 1 agent)_

- "Calculate the compound interest for a principal of $10,000 at 5% annual rate for 10 years."
  - _Should use: Calculator (only 1 agent)_

- "Predict the future of renewable energy adoption in the next decade."
  - _Should use: Predictor (only 1 agent)_

#### **Smart Orchestration Test Queries**
- "I have uploaded multiple research papers about AI. Please analyze them and predict future developments in the field."
  - _Should use: File Reader → Summarizer → Predictor (only 3 agents, no web agents)_

- "From the uploaded financial documents, calculate key metrics and elaborate on their business implications."
  - _Should use: File Reader → Calculator → Elaborator (only 3 agents, no web agents)_

- "Analyze the uploaded strategy documents, summarize the main points, and predict implementation challenges."
  - _Should use: File Reader → Summarizer → Predictor (only 3 agents)_

#### **Edge Case Testing Queries**
- "Calculate 25 * (3 + 7) and then explain the mathematical concepts involved."
  - _Should use: Calculator → Elaborator (only 2 agents)_

- "Summarize this: 'Quantum computing represents a paradigm shift' and then predict its impact."
  - _Should use: Summarizer → Predictor (only 2 agents)_

- "From uploaded docs, calculate statistics and predict trends, then elaborate on implications."
  - _Should use: File Reader → Calculator → Predictor → Elaborator (only 4 agents, no web)_

#### **Negative Test Cases (Should Use Minimal Agents)**
- "What is 2+2?"
  - _Should use: Calculator (only 1 agent)_

- "Explain photosynthesis."
  - _Should use: Elaborator (only 1 agent)_

- "Summarize: 'The sky is blue because of light scattering.'"
  - _Should use: Summarizer (only 1 agent)_

- "Will it rain tomorrow?"
  - _Should use: Predictor (only 1 agent)_

#### **Data Analysis & Prediction**
- "Search for information about global electric vehicle sales trends, scrape relevant data, analyze it, and predict future market growth."
  - _Uses: Web Search → Web Scraper → File Reader → Calculator → Predictor_

- "Find data on renewable energy adoption rates, extract the information, summarize key trends, and elaborate on future implications."
  - _Uses: Web Search → Web Scraper → Summarizer → Elaborator → Predictor_

#### **Research & Calculation**
- "Search for current cryptocurrency prices, extract the data, calculate percentage changes, and predict market trends."
  - _Uses: Web Search → Web Scraper → Calculator → Predictor_

- "Find information about quantum computing developments, scrape relevant articles, summarize findings, and explain the technology in detail."
  - _Uses: Web Search → Web Scraper → Summarizer → Elaborator_

### **Single Agent Queries**

#### **Web Search Agent**
- "What is the latest news about artificial intelligence?"
- "Find information about the history of blockchain technology."

#### **Web Scraper Agent**
- "Scrape the content from this URL: https://newsroom.ibm.com/Accelerating-our-future-and-growth-strategy"
- "Extract key points from https://example.com."

#### **File Reader Agent**
- "Read and summarize the content of the uploaded file."
- "What are the key insights from the uploaded CSV file?"  
  _The File Reader Agent now uses LLMs to answer queries, leveraging relevant chunks from the vector store for context-aware, generative responses._

#### **Summarizer Agent**
- "Summarize this text: Artificial intelligence is transforming industries by enabling automation and data-driven decision-making."
- "Provide a concise summary of the following article."

#### **Elaborator Agent**
- "Explain the concept of quantum computing in detail."
- "Elaborate on the benefits of using renewable energy."

#### **Calculator Agent**
- "What is the result of 25 * (3 + 7)?"
- "Calculate the square root of 144."

#### **Predictor Agent**
- "Predict the weather for tomorrow in New York."
- "What are the future trends in AI development?"
- "Based on current trends, what will be the global demand for electric vehicles in 2030?"

## References

- [A2A Protocol Documentation](https://google.github.io/A2A/#/documentation)
- [A2A Protocol GitHub](https://github.com/google/A2A)

**Credits**: Made by Ashutosh Srivastava