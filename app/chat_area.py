from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame, QHBoxLayout, QLineEdit, QPushButton, QFileDialog
from PySide6.QtCore import Qt, QTimer
from .message_bubble import MessageBubble
from .api_client import OpenAIClient
from .image_utils import image_to_base64
import asyncio

class ChatArea(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("chatArea")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Scroll area for messages
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.messages_container = QWidget()
        self.messages_container.setObjectName("messagesContainer")
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setAlignment(Qt.AlignTop)
        self.messages_layout.setContentsMargins(20, 20, 20, 20)
        self.messages_layout.setSpacing(10)

        scroll_area.setWidget(self.messages_container)
        layout.addWidget(scroll_area, 1)
        
        # Input area
        input_widget = QWidget()
        input_widget.setObjectName("inputArea")
        input_layout = QHBoxLayout(input_widget)
        input_layout.setContentsMargins(15, 15, 15, 15)
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Message...")
        
        self.image_button = QPushButton("🖼️")
        self.image_button.setToolTip("Add image")
        self.image_button.setFixedSize(40, 40)
        self.image_button.clicked.connect(self.add_image)
        
        self.send_button = QPushButton("Send")
        self.send_button.setFixedWidth(80)
        
        input_layout.addWidget(self.image_button)
        input_layout.addWidget(self.message_input, 1)
        input_layout.addWidget(self.send_button)
        
        layout.addWidget(input_widget)
        
        # Connect signals
        self.send_button.clicked.connect(self.send_message)
        self.message_input.returnPressed.connect(self.send_message)
        
        # State
        self.current_model = None
        self.message_history = []
        self.current_image = None
        self.client = None
    
    def set_current_model(self, model_config):
        self.current_model = model_config
        self.client = OpenAIClient(model_config)
        self.clear_chat()
    
    def clear_chat(self):
        # Clear chat history
        while self.messages_layout.count():
            item = self.messages_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.message_history = []
        self.current_image = None
    
    def add_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            base64_image = image_to_base64(file_path)
            if base64_image:
                self.current_image = base64_image
                
                # Show preview
                preview = MessageBubble("user", {"image_base64": base64_image})
                preview.setAlignment(Qt.AlignRight)
                self.messages_layout.addWidget(preview)
                self.scroll_to_bottom()
    
    def send_message(self):
        text = self.message_input.text().strip()
        if not text and not self.current_image:
            return
        
        # Create message content
        content = {"text": text} if text else {}
        if self.current_image:
            content["image_base64"] = self.current_image
        
        # Add user message
        user_bubble = MessageBubble("user", content)
        self.messages_layout.addWidget(user_bubble, alignment=Qt.AlignRight | Qt.AlignTop)
        self.scroll_to_bottom()
        
        # Add to history
        self.message_history.append({"role": "user", "content": content})
        
        # Clear input
        self.message_input.clear()
        self.current_image = None
        
        # Get AI response
        asyncio.create_task(self.get_ai_response())
    
    async def get_ai_response(self):
        # Add thinking message
        thinking_bubble = MessageBubble("assistant", "Thinking...")
        self.messages_layout.addWidget(thinking_bubble, alignment=Qt.AlignLeft | Qt.AlignTop)
        self.scroll_to_bottom()
        
        try:
            # Send request to API
            response = await self.client.send_request(self.message_history)
            
            # Add response to history
            self.message_history.append({"role": "assistant", "content": response})
            
            # Replace thinking bubble with actual response
            self.messages_layout.removeWidget(thinking_bubble)
            thinking_bubble.deleteLater()

            response_bubble = MessageBubble("assistant", response)
            self.messages_layout.addWidget(response_bubble, alignment=Qt.AlignLeft | Qt.AlignTop)
        except Exception as e:
            # Show error message
            self.messages_layout.removeWidget(thinking_bubble)
            thinking_bubble.deleteLater()
            
            error_bubble = MessageBubble("assistant", f"Error: {str(e)}")
            self.messages_layout.addWidget(error_bubble)
        
        self.scroll_to_bottom()
    
    def scroll_to_bottom(self):
        # Use timer to scroll after UI updates
        QTimer.singleShot(100, self._scroll_to_bottom)
    
    def _scroll_to_bottom(self):
        scrollbar = self.parent().findChild(QScrollArea).verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())