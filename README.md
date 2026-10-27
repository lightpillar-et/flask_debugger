# Flask Debugger

**See every request. Find every error. Understand your Flask app faster.**

Flask Debugger is a lightweight development middleware that inspects Flask
requests, responses, errors, and execution time in real time. It includes a
local dashboard for request history, performance, and error monitoring.

## Features

- Request and response inspection
- Execution-time tracking
- HTTP error capture
- Sensitive header, query, and body-field redaction
- In-memory request history with a 200-record limit
- Browser dashboard with request filters and performance metrics
- WSGI middleware support

## Run it

```bash
git clone https://github.com/lightpillar-et/flask_debugger.git
cd flask_debugger
python -m venv .venv
source .venv/bin/activate
pip install Flask Werkzeug
python app.py
```

Open:

- **Dashboard:** http://127.0.0.1:5000/debug/
- **Sample app 1:** http://127.0.0.1:5000/app1/
- **Sample app 2:** http://127.0.0.1:5000/app2/
- **Sample app 3:** http://127.0.0.1:5000/app3/

## How it works

`DebuggerMiddleware` wraps the Flask dispatcher, records each request, measures
its duration, captures the response status, and stores a sanitized record.
The dashboard reads that history through JSON endpoints under `/debug/api/`.

This tool is intended for **local development only**. Request history is
stored in memory and is cleared when the process stops.
