import pytest
from flask_jwt_extended import create_access_token

from app import create_app, db
from app.config.paths import Paths
from app.models.user import User
from app.services.prediction_registry import PredictionModelRegistry, PredictionModelSpec
from app.utils.decorators import require_admin, require_dispatcher_or_admin, with_error_handler
from app.utils.response import error_response, paginated_response, success_response


@pytest.fixture()
def app():
    return create_app("testing")


def test_response_helpers_return_stable_shapes(app):
    with app.app_context():
        response, status = success_response({"id": 1}, "ok", 201)
        assert status == 201
        assert response.get_json() == {"message": "ok", "data": {"id": 1}}

        response, status = error_response("bad request", 400)
        assert status == 400
        assert response.get_json() == {"error": "bad request"}

        response = paginated_response([{"id": 1}], total=11, page=2, per_page=5)
        assert response.get_json() == {
            "data": [{"id": 1}],
            "total": 11,
            "pages": 3,
            "current_page": 2,
            "per_page": 5,
        }


def test_error_handler_maps_common_exceptions(app):
    @with_error_handler
    def bad_value():
        raise ValueError("invalid field")

    @with_error_handler
    def forbidden():
        raise PermissionError("no access")

    with app.app_context():
        response, status = bad_value()
        assert status == 400
        assert response.get_json()["error"] == "invalid field"

        response, status = forbidden()
        assert status == 403
        assert response.get_json()["error"] == "no access"


def test_role_decorators_allow_and_reject_by_role(app):
    with app.app_context():
        admin = User(
            username="refactor_admin",
            email="refactor_admin@example.com",
            role="admin",
            is_active=True,
        )
        admin.set_password("admin123")
        operator = User(
            username="refactor_operator",
            email="refactor_operator@example.com",
            role="operator",
            is_active=True,
        )
        operator.set_password("operator123")
        db.session.add_all([admin, operator])
        db.session.commit()

        admin_token = create_access_token(identity=str(admin.id))
        operator_token = create_access_token(identity=str(operator.id))

        @require_admin
        def admin_only(current_user):
            return {"username": current_user.username}

        @require_dispatcher_or_admin
        def dispatcher_or_admin(current_user):
            return {"role": current_user.role}

        with app.test_request_context(headers={"Authorization": f"Bearer {admin_token}"}):
            assert admin_only()["username"] == "refactor_admin"
            assert dispatcher_or_admin()["role"] == "admin"

        with app.test_request_context(headers={"Authorization": f"Bearer {operator_token}"}):
            response, status = admin_only()
            assert status == 403
            assert response.get_json()["error"] == "权限不足"


def test_path_config_builds_predictable_locations(tmp_path):
    assert Paths.model_file("DLinear", "future.json").name == "DLinear_future.json"
    assert Paths.model_file("TimesNet", "params.json").parent == Paths.MODEL_CHECKPOINTS

    created = Paths.ensure_dir(tmp_path / "uploads" / "avatars")
    assert created.exists()
    assert created.is_dir()


def test_prediction_model_registry_centralizes_supported_models():
    registry = PredictionModelRegistry(
        [
            PredictionModelSpec("DLinear", "DLinear"),
            PredictionModelSpec("TiDE", "TiDE"),
        ]
    )

    assert registry.names() == ["DLinear", "TiDE"]
    assert registry.require("DLinear").future_path.name == "DLinear_future.json"

    with pytest.raises(ValueError, match="Unsupported prediction model"):
        registry.require("UnknownModel")
