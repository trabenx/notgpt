from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLabel
from PySide6.QtCore import Signal, QTimer

class Sidebar(QWidget):
    modelSelected = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self.setObjectName("sidebar")
        self.setMinimumWidth(250)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title = QLabel("Models")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            padding: 15px;
            border-bottom: 1px solid #2d2d2d;
        """)
        layout.addWidget(title)
        
        # Model list
        self.model_list = QListWidget()
        self.model_list.setStyleSheet("""
            QListWidget::item {
                padding: 12px 15px;
            }
        """)
        self.model_list.itemSelectionChanged.connect(self._on_model_selected)
        layout.addWidget(self.model_list, 1)
        
        self.models = []
    
    def load_models(self, models):
        self.models = models or []
        self.model_list.clear()
        for model in self.models:
            self.model_list.addItem(model["name"])
    
    def select_first_model(self):
        """Select and emit the first model if available"""
        if self.model_list.count() > 0:
            self.model_list.setCurrentRow(0)
            self._on_model_selected()
    
    def _on_model_selected(self):
        selected_index = self.model_list.currentRow()
        if 0 <= selected_index < len(self.models):
            self.modelSelected.emit(self.models[selected_index])