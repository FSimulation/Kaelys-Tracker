import json, sys, os, socket


def save_json(data, filename):
    """
    Save data to a JSON file.
    """
    with open(filename, 'w') as f:
        json.dump(data, f)


def load_json(filename):
    """
    Load data from a JSON file.
    """
    with open(filename, 'r') as f:
        return json.load(f)


def resource_path(relative_path):
    """Retourne le chemin absolu vers une ressource, que ce soit en .exe ou non"""
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)


def is_server_running(host="localhost", port=25555):
    try:
        with socket.create_connection((host, port), timeout=2):
            return True
    except OSError:
        return False
    