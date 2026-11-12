import json
import zmq

def validate_required_field(data, rules):
    errors = []

    for field, field_rules in rules.items():
        # required is False if no required key in field's rules
        required = field_rules.get("required", False)

        if not isinstance(required, bool):
            errors.append(f"{field}: required must be a Boolean")
            continue

        if not required:
            continue

        value = data.get(field)

        if value is None or (isinstance(value, str) and not value.strip()):
            errors.append(f"{field}: missing field")

    return errors


def validate_data_type(data, rules):
    errors = []

    for field, field_rules in rules.items():
        expected_type = field_rules.get("type")

        if expected_type is None:
            continue

        value = data.get(field)

        # Missing values are handled by required-field validation
        if value is None:
            continue

        if expected_type == "string":
            if not isinstance(value, str):
                errors.append(f"{field}: must be a string")

        elif expected_type == "number":
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                errors.append(f"{field}: must be a number")

    return errors



def validate_numerical_range(data, rules):
    errors = []

    for field, field_rules in rules.items():
        minimum = field_rules.get("min")
        maximum = field_rules.get("max")

        # Skip fields without numerical range rules
        if minimum is None and maximum is None:
            continue

        # Check that range limits are valid numbers
        if minimum is not None:
            if isinstance(minimum, bool) or not isinstance(minimum, (int, float)):
                errors.append(f"{field}: min must be a number")
                continue

        if maximum is not None:
            if isinstance(maximum, bool) or not isinstance(maximum, (int, float)):
                errors.append(f"{field}: max must be a number")
                continue

        value = data.get(field)

        # Missing values are handled by required-field validation
        if value is None:
            continue

        # Incorrect data types are handled by type validation
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue

        if minimum is not None and value < minimum:
            errors.append(f"{field} must be at least {minimum}")

        if maximum is not None and value > maximum:
            errors.append(f"{field} must be at most {maximum}")

    return errors


def process_request(request):

    # Check that the request is a dictionary
    if not isinstance(request, dict):
        return {
            "valid": False,
            "data": None,
            "errors": ["Request must be a JSON object"],
        }

    data = request.get("data")
    rules = request.get("rules")

    # check that data and rules are dictionaries
    if not isinstance(data, dict) or not isinstance(rules, dict):
        return {
            "valid": False,
            "data": None,
            "errors": ["data and rules must be JSON objects"],
        }

    # check that rules for each field is a dictionary
    for field, field_rules in rules.items():
        if not isinstance(field_rules, dict):
            return {
                "valid": False,
                "data": None,
                "errors": ["Rules for {field} must be a JSON object"],
            }

    # Validate
    errors = validate_required_field(data, rules)
    errors.extend(validate_data_type(data, rules))
    errors.extend(validate_numerical_range(data, rules))

    return {
        "valid": not errors,
        "data": data if not errors else None,
        "errors": errors
    }    

def main():
    context = zmq.Context()
    socket = context.socket(zmq.REP)

    try:
        socket.bind("tcp://127.0.0.1:55001")
        print("Data Validation Service listening on port 55001")

        while True:
            message = socket.recv()
            print("Received: validation request")

            try: 
                request = json.loads(message)
                response = process_request(request)
                print(f"Processed: valid={response['valid']}, errors={len(response['errors'])}")
            except (json.JSONDecodeError, UnicodeDecodeError):
                response = {
                    "valid": False,
                    "data": None,
                    "errors": ["Request must contain valid JSON"]
                }

            socket.send_json(response)
            print("Sent: validation response")

    except KeyboardInterrupt:
        print("\nStopping Data Validation Service")
    finally:
        socket.close(linger=0)
        context.term()

if __name__ == "__main__":
    main()

