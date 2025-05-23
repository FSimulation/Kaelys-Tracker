import customtkinter as ctk, threading, time, json, asyncio, tkinter as tk, requests
from PIL import Image
from io import BytesIO
from tkinter import filedialog
from ktrack import tracking_disabled
from src.components.pretools import KaelysAPI, GeneralTools, AppSettings
from werkzeug.security import generate_password_hash
import sys


tools = GeneralTools()
api = KaelysAPI()
settings = AppSettings()


lastData = {}


class JobCard(ctk.CTkFrame):
    def __init__(self, parent, job_data, **kwargs):
        super().__init__(parent, fg_color="#323232", **kwargs)
        
        # Exemple de job_data : {"title": "Livraison Paris", "status": "En cours"}
        self.label_title = ctk.CTkLabel(self, text=job_data["title"], font=("Arial", 14, "bold"))
        self.label_title.pack(anchor="w", padx=10, pady=(5, 0))

        self.label_status = ctk.CTkLabel(self, text=f"Status: {job_data['status']}", text_color="gray")
        self.label_status.pack(anchor="w", padx=10, pady=(0, 5))




class UserProfile(ctk.CTkFrame):
    """
    User profile frame for displaying user information.
    """
    def __init__(self, master=None, *args, **kwargs):
        super().__init__(master, fg_color="transparent", *args, **kwargs)
        self.previous_pick = None # For user data pick in update_user_loop


        ### TOP FRAME
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.pack(pady=0.5)


        # PROFILE LABEL
        self.profile_label = ctk.CTkLabel(self.top_frame, text="Profile", font=("Poppins", 20, "italic"))
        self.profile_label.pack(pady=10)

        # PROFILE PICTURE
        pfp_image = Image.open(tools.resource_path("src/static/default_pfp.png"))
        self.profile_image = ctk.CTkImage(size=(100, 100), light_image=pfp_image)
        self.pfp_label = ctk.CTkLabel(self.top_frame, image=self.profile_image, text="")
        self.pfp_label.pack(pady=5)

        # USER INFOS
        self.user_id_label = ctk.CTkLabel(self.top_frame, text="Your ID:", font=("Poppins", 12, "bold"))
        self.user_id_label.pack(pady=2)
        self.user_discordID_label = ctk.CTkLabel(self.top_frame, text=f"Your Discord ID:", font=("Poppins", 12, "bold"))
        self.user_discordID_label.pack(pady=2)
        
        ### SEPARATION BAR
        self.horizontal_bar = ctk.CTkFrame(self, height=3, width=300, corner_radius=0)
        self.horizontal_bar.pack(padx=20, pady=20)

        ### BOTTOM FRAME
        ### STATISTICS
        self.stats_label = ctk.CTkLabel(self, text="Statistics", font=("Poppins", 20, "italic"))
        self.stats_label.pack(pady=10)


        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.pack(pady=10)

        # LEFT FRAME
        self.left_frame = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        self.left_frame.pack(side="left", padx=10)

        self.deliveries_total_label = ctk.CTkLabel(self.left_frame, text="Deliveries", font=("Arial", 14))
        self.deliveries_total_label.pack(padx=15, pady=5)
        self.deliveries_total_value = ctk.CTkLabel(self.left_frame, text="", font=("Arial", 14))
        self.deliveries_total_value.pack(padx=15, pady=5)

        # SEPARATOR 1
        self.separator1 = ctk.CTkLabel(self.bottom_frame, text="", width=2, height=50, fg_color="white")
        self.separator1.pack(side="left", pady=5)

        # MIDDLE FRAME
        self.middle_frame = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        self.middle_frame.pack(side="left", padx=10)

        self.wallet_label = ctk.CTkLabel(self.middle_frame, text="Wallet", font=("Arial", 14))
        self.wallet_label.pack(padx=15, pady=5)
        self.wallet_value = ctk.CTkLabel(self.middle_frame, text="", font=("Arial", 14))
        self.wallet_value.pack(padx=15, pady=5)

        # SEPARATOR 2
        self.separator2 = ctk.CTkLabel(self.bottom_frame, text="", width=2, height=50, fg_color="white")
        self.separator2.pack(side="left", pady=5)

        # RIGHT FRAME
        self.right_frame = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        self.right_frame.pack(side="left", padx=10)

        self.rank_label = ctk.CTkLabel(self.right_frame, text="Rank", font=("Arial", 14))
        self.rank_label.pack(padx=15, pady=5)
        self.rank_value = ctk.CTkLabel(self.right_frame, text="", font=("Arial", 14))
        self.rank_value.pack(padx=15, pady=5)

        ### LAUNCH UPDATE THREAD LOOP
        self.user_data = tools.load_json(tools.resource_path("data/user.json"))
        self.user_id = self.user_data["id"]
        self.update_profile_loop = threading.Thread(target=self.update_user_profile, daemon=True)
        self.update_profile_loop.start()


        # ### ACTIVE CONTRACTS
        # # === Label ===
        # self.active_contracts_label = ctk.CTkLabel(self, text="Active Contracts", font=("Poppins", 16, "italic"))
        # self.active_contracts_label.pack(pady=(20, 5))

        # # === Affichage des contrats ===
        # contracts = self.get_user_contracts(self.user_id)
        # if contracts:
        #     # === Scrollable Frame (taille réduite) ===
        #     self.contracts_frame = ctk.CTkScrollableFrame(
        #         self,
        #         width=300,
        #         height=120,
        #         fg_color="transparent"
        #     )
        #     self.contracts_frame.pack(pady=(0, 10), padx=10)
        #     for contract in contracts[:1]:
        #         card = ctk.CTkFrame(
        #             self.contracts_frame,
        #             corner_radius=6,
        #             border_width=1,
        #             fg_color="#1a1a1a",
        #             border_color="#444"
        #         )
        #         card.pack(pady=4, padx=5, fill="x")

        #         ctk.CTkLabel(card, text=f"{contract['title']}", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(5, 0))
        #         ctk.CTkLabel(card, text=f"{contract['origin']} → {contract['destination']}", font=("Arial", 10)).pack(anchor="w", padx=10, pady=(0, 5))
        # else:
        #     ctk.CTkLabel(self, text="Nothing to show in here.", font=("Arial", 11, "italic")).pack(pady=10)
        
    

    def update_user_profile(self):
        """
        Fetch user information from the server.
        """
        while True:
            payload = {"id": self.user_id}

            try:
                data = asyncio.run(api.get("/tracker/user", payload))
                if data["error"]:
                    tools.write_log(f"Error fetching user info: {data['message']}", type="error")
                    return
                else:
                    self.pick = data["user"]
                    if not self.previous_pick or self.pick != self.previous_pick:
                        async def load_profile():
                            tools.write_log("Loading profile...")    
                            self.user_id_label.configure(text=f"Your ID: {self.pick['id']}", font=("Poppins", 12, "bold"))
                            self.user_discordID_label.configure(text=f"Your Discord ID: {self.pick['discordID']}", font=("Poppins", 12, "bold"))
                            self.deliveries_total_value.configure(text=f"{self.pick['deliveriesTotal']}")
                            self.wallet_value.configure(text=f"${self.pick['wallet']}")
                            self.rank_value.configure(text=f"N°{self.pick['rank']}")

                            image_response = requests.get(self.pick["avatarURL"])
                            image = Image.open(BytesIO(image_response.content))
                            ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=(100, 100))
                            self.pfp_label.configure(image=ctk_image)
                            self.pfp_label.update()
                            tools.write_log("Profile loaded from API request")

                            self.previous_pick = self.pick
                        
                        asyncio.run(load_profile())
            
            except Exception as e:
                tools.write_log(f"Error fetching user info: {str(e)}", type="error")
                return None
                
            time.sleep(30)  # Update every 30 seconds



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
        



