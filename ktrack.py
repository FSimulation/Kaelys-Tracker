import customtkinter as ctk, threading, time, sys, asyncio, keyboard
from truck_telemetry import truck_telemetry
from PIL import Image, ImageTk
from src.components.tracking.deliveries import Deliveries
from src.components.pretools import GeneralTools, KaelysAPI, AppSettings
import src.components.operations.ui as ui
import src.components.operations.discord_integ as dinteg
from cryptography.fernet import Fernet


tools = GeneralTools()
api = KaelysAPI()
settings = AppSettings()


"save_json, load_json, resource_path, write_log, save_txt, load_settings"

lastData = {}

tracking_disabled = True

# Replace with your actual key
ENCRYPTION_KEY = b'GHq79RDXt6UoVUK44gutkHQOg1zKIH50UYTrKdGkCXI=' 
cipher = Fernet(ENCRYPTION_KEY)


def game_notif(message: str, delay=5000):
    notif = ctk.CTkToplevel()
    notif.overrideredirect(True)
    notif.attributes("-topmost", True)

    width, height = 250, 100
    notif.geometry(f"{width}x{height}+10+10")

    ctk.CTkLabel(notif, text="KaelysTrack", font=ctk.CTkFont(size=12)).pack(pady=2)
    ctk.CTkLabel(notif, text=message, font=ctk.CTkFont(size=15, weight="bold")).pack(pady=2)

    notif.after(delay, notif.destroy)



