import requests, customtkinter as ctk, threading, time
from PIL import Image
from truck_telemetry import truck_telemetry
from ktrack import API_URL
from src.components.pretools import write_log, load_json, resource_path, load_txt
from src.components.tracking.deliveries import Deliveries


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


        ### TOP FRAME
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.pack(pady=10)

        self.profile_label = ctk.CTkLabel(self.top_frame, text="Profile", font=("Poppins", 20, "italic"))
        self.profile_label.pack(pady=10)

        # PROFILE PICTURE
        pfp_image = Image.open(resource_path("src/static/default_pfp.png"))
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
        self.user_data = load_json(resource_path("data/user.json"))
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
                response = requests.get(f"{API_URL}/tracker/user", json=payload)
                data = response.json()
                if data["error"]:
                    write_log(f"Error fetching user info: {data['message']}", type="error")
                    return
                else:
                    pick = data["user"]
                    self.user_id_label.configure(text=f"Your ID: {pick['id']}", font=("Poppins", 12, "bold"))
                    self.user_discordID_label.configure(text=f"Your Discord ID: {pick['discordID']}", font=("Poppins", 12, "bold"))
                    self.deliveries_total_value.configure(text=f"{pick['deliveriesTotal']}")
                    self.wallet_value.configure(text=f"{pick['wallet']}")
                    self.rank_value.configure(text=f"{pick['rank']}")
        
            except requests.RequestException as e:
                write_log(f"Error fetching user info: {e}", type="error")
                return None
            
            time.sleep(15)  # Update every 30 seconds



    def get_user_contracts(self, user_id):
        """
        Fetch user contracts from the server.
        """
        payload = {"id": user_id}

        try:
            response = requests.get(f"{API_URL}/tracker/user/contracts", json=payload)
            data = response.json()
            if data["error"]:
                write_log(f"Error fetching user contracts: {data['message']}", type="error")
                return None
            else:
                return data
        
        except requests.RequestException as e:
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
        notice = "⚠️ These settings are implemented as beta features. They might not work as expected.\n Please report any issues you may encounter."
        self.settings_label = ctk.CTkLabel(self, text=notice, font=("Poppins", 10, "bold"))
        self.settings_label.pack(pady=2)

        # === FRAME PRINCIPAL ===
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(pady=10)


        # === COLUMNS CONFIGS ===
        # Column 1
        self.column_1 = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.column_1.pack(side="left", padx=20)

        # Column 2
        self.column_2 = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.column_2.pack(side="left", padx=20)

        # Column 3
        self.column_3 = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.column_3.pack(side="left", padx=20)


        # === COLUMNS CONTENTS ===
        # Column 1
        self.job_notif_label = ctk.CTkLabel(self.column_1, text="Job Notifications (disabled)", font=("Poppins", 16, "bold"))
        self.job_notif_label.pack(pady=5, padx=10)
        self.job_notif_select = ctk.CTkOptionMenu(
            self.column_1,
            values=["Discord Guild", "Direct Message", "Both"],
            command=lambda x: print(f"Job notifications set to {x}"),
            text_color="white",
        )
        self.job_notif_select.pack(pady=5, padx=10)



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
        self.main_frame.pack(pady=10)


        # === CHANGELOG ===
        display = self.load_infos()
        display.pack(pady=2, padx=2, fill="x")

    
    def load_infos(self):
        """
        Load the changelog from local.
        """
        display_text = load_txt(resource_path("properties/readme.txt"))
        display = ctk.CTkLabel(self.main_frame, width=300, height=300, text=display_text, anchor="w", justify="left", font=("Poppins", 12), text_color="white")
        return display