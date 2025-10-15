import customtkinter as ctk, threading, time, asyncio, tkinter as tk, requests, sys
from PIL import Image
from io import BytesIO
from tkinter import filedialog
from NaviTrack import tracking_disabled
from src.components.pretools import KaelysAPI, GeneralTools, AppSettings
from truck_telemetry import truck_telemetry
from src.components.tracking.deliveries import Deliveries
from tkinter import messagebox


tools = GeneralTools()
api = KaelysAPI()
settings = AppSettings()


lastData = {}


# class JobCard(ctk.CTkFrame):
#     def __init__(self, parent, job_data, **kwargs):
#         super().__init__(parent, fg_color="#323232", **kwargs)
        
#         # Exemple de job_data : {"title": "Livraison Paris", "status": "En cours"}
#         self.label_title = ctk.CTkLabel(self, text=job_data["title"], font=("Arial", 14, "bold"))
#         self.label_title.pack(anchor="w", padx=10, pady=(5, 0))

#         self.label_status = ctk.CTkLabel(self, text=f"Status: {job_data['status']}", text_color="gray")
#         self.label_status.pack(anchor="w", padx=10, pady=(0, 5))



class HomeLeft(ctk.CTkFrame):
    def __init__(self, master=None, *args, **kwargs):
        super().__init__(master, fg_color="transparent", *args, **kwargs)
        self.custom_font = ctk.CTkFont(family="Poppins", size=16, weight="bold")
        self.previous_pick = None
        self.user = tools.load_json(tools.resource_path("data/user.json"))
        self.setup_ui()


    def setup_ui(self):
        ### === USER PROFILE FRAME ===
        ## == PROFILE FRAME == 
        profile_frame = ctk.CTkFrame(self, fg_color="transparent")
        profile_frame.grid(row=0, column=0)

        ## == TOP ==
        top_profile_frame = ctk.CTkFrame(profile_frame, fg_color="transparent")
        top_profile_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        top_profile_frame.grid_columnconfigure(0, weight=1)
        top_profile_frame.grid_columnconfigure(1, weight=1)

        # = TOP CONTENT =
        image = Image.open(tools.resource_path("src/static/icon/default_pfp.png"))
        std_image = ctk.CTkImage(light_image=image, dark_image=image, size=(100, 100))
        self.pfp_label = ctk.CTkLabel(top_profile_frame, text="", image=std_image, justify="left")
        self.pfp_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.pfp_infos = ctk.CTkLabel(top_profile_frame, text="Loading profile...", font=self.custom_font)
        self.pfp_infos.grid(row=0, column=1, padx=5, pady=5, sticky="e")

        ## == BOTTOM ==
        bottom_profile_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_profile_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        bottom_profile_frame.grid_columnconfigure(0, weight=1)
        bottom_profile_frame.grid_columnconfigure(1, weight=1)

        # = BOTTOM CONTENT =
        self.user_role_label = ctk.CTkLabel(bottom_profile_frame, text="Role:", font=self.custom_font, justify="left")
        self.user_role_label.grid(row=1, column=0, sticky="w", pady=5, padx=(0, 15))

        self.user_role_value = ctk.CTkLabel(bottom_profile_frame, text="", font=self.custom_font, justify="left")
        self.user_role_value.grid(row=1, column=1, sticky="w", pady=5, padx=(15, 0))

        self.user_discordID_label = ctk.CTkLabel(bottom_profile_frame, text="Discord ID:", font=self.custom_font, justify="left")
        self.user_discordID_label.grid(row=0, column=0, sticky="w", pady=5, padx=(0, 15))

        self.user_discordID_value = ctk.CTkLabel(bottom_profile_frame, text="", font=self.custom_font, justify="left")
        self.user_discordID_value.grid(row=0, column=1, sticky="w", pady=5, padx=(15,0))

        ## == STATISTICS FRAME ==
        self.statistics_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.statistics_frame.grid(row=2, column=0, sticky="ew")
        self.statistics_frame.grid_columnconfigure((0, 1), weight=1)

        # 
        self.separator = ctk.CTkFrame(self.statistics_frame, height=2, fg_color="#555555")
        self.separator.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=(10, 20))


        # ---- Deliveries ----
        self.deliveries_frame = ctk.CTkFrame(self.statistics_frame, fg_color="transparent")
        self.deliveries_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.deliveries_frame.grid_columnconfigure(1, weight=1)

        self.deliveries_icon_label = ctk.CTkLabel(
            self.deliveries_frame, text="", 
            image=ctk.CTkImage(light_image=Image.open(tools.resource_path("src/static/icon/delivery.png")),
                               dark_image=Image.open(tools.resource_path("src/static/icon/delivery.png")), size=(48, 48))
        )
        self.deliveries_icon_label.grid(row=0, column=0, rowspan=2, padx=5, pady=5, sticky="w")
        self.deliveries_label = ctk.CTkLabel(self.deliveries_frame, text="Deliveries", font=self.custom_font)
        self.deliveries_label.grid(row=0, column=1, padx=5, pady=(5, 0), sticky="w")
        self.deliveries_value = ctk.CTkLabel(self.deliveries_frame, text="0", font=self.custom_font)
        self.deliveries_value.grid(row=1, column=1, padx=5, pady=(0, 5), sticky="w")

        # ---- Wallet ----
        self.wallet_frame = ctk.CTkFrame(self.statistics_frame, fg_color="transparent")
        self.wallet_frame.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.wallet_frame.grid_columnconfigure(1, weight=1)

        self.wallet_icon_label = ctk.CTkLabel(
            self.wallet_frame, text="",
            image=ctk.CTkImage(light_image=Image.open(tools.resource_path("src/static/icon/wallet.png")),
                               dark_image=Image.open(tools.resource_path("src/static/icon/wallet.png")), size=(48, 48))
        )
        self.wallet_icon_label.grid(row=0, column=0, rowspan=2, padx=5, pady=5, sticky="w")
        self.wallet_label = ctk.CTkLabel(self.wallet_frame, text="Wallet", font=self.custom_font)
        self.wallet_label.grid(row=0, column=1, padx=5, pady=(5, 0), sticky="w")
        self.wallet_value = ctk.CTkLabel(self.wallet_frame, text="$0", font=self.custom_font)
        self.wallet_value.grid(row=1, column=1, padx=5, pady=(0, 5), sticky="w")

        # ---- Rank ----
        self.rank_frame = ctk.CTkFrame(self.statistics_frame, fg_color="transparent")
        self.rank_frame.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        self.rank_frame.grid_columnconfigure(1, weight=1)

        self.rank_icon_label = ctk.CTkLabel(
            self.rank_frame, text="",
            image=ctk.CTkImage(light_image=Image.open(tools.resource_path("src/static/icon/rank.png")),
                               dark_image=Image.open(tools.resource_path("src/static/icon/rank.png")), size=(48, 48))
        )
        self.rank_icon_label.grid(row=0, column=0, rowspan=2, padx=5, pady=5, sticky="w")
        self.rank_label = ctk.CTkLabel(self.rank_frame, text="Rank", font=self.custom_font)
        self.rank_label.grid(row=0, column=1, padx=5, pady=(5, 0), sticky="w")
        self.rank_value = ctk.CTkLabel(self.rank_frame, text="0", font=self.custom_font)
        self.rank_value.grid(row=1, column=1, padx=5, pady=(0, 5), sticky="w")

        # ---- Logbook Button ----
        self.logbook_btn_frame = ctk.CTkFrame(self.statistics_frame, fg_color="transparent")
        self.logbook_btn_frame.grid(row=2, column=1, padx=3, pady=5, sticky="ew")
        self.logbook_btn_frame.grid_columnconfigure(1, weight=1)

        self.logbook_button = ctk.CTkButton(self.logbook_btn_frame, text="Logbook", height=40,
                                       fg_color="#12a4b7", hover_color="#0e8ea0",
                                       font=self.custom_font, state="disabled")
        self.logbook_button.grid(row=0, column=1, padx=5, pady=(5, 0), sticky="w")

        #[UNUSED]
        # # ---- Total playtime ----
        # self.playtime_frame = ctk.CTkFrame(self.statistics_frame, fg_color="transparent")
        # self.playtime_frame.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        # self.playtime_frame.grid_columnconfigure(1, weight=1)

        # self.playtime_icon_label = ctk.CTkLabel(
        #     self.playtime_frame, text="",
        #     image=ctk.CTkImage(light_image=Image.open("src/static/playtime.png"),
        #                        dark_image=Image.open("src/static/playtime.png"), size=(48, 48))
        # )
        # self.playtime_icon_label.grid(row=0, column=0, rowspan=2, padx=5, pady=5, sticky="w")
        # # self.playtime_label = ctk.CTkLabel(self.playtime_frame, text="Total playtime", font=self.custom_font)
        # # self.playtime_label.grid(row=0, column=1, padx=5, pady=(5, 0), sticky="w")
        # self.playtime_value = ctk.CTkLabel(self.playtime_frame, text="0 h", font=self.custom_font)
        # self.playtime_value.grid(row=1, column=1, padx=5, pady=(0, 5), sticky="w")

        # # ---- Current job ----
        # self.current_job_frame = ctk.CTkFrame(self.statistics_frame, fg_color="transparent")
        # self.current_job_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        # self.current_job_frame.grid_columnconfigure(1, weight=1)

        # self.current_job_icon_label = ctk.CTkLabel(
        #     self.current_job_frame, text="",
        #     image=ctk.CTkImage(light_image=Image.open("src/static/current_job.png"),
        #                        dark_image=Image.open("src/static/current_job.png"), size=(48, 48))
        # )
        # self.current_job_icon_label.grid(row=0, column=0, rowspan=2, padx=5, pady=5, sticky="w")
        # self.current_job_label = ctk.CTkLabel(self.current_job_frame, text="Current job", font=self.custom_font)
        # self.current_job_label.grid(row=0, column=1, padx=5, pady=(5, 0), sticky="w")
        # self.current_job_value = ctk.CTkLabel(self.current_job_frame, text="—", font=self.custom_font)
        # self.current_job_value.grid(row=1, column=1, padx=5, pady=(0, 5), sticky="w")


        #### UPDATE PROFILE LOOP
        thread = threading.Thread(target=self.update_user_profile, daemon=True)
        thread.start()
        
    
    def update_user_profile(self):
        """
        Background loop to fetch user information from the server every 30s.
        Updates the UI directly via self.after().
        """
        payload = {"id": self.user["id"]}

        while True:
            try:
                data = asyncio.run(api.get("/tracker/user", payload))
                if data.get("error"):
                    tools.write_log(f"Error fetching user info: {data['message']}", type="error")
                else:
                    pick = data["user"]

                    if not self.previous_pick or pick != self.previous_pick:
                        self.previous_pick = pick

                        # --- UI update wrapped in self.after ---
                        def _update():
                            tools.write_log("Loading profile...")

                            # pfp
                            if pick["avatarURL"]:
                                response = requests.get(pick["avatarURL"])
                                image_data = BytesIO(response.content)
                                image = Image.open(image_data)
                                ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=(100, 100))
                                self.pfp_label.configure(image=ctk_image)
                            # self.pfp_label.image = ctk_image  # prevent garbage collection

                            # pfp infos
                            self.pfp_infos.configure(text=f"{self.user['username']} #{self.user['id']}")

                            # user role
                            self.user_role_label.configure(text="Role:")
                            if pick["isStaff"]:
                                self.user_role_value.configure(text="Staff", text_color="#871D1D")
                            else:
                                self.user_role_value.configure(text="Driver", text_color="#0D4B57")

                            # user discordID
                            self.user_discordID_label.configure(text="Discord ID:")
                            self.user_discordID_value.configure(text=str(pick["discordID"]))

                            # statistics
                            self.deliveries_value.configure(text=str(pick["deliveriesTotal"]))
                            self.wallet_value.configure(text=f"${pick['wallet']}")
                            self.rank_value.configure(text=str(pick["rank"]))
                            # self.playtime_value.configure(text=f"{pick['totalPlaytime']} h")

                            tools.write_log("Profile loaded from API request")

                        self.after(0, _update)  # 🔥 trigger update inside the loop

            except Exception as e:
                tools.write_log(f"Error fetching user info: {str(e)}", type="error")

            time.sleep(30)



    def get_user_contracts(self, user_id):
        """
        Fetch user contracts from the server.
        """
        payload = {"id": user_id}

        try:
            data = asyncio.run(api.get("/tracker/user/contracts", payload))
            if data["error"]:
                tools.write_log(f"Error fetching user contracts: {data['message']}", type="error")
                return None
            else:
                return data
        
        except Exception as e:
            print(f"Error fetching user contracts: {e}")
            return None
        

