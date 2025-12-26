import subprocess
import time
import sys
import platform

# Define the agents and their respective ports
agents = [
    {"name": "Web Search Agent", "module": "agents.web_search_agent", "port": 5101},
    {"name": "Web Scraper Agent", "module": "agents.web_scraper_agent", "port": 5102},
    {"name": "File Reader Agent", "module": "agents.file_reader_agent", "port": 5103},
    {"name": "Summarizer Agent", "module": "agents.summarizer_agent", "port": 5104},
    {"name": "Elaborator Agent", "module": "agents.elaborator_agent", "port": 5105},
    {"name": "Calculator Agent", "module": "agents.calculator_agent", "port": 5106},
    {"name": "Predictor Agent", "module": "agents.predictor_agent", "port": 5107},
    {"name": "Orchestrator Agent", "module": "agents.orchestrator_agent", "port": 5108},
]

processes = []

try:
    for agent in agents:
        print(f"Launching {agent['name']} on port {agent['port']} in a new terminal...")
        if platform.system() == "Windows":
            # Use PowerShell to open a new terminal window for each agent
            cmd = [
                "powershell",
                "-NoExit",
                "-Command",
                f"uvicorn {agent['module']}:app --host 0.0.0.0 --port {agent['port']} --reload"
            ]
            subprocess.Popen(cmd)
        else:
            # For Unix-like systems, use x-terminal-emulator or gnome-terminal
            cmd = [
                "x-terminal-emulator", "-e",
                f"uvicorn {agent['module']}:app --host 0.0.0.0 --port {agent['port']} --reload"
            ]
            subprocess.Popen(cmd)
        time.sleep(5)  # Increased delay to ensure agents fully start up

    print("\nAll agents have been launched in separate terminals.")
    print("Waiting for all agents to fully start up...")
    time.sleep(20)  # Give all agents more time to start up completely
    print("All agents should now be ready!")
    print("Monitor each terminal window for logs. Close a terminal to stop an agent.")
    print("You can close this window now.")

except Exception as e:
    print(f"Error launching agents: {e}")
    sys.exit(1)