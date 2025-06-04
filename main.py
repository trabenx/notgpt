import sys
import asyncio
import qasync
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QFile, QTextStream, QTimer
from app.main_window import MainWindow
from app.config_loader import load_models_config
import logging
logging.basicConfig(level=logging.DEBUG)

def main():
    app = QApplication(sys.argv)
    
    # Load stylesheet
    style_file = QFile("style.qss")
    if style_file.open(QFile.ReadOnly | QFile.Text):
        stream = QTextStream(style_file)
        app.setStyleSheet(stream.readAll())
        style_file.close()
    app.setStyleSheet(app.styleSheet() + """
        QToolTip {
            opacity: 230;
        }
    """)

    # Load models
    models = load_models_config()
    
    logging.info("Application starting")

    # Create main window
    window = MainWindow()
    window.show()
    
    # Load models and select first one
    window.sidebar.load_models(models)
    if models:
        # Use timer to ensure UI is ready
        QTimer.singleShot(100, window.sidebar.select_first_model)
    
    # Set up asyncio event loop
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    with loop:
        sys.exit(loop.run_forever())

if __name__ == "__main__":
    main()