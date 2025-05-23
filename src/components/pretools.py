import json, sys, os, aiohttp, hashlib, customtkinter as ctk, asyncio
from datetime import datetime
from playsound import playsound



## GENERAL TOOLS
class GeneralTools():
    def __init__(self, api=None):
        self.api = api


    def save_json(self, data: dict, filename: str) -> None:
        with open(filename, 'w') as f:
            json.dump(data, f)


    def load_json(self, filename: str) -> dict:
        with open(filename, 'r') as f:
            return json.load(f)


    def load_txt(self, filename: str) -> str:
        with open(filename, 'r') as f:
            return f.read()


    def save_txt(self, data: str, filename: str) -> None:
        with open(filename, 'w') as f:
            f.write(data)


    def resource_path(self, relative_path: str) -> str:
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        return os.path.join(base_path, relative_path)


    def write_log(self, message: str, type: str = "info") -> None:
        now = datetime.now()
        now_str = now.strftime("%H:%M:%S")
        if type == "info":
            file = self.resource_path("logs.txt")
        elif type == "error":
            file = self.resource_path("crash.txt")
        
        try:
            text = self.load_txt(file)
            text += f"[{now_str}] | {type.upper()}: {message}\n"
            self.save_txt(text, file)
        except FileNotFoundError:
            self.save_txt(f"[{now_str}] | {type.upper()}: {message}\n", file)

        print(f"[{now_str}] | {type.upper()}: {message}")


    def convert_game_time(self, iso_str: str):
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return round(dt.hour + dt.minute / 60 + dt.second / 3600, 2)


    def generate_job_id(self, job_data: dict) -> int:
        signature = f"{job_data['market']}_{job_data['source_city_id']}_{job_data['destination_city_id']}_{job_data['destination_company_id']}_{job_data['cargo_definition_id']}"
        hash_object = hashlib.md5(signature.encode())
        hash_int = int(hash_object.hexdigest(), 16)
        return hash_int % 1000000


    def get_switch_value(self, switch: ctk.CTkSwitch) -> bool:
        return True if switch.get() == 1 else False
    

    def walkie_sound(self):
        playsound(self.resource_path("src/static/walkie.mp3"))



## API TOOLS
class KaelysAPI():
    def __init__(self):
        self.API_URL = "https://api-kaelysvirtual.onrender.com"
        self.tools = GeneralTools()
        if not self.tools:
            raise ValueError("KaelysAPI requires a 'tools' instance.")


    async def get_status(self):
        async with aiohttp.ClientSession() as session:
            self.tools.write_log("API -> GET STATUS")
            async with session.get(f"{self.API_URL}/") as response:
                return response.status


    async def get(self, route: str, request_data: dict = None):
        async with aiohttp.ClientSession() as session:
            self.tools.write_log(f'API -> GET {route}')

            url = f'{self.API_URL}{route}'
            
            if request_data is not None:
                async with session.get(url, json=request_data) as response:
                    self.tools.write_log(f'Response status: {response.status}')
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        message = "Interaction with the API has failed"
                        self.tools.write_log(message, type="error")
                        return {"error": True, "message": message}
            else:
                async with session.get(url) as response:
                    self.tools.write_log(f'Response status: {response.status}')
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        message = "Interaction with the API has failed"
                        self.tools.write_log(message, type="error")
                        return {"error": True, "message": message}


    async def post(self, route: str, request_data: dict):
        async with aiohttp.ClientSession() as session:
            self.tools.write_log(f'API -> POST {route}')
            async with session.post(f'{self.API_URL}{route}', json=request_data) as response:
                self.tools.write_log(f'Response status: {response.status}')
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    message = "Interaction with the API has failed"
                    self.tools.write_log(message, type="error")
                    return {"error": True, "message": message}


    async def delete(self, route: str, request_data: dict):
        async with aiohttp.ClientSession() as session:
            self.tools.write_log(f'API -> DELETE {route}')
            async with session.delete(f'{self.API_URL}{route}', json=request_data) as response:
                self.tools.write_log(f'Response status: {response.status}')
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    message = "Interaction with the API has failed"
                    self.tools.write_log(message, type="error")
                    return {"error": True, "message": message}


    async def get_job_export(self):
        user_data = self.tools.load_json(self.tools.resource_path("data/user.json"))
        userID = user_data["id"]
        payload = {"id": userID}

        route = "/tracker/deliveries/export"
        async with aiohttp.ClientSession() as session:
            self.tools.write_log(f'API -> GET {route}')
            async with session.get(f"{self.API_URL}{route}", json=payload) as response:
                if response.status == 200:
                    return True, response.headers, response.content
                else:
                    return False, "", ""
                
                

# TEMPORARY -> SETTINGS MATTERS | Please don't edit anything here.
class AppSettings():
    def __init__(self):
        self.tools = GeneralTools()
        self.api = KaelysAPI()


    async def save(self, s: dict) -> bool:
        user_data = self.tools.load_json(self.tools.resource_path("data/user.json"))
        payload = {
            "userID": user_data["id"],
            "settings": s
        }

        try:
            response = await self.api.post("/tracker/settings", payload)
            if response["error"]:
                self.tools.write_log(f'Error while saving settings: {response["message"]}', type="error")
                return False
            else:
                self.tools.write_log("Settings saved successfully")

                new_settings = response["settings"]
                memory = self.tools.load_json(self.tools.resource_path("data/memory.json"))
                memory["settings"] = new_settings
                self.tools.save_json(memory, self.tools.resource_path("data/memory.json"))
                self.tools.write_log("Settings loaded to memory")

                return True
        except Exception as e:
            self.tools.write_log(f'Error while saving settings: {e}', type="error")
            return False


    async def load(self) -> bool:
        user_data = self.tools.load_json(self.tools.resource_path("data/user.json"))
        payload = {
            "id": user_data["id"]
        }

        response = await self.api.get("/tracker/settings/init", payload)

        if response["error"]:
            self.tools.write_log(f'Error while loading settings: {response["message"]}', type="error")
            return False
        else:
            memory = self.tools.load_json(self.tools.resource_path("data/memory.json"))
            memory["settings"] = response["settings"]
            self.tools.write_log("Settings loaded to memory")
            return True





