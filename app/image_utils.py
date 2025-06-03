from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, QBuffer, QIODevice, QByteArray
import base64
import requests
from io import BytesIO

def image_to_base64(image_path, max_size=512):
    """Convert image to base64 string with resizing"""
    pixmap = QPixmap(image_path)
    if pixmap.isNull():
        return None
        
    # Scale if needed
    if pixmap.width() > max_size or pixmap.height() > max_size:
        pixmap = pixmap.scaled(max_size, max_size, Qt.KeepAspectRatio)
    
    # Convert to base64
    image = pixmap.toImage()
    buffer = QBuffer()
    buffer.open(QIODevice.WriteOnly)
    image.save(buffer, "PNG")
    buffer.close()
    return base64.b64encode(buffer.data()).decode('utf-8')

def base64_to_pixmap(base64_str):
    """Convert base64 string to QPixmap"""
    image_data = base64.b64decode(base64_str)
    pixmap = QPixmap()
    pixmap.loadFromData(image_data)
    return pixmap

def download_image(url):
    """Download image from URL and return as base64"""
    response = requests.get(url)
    if response.status_code == 200:
        return base64.b64encode(response.content).decode('utf-8')
    return None