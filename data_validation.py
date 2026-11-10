import json
import zmq

def validate_required_field():
    # TO-DO: Method for required field validation
    pass

def validate_data_type():
    # TO-DO: Method for data type validation
    pass

def validate_numerical_range():
    # TO-DO: Method for numerical range validation
    pass

def process_request():
    # TO-DO: Method to check request and run all validations
    pass

def main():
    context = zmq.Context()
    socket = context.socket(zmq.REP)

    try:
        socket.bind("tcp://127.0.0.1.55001")
        print("Data Validation Service listening on port 55001")

        while True:
            message = socket.recv()

            try: 
                request = json.loads(message)
                response = process_request(request)
            except (json.JSONDecodeError, UnicodeDecodeError):
                response = {
                    "valid": False,
                    "data": None,
                    "errors": ["Request must contain valid JSON"]
                }

            socket.send_json(response)

    except KeyboardInterrupt:
        print("\nStopping Data Validation Service")
    finally:
        socket.close(linger=0)
        context.term()

if __name__ == "__main__":
    main()

