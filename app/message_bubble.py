from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QDateTime
import base64

class MessageBubble(QFrame):
    def __init__(self, message_type, content, parent=None):
        super().__init__(parent)
        self.setObjectName("messageBubble")
        self.setProperty("type", message_type)
    
        # Set minimum width and height
        self.setMinimumWidth(100)
        self.setMinimumHeight(40)
    
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)
    
        # Add content based on type
        color = 'white' if message_type == 'assistant' else '#FFF2DD'        
        if isinstance(content, dict):
            # Multimodal message (text + image)
            if content.get('text'):
                text_label = QLabel(content if not isinstance(content, dict) else content['text'])
                text_label.setWordWrap(True)
                text_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
                text_label.setStyleSheet(f"background: transparent; color: {color};")
                layout.addWidget(text_label)
            
            if content.get('image_base64'):
                pixmap = QPixmap()
                pixmap.loadFromData(base64.b64decode(content['image_base64']))
                image_label = QLabel()
                image_label.setPixmap(pixmap.scaled(300, 300, Qt.KeepAspectRatio))
                image_label.setObjectName("imagePreview")
                image_label.setStyleSheet("background: transparent;")
                layout.addWidget(image_label)
        else:
            # Text-only message
            text_label = QLabel(content)
            text_label.setWordWrap(True)
            text_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            text_label.setStyleSheet(f"background: transparent; color: {color};")
            layout.addWidget(text_label)
    
        # Add timestamp
        timestamp = QDateTime.currentDateTime().toString("hh:mm AP")
        time_label = QLabel(timestamp)
        time_label.setObjectName("timestamp")
        time_label.setStyleSheet(f"background: transparent; color: {color};")
        time_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        layout.addWidget(time_label)


    def setAlignment(self, alignment):
        if alignment == Qt.AlignRight:
            self.setProperty("type", "user")
        elif alignment == Qt.AlignLeft:
            self.setProperty("type", "assistant")
        # Force style update
        self.style().unpolish(self)
        self.style().polish(self)