import customtkinter as ctk, threading, time, asyncio, requests
from src.components.pretools import KaelysAPI, GeneralTools, AppSettings


tools = GeneralTools()
api = KaelysAPI()
settings = AppSettings()


tracking_disabled = True


lastData = {}


class DriverCard(ctk.CTkFrame):
    def __init__(self, master, name, game, *args, **kwargs):
        super().__init__(master, fg_color="#1e2a38", corner_radius=10, *args, **kwargs)
        self.custom_font = ctk.CTkFont(family="Poppins", size=16, weight="bold")

        # Icon (user/truck)
        self.icon = ctk.CTkLabel(self, text="🚛" if game == "ETS2" else "🚚", font=("Arial", 18))
        self.icon.pack(side="left", padx=10, pady=10)

        # Driver name
        self.name_label = ctk.CTkLabel(self, text=name, font=self.custom_font)
        self.name_label.pack(side="left", padx=5, pady=10, anchor="w")

        # Badge game
        badge_color = "#0d6efd" if game == "ETS2" else "#dc3545"
        self.badge = ctk.CTkLabel(
            self,
            text=game,
            font=self.custom_font,
            fg_color=badge_color,
            text_color="white",
            corner_radius=8,
            width=50,
            height=20
        )
        self.badge.pack(side="right", padx=10, pady=10)



class LiveDrivers(ctk.CTkFrame):
    def __init__(self, master=None, *args, **kwargs):
        super().__init__(master, fg_color="transparent", *args, **kwargs)
        self.custom_font = ctk.CTkFont(family="Poppins", size=18, weight="bold")

        # UI setup
        self.setup_ui()

        # Thread update loop
        self.previous_live_drivers = None
        threading.Thread(target=self.update_live_drivers, daemon=True).start()


    def setup_ui(self):
        # Title
        self.live_drivers_label = ctk.CTkLabel(
            self, text="Drivers Online", font=self.custom_font
        )
        self.live_drivers_label.pack(pady=(10, 5))

        # Scrollable frame
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self, fg_color="transparent", orientation="vertical", width=360, height=400
        )
        self.scrollable_frame.pack(padx=15, pady=10)

        # Placeholder
        self.placeholder = ctk.CTkLabel(
            self.scrollable_frame,
            text="No drivers currently in-game",
            font=self.custom_font,
            text_color="grey"
        )
        self.placeholder.pack(pady=10)


    def clear_scrollable(self):
        """Remove all widgets from the scrollable frame"""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()


    def update_live_drivers(self):
        """Background loop to fetch live drivers from API"""
        while True:
            try:
                data = asyncio.run(api.get("/tracker/user/live"))
                if data.get("error"):
                    tools.write_log(f"Error fetching live drivers: {data['message']}", type="error")
                else:
                    live_drivers_ets2 = data.get("ets2", [])
                    live_drivers_ats = data.get("ats", [])

                    self.after(0, lambda: self.refresh_ui(live_drivers_ets2, live_drivers_ats))

            except Exception as e:
                tools.write_log(f"Error fetching live drivers: {str(e)}", type="error")

            time.sleep(30)


    def refresh_ui(self, ets2_list, ats_list):
        """Refresh UI with new drivers list"""
        self.clear_scrollable()

        if not ets2_list and not ats_list:
            self.placeholder = ctk.CTkLabel(
                self.scrollable_frame,
                text="Nobody is online.",
                font=self.custom_font,
                text_color="grey"
            )
            self.placeholder.pack(pady=10)
            return

        # Add ETS2 drivers
        for driver in ets2_list:
            card = DriverCard(self.scrollable_frame, driver, "ETS2")
            card.pack(fill="x", padx=5, pady=5)

        # Add ATS drivers
        for driver in ats_list:
            card = DriverCard(self.scrollable_frame, driver, "ATS")
            card.pack(fill="x", padx=5, pady=5)



class TMPServers(ctk.CTkFrame):
    def __init__(self, master=None, *args, **kwargs):
        super().__init__(master, fg_color="transparent", *args, **kwargs)
        self.custom_font = ctk.CTkFont(family="Poppins", size=18, weight="bold")
        self.setup_ui()
        threading.Thread(target=self.update_servers_loop, daemon=True).start()


    def setup_ui(self):
        # Title
        self.servers_label = ctk.CTkLabel(
            self, text="TruckersMP Traffic", font=self.custom_font
        )
        self.servers_label.pack(pady=(10, 5))

        # Scrollable frame
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self, fg_color="transparent", orientation="vertical", width=320, height=400
        )
        self.scrollable_frame.pack(padx=15, pady=10)

        # Placeholder
        self.placeholder = ctk.CTkLabel(
            self.scrollable_frame,
            text="Loading servers...",
            font=self.custom_font,
            text_color="grey"
        )
        self.placeholder.pack(pady=10)


    def clear_scrollable(self):
        """Remove all widgets from the scrollable frame"""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()


    def update_servers_loop(self):
        """Background loop to fetch TMP servers from API"""
        while True:
            try:
                request = requests.get("https://api.truckersmp.com/v2/servers")
                data = request.json()
                # if data["error"]:
                #     tools.write_log(f"Error fetching TMP servers: {data['message']}", type="error")
                # else:
                tools.write_log("Fetched TMP servers successfully")
                servers = data["response"]
                self.after(0, lambda: self.refresh_ui(servers))

            except Exception as e:
                tools.write_log(f"Error fetching TMP servers: {str(e)}", type="error")

            time.sleep(300)  # Update every 5 minutes


    def refresh_ui(self, servers):
        """Refresh UI with new servers list"""
        self.clear_scrollable()

        if not servers:
            self.placeholder = ctk.CTkLabel(
                self.scrollable_frame,
                text="No server information available.",
                font=self.custom_font,
                text_color="grey"
            )
            self.placeholder.pack(pady=10)
            return

        for server in  servers:
            status_color = "green" if server["online"] == True else "red"
            server_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="#1e2a38", corner_radius=10)
            server_frame.pack(fill="x", padx=5, pady=5)

            status_label = ctk.CTkLabel(server_frame, text=server["shortname"], font=self.custom_font, text_color=status_color)
            status_label.pack(side="left", padx=10, pady=10)

            players_label = ctk.CTkLabel(server_frame, text=f"{server['players']} drivers", font=self.custom_font)
            players_label.pack(side="right", padx=10, pady=10)