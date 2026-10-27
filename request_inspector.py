# request_inspector.py

import json
from urllib.parse import parse_qs
from werkzeug.wrappers import Request


class RequestInspector:

    def inspect(self, environ):
        request = Request(environ)

        print("\n========== REQUEST DATA ==========")

        # 1. Inspect query parameters
        if request.args:
            print("Query Parameters:", request.args.to_dict(flat=False))

        # 2. Inspect JSON body
        if request.is_json:
            data = request.get_json(silent=True)

            if data is not None:
                print("JSON Data:")
                print(json.dumps(data, indent=4))

        # 3. Inspect form data
        elif request.mimetype == "application/x-www-form-urlencoded":
            body = request.get_data(cache=True, parse_form_data=False)
            form_data = parse_qs(
                body.decode("utf-8", errors="replace"),
                keep_blank_values=True
            )
            print("Form Data:", form_data)

        print("==================================\n")