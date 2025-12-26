"""Run a single prediction cycle now for the DLinear model."""
import sys, os
from datetime import datetime

# Ensure project root in sys.path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.services.scheduler import scheduler

if __name__ == "__main__":
    print("Running prediction cycle (DLinear) at", datetime.utcnow().isoformat())
    try:
        scheduler.run_prediction_cycle(datetime.utcnow(), model_name='DLinear')
        print("Prediction cycle completed.")
    except Exception as e:
        print("Prediction cycle failed:", e)
        raise
