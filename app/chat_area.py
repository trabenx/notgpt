from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QFrame, QHBoxLayout, 
    QLineEdit, QPushButton, QFileDialog, QSizePolicy, QLabel
)
from PySide6.QtCore import Qt, QTimer
from .message_bubble import MessageBubble
from .api_client import OpenAIClient
from .image_utils import image_to_base64
from .audio_utils import record_audio, audio_to_base64
import asyncio
import base64
import threading
import sounddevice as sd
from PySide6.QtGui import QPixmap


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
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.scroll_area = scroll_area
        
        self.messages_container = QWidget()
        self.messages_container.setObjectName("messagesContainer")
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.messages_layout.setContentsMargins(20, 20, 20, 20)
        self.messages_layout.setSpacing(10)
        
        # Add spacer to push messages to top
        self.spacer = QWidget()
        self.spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.messages_layout.addWidget(self.spacer)
        
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
        self.image_button.setObjectName("imageButton")  # Add this
        self.image_button.setToolTip("Add image")
        self.image_button.setFixedSize(40, 40)
        self.image_button.clicked.connect(self.add_image)
        
        # Add audio button to input area
        self.audio_button = QPushButton("🎤")
        self.audio_button.setObjectName("audioButton")  # Add this
        self.audio_button.setToolTip("Record audio")
        self.audio_button.setFixedSize(40, 40)
        self.audio_button.clicked.connect(self.start_audio_recording)
        
        # Audio state
        self.is_recording = False
        self.audio_data = None
        self.sample_rate = 44100  # Default sample rate
        self.recording_timer = QTimer()
        self.recording_timer.timeout.connect(self.update_recording_timer)
        self.recording_time = 0
        
        self.send_button = QPushButton("Send")
        self.send_button.setFixedWidth(80)
        
        input_layout.addWidget(self.image_button)
        input_layout.addWidget(self.audio_button)  # Add to your input layout
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
        
        # Add modality support state
        self.supports_image = False
        self.supports_audio = False

    
    def set_current_model(self, model_config):
        self.current_model = model_config
        self.client = OpenAIClient(model_config)
        # Update modality support
        modalities = model_config.get('modalities', [])
        self.supports_image = 'image' in modalities
        self.supports_audio = 'audio' in modalities
        
        # Update button states
        self.update_button_states()
        self.clear_chat()
    
    def update_button_states(self):
        """Update button states based on model capabilities"""
        self.image_button.setEnabled(self.supports_image)
        self.audio_button.setEnabled(self.supports_audio)
        
        # Update tooltips
        if not self.supports_image:
            self.image_button.setToolTip("Current model doesn't support images")
        else:
            self.image_button.setToolTip("Add image")
            
        if not self.supports_audio:
            self.audio_button.setToolTip("Current model doesn't support audio")
        else:
            self.audio_button.setToolTip("Record audio (10 seconds)")


    def clear_chat(self):
        # Clear chat history
        while self.messages_layout.count() > 1:  # Keep spacer
            item = self.messages_layout.itemAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            self.messages_layout.removeItem(item)
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
                self.add_message_bubble(preview, Qt.AlignRight)
    
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
        self.add_message_bubble(user_bubble, Qt.AlignRight)
        
        # Add to history
        self.message_history.append({"role": "user", "content": content})
        
        # Clear input
        self.message_input.clear()
        self.current_image = None
        
        # Get AI response
        asyncio.create_task(self.get_ai_response())
    
    def add_message_bubble(self, bubble, alignment):
        # Insert before spacer
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, bubble, alignment=alignment)
        self.scroll_to_bottom()
        
    async def get_ai_response(self):
        # Create thinking bubble
        thinking_bubble = MessageBubble("assistant", "Thinking...")
        self.add_message_bubble(thinking_bubble, Qt.AlignLeft)
    
        try:
            # For streaming responses
            full_response = ""
            async for chunk in self.client.stream_response(self.message_history):
                full_response += chunk
                # Update existing bubble
                thinking_bubble.update_content(full_response)
                self.scroll_to_bottom()
            
            # Final update
            self.message_history.append({"role": "assistant", "content": full_response})
            thinking_bubble.update_content(full_response)
        
        except Exception as e:
            # Handle errors
            error_bubble = MessageBubble("assistant", f"Error: {str(e)}")
            self.add_message_bubble(error_bubble, Qt.AlignLeft)

    
    async def get_ai_response(self):
        # Add thinking message
        thinking_bubble = MessageBubble("assistant", "Thinking...")
        self.add_message_bubble(thinking_bubble, Qt.AlignLeft)
    
        try:
            full_response = ""
            response_bubble = None
        
            # For streaming API
            if hasattr(self.client, 'stream_response'):
                async for chunk in self.client.stream_response(self.message_history):
                    if not response_bubble:
                        # Remove thinking bubble
                        self.remove_message_bubble(thinking_bubble)
                    
                        # Create new bubble for actual response
                        response_bubble = MessageBubble("assistant", chunk)
                        self.add_message_bubble(response_bubble, Qt.AlignLeft)
                    else:
                        # Update existing bubble
                        response_bubble.update_content(full_response + chunk)
                
                    full_response += chunk
                    self.scroll_to_bottom()
                
                    # Small delay to allow UI updates
                    await asyncio.sleep(0.01)
            else:
                # Non-streaming fallback
                response = await self.client.send_request(self.message_history)
                self.remove_message_bubble(thinking_bubble)
                response_bubble = MessageBubble("assistant", response)
                self.add_message_bubble(response_bubble, Qt.AlignLeft)
                full_response = response
        
            # Add to history
            self.message_history.append({"role": "assistant", "content": full_response})
        
        except Exception as e:
            # Remove thinking bubble
            self.remove_message_bubble(thinking_bubble)
        
            # Show error message
            error_bubble = MessageBubble("assistant", f"Error: {str(e)}")
            self.add_message_bubble(error_bubble, Qt.AlignLeft)
    
        self.scroll_to_bottom()

    def remove_message_bubble(self, bubble):
        """Remove a message bubble from the layout"""
        for i in range(self.messages_layout.count()):
            item = self.messages_layout.itemAt(i)
            widget = item.widget()
            if widget == bubble:
                self.messages_layout.removeWidget(bubble)
                bubble.deleteLater()
                return


    def start_audio_recording(self):
        """Start audio recording in a separate thread"""
        if self.is_recording:
            self.stop_audio_recording()
            return
            
        self.is_recording = True
        self.recording_time = 0
        self.audio_data = None  # Reset previous audio data
        self.audio_button.setText("⏹️")
        self.audio_button.setStyleSheet("background-color: #ff5555;")
        
        # Start timer for UI updates
        self.recording_timer.start(1000)  # Update every second
        
        # Start recording in a separate thread
        self.audio_thread = threading.Thread(target=self.record_audio_thread)
        self.audio_thread.daemon = True  # Allow thread to exit with app
        self.audio_thread.start()
    
    def record_audio_thread(self):
        """Thread for audio recording"""
        try:
            # Record audio for up to 10 seconds
            duration = 10
            self.audio_data = sd.rec(int(duration * self.sample_rate),
                                    samplerate=self.sample_rate,
                                    channels=1,
                                    dtype='float32')
            sd.wait()  # Wait until recording is finished
        except Exception as e:
            print(f"Recording error: {str(e)}")
    
    def update_recording_timer(self):
        """Update UI during recording"""
        self.recording_time += 1
        self.audio_button.setText(f"⏹️{self.recording_time}s")
        
        # Add flashing indicator
        if self.recording_time % 2 == 0:
            self.audio_button.setStyleSheet("background-color: #ff5555;")
        else:
            self.audio_button.setStyleSheet("background-color: #ff0000;")
            
        # Auto-stop after 10 seconds
        if self.recording_time >= 10:
            self.stop_audio_recording()

    def stop_audio_recording(self):
        """Stop recording and process audio"""
        if not self.is_recording:
            return
            
        self.is_recording = False
        self.recording_timer.stop()
        self.audio_button.setText("🎤")
        self.audio_button.setStyleSheet("")
        
        # Wait for recording thread to finish
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join(timeout=1.0)  # Wait up to 1 second
        
        # Check if we have audio data
        if self.audio_data is None or len(self.audio_data) == 0:
            print("No audio data recorded")
            return
            
        try:
            # Convert to base64
            base64_audio = audio_to_base64(self.audio_data, self.sample_rate)
            
            # Create message content
            content = {"audio_base64": base64_audio}
            
            # Add user message (audio)
            user_bubble = MessageBubble("user", content)
            self.add_message_bubble(user_bubble, Qt.AlignRight)
            
            # Add to history
            self.message_history.append({"role": "user", "content": content})
            
            # Send to API
            asyncio.create_task(self.get_ai_response())
        except Exception as e:
            print(f"Audio processing error: {str(e)}")
            error_bubble = MessageBubble("assistant", f"Audio error: {str(e)}")
            self.add_message_bubble(error_bubble, Qt.AlignLeft)

    
    def scroll_to_bottom(self):
        # Scroll to bottom after UI updates
        QTimer.singleShot(50, self._scroll_to_bottom)
    
    def _scroll_to_bottom(self):
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())