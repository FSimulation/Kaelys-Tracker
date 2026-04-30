import customtkinter as ctk
from src.components.pretools import KaelysAPI, GeneralTools, AppSettings


tools = GeneralTools()
api = KaelysAPI()
settings = AppSettings()


lastData = {}


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