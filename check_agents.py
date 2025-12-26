import requests

agents = [
    {"name": "Web Search Agent", "port": 5101},
    {"name": "Web Scraper Agent", "port": 5102},
    {"name": "File Reader Agent", "port": 5103},
    {"name": "Summarizer Agent", "port": 5104},
]

print("Testing Agent Availability")
print("=" * 40)

for agent in agents:
    try:
        url = f"http://localhost:{agent['port']}/.well-known/agent.json"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {agent['name']} - RUNNING")
            print(f"   Capabilities: {data.get('capabilities', [])}")
        else:
            print(f"❌ {agent['name']} - ERROR {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"❌ {agent['name']} - NOT RUNNING")
    except Exception as e:
        print(f"❌ {agent['name']} - ERROR: {e}")
    print()