# CTK INTERFACE
class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        try:
            self.title("KaelysTrack")
            self.geometry("600x400")
            #self.iconbitmap(resource_path("src/static/ktrack.ico")) changed to self.iconphoto for better compatibility (Ln 46 and 164)
            icon_path = tools.resource_path("src/static/ktrack.png")
            icon_image = Image.open(icon_path)
            icon_photo = ImageTk.PhotoImage(icon_image)
            self.iconphoto(True, icon_photo)
            ctk.set_appearance_mode("Dark")
            ctk.set_default_color_theme(tools.resource_path("src/theme.json"))
            self.resizable(False, False)
            self.protocol("WM_DELETE_WINDOW", lambda: None)

            # if self.auto_login():
            #     return

            self.close_button = ctk.CTkButton(self, text="✖ Leave KaelysTrack", width=30, 
                                            command=self.on_close,
                                            fg_color="darkred", hover_color="red")
            self.close_button.place(relx=1.0, x=-10, y=10, anchor="ne")
            self.close_button_label = ctk.CTkLabel(self, text="Standard X button has been disabled.", text_color="grey", font=("Poppins", 7, "bold"))
            self.close_button_label.place(relx=1.0, x=-10, y=40, anchor="ne")

            self.setup_ui()
        
        except Exception as e:
            tools.write_log(f"Couldn't launch LoginWindow: {e}")


    # def auto_login(self):
    #     try:
    #         user_data = load_json(resource_path("data/user.json"))
    #         if "encrypted_password" in user_data:
    #             # Decrypt the password
    #             decrypted_password = cipher.decrypt(user_data["encrypted_password"].encode()).decode()

    #             # Try auto-login
    #             response = requests.get(f"{API_URL}/tracker/login", json={
    #                 "username": user_data["username"],
    #                 "password": decrypted_password
    #             })
    #             if response.status_code == 200:
    #                 data = response.json()
    #                 if not data["error"]:
    #                     write_log("Auto-login successful.", type="info")
    #                     self.destroy()
    #                     self.main_window = MainWindow()
    #                     self.main_window.mainloop()
    #                     return True
    #     except Exception as e:
    #         write_log(f"Auto-login failed: {e}", type="error")
    #     return False         
    

    def on_close(self):
        try:
            tools.write_log("Application closed cleanly")
            self.destroy()
        except Exception as e:
            tools.write_log(f"Application closed with error: {e}", type="error")
        sys.exit()


    def setup_ui(self):
        image_path = tools.resource_path("src/static/LoginBanner.png")
        pil_image = Image.open(image_path)
        image = ctk.CTkImage(size=(250, 140), light_image=pil_image)
        image_label = ctk.CTkLabel(self, image=image, text="")
        image_label.pack(pady=10)

        # API CHECK
        status = asyncio.run(api.get_status())
        if status == 200:
            self.api_status = "ONLINE"
        else:
            self.api_status = "OFFLINE"

        self.api_check_label = ctk.CTkLabel(self, text="API check", font=("Poppins", 12))
        self.api_check_label.pack(pady=0)

        if self.api_status == "ONLINE":
            self.api_state_label = ctk.CTkLabel(self, text="ONLINE", font=("Poppins", 12), text_color="green")
        # elif self.api_status == "DISABLED":
        #     self.api_state_label = ctk.CTkLabel(self, text="MAINTENANCE", font=("Poppins", 12), text_color="yellow")
        elif self.api_status == "OFFLINE":
            self.api_state_label = ctk.CTkLabel(self, text="OFFLINE", font=("Poppins", 12), text_color="red")

        self.api_state_label.pack(pady=0)

        self.username = ctk.CTkEntry(self, placeholder_text="Username")
        self.username.pack(pady=10)

        self.password = ctk.CTkEntry(self, placeholder_text="Password", show="*")
        self.password.pack(pady=10)

        self.login_button = ctk.CTkButton(self, text="Go!", command=self.login)
        self.login_button.pack(pady=10)


    def login(self):
        if not self.api_status == "OFFLINE":
            self.login_button.configure(text="Loading...")
            self.login_button.update()
            creds = {
                "username": self.username.get(),
                "password": self.password.get()
            }
            data = asyncio.run(api.get("/tracker/login", creds))
            if data["error"]:
                tools.write_log(data["message"], type="error")
                error_label = ctk.CTkLabel(self, text=data["message"], text_color="red")
                error_label.pack(pady=5)
                self.login_button.configure(text="Go!")
                self.login_button.update()
            else:
                tools.write_log("Logged in successfully", type="info")
                user_data = data["user"]

                ## Encrypt the password before saving (disabled for now)
                # encrypted_password = cipher.encrypt(creds["password"].encode()).decode()
                # user_data["encrypted_password"] = encrypted_password

                tools.save_json(user_data, tools.resource_path("data/user.json"))
                self.destroy()
                self.main_window = MainWindow()
                self.main_window.mainloop()
        
        else:
            self.show_error("The API is not available. Please try again later.")
    

    def show_error(self, message: str):
        error_window = ctk.CTkToplevel()
        error_window.geometry("300x150")
        error_window.title("Error")
        error_window.resizable(False, False)

        ctk.CTkLabel(error_window, text="An error occured.", text_color="red", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(20, 5))
        ctk.CTkLabel(error_window, text=message, wraplength=250).pack(pady=5)
        ctk.CTkButton(error_window, text="Close", command=error_window.destroy).pack(pady=10)

        error_window.grab_set()
        tools.write_log(message, type="error")





