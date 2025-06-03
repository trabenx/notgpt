from PySide6.QtWidgets import QComboBox
from PySide6.QtCore import Signal

class ModelSelector(QComboBox):
    modelChanged = Signal(dict)  # Signal emits model config
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model_configs = []
        self.currentIndexChanged.connect(self._emit_model_changed)
    
    def load_models(self, models):
        self.model_configs = models
        self.clear()
        for model in models:
            self.addItem(model["name"], model)
    
    def _emit_model_changed(self, index):
        model_config = self.itemData(index)
        self.modelChanged.emit(model_config)