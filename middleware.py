from request_logger import RequestLogger
from request_inspector import RequestInspector
from response_inspector import ResponseInspector
from execution_timer import ExecutionTimer
from debug_report import DebugReport
from dashboard.records import build_request_record, redact_headers
from dashboard.store import RequestHistory


class DebuggerMiddleware:

    def __init__(self, app, show_debug_output=False, history=None):
        self.app = app
        self.show_debug_output = show_debug_output
        self.history = history or RequestHistory()
        self.logger = RequestLogger()
        self.inspector = RequestInspector()
        self.response_inspector = ResponseInspector()
        self.timer = ExecutionTimer()
        

    def __call__(self, environ, start_response):
        # Dashboard requests bypass monitoring to avoid recursively recording itself.
        if environ.get("SCRIPT_NAME", "").startswith("/debug") or environ.get(
            "PATH_INFO", ""
        ).startswith("/debug"):
            return self.app(environ, start_response)

        # 1. Start timer
        start_time = self.timer.start()
        debug_report = DebugReport()
        debug_report.collect_request(environ)
        record = build_request_record(environ)
        if self.show_debug_output:
            print("\n========== 1. INCOMING REQUEST ==========")
            print("Method:", environ.get("REQUEST_METHOD"))
            print("Path:", environ.get("PATH_INFO"))
            print("Query String:", environ.get("QUERY_STRING"))
            print("========== END INCOMING REQUEST ==========\n")
        
        #using the Request Logger we imported we log the incoming request 
        self.logger.log(environ)
        self.inspector.inspect(environ)

        def custom_start_response(status, headers, exc_info=None):
            headers = list(headers)
            headers.append(("Custom-Header", "Custom Header By Inspecting"))
            debug_report.collect_response(status, headers)
            record["status"] = status
            record["status_code"] = int(status.split(" ", 1)[0])
            record["response_headers"] = redact_headers(headers)

            if self.show_debug_output:
                print("\n========== 3. OUTGOING RESPONSE ==========")
                print("Status:", status)

                for name, value in headers:
                    print(f"{name}: {value}")

                print("========== END OUTGOING RESPONSE ==========\n")

            return start_response(status, headers, exc_info)

        if self.show_debug_output:
            print("========== 2. FLASK PROCESSING ==========")

        try:
            response = self.app(environ, custom_start_response)
        except Exception as error:
            record["error"] = {
                "type": type(error).__name__,
                "message": str(error),
            }
            record["duration_ms"] = self.timer.stop(start_time)
            self.history.add(record)
            raise

        if self.show_debug_output:
            print("========== END FLASK PROCESSING ==========\n")
        
        duration = self.timer.stop(start_time)
        self.timer.report(environ, duration)
        debug_report.collect_duration(duration)
        record["duration_ms"] = duration
        if record["status_code"] >= 400 and record["error"] is None:
            record["error"] = {"type": "HTTPError", "message": record["status"]}
        self.history.add(record)
        if self.show_debug_output:
            debug_report.display()


        return response