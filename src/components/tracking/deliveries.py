import requests, customtkinter as ctk
from src.components.pretools import load_json, save_json, resource_path, write_log, generate_job_id



class Deliveries:
    def __init__(self, webhook_url=None):
        self.webhook_url = webhook_url


    def handle(self, data: dict):
        game = str(data["game"])
        event_type = ""


        if data["onJob"]:
            job_data = {
                "market": data["jobMarket"],
                "truck_model_id": data["truckId"],
                "truck_name": f'{data["truckBrand"]} {data["truckName"]}',
                "source_city_id": data["citySrcId"],
                "source_city_name": data["citySrc"],
                "destination_city_id": data["cityDstId"],
                "destination_city_name": data["cityDst"],
                "destination_company_id": data["compDstId"],
                "destination_company_name": data["compDst"],
                "cargo_definition_name": data["cargo"],
                "cargo_definition_id": data["cargoId"],
                "cargo_definition_mass": data["cargoMass"],
                "cargo_definition_overweight": data["specialJob"],
                "driven_distance": data["plannedDistanceKm"],
            }
            memory = load_json(resource_path("data/memory.json"))

            if not job_data == memory["jobs"][game]:
                event_type = "job_started"

                self._handle_job_start(job_data)
                ### AFTER HANDLING
                write_log("- Updating local memory...")
                memory["jobs"][game] = job_data
                save_json(memory, resource_path("data/memory.json"))
                write_log("- Local memory updated.")


        elif data["jobCancelled"]:
            memory = load_json(resource_path("data/memory.json"))
            job_data = memory["jobs"][game]
            if not job_data == {}:
                event_type = "job_cancelled"
                self._handle_job_cancelled(job_data)
                # AFTER HANDLING
                write_log("- Updating local memory...")
                memory["jobs"][game] = {}
                save_json(memory, resource_path("data/memory.json"))
                write_log("- Local memory updated.")


        else:
            memory = load_json(resource_path("data/memory.json"))
            job_data = memory["jobs"][game]
            if not job_data == {}:
                event_type = "job_delivered"
                job_data["jobStartingTime"] = data["jobStartingTime"]
                job_data["jobFinishedTime"] = data["jobFinishedTime"]
                self._handle_job_delivered(job_data)
                # AFTER HANDLING
                write_log("- Updating local memory...")
                memory["jobs"][game] = {}
                save_json(memory, resource_path("data/memory.json"))
                write_log("- Local memory updated.")


        return event_type 



    def _handle_job_start(self, job_data: dict):
        write_log("Event Triggered: job_started")
        write_log("- Transmitting data to API...")

        user_data = load_json(resource_path("data/user.json"))
        jobID = generate_job_id(job_data)

        payload = {
            "event": "job_started",
            "user": user_data,
            "data": {
                "id": jobID,
                "plannedDistance": job_data["driven_distance"],
                "source_city_name": job_data["source_city_name"],
                "destination_city_name": job_data["destination_city_name"],
                "destination_company_name": job_data["destination_company_name"],
                "market": job_data["market"],
                "cargo_name": job_data["cargo_definition_name"]
            }
        }
        response = requests.post(self.webhook_url, json=payload)
        write_log(f"- Response status: {response.status_code} | ")



    def _handle_job_delivered(self, job_data: dict):
        write_log("Event Triggered: job_delivered")
        write_log("- Transmitting data to API...")

        user_data = load_json(resource_path("data/user.json"))

        jobID = generate_job_id(job_data)
        job_data["id"] = jobID

        payload = {
            "event": "job_delivered",
            "user": user_data,
            "data": job_data
        }
        response = requests.post(self.webhook_url, json=payload)
        write_log(f"- Response status: {response.status_code} | ")


    def _handle_job_cancelled(self, job_data: dict):
        write_log("Event Triggered: job_cancelled")
        write_log("- Transmitting data to API...")

        user_data = load_json(resource_path("data/user.json"))

        jobID = generate_job_id(job_data)

        payload = {
            "event": "job_cancelled",
            "user": user_data,
            "data": {"id": jobID}
        }
        response = requests.post(self.webhook_url, json=payload)
        write_log(f"- Response status: {response.status_code} | ")
