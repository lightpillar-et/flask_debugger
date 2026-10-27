
from datetime import datetime
from werkzeug.wrappers import Request


class RequestLogger:

    def log(self, environ):
        # Build a request object from the WSGI environment
        request = Request(environ)

        # Record request information
        timestamp = datetime.now().isoformat(timespec="seconds")
        method = request.method
        path = request.path
        query = request.query_string.decode("utf-8", errors="replace")
        user_agent = request.headers.get("User-Agent", "Unknown")

        # Display the request log
        print("\n========== INCOMING REQUEST ==========")
        print(f"Timestamp: {timestamp}")
        print(f"Method: {method}")
        print(f"Path: {path}")
        print(f"Query String: {query}")
        print(f"User-Agent: {user_agent}")
        print("======================================\n")