# locustfile.py
from locust import HttpUser, task, between
import uuid

class ButlerUser(HttpUser):
    wait_time = between(1, 5)
    host = "http://localhost:8080" # The orchestrator's address
    session_id = None

    def on_start(self):
        """Called when a Locust start before any task is scheduled"""
        self.session_id = str(uuid.uuid4())

    @task
    def chat_flow(self):
        # Test a simple recommendation flow
        self.client.post("/chat", json={
            "user_input": "What do you recommend for me today?",
            "session_id": self.session_id,
            "customer_id": "user123"
        })