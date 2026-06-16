import json
from datetime import datetime

from sqlalchemy import and_, func

from app import db
from app.config.paths import Paths
from app.models.bike_history import BikeHistory
from app.models.demand_data import DemandData
from app.models.station import Station
from app.services.time_service import time_service


class DashboardService:
    def get_station_overview(self, model_name: str = "DLinear") -> list[dict]:
        system_time = time_service.get_current_time()
        stations = Station.query.all()
        bikes_map = self._latest_bikes(system_time)
        prediction_map = self._future_prediction_map(model_name, system_time)
        real_demand_map = self._latest_demands(system_time)

        result = []
        for station in stations:
            station_data = station.to_dict()
            station_data["current_bikes"] = bikes_map.get(station.id, 0)
            station_data["predicted_demand"] = prediction_map.get(station.id, 0)
            station_data["real_demand"] = real_demand_map.get(station.id, 0)
            result.append(station_data)
        return result

    def _latest_bikes(self, system_time: datetime) -> dict[int, int]:
        subquery = (
            db.session.query(
                BikeHistory.station_id, func.max(BikeHistory.timestamp).label("max_ts")
            )
            .filter(BikeHistory.timestamp <= system_time)
            .group_by(BikeHistory.station_id)
            .subquery()
        )
        records = (
            db.session.query(BikeHistory)
            .join(
                subquery,
                and_(
                    BikeHistory.station_id == subquery.c.station_id,
                    BikeHistory.timestamp == subquery.c.max_ts,
                ),
            )
            .all()
        )
        return {record.station_id: record.available_bikes for record in records}

    def _latest_demands(self, system_time: datetime) -> dict[int, int]:
        subquery = (
            db.session.query(
                DemandData.station_id, func.max(DemandData.timestamp).label("max_ts")
            )
            .filter(DemandData.timestamp <= system_time)
            .group_by(DemandData.station_id)
            .subquery()
        )
        records = (
            db.session.query(DemandData)
            .join(
                subquery,
                and_(
                    DemandData.station_id == subquery.c.station_id,
                    DemandData.timestamp == subquery.c.max_ts,
                ),
            )
            .all()
        )
        return {record.station_id: record.demand for record in records}

    def _future_prediction_map(
        self, model_name: str, system_time: datetime
    ) -> dict[int, int]:
        path = Paths.model_file(model_name, "future.json")
        if not path.exists():
            return {}

        with path.open("r", encoding="utf-8") as file:
            raw_data = json.load(file)

        prediction_map: dict[int, int] = {}
        for item in raw_data:
            future_predictions = []
            archived_predictions = []
            for prediction in item.get("predictions", []):
                timestamp = prediction.get("timestamp", "").removesuffix("Z")
                prediction_time = datetime.fromisoformat(timestamp)
                demand = int(prediction.get("demand", 0))
                archived_predictions.append((prediction_time, demand))
                if prediction_time > system_time:
                    future_predictions.append((prediction_time, demand))

            if future_predictions:
                future_predictions.sort(key=lambda row: row[0])
                prediction_map[int(item["station_id"])] = future_predictions[0][1]
            elif archived_predictions:
                archived_predictions.sort(key=lambda row: row[0], reverse=True)
                prediction_map[int(item["station_id"])] = archived_predictions[0][1]
        return prediction_map


dashboard_service = DashboardService()
