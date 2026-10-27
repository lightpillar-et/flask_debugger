from flask import Blueprint, current_app, jsonify, render_template, request


dashboard_bp = Blueprint("dashboard", __name__)


def _history():
    return current_app.config["REQUEST_HISTORY"]


@dashboard_bp.route("/")
def dashboard():
    return render_template("dashboard.html")


@dashboard_bp.route("/api/summary")
def summary():
    return jsonify(_history().summary())


@dashboard_bp.route("/api/requests")
def requests():
    status = request.args.get("status", type=int)
    limit = min(max(request.args.get("limit", 50, type=int), 1), 200)
    return jsonify({
        "requests": _history().query(
            method=request.args.get("method"),
            status=status,
            url=request.args.get("url"),
            limit=limit,
        )
    })


@dashboard_bp.route("/api/requests/<record_id>")
def request_detail(record_id):
    record = _history().get(record_id)
    if record is None:
        return jsonify({"error": "Request record not found"}), 404
    return jsonify(record)


@dashboard_bp.route("/api/errors")
def errors():
    return jsonify({"errors": _history().errors()})


@dashboard_bp.route("/api/performance")
def performance():
    return jsonify(_history().performance())
