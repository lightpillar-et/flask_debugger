from werkzeug.test import Client
from app import middleware

# Create test client
client = Client(middleware)


# ========== TEST 1: DISPATCHER ROUTING ==========

test_cases = [
    ("/app1/", "Hello from App 1!"),
    ("/app2/", "Hello from App 2!"),
    ("/app3/", "Hello from App 3!")
]

for path, expected in test_cases:

    response = client.get(path)
    actual = response.get_data(as_text=True)

    assert response.status_code == 200
    assert actual == expected

    print(f"PASSED: Dispatcher routing {path}")


# ========== TEST 2: MIDDLEWARE INSPECTION ==========

response = client.get("/app2/")

assert response.status_code == 200

print("PASSED: Middleware request completed")


# ========== TEST 3: CUSTOM RESPONSE HEADER ==========

response = client.get("/app1/")

assert response.headers.get("Custom-Header") == "Custom Header By Inspecting"

print("PASSED: Custom response header")


# ========== TEST 4: CUSTOM 404 HANDLER ==========

response = client.get("/app2/unknown")

assert response.status_code == 404
assert response.get_data(as_text=True) == "404 - This route does not exist!"

print("PASSED: Custom 404 error handler")


print("\n========== ALL TESTS PASSED ==========")