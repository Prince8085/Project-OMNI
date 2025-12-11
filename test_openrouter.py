
import sys
import os
from pathlib import Path
import yaml

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.executors.open_interpreter import OpenInterpreterExecutor

def test_openrouter():
    print("Testing OpenRouter Integration...")
    
    # Load config manually to ensure we pick up the changes
    with open('config/models.yaml', 'r') as f:
        config = yaml.safe_load(f)
        
    executor = OpenInterpreterExecutor(config)
    
    print(f"Provider: {executor.provider}")
    print(f"Model: {executor.model_name}")
    print(f"API URL: {executor.api_url}")
    
    if executor.provider != 'openrouter':
        print("❌ Error: Provider is not openrouter")
        return
        
    response = executor.execute("Say 'Hello from OpenRouter' and nothing else.")
    print("\nResponse:")
    print(response.get('output'))
    
    if response.get('success'):
        print("\n✅ Test Passed!")
    else:
        print("\n❌ Test Failed!")

if __name__ == "__main__":
    test_openrouter()
