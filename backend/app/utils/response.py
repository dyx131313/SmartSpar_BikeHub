from math import ceil
from typing import Any

from flask import jsonify


def success_response(data: Any = None, message: str | None = None, status: int = 200):
    payload: dict[str, Any] = {}
    if message is not None:
        payload["message"] = message
    if data is not None:
        payload["data"] = data
    return jsonify(payload), status


def error_response(error: str, status: int = 500):
    return jsonify({"error": error}), status


def paginated_response(items: list[Any], total: int, page: int, per_page: int):
    return jsonify(
        {
            "data": items,
            "total": total,
            "pages": ceil(total / per_page) if per_page else 1,
            "current_page": page,
            "per_page": per_page,
        }
    )
