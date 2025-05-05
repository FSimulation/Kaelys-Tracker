import customtkinter as ctk, requests, threading, time
from truck_telemetry import truck_telemetry
from PIL import Image
from src.components.tracking.deliveries import Deliveries
from src.components.pretools import save_json, load_json, resource_path, write_log


lastData = {}




def game_notif(message: str, delay=5000):
    notif = ctk.CTkToplevel()
    notif.overrideredirect(True)
    notif.attributes("-topmost", True)

    width, height = 250, 80
    notif.geometry(f"{width}x{height}+10+10")

    ctk.CTkLabel(notif, text="KaelysTrack", font=ctk.CTkFont(size=12)).pack(pady=2)
    ctk.CTkLabel(notif, text=message, font=ctk.CTkFont(size=15, weight="bold")).pack(pady=2)

    notif.after(delay, notif.destroy)



# CTK INTERFACE
class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("KaelysTrack")
        self.geometry("600x400")
        self.iconbitmap(resource_path("src/static/ktrack.ico"))
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        self.resizable(False, False)

        self.setup_ui()


    def setup_ui(self):
        image_path = resource_path("src/static/KaelysHUB.png")
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
        self.iconbitmap(resource_path("src/static/ktrack.ico"))
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        self.user_data = load_json(resource_path("data/user.json"))
        self.stop_event = threading.Event()
        self.stop_event.set()

        self.setup_ui()



    def print_game_data(self):
        truck_telemetry.init()
        data = truck_telemetry.get_data()
        write_log(data)
        truck_telemetry.deinit()


    
    def update_game_status(self, status: str):
        self.game_status_label.configure(text=status, text_color="green")
        self.game_status_label.update()


    
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
        deliveries = Deliveries("https://api-kaelysvirtual.onrender.com/tracker/deliveries")

        while not self.stop_event.is_set():
            try:
                data = truck_telemetry.get_data()
                write_log("Data received from SDK")

                if lastData == str(data):
                    write_log("No data change detected.")
                else:
                    write_log("Data change detected.")
                    lastData = str(data)
                    # ON SAIT QUE LES DONNES SONT MISES A JOUR
                    if data["game"] == 1:
                        self.update_game_status("Euro Truck Simulator 2")
                    elif data["game"] == 2:
                        self.update_game_status("American Truck Simulator")

                    write_log("Deliveries object ready")
                    event_type = deliveries.handle(data)
                    write_log("Deliveries handled")

                    if event_type == "job_started":
                        self.game_notif("Delivery in progress. Drive safe!", delay=5000)
                    elif event_type == "job_delivered":
                        self.game_notif("Delivery completed. Good job!", delay=5000)
                    elif event_type == "job_cancelled":
                        self.game_notif("Delivery cancelled. Another \ndriver got the freight away.", delay=5000)
                    

            except (FileNotFoundError, AttributeError) as sdk_err:
                self.stop_tracking()
                self.show_error("Tracking disabled due to SDK disconnection.")
                write_log(f"[SDK Error] {sdk_err}", type="error")
                break

            except Exception as outer:
                write_log(f"[Thread crash] {outer}", type="error")
                self.show_error("Tracking stopped unexpectedly.")
                self.stop_tracking()
                break

            time.sleep(3)



    def start_tracking(self):
        if hasattr(self, "sdk_thread") and self.sdk_thread.is_alive():
            write_log("Tracking thread already running, skipping start.")
            return

        try:
            truck_telemetry.init()
            self.stop_event.clear()
            self.sdk_thread = threading.Thread(target=self.run_sdk_loop, daemon=True)
            self.sdk_thread.start()
            self.tracking_button.configure(text="Stop tracking", command=self.stop_tracking)
        except FileNotFoundError:
            self.show_error("Unable to load the SDK. Either the game is not running or the SDK plugin is not installed.")
            write_log("SDK init failed: FileNotFoundError", type="error")



    def stop_tracking(self):
        self.stop_event.set()
        truck_telemetry.deinit()
        self.tracking_button.configure(text="Start tracking", command=self.start_tracking)
        self.game_status_label.configure(text="Tracking is disabled", text_color="red")
        self.game_status_label.update()
        write_log("Tracking stopped cleanly")

    

    def setup_ui(self):
        welcome_label = ctk.CTkLabel(self, text=f'Welcome, {self.user_data["username"]}!', font=("Arial", 20, "bold"))
        welcome_label.pack(pady=10)
        version_label = ctk.CTkLabel(master=self, text="version 05-05-2025", text_color="gray")
        version_label.place(relx=0.01, rely=1.0, anchor="sw")  # En bas à gauche


        self.game_status_label = ctk.CTkLabel(self, text="Tracking is disabled", font=("Arial", 14), text_color="red")
        self.game_status_label.pack(pady=5)

        self.tracking_button = ctk.CTkButton(self, text="Start tracking", command=self.start_tracking)
        self.tracking_button.pack(pady=10)

        # BOUTON DE TEST POUR L'AFFICHAGE DES DONNES DU SDK
        #self.test_button = ctk.CTkButton(self, text="Print game data", command=self.print_game_data)
        #self.test_button.pack(pady=10)



if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()

