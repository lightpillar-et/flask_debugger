from flask import Flask 
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

@app2.route("/")
def home ():
    return "Hello From Application TWO"
@app2.route("/info")
def info ():
    return {
        "name" : app2.config["APP_NAME"], 
        "version" : app2.config["APP_VERSION"]
    }

@app3.route("/")
def app3_home():
    return "Welcome to Application Three"

@app3.route("/info")
def info ():
    return {
        "name" : app3.config["APP_NAME"], 
    "version" : app3.config["APP_VERSION"]
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


