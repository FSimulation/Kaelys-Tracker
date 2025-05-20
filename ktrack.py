import customtkinter as ctk, requests, threading, time, sys
from truck_telemetry import truck_telemetry
from PIL import Image, ImageTk
from src.components.tracking.deliveries import Deliveries
from src.components.pretools import save_json, load_json, resource_path, write_log, save_txt, load_settings
import src.components.operations.ui as ui
import src.components.operations.discord_integ as dinteg
from src.components.cfg import API_URL
import keyboard
from cryptography.fernet import Fernet


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
        self.title("KaelysTrack")
        self.geometry("600x375")
        #self.iconbitmap(resource_path("src/static/ktrack.ico")) changed to self.iconphoto for better compatibility (Ln 46 and 164)
        icon_path = resource_path("src/static/ktrack.png")
        icon_image = Image.open(icon_path)
        icon_photo = ImageTk.PhotoImage(icon_image)
        self.iconphoto(True, icon_photo)
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme(resource_path("src/theme.json"))
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", lambda: None)

        # if self.auto_login():
        #     return

        self.close_button = ctk.CTkButton(self, text="✖ Leave KaelysTrack", width=30, command=self.on_close, fg_color="darkred", hover_color="red")
        self.close_button.place(relx=1.0, x=-10, y=10, anchor="ne")
        self.close_button_label = ctk.CTkLabel(self, text="Standard X button has been disabled.", text_color="grey", font=("Poppins", 7, "bold"))
        self.close_button_label.place(relx=1.0, x=-10, y=40, anchor="ne")

        self.setup_ui()


    def auto_login(self):
        try:
            user_data = load_json(resource_path("data/user.json"))
            if "encrypted_password" in user_data:
                # Decrypt the password
                decrypted_password = cipher.decrypt(user_data["encrypted_password"].encode()).decode()

                # Try auto-login
                response = requests.get(f"{API_URL}/tracker/login", json={
                    "username": user_data["username"],
                    "password": decrypted_password
                })
                if response.status_code == 200:
                    data = response.json()
                    if not data["error"]:
                        write_log("Auto-login successful.", type="info")
                        self.destroy()
                        self.main_window = MainWindow()
                        self.main_window.mainloop()
                        return True
        except Exception as e:
            write_log(f"Auto-login failed: {e}", type="error")
        return False         
    

    def on_close(self):
        try:
            write_log("Application closed cleanly")
            self.destroy()
        except Exception as e:
            write_log(f"Application closed with error: {e}", type="error")
        sys.exit()


    def setup_ui(self):
        image_path = resource_path("src/static/LoginBanner.png")
        pil_image = Image.open(image_path)
        image = ctk.CTkImage(size=(250, 140), light_image=pil_image)
        image_label = ctk.CTkLabel(self, image=image, text="")
        image_label.pack(pady=10)

        # API CHECK
        response = requests.get(f"{API_URL}/")
        if response.status_code == 200:
            data = response.json()
            self.api_status = data["state"]
        else:
            self.api_status = "OFFLINE"

        self.api_check_label = ctk.CTkLabel(self, text="API check", font=("Poppins", 12))
        self.api_check_label.pack(pady=0)
        if self.api_status == "ONLINE":
            self.api_state_label = ctk.CTkLabel(self, text="ONLINE", font=("Poppins", 12), text_color="green")
        elif self.api_status == "DISABLED":
            self.api_state_label = ctk.CTkLabel(self, text="MAINTENANCE", font=("Poppins", 12), text_color="yellow")
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
            response = requests.get(f"{API_URL}/tracker/login", json=creds)
            if response.status_code == 200:
                data = response.json()

                if data["error"]:
                    write_log(data["message"], type="error")
                    error_label = ctk.CTkLabel(self, text=data["message"], text_color="red")
                    error_label.pack(pady=5)
                    self.login_button.configure(text="Go!")
                    self.login_button.update()
                else:
                    write_log("Logged in successfully", type="info")
                    user_data = data["user"]

                    # Encrypt the password before saving
                    encrypted_password = cipher.encrypt(creds["password"].encode()).decode()
                    user_data["encrypted_password"] = encrypted_password

                    save_json(user_data, resource_path("data/user.json"))
                    self.destroy()
                    self.main_window = MainWindow()
                    self.main_window.mainloop()

            else:
                write_log("Error: Unable to connect to the server.", type="error")
                error_label = ctk.CTkLabel(self, text="Unable to connect to the server.", text_color="red")
                error_label.pack(pady=5)
                self.login_button.configure(text="Go!")
                self.login_button.update()
        
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
        write_log(message, type="error")



