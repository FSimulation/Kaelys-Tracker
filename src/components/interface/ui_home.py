import customtkinter as ctk, threading, time, asyncio, requests
from PIL import Image
from io import BytesIO
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

        # # ---- Rank ----
        # self.rank_frame = ctk.CTkFrame(self.statistics_frame, fg_color="transparent")
        # self.rank_frame.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        # self.rank_frame.grid_columnconfigure(1, weight=1)

        # self.rank_icon_label = ctk.CTkLabel(
        #     self.rank_frame, text="",
        #     image=ctk.CTkImage(light_image=Image.open(tools.resource_path("src/static/icon/rank.png")),
        #                        dark_image=Image.open(tools.resource_path("src/static/icon/rank.png")), size=(48, 48))
        # )
        # self.rank_icon_label.grid(row=0, column=0, rowspan=2, padx=5, pady=5, sticky="w")
        # self.rank_label = ctk.CTkLabel(self.rank_frame, text="Rank", font=self.custom_font)
        # self.rank_label.grid(row=0, column=1, padx=5, pady=(5, 0), sticky="w")
        # self.rank_value = ctk.CTkLabel(self.rank_frame, text="0", font=self.custom_font)
        # self.rank_value.grid(row=1, column=1, padx=5, pady=(0, 5), sticky="w")

        # # ---- Logbook Button ----
        # self.logbook_btn_frame = ctk.CTkFrame(self.statistics_frame, fg_color="transparent")
        # self.logbook_btn_frame.grid(row=2, column=1, padx=3, pady=5, sticky="ew")
        # self.logbook_btn_frame.grid_columnconfigure(1, weight=1)

        # self.logbook_button = ctk.CTkButton(self.logbook_btn_frame, text="Logbook", height=40,
        #                                fg_color="#12a4b7", hover_color="#0e8ea0",
        #                                font=self.custom_font, state="disabled")
        # self.logbook_button.grid(row=0, column=1, padx=5, pady=(5, 0), sticky="w")

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