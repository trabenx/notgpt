import httpx
import os
import json
import base64

class OpenAIClient:
    def __init__(self, config):
        self.config = config
        self.api_key = config.get("api_key", "") or os.getenv(f"{config['name'].upper().replace(' ', '_')}_API_KEY", "")
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}" if self.api_key else ""
        }

    async def send_request(self, messages, max_tokens=1500):
        # Prepare messages for API
        api_messages = []
        for msg in messages:
            # Handle multimodal messages
            content = []
            
            if isinstance(msg['content'], dict):
                # Handle image + text
                if 'text' in msg['content'] and msg['content']['text']:
                    content.append({"type": "text", "text": msg['content']['text']})
                
                if 'image_base64' in msg['content'] and msg['content']['image_base64']:
                    content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{msg['content']['image_base64']}"
                        }
                    })
            else:
                # Text-only
                content.append({"type": "text", "text": msg['content']})
            
            api_messages.append({
                "role": msg['role'],
                "content": content
            })
        
        payload = {
            "model": self.config["model_name"],
            "messages": api_messages,
            "max_tokens": max_tokens
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.config["endpoint"],
                    headers=self.headers,
                    json=payload,
                    timeout=60.0
                )
                
                if response.status_code != 200:
                    error_msg = f"API Error {response.status_code}: {response.text}"
                    return error_msg
                
                data = response.json()
                # Extract text from response
                if data.get("choices") and len(data["choices"]) > 0:
                    content = data["choices"][0]["message"]["content"]
                    if isinstance(content, list):
                        # Handle multimodal response
                        return "\n".join([item.get("text", "") for item in content if item.get("text")])
                    return content
                return "No response from model"
                
        except httpx.RequestError as e:
            return f"Network error: {str(e)}"
        except json.JSONDecodeError:
            return "Invalid JSON response from API"
        except KeyError:
            return "Unexpected API response format"
        except Exception as e:
            return f"Unexpected error: {str(e)}"