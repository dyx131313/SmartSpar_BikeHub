from flask import request

from app.routes import api_bp
from app.services.task_service import task_service
from app.utils.decorators import require_any_authenticated, with_error_handler
from app.utils.response import paginated_response, success_response


@api_bp.route("/dispatch-tasks", methods=["GET"])
@with_error_handler
@require_any_authenticated
def get_dispatch_tasks(current_user):
    """获取调度任务列表"""
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 20, type=int), 100)
    pagination = task_service.list_tasks(
        current_user=current_user,
        page=page,
        per_page=per_page,
        status=request.args.get("status"),
        priority=request.args.get("priority", type=int),
        assigned_to=request.args.get("assigned_to", type=int),
    )
    return paginated_response(
        [task.to_dict() for task in pagination.items],
        pagination.total,
        page,
        per_page,
    )


@api_bp.route("/dispatch-tasks", methods=["POST"])
@with_error_handler
@require_any_authenticated
def create_dispatch_task(current_user):
    """创建调度任务"""
    task = task_service.create_task(current_user, request.get_json() or {})
    return success_response(task.to_dict(), "调度任务创建成功", 201)


@api_bp.route("/dispatch-tasks/<int:id>", methods=["GET"])
@with_error_handler
@require_any_authenticated
def get_dispatch_task(current_user, id):
    """获取单个调度任务"""
    task = task_service.get_task(current_user, id)
    return success_response(task.to_dict())


@api_bp.route("/dispatch-tasks/<int:id>", methods=["PUT"])
@with_error_handler
@require_any_authenticated
def update_dispatch_task(current_user, id):
    """更新调度任务"""
    task = task_service.update_task(current_user, id, request.get_json() or {})
    return success_response(task.to_dict(), "调度任务更新成功")


@api_bp.route("/dispatch-tasks/<int:id>", methods=["DELETE"])
@with_error_handler
@require_any_authenticated
def delete_dispatch_task(current_user, id):
    """删除调度任务"""
    task_service.delete_task(current_user, id)
    return success_response(message="调度任务删除成功")


@api_bp.route("/dispatch-tasks/<int:id>/assign", methods=["POST"])
@with_error_handler
@require_any_authenticated
def assign_dispatch_task(current_user, id):
    """分配调度任务"""
    data = request.get_json() or {}
    task = task_service.assign_task(current_user, id, data.get("operator_id"))
    return success_response(task.to_dict(), "任务分配成功")
