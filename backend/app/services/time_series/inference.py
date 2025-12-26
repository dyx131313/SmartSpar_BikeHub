import torch
import json
import os
import sys
import numpy as np
from types import SimpleNamespace

# Add current directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from models import DLinear, TiDE, TimesNet


class TimeSeriesInference:
    def __init__(self, model_name, checkpoint_dir="./checkpoints"):
        self.model_name = model_name
        self.checkpoint_dir = checkpoint_dir
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.load_model()

    def load_model(self):
        # Load params
        params_path = os.path.join(
            self.checkpoint_dir, f"{self.model_name}_params.json"
        )
        if not os.path.exists(params_path):
            raise FileNotFoundError(f"Params file not found: {params_path}")

        with open(params_path, "r") as f:
            self.params = json.load(f)

        # Convert dict to object for config
        self.configs = SimpleNamespace(**self.params)
        # Ensure Config class structure matches what models expect
        self.configs.task_name = "long_term_forecast"
        self.configs.label_len = self.configs.seq_len // 2
        self.configs.embed = "timeF"
        self.configs.freq = "h"
        self.configs.num_kernels = 6
        self.configs.top_k = 5
        self.configs.moving_avg = 25

        # Initialize model
        if self.model_name == "DLinear":
            self.model = DLinear.Model(self.configs).to(self.device)
        elif self.model_name == "TiDE":
            self.model = TiDE.Model(self.configs).to(self.device)
        elif self.model_name == "TimesNet":
            self.model = TimesNet.Model(self.configs).to(self.device)
        else:
            raise ValueError(f"Unknown model: {self.model_name}")

        # Load weights
        weights_path = os.path.join(self.checkpoint_dir, f"{self.model_name}_best.pth")
        self.model.load_state_dict(torch.load(weights_path, map_location=self.device))
        self.model.eval()

    def predict(self, input_data):
        """
        input_data: numpy array of shape [Batch, Seq_Len, Channels]
        Returns: numpy array of shape [Batch, Pred_Len, Channels]
        """
        with torch.no_grad():
            x = torch.FloatTensor(input_data).to(self.device)

            B, L, C = x.shape
            x_mark_enc = torch.zeros(B, L, 4).to(self.device)
            x_dec = torch.zeros(B, self.configs.pred_len, C).to(self.device)
            x_mark_dec = torch.zeros(B, self.configs.pred_len, 4).to(self.device)

            outputs = self.model(x, x_mark_enc, x_dec, x_mark_dec)
            return outputs.cpu().numpy()

    def get_hyperparameters(self):
        return self.params
