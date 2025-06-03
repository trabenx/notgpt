from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QSizePolicy, QPushButton
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QDateTime, QSize, QTimer
import sys
import base64
import tempfile
import os
import subprocess

class MessageBubble(QFrame):
    def __init__(self, message_type, content, parent=None):
        super().__init__(parent)
        self.setObjectName("messageBubble")
        self.setProperty("type", message_type)
        
        # Set size policy to expand vertically
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(12, 8, 12, 8)
        self.layout.setSpacing(4)
        
        # Create content
        self.create_content(content)
        
        # Set bubble color based on type
        self.update_stylesheet()
    
    def create_content(self, content):
        """Create content widgets based on message type"""
        # Clear any existing content
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add content based on type
        if isinstance(content, dict):
            # Multimodal message (text + image)
            if content.get('text'):
                self.add_text_label(content['text'])
            if content.get('image_base64'):
                self.add_image_label(content['image_base64'])
            if content.get('audio_base64'):
                self.add_audio_label(content['audio_base64'])
        else:
            # Text-only message
            self.add_text_label(content)
        
        # Add timestamp
        self.add_timestamp()
    
    def add_text_label(self, text):
        """Add text label to the bubble"""
        text_label = QLabel(text)
        text_label.setWordWrap(True)
        text_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        text_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        text_label.setStyleSheet("""
            background: transparent; 
            color: white;
            padding: 0;
            margin: 0;
        """)
        self.layout.addWidget(text_label)
    
    def add_image_label(self, image_base64):
        """Add image to the bubble"""
        pixmap = QPixmap()
        pixmap.loadFromData(base64.b64decode(image_base64))
        image_label = QLabel()
        image_label.setPixmap(pixmap.scaled(300, 300, Qt.KeepAspectRatio))
        image_label.setObjectName("imagePreview")
        image_label.setStyleSheet("""
            background: transparent;
            padding: 0;
            margin: 0;
        """)
        self.layout.addWidget(image_label)
    
    def add_audio_label(self, audio_base64):
        """Add audio player to the bubble"""
        audio_label = QLabel("🔊 Audio Message")
        audio_label.setStyleSheet("""
            background: transparent; 
            color: white;
            padding: 0;
            margin: 0;
        """)
        self.layout.addWidget(audio_label)
        
        # Add play button
        play_button = QPushButton("▶️ Play")
        play_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 10px;
                padding: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #66BB6A;
            }
        """)
        play_button.setFixedSize(80, 30)
        
        # Store audio data in the button
        play_button.audio_base64 = audio_base64
        
        # Connect the click event
        play_button.clicked.connect(lambda: self.play_audio(play_button.audio_base64))
        
        self.layout.addWidget(play_button)

    def play_audio(self, audio_base64):
        """Play audio using system player"""
        try:
            # Decode the base64 audio data
            audio_bytes = base64.b64decode(audio_base64)
            
            # Create temporary audio file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_bytes)
                temp_path = temp_file.name
            
            # Play audio using system player
            if sys.platform == "win32":  # Windows
                os.startfile(temp_path)
            elif sys.platform == "darwin":  # macOS
                subprocess.run(["afplay", temp_path])
            else:  # Linux
                subprocess.run(["aplay", temp_path])
                
            # Schedule file deletion after playback
            QTimer.singleShot(10000, lambda: os.unlink(temp_path))
            
        except Exception as e:
            print(f"Error playing audio: {str(e)}")

    
    def add_timestamp(self):
        """Add timestamp to the bubble"""
        timestamp = QDateTime.currentDateTime().toString("hh:mm AP")
        time_label = QLabel(timestamp)
        time_label.setObjectName("timestamp")
        time_label.setStyleSheet("""
            background: transparent; 
            color: rgba(255, 255, 255, 0.7);
            font-size: 11px;
            padding-top: 4px;
            margin: 0;
        """)
        time_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.layout.addWidget(time_label)
    
    def update_content(self, new_content):
        """Update bubble content dynamically"""
        self.create_content(new_content)
        self.update_stylesheet()
        self.adjustSize()
    
    def update_stylesheet(self):
        """Update styles based on message type"""
        if self.property("type") == "assistant":
            self.setStyleSheet("""
                MessageBubble[type="assistant"] {
                    background-color: #333333;
                    border-radius: 18px;
                    border-bottom-left-radius: 4px;
                    padding: 12px 16px;
                    margin-left: 0;
                    margin-right: 20%;
                    color: white;
                }
            """)
        else:
            self.setStyleSheet("""
                MessageBubble[type="user"] {
                    background-color: #0B57D0;
                    border-radius: 18px;
                    border-bottom-right-radius: 4px;
                    padding: 12px 16px;
                    margin-left: 20%;
                    margin-right: 0;
                    color: white;
                }
            """)
    
    def sizeHint(self):
        """Provide appropriate size hint for dynamic content"""
        return QSize(super().sizeHint().width(), 
                     self.layout.sizeHint().height() + 20)