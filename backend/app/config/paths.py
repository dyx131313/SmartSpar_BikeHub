from pathlib import Path


APP_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = APP_DIR.parent
PROJECT_DIR = BACKEND_DIR.parent


class Paths:
    MODEL_CHECKPOINTS = APP_DIR / "services" / "time_series" / "checkpoints"
    MODEL_DIR = APP_DIR / "services" / "models"
    STATIC_DIR = APP_DIR / "static"
    UPLOADS_DIR = STATIC_DIR / "uploads"
    AVATARS_DIR = UPLOADS_DIR / "avatars"
    DATA_DIR = BACKEND_DIR / "data"
    DATABASE_DIR = BACKEND_DIR / "database"

    @classmethod
    def model_file(cls, model_name: str, suffix: str) -> Path:
        return cls.MODEL_CHECKPOINTS / f"{model_name}_{suffix}"

    @classmethod
    def ensure_dir(cls, path: Path) -> Path:
        path.mkdir(parents=True, exist_ok=True)
        return path