class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        # INIT SETTINGS
        try:
            success = asyncio.run(settings.load())
            if not success:
                self.show_error("CRITICAL: Couldn't load settings. Aborting startup.")
                sys.exit()
                return

            # BUILD APP
            self.title("KaelysTrack")
            self.geometry("700x700")
            self.iconbitmap(tools.resource_path("src/static/ktrack.ico"))
            # icon_path = tools.resource_path("src/static/ktrack.png") -> Disabled because not working
            # icon_image = Image.open(icon_path)
            # icon_photo = ImageTk.PhotoImage(icon_image)
            # self.iconphoto(False, icon_photo)
            ctk.set_appearance_mode("Dark")
            ctk.set_default_color_theme(tools.resource_path("src/theme.json"))
            self.user_data = tools.load_json(tools.resource_path("data/user.json"))
            self.resizable(False, False)
            self.protocol("WM_DELETE_WINDOW", lambda: None)

            self.close_button = ctk.CTkButton(self, text="✖ Leave KaelysTrack", width=30, 
                                            command=self.on_close, 
                                            fg_color="darkred", hover_color="red")
            self.close_button.place(relx=1.0, x=-10, y=10, anchor="ne")
            self.close_button_label = ctk.CTkLabel(self, text="Standard X button has been disabled.", text_color="grey", font=("Poppins", 7, "bold"))
            self.close_button_label.place(relx=1.0, x=-10, y=40, anchor="ne")

            self.stop_event = threading.Event()
            self.stop_event.set()

            # DISCORD RPC
            self.rpc = dinteg.RichPresence()
            self.rpc_thread = threading.Thread(target=self.rpc.run_loop, daemon=True)
            self.rpc_thread.start()

            self.setup_ui()

            self.start_key_listener()

        except Exception as e:
            tools.write_log(f"Couldn't launch MainWindow: {e}")


    ### CLOSE APP
    def on_close(self):
        try:
            global tracking_disabled
            if tracking_disabled == False:
                self.stop_tracking()
            self.rpc.stop()
            tools.write_log("Application closed cleanly")
        except Exception as e:
            tools.write_log(f"Application closed with error: {e}", type="error")
        sys.exit()



    ### OPERATIONS
    def print_game_data(self):
        truck_telemetry.init()
        data = truck_telemetry.get_data()
        tools.write_log(data)
        truck_telemetry.deinit()


    
    def show_error(self, message: str):
        error_window = ctk.CTkToplevel()
        error_window.geometry("300x150")
        error_window.title("Error")
        error_window.resizable(False, False)

        ctk.CTkLabel(error_window, text="An error occured.", text_color="red", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(20, 5))
        ctk.CTkLabel(error_window, text=message, wraplength=250).pack(pady=5)
        ctk.CTkButton(error_window, text="Close", command=error_window.destroy).pack(pady=10)

        error_window.grab_set()
        tools.write_log(message, type="error")

    

    def game_notif(self, message: str, delay=5000):
        self.after(500, self.show_game_notification, message, delay)



    def show_game_notification(self, message: str, delay: int):
        tools.walkie_sound()
        notif = ctk.CTkToplevel()
        notif.overrideredirect(True)
        notif.attributes("-topmost", True)

        width, height = 250, 80
        notif.geometry(f"{width}x{height}+10+10")

        ctk.CTkLabel(notif, text="KaelysTrack", font=ctk.CTkFont(size=12)).pack(pady=2)
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
                    elif self.telemetry_data["game"] == 2:
                        self.game_status.configure(text="American Truck Simulator", text_color="green")

                    event_type = deliveries.handle(self.telemetry_data)

                    if event_type == "job_started":
                        self.game_notif("Delivery in progress. Drive safe!", delay=5000)
                    elif event_type == "job_delivered":
                        self.game_notif("Delivery completed. Good job!", delay=5000)
                    elif event_type == "job_cancelled":
                        self.game_notif("Delivery cancelled. Another \ncompany got the freight away.", delay=5000)
                    
            except Exception:
                stopping_txt = "Tracking stopped due to the game being closed."
                self.show_error(stopping_txt)
                tools.write_log(stopping_txt)
                asyncio.run(self.stop_tracking_async())
                break

            time.sleep(3)
    

    async def start_tracking_async(self):
        threading.Thread(target=self._run_tracking_async, daemon=True).start()

    
    def _run_tracking_async(self):
        self.start_tracking()


    def start_tracking(self):
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
            self.tracking_button.configure(text="Stop tracking", command=lambda: [asyncio.run(self.stop_tracking_async())], fg_color="darkred", hover_color="#670000")
            tools.write_log("Tracking started")

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


    async def stop_tracking_async(self):
        threading.Thread(target=self._run_tracking_stop_async, daemon=True).start()

    
    def _run_tracking_stop_async(self):
        self.stop_tracking()


    def stop_tracking(self):
        global tracking_disabled
        tracking_disabled = True
        self.stop_event.set()
        truck_telemetry.deinit()
        self.tracking_button.configure(text="Start tracking", command=lambda: [asyncio.run(self.start_tracking_async())], fg_color="#00A000", hover_color="#008D00")
        self.game_status.configure(text="No game running.", text_color="grey")
        self.game_status.update()
        tools.write_log("Tracking stopped cleanly")

        # UPDATE LIVE DRIVERS
        user_data = tools.load_json(tools.resource_path("data/user.json"))
        userID = user_data["id"]

        payload = {"id": userID}
        asyncio.run(api.delete("/tracker/user/live/remove", payload))
        # result = req.json()
        # if result["error"]:
        #     write_log(result["message"], type="error")

    

    def update_live_drivers(self):
        while True:
            response = asyncio.run(api.get("/tracker/user/live"))

            if response["error"]:
                tools.write_log(response["message"], type="error")
            else:
                # ETS2
                ets2_players = response["ets2"]
                if ets2_players == []:
                    self.online_ets2_players.configure(text="Nobody is online.", font=("Poppins", 10, "italic"), text_color="grey")
                    self.online_ets2_players.update()
                else:
                    display_txt = ""
                    for player_name in ets2_players:
                        display_txt += f"{player_name}\n"
                    self.online_ets2_players.configure(text=display_txt, font=("Poppins", 10), text_color="white")
                    self.online_ets2_players.update()

                # ATS
                ats_players = response["ats"]
                if ats_players == []:
                    self.online_ats_players.configure(text="Nobody is online.", font=("Poppins", 10, "italic"), text_color="grey")
                    self.online_ats_players.update()
                else:
                    display_txt = ""
                    for player_name in ats_players:
                        display_txt += f"{player_name}\n"
                    self.online_ats_players.configure(text=display_txt, font=("Poppins", 10, "bold"), text_color="white")
                    self.online_ats_players.update()

                time.sleep(30)


    ### UI SETUP
    def setup_ui(self):
        # WELCOME & VERSION LABELS
        self.welcome_label = ctk.CTkLabel(self, text=f'Welcome, {self.user_data["username"]}!', font=("Poppins", 20, "italic"))
        self.welcome_label.pack(pady=10)
        self.version_label = ctk.CTkLabel(master=self, text="version 09-05-2025", text_color="gray")
        self.version_label.place(relx=0.01, rely=1.0, anchor="sw")  # En bas à gauche

        ## TAB VIEW
        self.tabview = ctk.CTkTabview(self, width=580, height=360)
        self.tabview.pack(padx=10, pady=10, fill="both", expand=True)

        self.tabview.add("Home")
        self.infos_warning_label = ctk.CTkLabel(self.tabview.tab("Home"), text="ⓘ  Informations displayed on this page are updated every 30 seconds.", text_color="grey", font=("Poppins", 10, "bold"))
        self.infos_warning_label.pack(pady=2)
        self.game_status = ctk.CTkLabel(self.tabview.tab("Home"), text="No game running.", text_color="grey", font=("Poppins", 13, "italic"))
        self.game_status.pack(pady=2, padx=2)

        self.tabview.add("Settings")

        self.tabview.add("Infos")

        ### HOME TAB
        ## LEFT FRAME
        self.frame_left_home = ctk.CTkFrame(
            self.tabview.tab("Home"),
            width=280,
            height=300,
            fg_color="#282828",  # gris foncé
            corner_radius=10
        )
        self.frame_left_home.pack(side="left", fill="both", expand=True, padx=(20, 10), pady=10)

        ## RIGHT FRAME
        self.frame_right_home = ctk.CTkFrame(
            self.tabview.tab("Home"),
            width=280,
            height=300,
            fg_color="#282828",
            corner_radius=10
        )
        self.frame_right_home.pack(side="right", fill="both", expand=True, padx=(10, 20), pady=10)

        ## LEFT FRAME CONTENTS
        self.user_profile = ui.UserProfile(self.frame_left_home)
        self.user_profile.pack(pady=20)

        ## RIGHT FRAME CONTENTS
        # Online Drivers
        self.online_ets2_label = ctk.CTkLabel(self.frame_right_home, text="ONLINE - ETS2", font=("Poppins", 10, "italic"), text_color="green")
        self.online_ets2_label.pack(pady=2)
        self.online_ets2_players = ctk.CTkLabel(self.frame_right_home, text="Nobody is online.", font=("Poppins", 10, "italic"), text_color="grey")
        self.online_ets2_players.pack(pady=2)
        self.online_ats_label = ctk.CTkLabel(self.frame_right_home, text="ONLINE - ATS", font=("Poppins", 10, "italic"), text_color="green")
        self.online_ats_label.pack(pady=2)
        self.online_ats_players = ctk.CTkLabel(self.frame_right_home, text="Nobody is online.", font=("Poppins", 10, "italic"), text_color="grey")
        self.online_ats_players.pack(pady=2)

        self.live_drivers_loop = threading.Thread(target=self.update_live_drivers, daemon=True)
        self.live_drivers_loop.start()

        # SEPARATION BAR
        self.horizontal_bar = ctk.CTkFrame(self.frame_right_home, height=3, width=150, corner_radius=0)
        self.horizontal_bar.pack(padx=5, pady=5)

        # Tracking Control
        self.tracking_button = ctk.CTkButton(self.frame_right_home, text="Start tracking", command=lambda: [asyncio.run(self.start_tracking_async())], fg_color="#00A000", hover_color="#008D00")
        self.tracking_button.pack(pady=10)


        # BOUTON DE TEST POUR L'AFFICHAGE DES DONNES DU SDK
        #self.test_button = ctk.CTkButton(self, text="Print game data", command=self.print_game_data)
        #self.test_button.pack(pady=10)


        ## SETTINGS TAB
        self.settings_page = ui.SettingsPage(self.tabview.tab("Settings"))
        self.settings_page.pack(pady=20)

        ## INFOS TAB
        self.infos_page = ui.InfosPage(self.tabview.tab("Infos"))
        self.infos_page.pack(pady=20)


    ## EXTRA FEATURES
    # CB EVENT
    def handle_cb_event(self, event_type, message):
        global tracking_disabled
        if tracking_disabled:
            payload = {
                "type": event_type,
                "message": message,
                "discordID": self.user_data["discordID"]
            }
            response = asyncio.run(api.post("/tracker/cbevent", payload))

            if response["error"]:
                tools.write_log(f"Error while submitting event: {response['message']}", type="error")
                self.game_notif("Couldn't submit event")
            else:
                tools.write_log(f"Event Submitted: {event_type} - {message}")
                self.game_notif(event_type)


    def start_key_listener(self):
        def on_key(event):
            if event.event_type != 'down':
                return

            now = time.strftime("%d-%m | %H:%M:%S")

            # Ctrl + number keys 1-6
            if keyboard.is_pressed('ctrl+1'):  # Ctrl + 1
                self.handle_cb_event("Driving Session", f"[{now}] | {self.user_data['username']} started driving.")

            elif keyboard.is_pressed('ctrl+2'):  # Ctrl + 2
                self.handle_cb_event("Fuel Stop", f"[{now}] | {self.user_data['username']} stopped for fuel.")

            elif keyboard.is_pressed('ctrl+3'):  # Ctrl + 3
                self.handle_cb_event("Accident", f"[{now}] | {self.user_data['username']} got into an accident.")

            elif keyboard.is_pressed('ctrl+4'):  # Ctrl + 4
                self.handle_cb_event("Detour", f"[{now}] | {self.user_data['username']} is taking a detour.")

            elif keyboard.is_pressed('ctrl+5'):  # Ctrl + 5
                self.handle_cb_event("Break", f"[{now}] | {self.user_data['username']} took an 8h break.")

            elif keyboard.is_pressed('ctrl+6'):  # Ctrl + 6
                self.handle_cb_event("End of Session", f"[{now}] | {self.user_data['username']} stopped driving.")

        threading.Thread(target=lambda: keyboard.hook(on_key), daemon=True).start()

    



if __name__ == "__main__":
    tools.save_txt("", tools.resource_path("logs.txt"))
    tools.save_txt("", tools.resource_path("crash.txt"))
    app = LoginWindow()
    app.mainloop()

