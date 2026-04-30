import customtkinter as ctk
from PIL import Image
from src.components.pretools import GeneralTools



tools = GeneralTools()



class Fleet(ctk.CTkFrame):
    def __init__(self, master=None, *args, **kwargs):
        super().__init__(master, fg_color="transparent", *args, **kwargs)
        self.custom_font = ctk.CTkFont("Poppins", size=16, weight="bold")
        self.user = tools.load_json(tools.resource_path("data/user.json"))
        self.setup_ui()


    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        ets2_path = tools.resource_path("src/static/fleet/genericETS2.png")
        ats_path = tools.resource_path("src/static/fleet/genericATS.png")

        self.ets2_image = ctk.CTkImage(
            light_image=Image.open(ets2_path),
            dark_image=Image.open(ets2_path),
            size=(320, 180)
        )
        self.ats_image = ctk.CTkImage(
            light_image=Image.open(ats_path),
            dark_image=Image.open(ats_path),
            size=(320, 180)
        )

        self.ets2_panel = self._build_game_panel(self, "Euro Truck Simulator 2", 0, self.ets2_image)
        self.ats_panel = self._build_game_panel(self, "American Truck Simulator", 1, self.ats_image)


    def _build_game_panel(self, parent, title, column_index, truck_image):
        game_frame = ctk.CTkFrame(parent, fg_color="#1C2B3A", corner_radius=20)
        game_frame.grid(row=0, column=column_index, sticky="nsew", padx=10, pady=10)
        game_frame.grid_columnconfigure(0, weight=1)
        game_frame.grid_rowconfigure(1, weight=1)

        header = ctk.CTkLabel(
            game_frame,
            text=title,
            font=ctk.CTkFont("Poppins", size=18, weight="bold"),
            anchor="center"
        )
        header.grid(row=0, column=0, padx=20, pady=(20, 10))

        image_card = ctk.CTkFrame(game_frame, fg_color="#152030", corner_radius=16)
        image_card.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 15))
        image_card.grid_columnconfigure(0, weight=1)
        image_card.grid_rowconfigure(0, weight=1)

        truck_img_label = ctk.CTkLabel(image_card, text="", image=truck_image)
        truck_img_label.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        info_card = ctk.CTkFrame(game_frame, fg_color="#152030", corner_radius=16)
        info_card.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        info_card.grid_columnconfigure(0, weight=1)
        info_card.grid_columnconfigure(1, weight=1)

        info_header = ctk.CTkLabel(
            info_card,
            text="Truck Infos",
            font=ctk.CTkFont("Poppins", size=16, weight="bold"),
            anchor="w"
        )
        info_header.grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=(15, 8))

        self._add_info_row(info_card, 1, "Truck:", "Unknown")
        self._add_info_row(info_card, 2, "Odometer:", "Unknown")
        self._add_info_row(info_card, 3, "Powertrain:", "Unknown")

        return game_frame


    def _add_info_row(self, container, row, label_text, value_text):
        label = ctk.CTkLabel(container, text=label_text, font=ctk.CTkFont("Poppins", size=13), text_color="#9aa5b5", anchor="w")
        label.grid(row=row, column=0, sticky="w", padx=(15, 10), pady=4)

        value = ctk.CTkLabel(container, text=value_text, font=ctk.CTkFont("Poppins", size=13, weight="bold"), anchor="e")
        value.grid(row=row, column=1, sticky="e", padx=(10, 15), pady=2)


        