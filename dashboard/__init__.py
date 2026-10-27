from flask import Flask

from .routes import dashboard_bp


def create_dashboard_app(history):
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )
    app.config["REQUEST_HISTORY"] = history
    app.register_blueprint(dashboard_bp)

    @app.before_request
    def restrict_to_local_development():
        from flask import abort, request

        if request.remote_addr not in (None, "127.0.0.1", "::1"):
            abort(403)

    return app