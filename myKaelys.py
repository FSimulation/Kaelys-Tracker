import customtkinter as ctk, threading, time, sys, asyncio, keyboard, aiohttp
from PIL import Image
from src.components.pretools import GeneralTools, KaelysAPI, AppSettings
import src.components.operations.ui as ui
import src.components.operations.discord_integ as dinteg
from cryptography.fernet import Fernet
from tkinter import messagebox


tools = GeneralTools()
api = KaelysAPI()
settings = AppSettings()


"save_json, load_json, resource_path, write_log, save_txt, load_settings"

lastData = {}

tracking_disabled = True


# Replace with your actual key
ENCRYPTION_KEY = b'GHq79RDXt6UoVUK44gutkHQOg1zKIH50UYTrKdGkCXI=' 
cipher = Fernet(ENCRYPTION_KEY)


def check_update():
    try:
        properties = tools.load_json(tools.resource_path("properties/infos.json"))
        current_version = properties["version"]

        latest_version = asyncio.run(api.get_tracker_latest())
        if latest_version != current_version:
            tools.write_log(f"Update available: {latest_version} (current: {current_version})", type="info")
            messagebox.showinfo("Update available", f"A new version of myKaelys Client is available: {latest_version}\nYou can run the installer to download this update.")
        else:
            tools.write_log("No update available", type="info")
    except Exception as e:
        tools.write_log(f"Couldn't check for updates: {e}", type="error")


def game_notif(message: str, delay=5000):
    notif = ctk.CTkToplevel()
    notif.overrideredirect(True)
    notif.attributes("-topmost", True)

    width, height = 250, 100
    notif.geometry(f"{width}x{height}+10+10")

    ctk.CTkLabel(notif, text="myKaelys Client", font=ctk.CTkFont(size=12)).pack(pady=2)
    ctk.CTkLabel(notif, text=message, font=ctk.CTkFont(size=15, weight="bold")).pack(pady=2)

    notif.after(delay, notif.destroy)