class SettingsPage(ctk.CTkFrame):
    """
    Settings page for the application.
    """
    def __init__(self, master=None, *args, **kwargs):
        super().__init__(master, fg_color="transparent", *args, **kwargs)

        # === SETTINGS LABEL ===
        self.settings_label = ctk.CTkLabel(self, text="Settings", font=("Poppins", 20, "italic"))
        self.settings_label.pack(pady=2)
        notice = "⚠️ Some settings may need a restart to apply."
        self.settings_label = ctk.CTkLabel(self, text=notice, font=("Poppins", 10, "bold"))
        self.settings_label.pack(pady=2)

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
        # Column 1
        self.delete_login_frame = ctk.CTkFrame(self.column_1, fg_color="#2B2B2B")
        self.delete_login_frame.pack(pady=5, padx=10)
        self.delete_login_button = ctk.CTkButton(self.delete_login_frame, text="Logout", font=("Poppins", 12), command=lambda: [tools.write_log("Logged out successfully!", type="info"), self.delete_login(), self.safe_close_app()])
        self.delete_login_button.pack(pady=5, padx=10)

        ## Switches
        # RPC -> CAUTION: self.rpc_var is only used to determine initial RPC switch value
        memory = tools.load_json(tools.resource_path("data/memory.json"))
        settings = memory["settings"]
        self.rpc_var = tk.IntVar(value=1 if settings["RPC"] else 0)
        self.discord_rpc_switch = ctk.CTkSwitch(self.column_1, text="Discord RPC", onvalue=1, offvalue=0, command=lambda: [tools.write_log(f"[ SETTINGS PRESET] Discord RPC set to {tools.get_switch_value(self.discord_rpc_switch)}", type="info")], variable=self.rpc_var)
        self.discord_rpc_switch.pack(pady=5, padx=10)

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

        self.settings_hotkeys_frame = ctk.CTkFrame(self.column_2, fg_color="#2B2B2B")
        self.settings_hotkeys_frame.pack(pady=5, padx=10)
        self.show_hotkeys_button = ctk.CTkButton(self.settings_hotkeys_frame, text="CB Hotkeys", font=("Poppins", 12), command=self.hotkeys_window)
        self.show_hotkeys_button.pack(pady=5, padx=10)

        # Column 3
        self.save_settings_frame = ctk.CTkFrame(self.column_3, fg_color="#2B2B2B")
        self.save_settings_frame.pack(pady=5, padx=10)
        self.save_settings_button = ctk.CTkButton(self.save_settings_frame, text="Save Settings", font=("Poppins", 12), command=self.save_settings_async, fg_color="#00A000", hover_color="#008D00")
        self.save_settings_button.pack(pady=5, padx=10)
    

    def save_settings_async(self):
        threading.Thread(target=self._run_async_save, daemon=True).start()


    def _run_async_save(self):
        asyncio.run(self.send_settings())


    async def send_settings(self):
            self.save_settings_button.configure(text="Processing...")
            self.save_settings_button.update()
            s = {
                "RPC": tools.get_switch_value(self.discord_rpc_switch)
            }

            memory = tools.load_json("data/memory.json")
            current_settings = memory["settings"]

            if s != current_settings:
                success = await settings.save(s)
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


    def show_error(self, message: str):
        error_window = ctk.CTkToplevel()
        error_window.geometry("300x150")
        error_window.title("Error")
        error_window.resizable(False, False)

        ctk.CTkLabel(error_window, text="An error occured.", text_color="red", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(20, 5))
        ctk.CTkLabel(error_window, text=message, wraplength=250).pack(pady=5)
        ctk.CTkButton(error_window, text="Close", command=error_window.destroy).pack(pady=10)

        error_window.grab_set()

    
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
        infos = self.load_infos()

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


    def load_infos(self):
        """
        Load the changelog from local.
        """
        with open(tools.resource_path("properties/infos.json"), 'r') as f:
            infos = json.load(f)
        return infos
    

    def delete_login(self):
        new_data = {"id": 0,
                    "username": "",
                    "steamID64": 0,
                    "discordID": 0,
                    "encrypted_password": ""}
        tools.save_json(new_data, tools.resource_path("data/user.json"))


    def safe_close_app(self):
        try:
            global tracking_disabled
            tracking_disabled = True
            time.sleep(0.5)
            tools.write_log("Application closed cleanly")
            self.destroy()
        except Exception as e:
            tools.write_log(f"Application closed with error: {e}", type="error")
        sys.exit()

            

