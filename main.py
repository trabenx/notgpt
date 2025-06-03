import sys
import asyncio
import qasync
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QFile, QTextStream
from app.main_window import MainWindow
from app.config_loader import load_models_config

def main():
    app = QApplication(sys.argv)
    
    # Load stylesheet
    style_file = QFile("style.qss")
    if style_file.open(QFile.ReadOnly | QFile.Text):
        stream = QTextStream(style_file)
        app.setStyleSheet(stream.readAll())
        style_file.close()
    
    # Load models
    models = load_models_config()
    
    # Create main window
    window = MainWindow()
    
    # Load models into sidebar
    window.sidebar.load_models(models)
    
    # Set initial model if available
    if models:
        # Select first model
        window.sidebar.model_list.setCurrentRow(0)
        # Manually trigger the model selection
        window.sidebar._on_model_selected()
    
    window.show()
    
    # Set up asyncio event loop
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    with loop:
        sys.exit(loop.run_forever())

if __name__ == "__main__":
    main()