class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        # INIT SETTINGS
        success = load_settings()
        if not success:
            self.show_error("CRITICAL: Couldn't load settings. Aborting startup.")
            return

        # BUILD APP
        self.title("KaelysTrack")
        self.geometry("700x700")
        #self.iconbitmap(resource_path("src/static/ktrack.ico"))
        icon_path = resource_path("src/static/ktrack.png")
        icon_image = Image.open(icon_path)
        icon_photo = ImageTk.PhotoImage(icon_image)
        self.iconphoto(False, icon_photo)
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme(resource_path("src/theme.json"))
        self.user_data = load_json(resource_path("data/user.json"))
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", lambda: None)

        self.close_button = ctk.CTkButton(self, text="✖ Leave KaelysTrack", width=30, command=self.on_close, fg_color="darkred", hover_color="red")
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



    ### CLOSE APP
    def on_close(self):
        try:
            global tracking_disabled
            tracking_disabled = True
            self.stop_tracking()
            self.rpc.stop()
            time.sleep(0.5)
            write_log("Application closed cleanly")
            self.destroy()
        except Exception as e:
            write_log(f"Application closed with error: {e}", type="error")
        sys.exit()



    ### OPERATIONS
    def print_game_data(self):
        truck_telemetry.init()
        data = truck_telemetry.get_data()
        write_log(data)
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
        write_log(message, type="error")

    

    def game_notif(self, message: str, delay=5000):
        self.after(500, self.show_game_notification, message, delay)



    def show_game_notification(self, message: str, delay: int):
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
        deliveries = Deliveries(f"{API_URL}/tracker/deliveries")

        while not self.stop_event.is_set():
            try:
                self.telemetry_data = truck_telemetry.get_data()

                if lastData == str(self.telemetry_data):
                    write_log("No data change detected.")
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
                    
            except Exception as outer:
                write_log(f"[Thread crash] {outer}", type="error")
                error_txt = "Tracking stopped unexpectedly, probably because the game was closed."
                self.show_error(error_txt)
                write_log(error_txt, type="error")
                self.stop_tracking()
                break

            time.sleep(3)
    


    def start_tracking(self):
        if hasattr(self, "sdk_thread") and self.sdk_thread.is_alive():
            write_log("Tracking thread already running, skipping start.")
            return

        try:
            global tracking_disabled
            tracking_disabled = False
            truck_telemetry.init()
            self.stop_event.clear()
            self.sdk_thread = threading.Thread(target=self.run_sdk_loop, daemon=True)
            self.sdk_thread.start()
            self.tracking_button.configure(text="Stop tracking", command=self.stop_tracking, fg_color="darkred", hover_color="#670000")
            write_log("Tracking started")

            # UPDATE LIVE DRIVERS
            game = ""
            user_data = load_json(resource_path("data/user.json"))
            userID = user_data["id"]
            if self.telemetry_data["game"] == 1:
                game = "ETS2"
            elif self.telemetry_data["game"] == 2:
                game = "ATS"

            payload = {"id": userID, "game": game}
            req = requests.post(f"{API_URL}/tracker/user/live/add", json=payload)
            # result = req.json()
            # if result["error"]:
            #     write_log(result["message"], type="error")

        except FileNotFoundError:
            self.show_error("Unable to load the SDK. Either the game is not running or the SDK plugin is not installed.")
            write_log("SDK init failed: FileNotFoundError", type="error")



    def stop_tracking(self):
        global tracking_disabled
        tracking_disabled = True
        self.stop_event.set()
        truck_telemetry.deinit()
        self.tracking_button.configure(text="Start tracking", command=self.start_tracking, fg_color="#003F3F", hover_color="#003737")
        self.game_status.configure(text="No game running.", text_color="grey")
        self.game_status.update()
        write_log("Tracking stopped cleanly")

        # UPDATE LIVE DRIVERS
        user_data = load_json(resource_path("data/user.json"))
        userID = user_data["id"]

        payload = {"id": userID}
        req = requests.delete(f"{API_URL}/tracker/user/live/remove", json=payload)
        # result = req.json()
        # if result["error"]:
        #     write_log(result["message"], type="error")

    

    def update_live_drivers(self):
        while True:
            req = requests.get(f"{API_URL}/tracker/user/live")
            response = req.json()

            if response["error"]:
                write_log(response["message"], type="error")
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
                    self.online_ets2_players.configure(text=display_txt, font=("Poppins", 10, "bold"), text_color="white")
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
        self.tracking_button = ctk.CTkButton(self.frame_right_home, text="Start tracking", command=self.start_tracking, fg_color="#003F3F", hover_color="#003737")
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
    def handle_cb_event(self, type, message):
        global tracking_disabled
        if not tracking_disabled:
            response = requests.post(f"{API_URL}/tracker/cbevent", json={
                "type": type,
                "message": message,
                "discordID": self.user_data["discordID"]
                    })
            payload = response.json()

            if payload["error"]:
                write_log(f"Error while submitting event: {payload['message']}", type="error")
                self.game_notif("Couldn't submit event")
            else:
                write_log(f"Event Submitted: {type} - {message}")
                self.game_notif(f"Report submitted: \n{message}")
            


    def start_key_listener(self):
        def on_key(event):
            if event.event_type != 'down':
                return

            keys_down = keyboard._pressed_events
            now = time.strftime("%d-%m | %H:%M:%S")

            # Check if Ctrl key (29) is pressed
            if 29 not in keys_down:
                return

            # Ctrl + number keys 1-9
            if 2 in keys_down:  # Ctrl + 1
                self.handle_cb_event("Driving Session", f"[{now}] | {self.user_data['username']} started driving.")
            elif 3 in keys_down:  # Ctrl + 2
                self.handle_cb_event("Stop", f"[{now}] | {self.user_data['username']} stopped for fuel.")
            elif 4 in keys_down:  # Ctrl + 3
                self.handle_cb_event("Road Event", f"[{now}] | {self.user_data['username']} got into an accident.")
            elif 5 in keys_down:  # Ctrl + 4
                self.handle_cb_event("Road Event", f"[{now}] | {self.user_data['username']} is taking a detour.")
            elif 6 in keys_down:  # Ctrl + 5
                self.handle_cb_event("Job Event", f"[{now}] | {self.user_data['username']} started a job.")
            elif 7 in keys_down:  # Ctrl + 6
                self.handle_cb_event("Job Event", f"[{now}] | {self.user_data['username']} ended a job.")
            elif 8 in keys_down:  # Ctrl + 7
                self.handle_cb_event("Job Event", f"[{now}] | {self.user_data['username']} cancelled a job")
            elif 9 in keys_down:  # Ctrl + 8
                self.handle_cb_event("Driving Session", f"[{now}] | {self.user_data['username']} took an 8h break.")
            elif 10 in keys_down:  # Ctrl + 9
                self.handle_cb_event("Driving Session", f"[{now}] | {self.user_data['username']} stopped driving.")

        threading.Thread(target=lambda: keyboard.hook(on_key), daemon=True).start()

    



if __name__ == "__main__":
    save_txt("", resource_path("logs.txt"))
    save_txt("", resource_path("crash.txt"))
    app = LoginWindow()
    app.mainloop()
    keyboard.wait('41')

