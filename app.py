from flask import Flask  , url_for , current_app , request
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple


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


@app1.route("/")
def home ():
    return "Hello From Application One"
@app1.route("/info")
def info ():
    return {
        "name": app1.config["APP_NAME"],
        "version": app1.config["APP_VERSION"]
    }
@app1.route("/inspect")
def inspect_app1():
    return inspect_application()


# ---------- Dynamic Routing Experiment ----------

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
    url = url_for("get_user_post" , user_id =50 , post_id =100)
    app = current_app.name
    return {
        "URL" : url, 
        "current_app" : app
    }


@app2.route("/")
def home ():
    return "Hello From Application TWO"

@app2.route("/info")
def info ():
    return {
        "name" : app2.config["APP_NAME"], 
        "version" : app2.config["APP_VERSION"]
    }
@app2.route("/inspect")
def incoming_inspector():
    return inspect_endpoint_resolution()


@app2.route("/application-inspect")
def inspect_app2 ():
    return inspect_application()

@app3.route("/")
def app3_home():
    return "Welcome to Application Three"

@app3.route("/info")
def info ():
    return {
        "name" : app3.config["APP_NAME"], 
        "version" : app3.config["APP_VERSION"]
    }
@app3.route("/inspect")
def inspect_app3():
    return inspect_application()

@app3.route("/files/<path:filename>")
def get_file_path(filename):
    return {
        "application": "app3",
        "filename": filename,
        "python_type": type(filename).__name__
    }

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
        "APP_NAME" : app.conifg.get["APP_NAME"],
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


wsgi_application = DispatcherMiddleware (app1 , {
    "/app1": app1,
    "/app2": app2,
    "/app3": app3,
})

if __name__ == "__main__":
    run_simple(
        hostname="127.0.0.1",       
        port=5000,                  
        application=wsgi_application,    
        use_debugger=True,         
        use_reloader=True          
    )

