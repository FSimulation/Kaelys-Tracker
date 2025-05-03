import json, sys, os, socket, hashlib, customtkinter as ctk
from datetime import datetime



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
    

def load_txt(filename):
    """
    Load data from a text file.
    """
    with open(filename, 'r') as f:
        return f.read()
    

def save_txt(data, filename):
    """
    Save data to a text file.
    """
    with open(filename, 'w') as f:
        f.write(data)


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
    

def write_log(message: str, type: str = "info"):
    """
    Write a log message to the console and a log file.
    """
    if type == "info":
        file = resource_path("logs.txt")
    elif type == "error":
        file = resource_path("crash.txt")
    
    try:
        text = load_txt(file)
        text += f"{type.upper()}: {message}\n"
        save_txt(text, file)
    except FileNotFoundError:
        save_txt(f"{type.upper()}: {message}\n", file)

    print(f"{type.upper()}: {message}")


def convert_game_time(iso_str: str):
    dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    return round(dt.hour + dt.minute / 60 + dt.second / 3600, 2)


def generate_job_id(job_data):
    signature = f"{job_data['market']}_{job_data['source_city_id']}_{job_data['destination_city_id']}_{job_data['destination_company_id']}_{job_data['cargo_definition_id']}"
    
    hash_object = hashlib.md5(signature.encode())
    hash_int = int(hash_object.hexdigest(), 16)
    
    return hash_int % 1000000


