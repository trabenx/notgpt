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
        # Determine API format (openai or custom)
        self.api_format = config.get("api_format", "openai")
        self.supports_streaming = config.get("supports_streaming", False)
        
    async def mocked_send_request(*args, **kwargs):
        return "As an AI developed by Microsoft, I don't possess consciousness, thoughts, or feelings. My responses are generated based on patterns in the data I've been trained on. If you have any questions or need assitance with something specific, feel free to ask!"

    async def stream_response(self, messages, max_tokens=1500):
        """Stream response from API if supported"""
        if not self.supports_streaming:
            # Fallback to regular request
            response = await self.send_request(messages, max_tokens)
            yield response
            return
        """Stream response from API for real-time updates"""
        payload = self._prepare_openai_payload(messages, max_tokens)
        payload["stream"] = True  # Enable streaming
        
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                self.config["endpoint"],
                headers=self.headers,
                json=payload,
                timeout=30.0
            ) as response:
                if response.status_code != 200:
                    error_msg = f"API Error {response.status_code}: {response.text}"
                    yield error_msg
                    return
                    
                async for chunk in response.aiter_lines():
                    if chunk.startswith("data: "):
                        data = chunk[6:]
                        if data == "[DONE]":
                            return
                        try:
                            data_json = json.loads(data)
                            if "choices" in data_json and data_json["choices"]:
                                delta = data_json["choices"][0].get("delta", {})
                                if "content" in delta:
                                    yield delta["content"]
                        except json.JSONDecodeError:
                            continue


    async def send_request(self, messages, max_tokens=1500):
        # Prepare payload based on API format
        if self.api_format == "openai":
            payload = self._prepare_openai_payload(messages, max_tokens)
        else:
            payload = self._prepare_custom_payload(messages, max_tokens)
        
        try:
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.post(
                    self.config["endpoint"],
                    headers=self.headers,
                    json=payload,
                    timeout=60.0
                )
                
                if response.status_code != 200:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', response.text)
                    return f"API Error {response.status_code}: {error_msg}"
                
                return self._parse_response(response.json())
                
        except httpx.RequestError as e:
            return f"Network error: {str(e)}"
        except json.JSONDecodeError:
            return "Invalid JSON response from API"
        except KeyError:
            return "Unexpected API response format"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
    
    def _prepare_openai_payload(self, messages, max_tokens=1500):
        api_messages = []
        for msg in messages:
            content = []
        
            # Handle text content
            if isinstance(msg['content'], dict) and 'text' in msg['content']:
                content.append({"type": "text", "text": msg['content']['text']})
        
            # Handle image content
            if isinstance(msg['content'], dict) and 'image_base64' in msg['content']:
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{msg['content']['image_base64']}"
                    }
                })
        
            # Handle audio content
            if isinstance(msg['content'], dict) and 'audio_base64' in msg['content']:
                content.append({
                    "type": "audio",
                    "audio": {
                        "url": f"data:audio/wav;base64,{msg['content']['audio_base64']}"
                    }
                })
        
            # Handle simple text
            if not isinstance(msg['content'], dict) and msg['content']:
                content.append({"type": "text", "text": msg['content']})
        
            api_messages.append({
                "role": msg['role'],
                "content": content
            })
    
        return {
            "model": self.config["model_name"],
            "messages": api_messages,
            "max_tokens": max_tokens
        }
    
    def _prepare_custom_payload(self, messages, max_tokens):
        """Prepare langchain-style payload"""
        # Extract all messages
        message_list = []
        for msg in messages:
            role = "user" if msg['role'] == "user" else "assistant"
            content = msg['content']
            if isinstance(content, dict):
                content = content.get('text', '')
            message_list.append({"role": role, "content": content})
    
        return {
            "model": self.config["model_name"],
            "messages": message_list,
            "max_tokens": max_tokens
        }
    
    def _parse_response(self, response_data):
        """Parse response based on API format"""
        if self.api_format == "openai":
            if response_data.get("choices") and len(response_data["choices"]) > 0:
                content = response_data["choices"][0]["message"]["content"]
                if isinstance(content, list):
                    return "\n".join([item.get("text", "") for item in content if item.get("text")])
                return content
            return "No response from model"
        else:
            # Custom format parsing
            if "response" in response_data:
                return response_data["response"]
            elif "text" in response_data:
                return response_data["text"]
            elif "output" in response_data:
                return response_data["output"]
            return "No response from model"