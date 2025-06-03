from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QSizePolicy
from PySide6.QtGui import QPixmap, QPalette, QColor
from PySide6.QtCore import Qt, QDateTime
import base64

class MessageBubble(QFrame):
    def __init__(self, message_type, content, parent=None):
        super().__init__(parent)
        self.setObjectName("messageBubble")
        self.setProperty("type", message_type)
        
        # Set size policy to expand vertically
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)
        
        # Add content based on type
        if isinstance(content, dict):
            # Multimodal message (text + image)
            if content.get('text'):
                text_label = QLabel(content['text'])
                text_label.setWordWrap(True)
                text_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
                text_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                text_label.setStyleSheet("""
                    background: transparent; 
                    color: white;
                    padding: 0;
                    margin: 0;
                """)
                layout.addWidget(text_label)
                
            if content.get('image_base64'):
                pixmap = QPixmap()
                pixmap.loadFromData(base64.b64decode(content['image_base64']))
                image_label = QLabel()
                image_label.setPixmap(pixmap.scaled(300, 300, Qt.KeepAspectRatio))
                image_label.setObjectName("imagePreview")
                image_label.setStyleSheet("""
                    background: transparent;
                    padding: 0;
                    margin: 0;
                """)
                layout.addWidget(image_label)
        else:
            # Text-only message
            text_label = QLabel(content)
            text_label.setWordWrap(True)
            text_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            text_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            text_label.setStyleSheet("""
                background: transparent; 
                color: white;
                padding: 0;
                margin: 0;
            """)
            layout.addWidget(text_label)
        
        # Add timestamp
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
        layout.addWidget(time_label)
        
        # Set bubble color based on type
        if message_type == "assistant":
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