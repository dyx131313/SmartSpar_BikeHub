from dataclasses import dataclass
from pathlib import Path

from app.config.paths import Paths


@dataclass(frozen=True)
class PredictionModelSpec:
    name: str
    display_name: str
    family: str = "time_series"

    @property
    def params_path(self) -> Path:
        return Paths.model_file(self.name, "params.json")

    @property
    def future_path(self) -> Path:
        return Paths.model_file(self.name, "future.json")


class PredictionModelRegistry:
    def __init__(self, specs: list[PredictionModelSpec] | None = None):
        specs = specs or [
            PredictionModelSpec("DLinear", "DLinear"),
            PredictionModelSpec("TiDE", "TiDE"),
            PredictionModelSpec("TimesNet", "TimesNet"),
        ]
        self._models = {spec.name: spec for spec in specs}

    def all(self) -> list[PredictionModelSpec]:
        return list(self._models.values())

    def names(self) -> list[str]:
        return list(self._models)

    def get(self, model_name: str) -> PredictionModelSpec | None:
        return self._models.get(model_name)

    def require(self, model_name: str) -> PredictionModelSpec:
        spec = self.get(model_name)
        if not spec:
            supported = ", ".join(self.names())
            raise ValueError(f"Unsupported prediction model: {model_name}. Supported: {supported}")
        return spec


prediction_model_registry = PredictionModelRegistry()
