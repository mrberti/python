from pathlib import Path
import webbrowser

base = Path(__file__).parent
index = base / "index.html"

webbrowser.open(index.as_uri())