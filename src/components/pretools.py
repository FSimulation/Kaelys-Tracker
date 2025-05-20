import json, sys, os, socket, hashlib, customtkinter as ctk, requests
from datetime import datetime
from src.components.cfg import API_URL



def save_json(data: dict, filename: str) -> None:
    """
    Save data to a JSON file.
    """
    with open(filename, 'w') as f:
        json.dump(data, f)



def load_json(filename: str) -> dict:
    """
    Load data from a JSON file.
    """
    with open(filename, 'r') as f:
        return json.load(f)



def load_txt(filename: str) -> str:
    """
    Load data from a text file.
    """
    with open(filename, 'r') as f:
        return f.read()
    


def save_txt(data: str, filename: str) -> None:
    """
    Save data to a text file.
    """
    with open(filename, 'w') as f:
        f.write(data)



def resource_path(relative_path: str) -> str:
    """Return absolute path to a file, either the program is compiled in .EXE or not"""
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)



def is_server_running(host: str="localhost", port: int=25555) -> bool:
    try:
        with socket.create_connection((host, port), timeout=2):
            return True
    except OSError:
        return False
    


def write_log(message: str, type: str = "info") -> None:
    """
    Write a log message to the console and a log file.
    """
    now = datetime.now()
    now_str = now.strftime("%H:%M:%S") # Format time and date for proper logging
    if type == "info":
        file = resource_path("logs.txt")
    elif type == "error":
        file = resource_path("crash.txt")
    
    try:
        text = load_txt(file)
        text += f"[{now_str}] | {type.upper()}: {message}\n"
        save_txt(text, file)
    except FileNotFoundError:
        save_txt(f"[{now_str}] | {type.upper()}: {message}\n", file)

    print(f"[{now_str}] | {type.upper()}: {message}")



def convert_game_time(iso_str: str):
    dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    return round(dt.hour + dt.minute / 60 + dt.second / 3600, 2)



def generate_job_id(job_data: dict) -> int:
    signature = f"{job_data['market']}_{job_data['source_city_id']}_{job_data['destination_city_id']}_{job_data['destination_company_id']}_{job_data['cargo_definition_id']}"
    
    hash_object = hashlib.md5(signature.encode())
    hash_int = int(hash_object.hexdigest(), 16)
    
    return hash_int % 1000000



def get_switch_value(switch: ctk.CTkSwitch) -> bool:
    """
    Get the value of a CTkSwitch.
    """
    return True if switch.get() == 1 else False
    


def save_settings(s: dict) -> bool:
    """
    Send new tracker settings to API | Save updated settings to memory
    return: True if success, else False
    """
    # Prepare payload
    user_data = load_json(resource_path("data/user.json"))
    payload = {
        "userID": user_data["id"],
        "settings": s
    }

    # Execute
    try:
        response = requests.post(f'{API_URL}/tracker/settings', json=payload)
        result = response.json()
        if result["error"]:
            write_log(f'Error while saving settings: {result["message"]}', type="error")
            return False
        else:
            write_log("Settings saved successfully")

            new_settings = result["settings"]
            memory = load_json(resource_path("data/memory.json"))
            memory["settings"] = new_settings
            save_json(memory, resource_path("data/memory.json"))
            write_log("Settings loaded to memory")

            return True
        
    except Exception as e:
        write_log(f'Error while saving settings: {e}', type="error")
        return False



def load_settings() -> bool:
    """
    Initialization of tracker settings (startup)
    return: True if success, else False
    """
    # Prepare payload
    user_data = load_json(resource_path("data/user.json"))
    payload = {
        "id": user_data["id"]
    }

    # Execute
    response = requests.get(f'{API_URL}/tracker/settings/init', json=payload)
    result = response.json()

    if result["error"]:
        write_log(f'Error while loading settings: {result["message"]}', type="error")
        return False
    else:
        memory = load_json(resource_path("data/memory.json"))
        memory["settings"] = result["settings"]
        write_log("Settings loaded to memory")
        
        return True
    