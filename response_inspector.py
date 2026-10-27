class ResponseInspector:

    def inspect(self, status, headers):

        print("\n========== RESPONSE INSPECTOR ==========")

        # Capture HTTP status
        print(f"Status: {status}")

        # Capture response headers
        print("Headers:")

        for name, value in headers:
            print(f"  {name}: {value}")

        # Extract Content-Type
        content_type = next(
            (value for name, value in headers
             if name.lower() == "content-type"),
            "Unknown"
        )

        print(f"Content-Type: {content_type}")
        print("========================================\n")