# CTK INTERFACE
class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        try:
            self.title("myKaelys Client - Login")
            # self.configure(fg_color="#2d4d66")
            self.geometry("600x650")
            self.iconbitmap(tools.resource_path("src/static/ktrack.ico")) #changed to self.iconphoto for better compatibility (Ln 46 and 164)
            # icon_path = tools.resource_path("src/static/ktrack.png")
            # icon_image = Image.open(icon_path)
            # icon_photo = ImageTk.PhotoImage(icon_image)
            # self.iconphoto(True, icon_photo)
            ctk.set_appearance_mode("Dark")
            # ctk.set_default_color_theme(tools.resource_path("src/theme.json"))
            self.resizable(False, False)
            self.protocol("WM_DELETE_WINDOW", self.on_close)
            self.custom_font = ctk.CTkFont(family="Poppins", size=14, weight="bold")

            self.setup_ui()
        except Exception as e:
            tools.write_log(f"Couldn't launch LoginWindow: {e}", type="error")
            # tools.write_log("Offline mode request awaiting...")
            # self.show_offline_request()       
    

    def on_close(self):
        try:
            tools.write_log("Application closed cleanly")
            self.destroy()
        except Exception as e:
            tools.write_log(f"Application closed with error: {e}", type="error")
        sys.exit()

    
    # def show_offline_request(self):
    #     self.request_window = ctk.CTkToplevel()
    #     self.request_window.geometry("300x150")
    #     self.request_window.title("Error")
    #     self.request_window.resizable(False, False)

    #     self.offline_title = ctk.CTkLabel(self.request_window, text="Couldn't connect with the API", text_color="red", font=("Poppins", 15, "italic")).pack(pady=5)
    #     self.offline_text = ctk.CTkLabel(self.request_window, text="Would you like to enable offline mode? \nYou won't need to login and your deliveries will be recorded locally.", wraplength=250).pack(pady=5)
        
    #     self.offline_confirm_button = ctk.CTkButton(self.request_window, text="Enable offline mode", command=lambda: [self.request_window.destroy(),
    #                                                                                                                   self.destroy(),
    #                                                                                                                   MainWindow(offline_mode=True).mainloop()
    #                                                                                                                   ]).pack(pady=10)


    def setup_ui(self):
        # ===== Window settings =====
        self.configure(fg_color="#0e1a27")  # deep navy

        # ===== Top banner / logo =====
        self.header = ctk.CTkFrame(self, fg_color="#0e1a27")
        self.header.pack(fill="x", pady=(26, 0))

        pil_logo = Image.open(tools.resource_path("src/static/LoginBanner.png"))
        logo_img = ctk.CTkImage(pil_logo, size=(175, 175))
        self.login_img = ctk.CTkLabel(self.header, image=logo_img, text="")
        self.login_img.pack()

        # ===== Center card =====
        self.card = ctk.CTkFrame(self, corner_radius=18, fg_color="#182636")   # glass-ish dark
        self.card.pack(pady=24, ipadx=16, ipady=16)

        # Username row
        user_row = ctk.CTkFrame(self.card, fg_color="#1d2d40", corner_radius=12)
        user_row.pack(fill="x", padx=24, pady=(24, 10))
        ctk.CTkLabel(user_row, text="👤", width=24, font=ctk.CTkFont(size=16)).pack(side="left", padx=12, pady=10)
        self.username = ctk.CTkEntry(user_row, placeholder_text="Username", border_width=0, font=self.custom_font, fg_color="#253446")
        self.username.pack(side="left", fill="x", expand=True, padx=(6, 10), pady=10)

        # Password row
        pass_row = ctk.CTkFrame(self.card, fg_color="#1d2d40", corner_radius=12)
        pass_row.pack(fill="x", padx=24, pady=10)
        ctk.CTkLabel(pass_row, text="🔒", width=24, font=ctk.CTkFont(size=16)).pack(side="left", padx=12, pady=10)
        self.password = ctk.CTkEntry(pass_row, placeholder_text="Password", show="•", border_width=0, font=self.custom_font, fg_color="#253446")
        self.password.pack(side="left", fill="x", expand=True, padx=(6, 10), pady=10)

        # Options row
        opts = ctk.CTkFrame(self.card, fg_color="#182636")
        opts.pack(fill="x", padx=24, pady=(4, 6))
        self.remember = ctk.CTkCheckBox(opts, text="Remember me (soon)", state="disabled", font=self.custom_font)
        self.remember.pack(side="left", pady=8)

        # Status indicators
        try:
            response_code = asyncio.run(api.get_status())
            if response_code == 200:
                self.api_status = "ONLINE"
                self.status_text = ctk.CTkLabel(opts, text="ONLINE", font=self.custom_font, text_color="#018801")
            else:
                self.api_status = "OFFLINE"
                self.status_text = ctk.CTkLabel(opts, text="OFFLINE", font=self.custom_font, text_color="#880000")
        except aiohttp.ClientConnectorDNSError:
            self.api_status = "NO INTERNET"
            self.status_text = ctk.CTkLabel(opts, text="NO INTERNET", font=self.custom_font, text_color="#880000")

        self.status_text.pack(side="right", padx=(0, 12))

        # Buttons
        self.login_button = ctk.CTkButton(self.card, text="Login", height=44,
                                       fg_color="#12a4b7", hover_color="#0e8ea0",
                                       command=self.login, font=self.custom_font)
        self.login_button.pack(fill="x", padx=24, pady=(10, 8))
        
        self.offline_btn = ctk.CTkButton(self.card, text="Enable offline mode (soon)",
                                         fg_color="#25374a", hover_color="#213140",
                                         state="disabled", font=self.custom_font)
        self.offline_btn.pack(fill="x", padx=24, pady=(0, 22))

        # error label
        self.error_label = ctk.CTkLabel(self.card, text="", text_color="red", font=self.custom_font)
        self.error_label.pack()
        # Footer
        infos = tools.load_json(tools.resource_path("properties/infos.json"))

        footer = ctk.CTkFrame(self, fg_color="#0e1a27")
        footer.pack(side="bottom", fill="x", pady=(0, 16))
        self.version_label = ctk.CTkLabel(footer, text=infos["version"], text_color="#8fa7be", font=self.custom_font)
        self.version_label.pack()



    def login(self):
        if self.api_status == "ONLINE":
            self.login_button.configure(text="Loading...")
            self.login_button.update()

            properties = tools.load_json(tools.resource_path("properties/infos.json"))
            version = properties["version"]

            creds = {
                "username": self.username.get(),
                "password": self.password.get(),
                "version": version
            }
            data = asyncio.run(api.get("/tracker/login", creds))
            if data["error"]:
                tools.write_log(data["message"], type="error")
                self.error_label.configure(text=data["message"])
                self.error_label.update()
                self.login_button.configure(text="Login")
                self.login_button.update()
            else:
                tools.write_log("Logged in successfully", type="info")
                user_data = data["user"]

                ## Encrypt the password before saving (disabled for now)
                # encrypted_password = cipher.encrypt(creds["password"].encode()).decode()
                # user_data["encrypted_password"] = encrypted_password

                tools.save_json(user_data, tools.resource_path("data/user.json"))
                self.destroy()
                MainWindow().mainloop()
        elif self.api_status == "NO INTERNET":
            self.show_error("Couldn't connect to the server. Please check your network connection. [NO INTERNET]")
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
    def __init__(self, offline_mode: bool = False):
        super().__init__()
        # INIT SETTINGS
        try:
            if not offline_mode:
                self.normal_mode()
            else:
                pass
                # self.offline_mode()

        except Exception as e:
            tools.write_log(f"Couldn't build MainWindow(): {e}\n {e.__class__}\n Cause: {e.__cause__}", type="error")


    def normal_mode(self):
        success = asyncio.run(settings.load())
        if not success:
            self.show_error("CRITICAL: Couldn't load settings. Aborting startup.")
            sys.exit()
            return

        # BUILD APP
        self.title("myKaelys Client")
        self.geometry("900x730")
        self.iconbitmap(tools.resource_path("src/static/ktrack.ico"))  # Changed to self.iconphoto for better compatibility (Ln 46 and 164)
        ctk.set_appearance_mode("Dark")
        self.configure(fg_color="#0f1a27")  # deep navy
        # ctk.set_default_color_theme(tools.resource_path("src/theme.json"))
        self.user_data = tools.load_json(tools.resource_path("data/user.json"))
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # DISCORD RPC
        self.rpc = dinteg.RichPresence()
        self.rpc_thread = threading.Thread(target=self.rpc.run_loop, daemon=True)
        self.rpc_thread.start()

        self.setup_ui()

        self.start_key_listener()


    # def offline_mode(self):
    #     self.title("KaelysTrack - Offline Mode")
    #     self.geometry("200x300")
    #     self.iconbitmap(tools.resource_path("src/static/ktrack.ico"))
    #     ctk.set_appearance_mode("Dark")
    #     # ctk.set_default_color_theme(tools.resource_path("src/theme.json"))
    #     self.user_data = tools.load_json(tools.resource_path("data/user.json"))
    #     self.resizable(False, False)
    #     self.protocol("WM_DELETE_WINDOW", self.on_close)

    #     # self.close_button = ctk.CTkButton(self, text="✖ Leave KaelysTrack", width=30, 
    #     #                                     command=self.on_close, 
    #     #                                     fg_color="darkred", hover_color="red")
    #     # self.close_button.place(relx=1.0, x=-10, y=10, anchor="ne")
    #     # self.close_button_label = ctk.CTkLabel(self, text="Standard X button has been disabled.", text_color="grey", font=("Poppins", 7, "bold"))
    #     # self.close_button_label.place(relx=1.0, x=-10, y=40, anchor="ne")

    #     # self.setup_ui()


    ### CLOSE APP
    def on_close(self):
        try:
            asyncio.run(self.home_right.stop_tracking_thread())
            self.rpc.stop()
            tools.write_log("Application closed cleanly")
        except Exception as e:
            tools.write_log(f"Application closed with error: {e}", type="error")
        sys.exit()



    ### UI SETUP
    def setup_ui(self):
        # ========== HEADER ==========
        # banner
        banner = Image.open(tools.resource_path("src/static/Header.png"))
        # banner = original.resize((1200, 180))  # largeur fenêtre, hauteur bannière
        banner_img = ctk.CTkImage(light_image=banner, dark_image=banner, size=(1000, 155))

        self.banner_label = ctk.CTkLabel(self, image=banner_img, text="")
        self.banner_label.pack(side="top", fill="x")

        # ======= TABVIEW =========
        tab_font = ctk.CTkFont(family="Poppins", size=14, weight="bold")
        self.tabview = ctk.CTkTabview(self, width=900, height=540, corner_radius=12, fg_color="#0f1a27", segmented_button_fg_color="#1c2b3a", segmented_button_unselected_color="#1c2b3a", segmented_button_unselected_hover_color="#243447")
        self.tabview.pack(padx=20, pady=20, fill="both", side="left", expand=True)

        # styliser le segmented button interne
        self.tabview._segmented_button.configure(font=tab_font)
        self.tabview._segmented_button.grid(sticky="e", padx=10)

        # TABS
        self.tabview.add("Home")
        self.tabview.add("Live Data")
        self.tabview.add("Settings")
        self.tabview.add("Informations")

        ### HOME TAB
        # self.game_status = ctk.CTkLabel(self.tabview.tab("Home"), text="No game running.", text_color="grey", font=("Poppins", 13, "bold"))
        # self.game_status.pack(pady=2, padx=2)

        ## LEFT FRAME
        self.frame_left_home = ctk.CTkFrame(
            self.tabview.tab("Home"),
            width=280,
            height=300,
            fg_color="#1C2B3A",
            corner_radius=10
        )
        self.frame_left_home.pack(side="left", fill="both", expand=True, padx=(20, 10), pady=10)

        ## RIGHT FRAME
        self.frame_right_home = ctk.CTkFrame(
            self.tabview.tab("Home"),
            width=280,
            height=300,
            fg_color="#1C2B3A",
            corner_radius=10
        )
        self.frame_right_home.pack(side="right", fill="both", expand=True, padx=(10, 20), pady=10)

        ## LEFT FRAME CONTENTS
        self.home_left = ui.HomeLeft(self.frame_left_home)
        self.home_left.pack(pady=20)

        ## RIGHT FRAME CONTENTS
        self.home_right = ui.HomeRight(self.frame_right_home)
        self.home_right.pack(pady=20)

        ### LIVE DATA TAB
        ## LEFT FRAME
        self.frame_left_live = ctk.CTkFrame(
            self.tabview.tab("Live Data"),
            width=360,
            height=300,
            fg_color="#1C2B3A",
            corner_radius=10
        )
        self.frame_left_live.pack(side="left", padx=5, pady=10)

        ## RIGHT FRAME
        self.frame_right_live = ctk.CTkFrame(
            self.tabview.tab("Live Data"),
            width=320,
            height=300,
            fg_color="#1C2B3A",
            corner_radius=10
        )
        self.frame_right_live.pack(side="right", padx=5, pady=10)

        ## LEFT FRAME CONTENTS
        self.live_drivers = ui.LiveDrivers(self.frame_left_live)
        self.live_drivers.pack(pady=20)

        ## RIGHT FRAME CONTENTS
        self.tmp_servers = ui.TMPServers(self.frame_right_live)
        self.tmp_servers.pack(pady=20)

        ## [UNUSED] RIGHT FRAME CONTENTS
        # Online Drivers
        # self.game_status_frame = ctk.CTkFrame(self.frame_right_home, fg_color="transparent")
        # self.game_status_frame.grid(row=0, column=0, padx=10, pady=10)
        # self.game_status_frame.columnconfigure(0, weight=1)
        # self.game_status_label = ctk.CTkLabel(self.game_status_frame, text="Game Status", font=("Poppins", 18), justify="left")
        # self.game_status_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")
        # self.online_ets2_label = ctk.CTkLabel(self.game_status_frame, text="ONLINE - ETS2", font=("Poppins", 10, "italic"), text_color="green")
        # self.online_ets2_label.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        # self.online_ets2_players = ctk.CTkLabel(self.game_status_frame, text="Nobody is online.", font=("Poppins", 10, "italic"), text_color="grey")
        # self.online_ets2_players.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        # self.online_ats_label = ctk.CTkLabel(self.game_status_frame, text="ONLINE - ATS", font=("Poppins", 10, "italic"), text_color="green")
        # self.online_ats_label.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        # self.online_ats_players = ctk.CTkLabel(self.game_status_frame, text="Nobody is online.", font=("Poppins", 10, "italic"), text_color="grey")
        # self.online_ats_players.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        # self.live_drivers_loop = threading.Thread(target=self.update_live_drivers, daemon=True)
        # self.live_drivers_loop.start()

        # SEPARATION BAR
        # self.horizontal_bar = ctk.CTkFrame(self.game_status_frame, height=3, width=150, corner_radius=0, fg_color="#4F4F4F")
        # self.horizontal_bar.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # Tracking Control
        # self.tracking_button = ctk.CTkButton(self.game_status_frame, text="Start tracking", command=lambda: [asyncio.run(self.start_tracking_async())], fg_color="#00A000", hover_color="#008D00")
        # self.tracking_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # self.settings_frame = ctk.CTkFrame(self.frame_right_home, fg_color="transparent")
        # self.settings_frame.grid(row=1, column=0, padx=10, pady=10)

        # self.settings_label = ctk.CTkLabel(self.settings_frame, text="Settings", font=("Poppins", 18), justify="left")
        # self.settings_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        # self.dark_mode_label = ctk.CTkLabel(self.settings_frame, text="Dark Mode", font=("Poppins", 12))
        # self.dark_mode_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        # self.dark_mode_switch = ctk.CTkSwitch(self.settings_frame, text="")
        # self.dark_mode_switch.grid(row=1, column=1, padx=10, pady=10, sticky="e")

        # self.font_dropdown = ctk.CTkOptionMenu(self.settings_frame, values=["Poppins", "Arial", "Courier New", "Comic Sans MS"])
        # self.font_dropdown.set("Poppins")
        # self.font_dropdown.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # self.hotkeys_button = ctk.CTkButton(self.settings_frame, text="Hotkeys", fg_color="#3D3D3D", hover_color="#2B2B2B")
        # self.hotkeys_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")


        # BOUTON DE TEST POUR L'AFFICHAGE DES DONNES DU SDK
        #self.test_button = ctk.CTkButton(self, text="Print game data", command=self.print_game_data)
        #self.test_button.pack(pady=10)


        ## SETTINGS TAB
        self.settings_page = ui.SettingsPage(self.tabview.tab("Settings"))
        self.settings_page.pack(pady=20)

        ## INFOS TAB
        self.infos_page = ui.InfosPage(self.tabview.tab("Informations"))
        self.infos_page.pack(pady=20)


    ## EXTRA FEATURES
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
    threading.Thread(target=check_update, daemon=True).start()
    app = LoginWindow()
    app.mainloop()

