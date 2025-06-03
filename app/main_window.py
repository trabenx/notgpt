from PySide6.QtWidgets import QMainWindow, QHBoxLayout, QWidget, QSplitter
from .sidebar import Sidebar
from .chat_area import ChatArea

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Not GPT")
        self.resize(1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Splitter for sidebar and chat area
        splitter = QSplitter()
        splitter.setHandleWidth(1)
        main_layout.addWidget(splitter)
        
        # Sidebar
        self.sidebar = Sidebar()
        splitter.addWidget(self.sidebar)
        
        # Chat area
        self.chat_area = ChatArea()
        splitter.addWidget(self.chat_area)
        
        # Set splitter sizes
        splitter.setSizes([250, 750])
        
        # Connect signals
        self.sidebar.modelSelected.connect(self.chat_area.set_current_model)