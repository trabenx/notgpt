from PySide6.QtWidgets import QWidget, QTextEdit, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import QTimer
from .api_client import OpenAIClient
import asyncio

class ChatWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.current_model = None
        self.message_history = []
        
        # Create UI
        layout = QVBoxLayout(self)
        
        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display, 1)
        
        # Input area
        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.send_button = QPushButton("Send")
        input_layout.addWidget(self.message_input, 1)
        input_layout.addWidget(self.send_button)
        layout.addLayout(input_layout)
        
        # Connections
        self.send_button.clicked.connect(self.send_message)
        self.message_input.returnPressed.connect(self.send_message)
    
    def set_current_model(self, model_config):
        self.current_model = model_config
        self.client = OpenAIClient(model_config)
        self.chat_display.append(f"\n=== Switched to: {model_config['name']} ===")
    
    def send_message(self):
        message = self.message_input.text().strip()
        if not message or not self.current_model:
            return
        
        self.message_input.clear()
        self.add_message("user", message)
        
        # Schedule async task
        asyncio.create_task(self.get_ai_response(message))
    
    async def get_ai_response(self, user_message):
        # Add temporary "Thinking..." message
        self.add_message("assistant", "Thinking...")
        self.thinking_message_id = self.chat_display.toPlainText().rfind("Thinking...")
        
        try:
            self.message_history.append({"role": "user", "content": user_message})
            response = await self.client.send_request(self.message_history)
            self.message_history.append({"role": "assistant", "content": response})
            
            # Update UI with actual response
            self.update_last_message(response)
        except Exception as e:
            self.update_last_message(f"Error: {str(e)}")
    
    def add_message(self, sender, text):
        prefix = "You: " if sender == "user" else "AI: "
        self.chat_display.append(f"{prefix}{text}")
    
    def update_last_message(self, new_text):
        # Get current text
        current_text = self.chat_display.toPlainText()
        
        # Find position of "Thinking..." message
        if hasattr(self, 'thinking_message_id') and self.thinking_message_id != -1:
            # Replace "Thinking..." with actual response
            new_text = current_text[:self.thinking_message_id] + f"AI: {new_text}"
            self.chat_display.setPlainText(new_text)
        
        # Scroll to bottom
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )