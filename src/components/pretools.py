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
    

# def save_settings(setting: str, value: int) -> None:
#     """
#     Save settings to the DB thru the API.
#     """
#     user_data = load_json(resource_path("data/user.json"))
#     payload = {
#         "userID": user_data["userID"],
#         "settings": {setting: value}
#         }
    
#     payload["settings"][setting] = value

#     memory = load_json(resource_path("data/memory.json"))
#     memory["settings"][setting] = value
#     save_json(memory, resource_path("data/memory.json"))
    
#     try:
#         requests.post(f"{API_URL}/tracker/settings", json=payload)
#         write_log(f"Saving settings...", type="info")
#     except requests.exceptions.RequestException as e:
#         write_log(f"Error saving settings: {e}", "error")
#         ctk.CTkMessagebox.show_error("Error", "Failed to save settings. Please check your internet connection.")
#     except json.JSONDecodeError as e:
#         write_log(f"Error decoding JSON: {e}", "error")
#         ctk.CTkMessagebox.show_error("Error", "Failed to save settings. Please check your internet connection.")
#     except Exception as e:
#         write_log(f"Unexpected error: {e}", "error")
#         ctk.CTkMessagebox.show_error("Error", "An unexpected error occurred. Please try again.")


# def load_setting(setting: str, switch: ctk.CTkSwitch) -> int:
#     """
#     Load settings from the API.
#     """
#     user_data = load_json(resource_path("data/user.json"))
#     payload = {
#         "userID": user_data["id"],
#         "settings": [setting]
#         }
    
#     try:
#         response = requests.get(f"{API_URL}/tracker/settings/init", json=payload)
#         response.raise_for_status()
#         if response.status_code != 200:
#             write_log(f"Error loading settings: {response.status_code}", "error")
#             ctk.CTkMessagebox.show_error("Error", "Failed to load settings. Please check your internet connection.")
#         else:
#             data = response.json()
#             switch.set(data["settings"][0])
            
#     except requests.exceptions.RequestException as e:
#         write_log(f"Error loading settings: {e}", "error")
#         ctk.CTkMessagebox.show_error("Error", "Failed to load settings. Please check your internet connection.")
#     except json.JSONDecodeError as e:
#         write_log(f"Error decoding JSON: {e}", "error")
#         ctk.CTkMessagebox.show_error("Error", "Failed to load settings. Please check your internet connection.")
#     except Exception as e:
#         write_log(f"Unexpected error: {e}", "error")
#         ctk.CTkMessagebox.show_error("Error", "An unexpected error occurred. Please try again.")