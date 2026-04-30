import customtkinter as ctk, asyncio, tkinter as tk, sys
from tkinter import filedialog
from src.components.pretools import KaelysAPI, GeneralTools, AppSettings
from tkinter import messagebox


tools = GeneralTools()
api = KaelysAPI()
settings = AppSettings()


lastData = {}


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