from request_logger import RequestLogger
class DebuggerMiddleware:

    def __init__(self, app, show_debug_output=False):
        self.app = app
        self.show_debug_output = show_debug_output
        self.logger = RequestLogger()

    def __call__(self, environ, start_response):
        if self.show_debug_output:
            print("\n========== 1. INCOMING REQUEST ==========")
            print("Method:", environ.get("REQUEST_METHOD"))
            print("Path:", environ.get("PATH_INFO"))
            print("Query String:", environ.get("QUERY_STRING"))
            print("========== END INCOMING REQUEST ==========\n")
        
        #using the Request Logger we imported we log the incoming request 
        self.logger.log(environ)

        def custom_start_response(status, headers, exc_info=None):
            headers = list(headers)
            headers.append(("Custom-Header", "Custom Header By Inspecting"))

            if self.show_debug_output:
                print("\n========== 3. OUTGOING RESPONSE ==========")
                print("Status:", status)

                for name, value in headers:
                    print(f"{name}: {value}")

                print("========== END OUTGOING RESPONSE ==========\n")

            return start_response(status, headers, exc_info)

        if self.show_debug_output:
            print("========== 2. FLASK PROCESSING ==========")

        response = self.app(environ, custom_start_response)

        if self.show_debug_output:
            print("========== END FLASK PROCESSING ==========\n")

        return response