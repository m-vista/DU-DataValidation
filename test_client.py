import zmq

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://127.0.0.1:55001")


def run_test(name, request, expected):

    # Send a request
    socket.send_json(request)

    # Recieve a response
    actual = socket.recv_json()

    # Display results
    rows = []

    for field in ["valid", "data", "errors"]:
        expected_value = str(expected[field])
        actual_value = str(actual[field])
        result = "PASS" if expected[field] == actual[field] else "FAIL"
        rows.append([field, expected_value, actual_value, result])

    headers = ["Field", "Expected", "Actual", "Result"]
    widths = [
        max(len(headers[i]), max(len(row[i]) for row in rows))
        for i in range(4)
    ]

    print(f"\n{name}")

    for row in [headers] + rows:
        print(" | ".join(value.ljust(widths[i]) for i, value in enumerate(row)))

    print("Overall:", "PASS" if actual == expected else "FAIL")

# Test 1: Valid data
request = {
    "data": {"name": "Lorelei", "age": 32},
    "rules": {
        "name": {"required": True, "type": "string"},
        "age": {"required": True, "type": "number", "min": 0, "max": 120},
    },
}

expected = {
    "valid": True,
    "data": {"name": "Lorelei", "age": 32},
    "errors": [],
}

run_test("Test 1: Valid data", request, expected)


# Test 2: Missing required field and incorrect data type
request = {
    "data": {"formula": "three"},
    "rules": {
        "breastMilk": {"required": True, "type": "number", "min": 0},
        "formula": {"required": True, "type": "number", "min": 0},
    },
}

expected = {
    "valid": False,
    "data": None,
    "errors": [
        "breastMilk: missing field",
        "formula: must be a number",
    ],
}

run_test("Test 2: Missing field and incorrect type", request, expected)


# Test 3: Numbers outside allowed limits
request = {
    "data": {"price": -5, "quantity": 150},
    "rules": {
        "price": {"required": True, "type": "number", "min": 0},
        "quantity": {"required": True, "type": "number", "min": 1, "max": 100},
    },
}

expected = {
    "valid": False,
    "data": None,
    "errors": [
        "price must be at least 0",
        "quantity must be at most 100",
    ],
}

run_test("Test 3: Outside numerical limits", request, expected)

socket.close()
context.term()