class HomeRight(ctk.CTkFrame):
    def __init__(self, master=None, *args, **kwargs):
        super().__init__(master, fg_color="transparent", *args, **kwargs)
        self.custom_font = ctk.CTkFont(family="Poppins", size=16, weight="bold")
        self.jobs = []
        self.previous_jobs = None
        self.user = tools.load_json(tools.resource_path("data/user.json"))
        self.stop_event = threading.Event()
        self.stop_event.set()
        self.setup_ui()
    

    def show_error(self, message: str):
        messagebox.showerror("Error", message)
        tools.write_log(message, type="error")


    def game_notif(self, message: str, delay=5000):
        self.after(500, self.show_game_notification, message, delay)


    def show_game_notification(self, message: str, delay: int):
        # tools.walkie_sound()
        notif = ctk.CTkToplevel()
        notif.overrideredirect(True)
        notif.attributes("-topmost", True)

        width, height = 250, 80
        notif.geometry(f"{width}x{height}+10+10")

        ctk.CTkLabel(notif, text="myKaelys Client", font=ctk.CTkFont(size=12)).pack(pady=2)
        ctk.CTkLabel(notif, text=message, font=ctk.CTkFont(size=15, weight="bold")).pack(pady=2)

        notif.after(delay, notif.destroy)


    def run_sdk_loop(self):
        global lastData
        deliveries = Deliveries()

        while not self.stop_event.is_set():
            try:
                self.telemetry_data = truck_telemetry.get_data()

                if lastData == str(self.telemetry_data):
                    tools.write_log("No data change detected.")
                else:
                    lastData = str(self.telemetry_data)
                    # ON SAIT QUE LES DONNES SONT MISES A JOUR
                    if self.telemetry_data["game"] == 1:
                        self.game_status.configure(text="Euro Truck Simulator 2", text_color="green")
                        self.game_img.configure(
                            image=ctk.CTkImage(
                                light_image=Image.open(tools.resource_path("src/static/icon/ETS2.png")),
                                dark_image=Image.open(tools.resource_path("src/static/icon/ETS2.png")),
                                size=(100, 100)
                            )
                        )
                    elif self.telemetry_data["game"] == 2:
                        self.game_status.configure(text="American Truck Simulator", text_color="green")
                        self.game_img.configure(
                            image=ctk.CTkImage(
                                light_image=Image.open(tools.resource_path("src/static/icon/ATS.png")),
                                dark_image=Image.open(tools.resource_path("src/static/icon/ATS.png")),
                                size=(100, 100)
                            )
                        )
                    self.truck_value.configure(text=f"{self.telemetry_data['truckBrand']} {self.telemetry_data['truckName']}")
                    if not self.telemetry_data['cargo'] == "":
                        self.cargo_value.configure(text=f"{self.telemetry_data['cargo']} ({int(self.telemetry_data['cargoMass'])} kg)")
                    else:
                        self.cargo_value.configure(text="—")
                    if not self.telemetry_data['citySrc'] == "" and not self.telemetry_data['cityDst'] == "":
                        self.route_value.configure(text=f"{self.telemetry_data['citySrc']} → {self.telemetry_data['cityDst']}")
                    else:
                        self.route_value.configure(text="—")

                    event_type = deliveries.handle(self.telemetry_data)

                    if event_type == "job_started":
                        self.game_notif("Delivery in progress. Drive safe!", delay=5000)
                    elif event_type == "job_delivered":
                        self.game_notif("Delivery completed. Good job!", delay=5000)
                    elif event_type == "job_cancelled":
                        self.game_notif("Delivery cancelled. Another \ncompany got the freight away.", delay=5000)
                    
            except Exception:
                stopping_txt = "Tracking stopped due to the game being closed."
                tools.write_log(stopping_txt)
                asyncio.run(self.stop_tracking_thread())
                break

            time.sleep(3)
    

    def start_tracking_thread(self):
        threading.Thread(target=self._start_tracking, daemon=True).start()


    def _start_tracking(self):
        if hasattr(self, "sdk_thread") and self.sdk_thread.is_alive():
            tools.write_log("Tracking thread already running, skipping start.")
            return

        try:
            global tracking_disabled
            tracking_disabled = False
            truck_telemetry.init()
            self.stop_event.clear()
            self.sdk_thread = threading.Thread(target=self.run_sdk_loop, daemon=True)
            self.sdk_thread.start()
            self.tracking_button.configure(
                text="Stop Tracking",
                command=lambda: [asyncio.run(self.stop_tracking_thread())],
                fg_color="#25374a", 
                hover_color="#213140"
            )

            # UPDATE LIVE DRIVERS
            game = ""
            user_data = tools.load_json(tools.resource_path("data/user.json"))
            userID = user_data["id"]
            if self.telemetry_data["game"] == 1:
                game = "ETS2"
            elif self.telemetry_data["game"] == 2:
                game = "ATS"

            payload = {"id": userID, "game": game}
            asyncio.run(api.post("/tracker/user/live/add", payload))

        except FileNotFoundError:
            self.show_error("Unable to load the SDK. Either the game is not running or the SDK plugin is not installed.")
            tools.write_log("SDK init failed: FileNotFoundError", type="error")


    async def stop_tracking_thread(self):
        threading.Thread(target=self._stop_tracking, daemon=True).start()


    def _stop_tracking(self):
        global tracking_disabled
        tracking_disabled = True
        self.stop_event.set()
        truck_telemetry.deinit()
        self.tracking_button.configure(
            text="Start Tracking",
            command=lambda: [asyncio.run(self.start_tracking_thread())],
            fg_color="#12a4b7",
            hover_color="#0e8ea0"
        )
        self.game_status.configure(text="No game running.", text_color="grey")
        self.game_img.configure(
                            image=ctk.CTkImage(
                                light_image=Image.open(tools.resource_path("src/static/icon/NoGameRunning.png")),
                                dark_image=Image.open(tools.resource_path("src/static/icon/NoGameRunning.png")),
                                size=(100, 100)
                            ))
        self.truck_value.configure(text="—")
        self.cargo_value.configure(text="—")
        self.route_value.configure(text="—")
        tools.write_log("Tracking stopped cleanly")

        # UPDATE LIVE DRIVERS
        user_data = tools.load_json(tools.resource_path("data/user.json"))
        userID = user_data["id"]

        payload = {"id": userID}
        asyncio.run(api.delete("/tracker/user/live/remove", payload))
        # result = req.json()
        # if result["error"]:
        #     write_log(result["message"], type="error")


    def setup_ui(self):
        # GAME DISPLAY
        game_idle_icon_src = Image.open(tools.resource_path("src/static/icon/NoGameRunning.png"))
        game_idle_icon = ctk.CTkImage(light_image=game_idle_icon_src, dark_image=game_idle_icon_src, size=(100, 100))
        self.game_img = ctk.CTkLabel(self, text="", image=game_idle_icon)
        self.game_img.grid(row=0, column=0, columnspan=2, pady=5)

        self.game_status = ctk.CTkLabel(self, text="No game running.", text_color="grey", font=self.custom_font)
        self.game_status.grid(row=1, column=0, columnspan=2, pady=2)

        # 1ST SEPARATOR
        self.first_separator = ctk.CTkFrame(self, height=2, fg_color="#555555")
        self.first_separator.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 20))

        ## Current Ride
        self.current_ride_label = ctk.CTkLabel(self, text="Current Ride", font=self.custom_font)
        self.current_ride_label.grid(row=3, column=0, columnspan=2, pady=(0, 2))

        # Truck
        self.truck_label = ctk.CTkLabel(self, text="Truck:", font=self.custom_font)
        self.truck_label.grid(row=4, column=0, sticky="w", pady=5, padx=(24, 5))
        self.truck_value = ctk.CTkLabel(self, text="—", font=self.custom_font)
        self.truck_value.grid(row=4, column=1, sticky="w", pady=5, padx=(5, 24))

        # Cargo
        self.cargo_label = ctk.CTkLabel(self, text="Cargo:", font=self.custom_font)
        self.cargo_label.grid(row=5, column=0, sticky="w", pady=5, padx=(24, 5))
        self.cargo_value = ctk.CTkLabel(self, text="—", font=self.custom_font)
        self.cargo_value.grid(row=5, column=1, sticky="w", pady=5, padx=(5, 24))

        # Route
        self.route_label = ctk.CTkLabel(self, text="Route:", font=self.custom_font)
        self.route_label.grid(row=6, column=0, sticky="w", pady=5, padx=(24, 5))
        self.route_value = ctk.CTkLabel(self, text="—", font=self.custom_font)
        self.route_value.grid(row=6, column=1, sticky="w", pady=5, padx=(5, 24))

        # 2ND SEPARATOR
        self.second_separator = ctk.CTkFrame(self, height=2, fg_color="#555555")
        self.second_separator.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(10, 20))

        # Tracking button
        self.tracking_button = ctk.CTkButton(
            self,
            text="Start Tracking",
            height=30,
            width=200,
            fg_color="#12a4b7",
            hover_color="#0e8ea0",
            command=lambda: [asyncio.run(self.start_tracking_thread())],
            font=self.custom_font
        )
        self.tracking_button.grid(row=8, column=0, columnspan=2, pady=(5, 10), padx=24, sticky="ew")



