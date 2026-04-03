from flask import jsonify


def error_response(message, status_code, **kwargs):
    return jsonify({"error": message, **kwargs}), status_code
