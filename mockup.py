import customtkinter as ctk
from PIL import Image
import time, threading


class MainWindow(ctk.CTk):
    def __init__(self, api_client):
        super().__init__()
        self.api = api_client

        self.title("myKaelys Client")
        self.geometry("1100x700")
        self.minsize(960, 600)
        self.configure(fg_color="#0f1a27")

        self.setup_ui()

        # lancer un thread pour updater l'heure et le status API
        threading.Thread(target=self.update_header_loop, daemon=True).start()

    def setup_ui(self):
        # ========== HEADER ==========
        header = ctk.CTkFrame(self, fg_color="#0f1a27")
        header.pack(fill="x", pady=(12, 0))

        # logo ou fallback
        try:
            pil_logo = Image.open("src/static/MainBanner.png")
            logo_img = ctk.CTkImage(pil_logo, size=(300, 110))
            ctk.CTkLabel(header, image=logo_img, text="").pack(side="left", padx=20)
        except Exception:
            ctk.CTkLabel(header, text="FSimulation",
                         font=ctk.CTkFont("Poppins", 26, "bold")).pack(side="left", padx=20)

        # horloge
        self.clock = ctk.CTkLabel(header, text="--:--",
                                  font=ctk.CTkFont("Poppins", 20, "bold"))
        self.clock.pack(side="right", padx=20)

        # ======= TABVIEW =========
        tab_font = ctk.CTkFont(family="Poppins", size=14, weight="bold")
        self.tabview = ctk.CTkTabview(self, width=900, height=540, corner_radius=12, fg_color="#0f1a27", segmented_button_fg_color="#1c2b3a", segmented_button_unselected_color="#1c2b3a", segmented_button_unselected_hover_color="#243447")
        self.tabview.pack(padx=20, pady=20, fill="both", expand=True)

        # styliser le segmented button interne
        self.tabview._segmented_button.configure(font=tab_font)

        # Onglets
        self.tab_home = self.tabview.add("Home")
        self.tab_settings = self.tabview.add("Settings")
        self.tab_info = self.tabview.add("Informations")

        # Remplir chaque onglet
        self.setup_home_tab()
        self.setup_settings_tab()
        self.setup_info_tab()

    # ====== ONGLET HOME ======
    def setup_home_tab(self):
        content = ctk.CTkFrame(self.tab_home, fg_color="#1c2b3a", corner_radius=12)
        content.pack(fill="both", expand=True, padx=20, pady=20)

        # Profil utilisateur
        profile_frame = ctk.CTkFrame(content, fg_color="#243447", corner_radius=12)
        profile_frame.pack(fill="x", pady=(10, 20), padx=20)

        avatar = ctk.CTkLabel(profile_frame, text="👤", font=ctk.CTkFont(size=48))
        avatar.pack(side="left", padx=20, pady=20)

        infos = ctk.CTkLabel(profile_frame,
                             text="User: FSimulation\nDiscord: 1038719463358484510\nRank: Roleplay Driver",
                             justify="left", font=ctk.CTkFont("Poppins", 14))
        infos.pack(side="left", padx=10)

        # Stats
        stats_frame = ctk.CTkFrame(content, fg_color="#243447", corner_radius=12)
        stats_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(stats_frame, text="Deliveries: 7", font=ctk.CTkFont(size=14)).grid(row=0, column=0, padx=20, pady=10)
        ctk.CTkLabel(stats_frame, text="Wallet: $725", font=ctk.CTkFont(size=14)).grid(row=0, column=1, padx=20, pady=10)
        ctk.CTkLabel(stats_frame, text="Rank: 15", font=ctk.CTkFont(size=14)).grid(row=1, column=0, padx=20, pady=10)
        ctk.CTkLabel(stats_frame, text="Playtime: 125h", font=ctk.CTkFont(size=14)).grid(row=1, column=1, padx=20, pady=10)
        ctk.CTkLabel(stats_frame, text="Current job: In a convoy", font=ctk.CTkFont(size=14)).grid(row=2, column=0, columnspan=2, pady=10)

    # ====== ONGLET SETTINGS ======
    def setup_settings_tab(self):
        content = ctk.CTkFrame(self.tab_settings, fg_color="#1c2b3a", corner_radius=12)
        content.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(content, text="⚙️ Settings",
                     font=ctk.CTkFont("Poppins", 18, "bold")).pack(pady=20)

        dark_mode = ctk.CTkSwitch(content, text="Dark Mode")
        dark_mode.pack(pady=10)

        api_opt = ctk.CTkCheckBox(content, text="Enable API Sync")
        api_opt.pack(pady=10)

    # ====== ONGLET INFORMATIONS ======
    def setup_info_tab(self):
        content = ctk.CTkFrame(self.tab_info, fg_color="#1c2b3a", corner_radius=12)
        content.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(content, text="ℹ️ Informations",
                     font=ctk.CTkFont("Poppins", 18, "bold")).pack(pady=20)

        info_text = """Bienvenue sur le client myKaelys !
Ici tu trouveras le changelog, des tutos, et des infos RP."""
        ctk.CTkLabel(content, text=info_text,
                     justify="left",
                     font=ctk.CTkFont("Poppins", 14)).pack(padx=20, pady=20, anchor="w")

    # ====== HEADER LOOP (status + heure) ======
    def update_header_loop(self):
        while True:
            # Update heure
            current_time = time.strftime("%H:%M")
            self.clock.configure(text=current_time)

            # API status (fake: alterne en exemple)
            try:
                # ICI tu peux brancher self.api.get_status()
                online = True
                if online:
                    self.status_text.configure(text="API Status: Online")
                    self.status_dot.configure(text_color="#25d366")
                else:
                    self.status_text.configure(text="API Status: Offline")
                    self.status_dot.configure(text_color="#ff5252")
            except Exception:
                self.status_text.configure(text="API Status: Error")
                self.status_dot.configure(text_color="#ff5252")

            time.sleep(5)

if __name__ == "__main__":
    # Simuler un client API
    class FakeAPIClient:
        def get_status(self):
            return True  # Simule toujours en ligne

    api_client = FakeAPIClient()
    app = MainWindow(api_client)
    app.mainloop()
