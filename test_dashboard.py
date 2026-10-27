from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.test import Client

from dashboard import create_dashboard_app
from dashboard.store import RequestHistory
from middleware import DebuggerMiddleware


def build_client():
    app = Flask("dashboard-test")

    @app.get("/hello")
    def hello():
        return "hello"

    history = RequestHistory(max_records=10)
    dashboard = create_dashboard_app(history)
    application = DebuggerMiddleware(
        DispatcherMiddleware(app, {"/debug": dashboard}),
        history=history,
    )
    return Client(application), history


def test_dashboard_collects_and_displays_request():
    client, history = build_client()

    response = client.get("/hello?token=private")

    assert response.status_code == 200
    records = client.get("/debug/api/requests").json["requests"]
    assert len(records) == 1
    assert records[0]["url"] == "/hello?token=%5BREDACTED%5D"
    assert records[0]["status_code"] == 200
    assert records[0]["duration_ms"] >= 0
    assert records[0]["request_headers"]["Host"] == "localhost"
    assert history.summary()["total_requests"] == 1


def test_dashboard_filters_by_method_status_and_url():
    client, _ = build_client()
    client.get("/hello")

    assert len(client.get("/debug/api/requests?method=GET").json["requests"]) == 1
    assert len(client.get("/debug/api/requests?status=404").json["requests"]) == 0
    assert len(client.get("/debug/api/requests?url=hello").json["requests"]) == 1


def test_dashboard_routes_and_api_data():
    client, _ = build_client()
    client.get("/hello")

    assert client.get("/debug/").status_code == 200
    assert b"Debug dashboard" in client.get("/debug/").data
    assert client.get("/debug/static/dashboard.css").status_code == 200
    assert client.get("/debug/api/summary").json["successful_requests"] == 1
    assert client.get("/debug/api/performance").json["count"] == 1
    assert client.get("/debug/api/errors").json["errors"] == []


def test_dashboard_requests_are_not_recorded_recursively():
    client, history = build_client()

    client.get("/debug/api/summary")

    assert history.summary()["total_requests"] == 0