class SettingsPage(ctk.CTkFrame):
    """
    Settings page for the application.
    """
    def __init__(self, master=None, *args, **kwargs):
        super().__init__(master, fg_color="transparent", *args, **kwargs)
        self.custom_font = ctk.CTkFont(family="Poppins", size=13, weight="bold")
        self.setup_ui()


    def setup_ui(self):
        # === FRAME PRINCIPAL ===
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(pady=10)

        # === COLUMNS CONFIGS ===
        # Column 1
        self.column_1 = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.column_1.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")

        # Column 2
        self.column_2 = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.column_2.grid(row=0, column=1, padx=20, pady=10, sticky="nsew")

        # Column 3
        self.column_3 = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.column_3.grid(row=0, column=2, padx=20, pady=10, sticky="nsew")

        # Configure grid weights for responsiveness
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(2, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # === COLUMNS CONTENTS ===
        ## Column 1
        # SAVE SETTINGS
        self.save_settings_button = ctk.CTkButton(self.column_1, text="Save", command=lambda: [self.send_settings()],
                                         fg_color="#12b791", hover_color="#0d8f70",
                                         font=self.custom_font)
        self.save_settings_button.pack(pady=5, padx=10)

        # CB HOTKEYS
        self.show_hotkeys_button = ctk.CTkButton(self.column_1, text="CB Hotkeys", command=lambda: [self.hotkeys_window()],
                                         fg_color="#12a4b7", hover_color="#0e8ea0",
                                         font=self.custom_font)
        self.show_hotkeys_button.pack(pady=5, padx=10)

        # LOGOUT (soon)
        self.logout_btn = ctk.CTkButton(self.column_1, text="Logout",
                                         fg_color="#25374a", hover_color="#213140", 
                                         font=self.custom_font, command=self.logout)
        self.logout_btn.pack(fill="x", pady=5, padx=10)

        ## Switches
        # RPC -> CAUTION: self.rpc_var is only used to determine initial RPC switch value
        memory = tools.load_json(tools.resource_path("data/memory.json"))
        settings = memory["settings"]
        self.rpc_var = tk.IntVar(value=1 if settings["RPC"] else 0)
        self.discord_rpc_switch = ctk.CTkSwitch(self.column_2, text="Discord RPC", font=self.custom_font, onvalue=1, offvalue=0, command=lambda: [tools.write_log(f"[ SETTINGS PRESET] Discord RPC set to {tools.get_switch_value(self.discord_rpc_switch)}", type="info")], variable=self.rpc_var)
        self.discord_rpc_switch.pack(pady=5, padx=10)

        # AUTO-TRACKING -> CAUTION: self.tracking_var is only used to determine initial Tracking switch value
        self.tracking_var = tk.IntVar(value=1 if settings["Auto-Tracking"] else 0)
        self.auto_tracking_switch = ctk.CTkSwitch(self.column_3, text="Auto-Tracking (restart needed)", font=self.custom_font, onvalue=1, offvalue=0, command=lambda: [tools.write_log(f"[ SETTINGS PRESET] Auto-Tracking set to {tools.get_switch_value(self.auto_tracking_switch)}", type="info")], variable=self.tracking_var, state="disabled")
        self.auto_tracking_switch.pack(pady=5, padx=10)

        ### WARNING: This code won't be used for now, keep it commented out :3
        # self.dm_notif_switch = ctk.CTkSwitch(self.switches_settings, text="DM Notifications", onvalue=1, offvalue=0, command=lambda: [write_log(f"DM Notifications set to {get_switch_value(self.dm_notif_switch)}", type="info"), self.dm_notif_switch.set(get_switch_value(self.dm_notif_switch))])
        # self.dm_notif_switch.pack(pady=5, padx=10)
        #Set switch values
        # load_setting("RPC", self.discord_rpc_switch)
        # load_setting("DM", self.dm_notif_switch)

        # Column 2
        # self.export_jobs_frame = ctk.CTkFrame(self.column_2, fg_color="#2B2B2B")
        # self.export_jobs_frame.pack(pady=5, padx=10)
        # self.export_jobs_label = ctk.CTkLabel(self.export_jobs_frame, text="", font=('Poppins', 10, 'italic'))
        # self.export_jobs_label.pack(pady=5, padx=10)
        # self.export_jobs_button = ctk.CTkButton(self.export_jobs_frame, text="Export jobs to CSV", font=("Poppins", 12), command=lambda: [asyncio.run(self.export_to_csv())])
        # self.export_jobs_button.pack(pady=5, padx=10)


    def send_settings(self):
        try:
            self.save_settings_button.configure(text="Processing...")
            self.save_settings_button.update()
            s = {
                "RPC": tools.get_switch_value(self.discord_rpc_switch),
                "Auto-Tracking": tools.get_switch_value(self.auto_tracking_switch)
            }

            memory = tools.load_json(tools.resource_path("data/memory.json"))
            current_settings = memory["settings"]

            if s != current_settings:
                success = asyncio.run(settings.save(s))
                if not success:
                    self.show_error("Couldn't save new settings.")
                else:
                    self.show_success("Settings saved!")
                self.save_settings_button.configure(text="Save Settings")
                self.save_settings_button.update()

            else:
                self.show_error("Settings already saved.")
                self.save_settings_button.configure(text="Save Settings")
                self.save_settings_button.update()
            
        except Exception as e:
            tools.write_log(f"Couldn't save settings: {e}", type="error")


    def show_error(self, message: str):
        messagebox.showerror("Error", message)
        tools.write_log(message, type="error")

    
    def show_success(self, message: str):
        success_window = ctk.CTkToplevel()
        success_window.geometry("300x150")
        success_window.title("Success")
        success_window.resizable(False, False)

        ctk.CTkLabel(success_window, text=message, wraplength=250).pack(pady=5)
        ctk.CTkButton(success_window, text="Close", command=success_window.destroy).pack(pady=10)

        success_window.grab_set()


    async def export_to_csv(self):
        file_path = filedialog.asksaveasfilename(
            initialdir="%USERPROFILE%\\Documents",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if file_path:
            with open(file_path, "w") as file:
                            
                success, headers, content = await api.get_job_export()

                if success:
                    if headers["X-Error"] == "True":
                        tools.write_log(headers["X-Error-Message"], type="error")
                        self.show_error("Couldn't export jobs to CSV.")
                    else:
                        with open(f'{file_path}', 'wb') as f:
                            f.write(content)

                        message = f"Jobs exported successfully \nto {file_path}"
                        tools.write_log(message)
                        self.show_success(message)

                else:
                    message = "Interaction with the API has failed"
                    tools.write_log(message)
                    self.show_error(message)


    def hotkeys_window(self):
        infos = tools.load_json(tools.resource_path("properties/infos.json"))

        hotkeys_window = ctk.CTkToplevel()
        hotkeys_window.geometry("400x200")
        hotkeys_window.title("Hotkeys")
        hotkeys_window.resizable(False, False)

        self.hotkeys_frame = ctk.CTkScrollableFrame(hotkeys_window, fg_color="#1B1B1B", orientation='vertical')
        self.hotkeys_frame.pack(pady=5, padx=10, fill="x")

        self.hotkeys_heading = ctk.CTkLabel(self.hotkeys_frame, text="📻 Hotkeys for CB", font=("Poppins", 20, "bold"))
        self.hotkeys_heading.pack(pady=5, padx=10)

        self.hotkeys_label = ctk.CTkLabel(self.hotkeys_frame, text="\n".join(f"> {hotkey}" for hotkey in infos['hotkeys']), font=("Poppins", 16), wraplength=550, justify="left", anchor="w")
        self.hotkeys_label.pack(pady=5, padx=10, fill="x", expand=True)
        self.close_button = ctk.CTkButton(self.hotkeys_frame, text="Close", command=hotkeys_window.destroy).pack(pady=10)

        hotkeys_window.grab_set()
    

    def on_close(self):
        try:
            tools.write_log("Application closed cleanly")
        except Exception as e:
            tools.write_log(f"Application closed with error: {e}", type="error")
        sys.exit()


    def logout(self):
        memory = tools.load_json(tools.resource_path("data/memory.json"))
        memory["local"]["Auto-Login"] = False
        tools.save_json(memory, tools.resource_path("data/memory.json"))
        self.on_close()


            

class InfosPage(ctk.CTkFrame):
    """
    Information page for the application.
    """
    def __init__(self, master=None, *args, **kwargs):
        super().__init__(master, fg_color="transparent", *args, **kwargs)
        self.custom_font = ctk.CTkFont(family="Poppins", size=16, weight="bold")
        self.setup_ui()


    def setup_ui(self):
        # === MAIN FRAME ===
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(pady=10, fill="both", expand=True)

        # Get infos dictionary
        infos = tools.load_json(tools.resource_path("properties/infos.json"))
        
        # Version heading
        self.infos_heading_label = ctk.CTkLabel(self.main_frame, text=infos["version"], font=self.custom_font)
        self.infos_heading_label.pack(pady=(0, 10))

        # === HOW TO INSTALL SECTION ===
        self.how_to_install_frame = ctk.CTkFrame(self.main_frame, fg_color="#1C2B3A")
        self.how_to_install_frame.pack(pady=5, padx=10, fill="x")

        self.how_to_install_heading = ctk.CTkLabel(self.how_to_install_frame, text="How to install", font=self.custom_font)
        self.how_to_install_heading.pack(pady=5, padx=10)

        self.how_to_install_text = ctk.CTkLabel(self.how_to_install_frame, text=infos["how_to_install"], font=self.custom_font, wraplength=550, justify="left", anchor="w")
        self.how_to_install_text.pack(pady=5, padx=10, fill="x", expand=True)

        # === HOW TO USE SECTION ===
        # self.how_to_use_frame = ctk.CTkFrame(self.main_frame, fg_color="#1B1B1B")
        # self.how_to_use_frame.pack(pady=5, padx=10, fill="x")

        # self.how_to_use_heading = ctk.CTkLabel(self.how_to_use_frame, text="How to use", font=("Poppins", 20, "bold"))
        # self.how_to_use_heading.pack(pady=5, padx=10)

        # self.how_to_use_text = ctk.CTkLabel(self.how_to_use_frame, text=infos["how_to_use"], font=("Poppins", 16), wraplength=550,  justify="left", anchor="w")
        # self.how_to_use_text.pack(pady=5, padx=10, fill="x", expand=True)

        # === CHANGELOG SECTION ===
        self.changelog_frame = ctk.CTkFrame(self.main_frame, fg_color="#1C2B3A")
        self.changelog_frame.pack(pady=5, padx=10, fill="x")

        self.changelog_heading = ctk.CTkLabel(self.changelog_frame, text="Changelog", font=self.custom_font)
        self.changelog_heading.pack(pady=5, padx=10)

        changelog_text = ""
        if isinstance(infos["changelog"], list):
            # Join list items with newlines if changelog is a list
            changelog_text = "\n".join(infos["changelog"])
        else:
            # Use as is if it's already a string
            changelog_text = infos["changelog"]
            
        self.changelog_text = ctk.CTkLabel(self.changelog_frame, text=changelog_text,font=self.custom_font, wraplength=600, justify="left", anchor="w")
        self.changelog_text.pack(pady=5, padx=10, fill="x", expand=True)

        # # === CREDIT ===
        # self.credits_frame = ctk.CTkFrame(self.main_frame, fg_color="#1C2B3A")
        # self.credits_frame.pack(pady=5, padx=10, fill="x")

        # self.credits_heading = ctk.CTkLabel(self.credits_frame, text="Credits", font=self.custom_font)
        # self.credits_heading.pack(pady=5, padx=10)

        # self.credits_text = ctk.CTkLabel(self.credits_frame, text=infos["credits"], font=self.custom_font, wraplength=600, justify="left", anchor="w")
        # self.credits_text.pack(pady=(0, 5), padx=10, fill="both", expand=True)

    # def load_infos(self):
    #     """
    #     Load the changelog from local.
    #     """
    #     with open(tools.resource_path("properties/infos.json"), 'r') as f:
    #         infos = json.load(f)
    #     return infos



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