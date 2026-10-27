from datetime import datetime

class DebugReport:

    def __init__(self):

        # Data belonging to one request
        self.request = {}
        self.response = {}
        self.duration = None

    def collect_request(self, environ):

        self.request = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "method": environ.get("REQUEST_METHOD"),
            "path": environ.get("PATH_INFO"),
            "query": environ.get("QUERY_STRING", "")
        }

    def collect_response(self, status, headers):

        self.response = {
            "status": status,
            "headers": dict(headers)
        }

    def collect_duration(self, duration):

        self.duration = duration

    def display(self):

        print("\n========== FLASK DEBUG REPORT ==========")

        print("\nREQUEST")
        for key, value in self.request.items():
            print(f"  {key}: {value}")

        print("\nRESPONSE")
        print(f"  Status: {self.response.get('status', 'Unknown')}")

        for key, value in self.response.get("headers", {}).items():
            print(f"  {key}: {value}")

        print("\nPERFORMANCE")
        print(f"  Duration: {self.duration} ms")

        print("\n========================================\n")