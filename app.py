from flask import Flask  , url_for , current_app , request
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
from middleware import DebuggerMiddleware
from dashboard import create_dashboard_app
from dashboard.store import RequestHistory

SHOW_DEBUG_OUTPUT = False

app1 = Flask ("app1")
app2 = Flask ("app2")
app3 = Flask ("app3")

app1.config["APP_NAME"] = "Application One"
app1.config["APP_VERSION"] = "1.0"
app1.config["DEBUG_MODE"] = True

app2.config["APP_NAME"] = "Application TWO"
app2.config["APP_VERSION"] = "2.0"
app2.config["DEBUG_MODE"] = True

app3.config["APP_NAME"] = "Application THREE"
app3.config["APP_VERSION"] = "3.0"
app3.config["DEBUG_MODE"] = True

# Application 1 routes

@app1.route("/")
def home():
    return "Hello from App 1!"


@app1.route("/users/<int:user_id>")
def get_user(user_id):
    return {
        "application": current_app.name,
        "user_id": user_id,
        "python_type": type(user_id).__name__
    }


@app1.route("/users/<int:user_id>/posts/<int:post_id>")
def get_user_post(user_id, post_id):
    return {
        "user_id": user_id,
        "post_id": post_id,
        "user_id_type": type(user_id).__name__,
        "post_id_type": type(post_id).__name__
    }


@app1.route("/url_finder")
def url_finder():
    url = url_for("get_user_post", user_id=50, post_id=100)
    app = current_app.name
    return {
        "URL": url,
        "current_app": app
    }





# Application 2 routes

@app2.route("/")
def app2_home():
    return "Hello from App 2!"


@app2.route("/inspect")
def incoming_inspector():
    return inspect_endpoint_resolution()


# Application 2 Life Cycle Hooks 

@app2.before_request
def before():
    if SHOW_DEBUG_OUTPUT:
        print("1. BEFORE REQUEST")


@app2.route("/hello")
def hello():
    if SHOW_DEBUG_OUTPUT:
        print("2. VIEW FUNCTION EXECUTED")
    return "Hello from App 2!"


# 3. AFTER REQUEST
@app2.after_request
def after(response):
    if SHOW_DEBUG_OUTPUT:
        print("3. AFTER REQUEST")
    return response


# 4. TEARDOWN REQUEST
@app2.teardown_request
def teardown_request(exception):
    if SHOW_DEBUG_OUTPUT:
        print("4. TEARDOWN REQUEST", flush=True)


# 5. TEARDOWN APP CONTEXT
@app2.teardown_appcontext
def teardown_app(exception):
    if SHOW_DEBUG_OUTPUT:
        print("5. TEARDOWN APP CONTEXT")

@app2.route("/error")
def fake_error():
    if SHOW_DEBUG_OUTPUT:
        print("Fake Erro Function Started")
    raise ValueError("Something went wrong!")


@app2.errorhandler(ValueError)
def handle_value_error(error):
    if SHOW_DEBUG_OUTPUT:
        print("ERROR HANDLER EXECUTED")
        print("Exception:", error)

    return "An error occurred, but Flask handled it!", 400

@app2.errorhandler(404)
def page_not_found(error):
    if SHOW_DEBUG_OUTPUT:
        print(error)
    return "404 - This route does not exist!", 404

# Application 3 routes

@app3.route("/")
def app3_home():
    return "Hello from App 3!"


@app3.route("/files/<path:filename>")
def get_file_path(filename):
    return {
        "application": "app3",
        "filename": filename,
        "python_type": type(filename).__name__
    }


# Shared routes

@app3.route("/info")
@app2.route("/info")
@app1.route("/info")
def info():
    return {
        "name": current_app.config["APP_NAME"],
        "version": current_app.config["APP_VERSION"]
    }


@app3.route("/inspect")
@app2.route("/inspect")
@app1.route("/inspect")
def inspect_app():
    return inspect_application()


@app3.route("/setup")
@app2.route("/setup")
@app1.route("/setup")
def setup():
    return inspect_application_setup()

@app3.route("/environ")
@app2.route("/environ")
@app1.route("/environ")
def environ_inspector():
    return inspect_wsgi_environ()

# Shared helper functions

def inspect_application():

    app = current_app

    view_functions = {}
    url_map = []
    endpoint_mapping = []

    for endpoint, function in app.view_functions.items():

        view_functions[endpoint] = function.__name__

    for rule in app.url_map.iter_rules():

        url_map.append({
            "url": rule.rule,
            "endpoint": rule.endpoint,
            "methods": sorted(rule.methods)
        })

    for rule in app.url_map.iter_rules():

        endpoint = rule.endpoint

        function = app.view_functions.get(endpoint)

        endpoint_mapping.append({
            "url": rule.rule,
            "endpoint": endpoint,
            "function": function.__name__ if function else None
        })

    return {
        "application": app.name,
        "url_map": url_map,

        "view_functions": view_functions,
        "endpoint_mapping": endpoint_mapping
    }

def inspect_endpoint_resolution():
    app = current_app
    endpoint = request.endpoint
    function = app.view_functions.get(endpoint)

    return {
        "incoming_request_url": request.url,
        "matched_rule": request.url_rule.rule if request.url_rule else None,
        "endpoint": endpoint,
        "incoming_arguments": request.args.to_dict(),
        "view_arguments": request.view_args,
        "function": function.__name__ if function else None,
    }

def inspect_application_setup():
    app = current_app
    configuration = {
        "APP_NAME" : app.config.get("APP_NAME"),
        "APP_VERSION": app.config.get("APP_VERSION")
    }

    return {
        "application": app.name,
        "import_name": app.import_name,
        "configuration": configuration,
        "debug": app.debug,
        "testing": app.testing,
        "registered_routes": len(list(app.url_map.iter_rules())),
        "registered_functions": len(app.view_functions)
    }

def inspect_wsgi_environ():

    environ = request.environ

    return {
        "application": current_app.name,

        "request_method": environ.get("REQUEST_METHOD"),
        "script_name": environ.get("SCRIPT_NAME"),
        "path_info": environ.get("PATH_INFO"),
        "query_string": environ.get("QUERY_STRING"),

        "server_name": environ.get("SERVER_NAME"),
        "server_port": environ.get("SERVER_PORT"),
        "server_protocol": environ.get("SERVER_PROTOCOL"),

        "content_type": environ.get("CONTENT_TYPE"),
        "content_length": environ.get("CONTENT_LENGTH"),

        "http_host": environ.get("HTTP_HOST"),
        "user_agent": environ.get("HTTP_USER_AGENT")
    }


history = RequestHistory(max_records=200)
dashboard = create_dashboard_app(history)

dispatcher = DispatcherMiddleware (app1 , {
    "/app1": app1,
    "/app2": app2,
    "/app3": app3,
    "/debug": dashboard,
})

middleware = DebuggerMiddleware(dispatcher, SHOW_DEBUG_OUTPUT, history)

if __name__ == "__main__":
    run_simple(
        hostname="127.0.0.1",       
        port=5000,                  
        application=middleware,    
        use_debugger=True,         
        use_reloader=False         
    )
