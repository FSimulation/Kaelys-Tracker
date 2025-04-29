import customtkinter as ctk, requests
from PIL import Image
from src.components.pretools import save_json, load_json, resource_path



class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("KaelysTrack")
        self.geometry("600x400")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        self.resizable(False, False)

        self.setup_ui()


    def setup_ui(self):
        image_path = resource_path("src/KaelysHUB.png")
        pil_image = Image.open(image_path)
        image = ctk.CTkImage(size=(250, 140), light_image=pil_image)
        image_label = ctk.CTkLabel(self, image=image, text="")
        image_label.pack(pady=10)

        label = ctk.CTkLabel(self, text="Login", font=("Arial", 20))
        label.pack(pady=10)

        self.username = ctk.CTkEntry(self, placeholder_text="Username")
        self.username.pack(pady=10)

        self.password = ctk.CTkEntry(self, placeholder_text="Password", show="*")
        self.password.pack(pady=10)

        self.login_button = ctk.CTkButton(self, text="Go!", command=self.login)
        self.login_button.pack(pady=10)


    def login(self):
        self.login_button.configure(text="Loading...")
        self.login_button.update()
        creds = {
            "username": self.username.get(),
            "password": self.password.get()
        }
        response = requests.get("https://api-kaelysvirtual.onrender.com/tracker/login", json=creds)
        if response.status_code == 200:
            data = response.json()

            if data["error"]:
                print(data["message"])
                error_label = ctk.CTkLabel(self, text=data["message"], text_color="red")
                error_label.pack(pady=5)
                self.login_button.configure(text="Go!")
                self.login_button.update()
            else:
                print(data)
                user_data = data["user"]
                save_json(user_data, resource_path("data/user.json"))
                self.destroy()
                self.main_window = MainWindow()
                self.main_window.mainloop()
        else:
            print("Error: Unable to connect to the server.")
            error_label = ctk.CTkLabel(self, text="Unable to connect to the server.", text_color="red")
            error_label.pack(pady=5)
            self.login_button.configure(text="Go!")
            self.login_button.update()



class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("KaelysTrack")
        self.geometry("700x700")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        self.user_data = load_json(resource_path("data/user.json"))

        self.setup_ui()
    

    def setup_ui(self):
        welcome_label = ctk.CTkLabel(self, text=f'Welcome, {self.user_data["username"]}!', font=("Arial", 20))
        welcome_label.pack(pady=10)



if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()

