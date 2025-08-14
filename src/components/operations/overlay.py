import customtkinter as ctk



class Overlay(ctk.CTk):
    def __init__(self, title="Overlay", size="300x100+100+100", opacity=1.0, transparent=False):
        super().__init__()

        # Configuration de la fenêtre
        self.title(title)
        self.geometry(size)
        self.overrideredirect(True)  # Supprime bordures/fenêtre
        self.wm_attributes("-topmost", True)  # Toujours visible

        if transparent:
            self.wm_attributes("-transparentcolor", "#123456")
            self.configure(bg="#123456")
        else:
            self.wm_attributes("-alpha", opacity)

        self.create_widgets()


    def create_widgets(self):
        """Créer les éléments de l'interface"""
        frame = ctk.CTkFrame(master=self, fg_color="#222222", corner_radius=10)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        label = ctk.CTkLabel(frame, text="Ceci est un overlay", text_color="white")
        label.pack(pady=10)

        button = ctk.CTkButton(frame, text="Fermer", command=self.quit_overlay)
        button.pack(pady=5)


    def quit_overlay(self):
        """Ferme proprement la fenêtre"""
        self.destroy()



if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Crée et lance l'overlay
    overlay = Overlay(opacity=0.9, transparent=False)
    overlay.mainloop()
