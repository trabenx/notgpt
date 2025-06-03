pip install pyinstaller
pyinstaller --onefile --windowed --name notgpt main.py
copy models.json dist\models.json
