
import time


class ExecutionTimer:

    def start(self):
        # Record starting time
        return time.perf_counter()

    def stop(self, start_time):
        # Calculate elapsed time in milliseconds
        duration = (time.perf_counter() - start_time) * 1000
        return round(duration, 2)

    def report(self, environ, duration):
        method = environ.get("REQUEST_METHOD")
        path = environ.get("PATH_INFO")

        print("\n========== EXECUTION TIMER ==========")
        print(f"Request: {method} {path}")
        print(f"Duration: {duration} ms")
        print("=====================================\n")