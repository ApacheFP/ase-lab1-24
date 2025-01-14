from flask import Flask, request, make_response, jsonify
import json
import sys
from random import uniform
from functools import reduce

app = Flask(__name__, instance_relative_config=True)

# FILE to track last successful operation (use as a lightweight datastore)
LAST_OPERATION_FILE = "last_operation.json"


def save_last_operation(operation, arguments, result):
    """Saves the last successful operation to a file."""
    data = {
        "operation": operation,
        "arguments": arguments,
        "result": result
    }
    with open(LAST_OPERATION_FILE, "w") as f:
        json.dump(data, f)


def get_last_operation():
    """Retrieves the last successful operation from the file."""
    try:
        with open(LAST_OPERATION_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


@app.route('/add')
def add():
    a = request.args.get('a', type=float)
    b = request.args.get('b', type=float)
    if a is not None and b is not None:
        result = a + b
        save_last_operation("add", f"({a}, {b})", result)
        return make_response(jsonify(s=result), 200)
    else:
        return make_response('Invalid input\n', 400)


@app.route('/mul')
def multiply():
    a = request.args.get('a', type=float)
    b = request.args.get('b', type=float)
    if a is not None and b is not None:
        result = a * b
        save_last_operation("mul", f"({a}, {b})", result)
        return make_response(jsonify(s=result), 200)
    else:
        return make_response('Invalid input\n', 400)


@app.route('/div')
def divide():
    a = request.args.get('a', type=float)
    b = request.args.get('b', type=float)
    if a is not None and b is not None:
        if b == 0:
            return make_response('Division by zero\n', 400)
        result = a / b
        save_last_operation("div", f"({a}, {b})", result)
        return make_response(jsonify(s=result), 200)
    else:
        return make_response('Invalid input\n', 400)


@app.route('/mod')
def mod():
    a = request.args.get('a', type=float)
    b = request.args.get('b', type=float)
    if a is not None and b is not None:
        if b == 0:
            return make_response('Division by zero\n', 400)
        result = a % b
        save_last_operation("mod", f"({a}, {b})", result)
        return make_response(jsonify(s=result), 200)
    else:
        return make_response('Invalid input\n', 400)


@app.route('/random')
def random_number():
    a = request.args.get('a', type=float)
    b = request.args.get('b', type=float)
    if a is not None and b is not None:
        if a > b:
            return make_response('Invalid input: a cannot be greater than b\n', 400)
        result = uniform(a, b)
        save_last_operation("random", f"({a}, {b})", result)
        return make_response(jsonify(s=result), 200)
    else:
        return make_response('Invalid input\n', 400)


@app.route('/upper')
def upper():
    a = request.args.get('a', default="", type=str)  # Uses "string" as the query parameter
    if not a:
        return make_response('Invalid input: Query parameter "string" is required\n', 400)  # Corrected message
    result = a.upper()
    save_last_operation("upper", f"({a})", result)  # Save operation detail
    return make_response(jsonify({"result": result}), 200)  # JSON response with "result" key


@app.route('/lower')
def lower():
    a = request.args.get('a', default="", type=str)  # Uses "string" as the query parameter
    if not a:
        return make_response('Invalid input: Query parameter "string" is required\n', 400)  # Corrected message
    result = a.lower()
    save_last_operation("lower", f"({a})", result)  # Save operation detail
    return make_response(jsonify({"result": result}), 200)  # JSON response with "result" key



@app.route('/concat')
def concat():
    a = request.args.get('a', type=str)
    b = request.args.get('b', type=str)
    if a is not None and b is not None:
        result = a + b
        save_last_operation("concat", f"({a}, {b})", result)
        return make_response(jsonify(s=result), 200)
    else:
        return make_response('Invalid input\n', 400)


@app.route('/reduce')
def reduce_operation():
    op = request.args.get("op", type=str)
    lst = request.args.get("lst", type=str)
    if op not in ["add", "sub", "mul", "div", "concat"]:
        return make_response('Invalid operator\n', 400)

    try:
        lst = json.loads(lst)  # Parse JSON list
        if not isinstance(lst, list) or len(lst) == 0:
            return make_response('Invalid list input\n', 400)
    except json.JSONDecodeError:
        return make_response('Invalid list input\n', 400)

    # Define operator functions
    operations = {
        "add": lambda x, y: x + y,
        "sub": lambda x, y: x - y,
        "mul": lambda x, y: x * y,
        "div": lambda x, y: x / y if y != 0 else float('inf'),
        "concat": lambda x, y: str(x) + str(y),
    }

    try:
        result = reduce(operations[op], lst)
        save_last_operation("reduce", f"({op}, {lst})", result)
        return make_response(jsonify(s=result), 200)
    except Exception as e:
        return make_response(f"Error during reduce operation: {str(e)}\n", 400)


@app.route('/crash')
def crash():
    result = jsonify({"message": "Service is crashing now", "host": request.host})
    save_last_operation("crash", f"(host={request.host})", "crash")
    sys.exit(0)  # Terminates the application
    return result  # (Unreachable)


@app.route('/last')
def last():
    last_operation = get_last_operation()
    if last_operation:
        operation = last_operation["operation"]
        arguments = last_operation["arguments"]
        result = last_operation["result"]
        return make_response(f"{operation}{arguments}={result}", 200)
    else:
        return make_response("No operation performed\n", 404)


if __name__ == '__main__':
    app.run(debug=True)
