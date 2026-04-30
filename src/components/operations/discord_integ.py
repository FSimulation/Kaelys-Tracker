import time, asyncio
from pypresence import Presence
from truck_telemetry import truck_telemetry
from src.components.pretools import GeneralTools, KaelysAPI


tools = GeneralTools()


infos = tools.load_json(tools.resource_path("properties/infos.json"))
CLIENT_ID = infos["RPC_Client"]



class RichPresence:
    def __init__(self):
        self.rpc = Presence(CLIENT_ID)
        self.connected = False
        self.running = False
        self.thread = None
        self.previous_game = None

    
    def get_game(self):
        try:
            data = truck_telemetry.get_data()
            return data["game"]
        except (FileNotFoundError, AttributeError):
            return "Idle"


    def connect(self):
        if not self.connected:
            self.rpc.connect()
            self.connected = True
            tools.write_log("Connected to Discord RPC")


    def update_presence(self):
        # Load settings
        memory = tools.load_json(tools.resource_path("data/memory.json"))
        settings = memory["settings"]
        enabledRPC = settings["RPC"]

        infos = tools.load_json(tools.resource_path("properties/infos.json"))
        version = infos["version"]

        # Execute
        if enabledRPC:
            try:
                self.connect()
                game_int = self.get_game()
                game = ""

                if game_int == 1:
                    game = "Euro Truck Simulator 2"
                    img = "ets2"
                elif game_int == 2:
                    game = "American Truck Simulator"
                    img = "ats"
                else:
                    game = game_int
                    img = "ktrack"

                if not self.previous_game or self.previous_game != game:
                    self.rpc.update(
                        state=version,
                        details=game,
                        start=time.time(),
                        large_image=img,
                        large_text=game,
                        buttons=[
                            {"label": "Visit our website", "url": "https://kaelys-virtual-trucking.com"}                        ]
                    )
                    self.previous_game = game
                    tools.write_log("Presence updated")
            except Exception as e:
                tools.write_log(f"Error encountered in RPC loop: {e}", type="error")
                

    def run_loop(self):
        self.running = True
        def loop():
            while self.running:
                self.update_presence()
                time.sleep(15)
        loop()


    def stop(self):
        self.running = False
        tools.write_log("Discord RPC stopped")



class LoginV2:
    def __init__(self, discordName: str):
        self.discordName = discordName
    

    def get_code(self):
        # get tracker version
        infos = tools.load_json(tools.resource_path("properties/infos.json"))
        version = infos["version"]

        # get login code from API
        api = KaelysAPI()
        response = asyncio.run(api.get("/tracker/loginv2/code", request_data={"discordName": self.discordName, "version": version}))
        if response["error"]:
            tools.write_log(f"Error getting login code: {response['message']}", type="error")
            return False
        else:
            return True


    def auth(self, code: str):
        # get tracker version
        infos = tools.load_json(tools.resource_path("properties/infos.json"))
        version = infos["version"]

        #get driverID from API
        api = KaelysAPI()
        response = asyncio.run(api.get("/tracker/loginv2/auth", request_data={"discordName": self.discordName, "code": code, "version": version}))
        
        if response["error"]:
            tools.write_log(f"Error authenticating: {response['message']}", type="error")
            return False, None
        else:
            return True, response["user"]
    

    def autologin(self):
        # get tracker version
        infos = tools.load_json(tools.resource_path("properties/infos.json"))
        version = infos["version"]

        # get driverID from API
        api = KaelysAPI()
        response = asyncio.run(api.get("/tracker/loginv2/autologin", request_data={"discordName": self.discordName, "version": version}))
        
        if response["error"]:
            tools.write_log(f"Error with autologin: {response['message']}", type="error")
            return False, None
        else:
            return True, response["user"]
        
