import os
import subprocess
import socket
import time
import webview

# Empêche l'ouverture du navigateur
os.environ["BROWSER"] = "none"

PORT = 8501

# Lance Streamlit comme un vrai process
process = subprocess.Popen(
    [
        "streamlit",
        "run",
        "app.py",
        "--server.port",
        str(PORT),
        "--server.headless",
        "true",
        "--browser.gatherUsageStats",
        "false",
    ],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)


# Attend que Streamlit démarre
def wait_for_server():
    while True:
        try:
            with socket.create_connection(("127.0.0.1", PORT), timeout=1):
                return
        except OSError:
            time.sleep(0.1)


wait_for_server()

# Ouvre la fenêtre desktop
webview.create_window(
    "Mon Application",
    f"http://127.0.0.1:{PORT}",
    width=1200,
    height=800,
)

# Lance pywebview
webview.start(gui="edgechromium")

# Ferme Streamlit quand l'app se ferme
process.kill()