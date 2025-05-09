from pypresence import Presence
from truck_telemetry import truck_telemetry
import time
from src.components.pretools import write_log


CLIENT_ID = "1370341805769625732"  # Ton client ID Discord



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
            return "Idling"


    def connect(self):
        if not self.connected:
            self.rpc.connect()
            self.connected = True
            write_log("Connected to Discord RPC")


    def update_presence(self, state):
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
                state=state,
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
            write_log("Presence updated")


    def run_loop(self):
        self.running = True

        def loop():
            while self.running:
                self.update_presence("www.kaelysvirtual.streamlit.app")
                time.sleep(15)

        loop()


    def stop(self):
        self.running = False
        write_log("Discord RPC stopped")
