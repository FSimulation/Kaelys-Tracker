from pypresence import Presence
from truck_telemetry import truck_telemetry
import time
from src.components.pretools import GeneralTools


tools = GeneralTools()


CLIENT_ID = "1322271148167135303"  # Ton client ID Discord



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
                            {"label": "Discord Guild", "url": "https://discord.gg/C95vassuy4"},
                            {"label": "Video Trailer", "url": "https://www.youtube.com/watch?v=BjgIGn5Wa4w"}
                        ]
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