class InfosPage(ctk.CTkFrame):
    """
    Information page for the application.
    """
    def __init__(self, master=None, *args, **kwargs):
        super().__init__(master, fg_color="transparent", *args, **kwargs)

        # === INFOS LABEL ===
        self.infos_label = ctk.CTkLabel(self, text="Infos", font=("Poppins", 20, "italic"))
        self.infos_label.pack(pady=2)

        # === FRAME PRINCIPAL ===
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(pady=10, fill="both", expand=True)

        # Get infos dictionary
        infos = tools.load_json("properties/infos.json")
        
        # Version heading
        self.infos_heading_label = ctk.CTkLabel(self.main_frame, text=infos["version"], font=('Poppins', 20, 'italic'))
        self.infos_heading_label.pack(pady=(0, 10))

        # === HOW TO INSTALL SECTION ===
        self.how_to_install_frame = ctk.CTkFrame(self.main_frame, fg_color="#1B1B1B")
        self.how_to_install_frame.pack(pady=5, padx=10, fill="x")

        self.how_to_install_heading = ctk.CTkLabel(self.how_to_install_frame, text="How to install", font=("Poppins", 20, "bold"))
        self.how_to_install_heading.pack(pady=5, padx=10)

        self.how_to_install_text = ctk.CTkLabel(self.how_to_install_frame, text=infos["how_to_install"], font=("Poppins", 16), wraplength=550, justify="left", anchor="w")
        self.how_to_install_text.pack(pady=5, padx=10, fill="x", expand=True)

        # === HOW TO USE SECTION ===
        # self.how_to_use_frame = ctk.CTkFrame(self.main_frame, fg_color="#1B1B1B")
        # self.how_to_use_frame.pack(pady=5, padx=10, fill="x")

        # self.how_to_use_heading = ctk.CTkLabel(self.how_to_use_frame, text="How to use", font=("Poppins", 20, "bold"))
        # self.how_to_use_heading.pack(pady=5, padx=10)

        # self.how_to_use_text = ctk.CTkLabel(self.how_to_use_frame, text=infos["how_to_use"], font=("Poppins", 16), wraplength=550,  justify="left", anchor="w")
        # self.how_to_use_text.pack(pady=5, padx=10, fill="x", expand=True)

        # === CHANGELOG SECTION ===
        self.changelog_frame = ctk.CTkFrame(self.main_frame, fg_color="#1B1B1B")
        self.changelog_frame.pack(pady=5, padx=10, fill="x")

        self.changelog_heading = ctk.CTkLabel(self.changelog_frame, text="Changelog", font=("Poppins", 20, "bold"))
        self.changelog_heading.pack(pady=5, padx=10)

        changelog_text = ""
        if isinstance(infos["changelog"], list):
            # Join list items with newlines if changelog is a list
            changelog_text = "\n".join(infos["changelog"])
        else:
            # Use as is if it's already a string
            changelog_text = infos["changelog"]
            
        self.changelog_text = ctk.CTkLabel(self.changelog_frame, text=changelog_text,font=("Poppins", 16), wraplength=600, justify="left", anchor="w")
        self.changelog_text.pack(pady=5, padx=10, fill="x", expand=True)


    # def load_infos(self):
    #     """
    #     Load the changelog from local.
    #     """
    #     with open(tools.resource_path("properties/infos.json"), 'r') as f:
    #         infos = json.load(f)
    #     return infos

