from datetime import datetime
from typing import Any

from app import db
from app.models.bike_history import BikeHistory
from app.models.dispatch_task import DispatchTask
from app.models.station import Station
from app.models.user import User


class TaskService:
    OPERATOR_STATUSES = {"in_progress", "completed"}
    MUTABLE_FIELDS = {
        "task_name",
        "from_station_id",
        "to_station_id",
        "bike_count",
        "priority",
        "status",
        "assigned_to",
    }

    def list_tasks(
        self,
        current_user: User,
        page: int,
        per_page: int,
        status: str | None = None,
        priority: int | None = None,
        assigned_to: int | None = None,
    ):
        query = DispatchTask.query

        if current_user.role == "operator":
            query = query.filter(DispatchTask.assigned_to == current_user.id)
        elif current_user.role == "dispatcher":
            query = query.filter(
                (DispatchTask.created_by == current_user.id)
                | (DispatchTask.assigned_to.isnot(None))
            )

        if status:
            query = query.filter(DispatchTask.status == status)
        if priority:
            query = query.filter(DispatchTask.priority == priority)
        if assigned_to:
            query = query.filter(DispatchTask.assigned_to == assigned_to)

        return query.order_by(DispatchTask.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

    def create_task(self, current_user: User, data: dict[str, Any]) -> DispatchTask:
        if current_user.role not in {"dispatcher", "admin"}:
            raise PermissionError("权限不足")

        self._validate_station(data.get("from_station_id"), "起点站点不存在")
        self._validate_station(data.get("to_station_id"), "终点站点不存在")
        self._validate_operator(data.get("assigned_to"))

        task = DispatchTask(
            task_name=data["task_name"],
            from_station_id=data.get("from_station_id"),
            to_station_id=data.get("to_station_id"),
            bike_count=data.get("bike_count", 0),
            priority=data.get("priority", 1),
            status="pending",
            assigned_to=data.get("assigned_to"),
            created_by=current_user.id,
        )
        db.session.add(task)
        db.session.commit()
        return task

    def get_task(self, current_user: User, task_id: int) -> DispatchTask:
        task = DispatchTask.query.get_or_404(task_id)
        self._ensure_can_read(current_user, task)
        return task

    def update_task(
        self, current_user: User, task_id: int, data: dict[str, Any]
    ) -> DispatchTask:
        task = DispatchTask.query.get_or_404(task_id)

        if current_user.role == "operator":
            self._update_as_operator(task, data)
        elif current_user.role in {"dispatcher", "admin"}:
            self._update_as_manager(task, data)
        else:
            raise PermissionError("权限不足")

        db.session.commit()
        return task

    def delete_task(self, current_user: User, task_id: int) -> None:
        task = DispatchTask.query.get_or_404(task_id)
        if current_user.role not in {"admin", "dispatcher"}:
            raise PermissionError("权限不足")
        if current_user.role == "dispatcher" and task.created_by != current_user.id:
            raise PermissionError("权限不足")

        db.session.delete(task)
        db.session.commit()

    def assign_task(
        self, current_user: User, task_id: int, operator_id: int | None
    ) -> DispatchTask:
        if current_user.role not in {"dispatcher", "admin"}:
            raise PermissionError("权限不足")
        if not operator_id:
            raise ValueError("运维员ID不能为空")

        self._validate_operator(operator_id)
        task = DispatchTask.query.get_or_404(task_id)
        task.assigned_to = operator_id
        task.status = "pending"
        db.session.commit()
        return task

    def _update_as_operator(self, task: DispatchTask, data: dict[str, Any]) -> None:
        if "status" not in data or len(set(data) - {"status"}) > 0:
            raise PermissionError("运维员只能更新任务状态")

        new_status = data["status"]
        if new_status not in self.OPERATOR_STATUSES:
            raise ValueError("运维员只能将任务更新为进行中或已完成")

        old_status = task.status
        task.status = new_status
        if old_status != "completed" and new_status == "completed":
            self._record_completion_inventory(task)

    def _update_as_manager(self, task: DispatchTask, data: dict[str, Any]) -> None:
        for field in set(data) & self.MUTABLE_FIELDS:
            if field == "from_station_id":
                self._validate_station(data[field], "起点站点不存在")
            elif field == "to_station_id":
                self._validate_station(data[field], "终点站点不存在")
            elif field == "assigned_to":
                self._validate_operator(data[field])
            setattr(task, field, data[field])

    def _record_completion_inventory(self, task: DispatchTask) -> None:
        bike_count = int(task.bike_count or 0)
        if bike_count <= 0:
            return

        now = datetime.utcnow()
        if task.from_station_id:
            self._append_bike_history(task.from_station_id, -bike_count, now)
        if task.to_station_id:
            self._append_bike_history(task.to_station_id, bike_count, now)

    def _append_bike_history(self, station_id: int, delta: int, timestamp: datetime):
        latest = (
            BikeHistory.query.filter_by(station_id=station_id)
            .order_by(BikeHistory.timestamp.desc())
            .first()
        )
        available = latest.available_bikes if latest else 0
        new_available = max(0, available + delta)

        db.session.add(
            BikeHistory(
                station_id=station_id,
                timestamp=timestamp,
                available_bikes=new_available,
                available_docks=latest.available_docks if latest else 0,
                total_bikes=latest.total_bikes if latest else new_available,
                total_docks=latest.total_docks if latest else 0,
                is_station_active=latest.is_station_active if latest else True,
                last_report_time=timestamp,
            )
        )

    def _ensure_can_read(self, current_user: User, task: DispatchTask) -> None:
        if current_user.role == "operator" and task.assigned_to != current_user.id:
            raise PermissionError("权限不足")
        if (
            current_user.role == "dispatcher"
            and task.created_by != current_user.id
            and task.assigned_to is None
        ):
            raise PermissionError("权限不足")

    def _validate_station(self, station_id: int | None, message: str) -> None:
        if station_id and not Station.query.get(station_id):
            raise ValueError(message)

    def _validate_operator(self, operator_id: int | None) -> None:
        if not operator_id:
            return
        operator = User.query.get(operator_id)
        if not operator or operator.role != "operator":
            raise ValueError("指定的运维员不存在")


task_service = TaskService()
