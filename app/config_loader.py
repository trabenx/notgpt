import json
import os

def load_models_config():
    with open('models.json', 'r') as f:
        models = json.load(f)
    
    # Set environment variables for API keys
    for model in models:
        if model.get('api_key'):
            os.environ[f"{model['name'].upper().replace(' ', '_')}_API_KEY"] = model['api_key']
    
    return models