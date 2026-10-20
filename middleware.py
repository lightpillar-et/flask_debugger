class DebuggerMiddleware:

    def __init__(self, app):
        # Store the dispatcher
        self.app = app

    def __call__(self, environ, start_response):

        # 1. BEFORE DISPATCHING — Inspect request
        print("\n========== INCOMING REQUEST ==========")
        print("Method:", environ.get("REQUEST_METHOD"))
        print("Path:", environ.get("PATH_INFO"))
        print("Query String:", environ.get("QUERY_STRING"))

        # 2. INTERCEPT THE RESPONSE
        def custom_start_response(status, headers, exc_info=None):

            print("\n========== OUTGOING RESPONSE ==========")
            print("Status:", status)

            print("Headers:")
            for name, value in headers:
                print(f"  {name}: {value}")

            print("======================================")

            # Forward to the original server callback
            return start_response(status, headers, exc_info)

        # 3. CALL THE DISPATCHER
        response = self.app(environ, custom_start_response)

        # 4. RETURN RESPONSE TO WSGI SERVER
        return response