import argparse
import os
import sys
import time
import json
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from tqdm import tqdm
from torch.utils.data import DataLoader

# Add current directory to sys.path to allow imports from models and layers
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from data_provider import DataProvider
from models import DLinear, TiDE, TimesNet


class Config:
    def __init__(self, args):
        self.task_name = "long_term_forecast"
        self.seq_len = args.seq_len
        self.label_len = args.seq_len // 2  # Usually label_len is part of seq_len
        self.pred_len = args.pred_len
        self.enc_in = args.enc_in
        self.dec_in = args.enc_in
        self.c_out = args.c_out
        self.d_model = args.d_model
        self.d_ff = args.d_ff
        self.e_layers = args.e_layers
        self.d_layers = args.d_layers
        self.dropout = args.dropout
        self.embed = "timeF"
        self.freq = "h"
        self.num_kernels = 6
        self.top_k = 5
        self.moving_avg = 25


def train(args):
    # 1. Data Preparation
    print("Loading data...")
    data_provider = DataProvider(
        json_path=args.data_path, seq_len=args.seq_len, pred_len=args.pred_len
    )

    train_dataset = data_provider.get_dataset("train")
    test_dataset = data_provider.get_dataset("test")

    train_loader = DataLoader(
        train_dataset, batch_size=args.batch_size, shuffle=True, drop_last=True
    )
    test_loader = DataLoader(
        test_dataset, batch_size=args.batch_size, shuffle=False, drop_last=False
    )

    print(f"Train samples: {len(train_dataset)}, Test samples: {len(test_dataset)}")

    # 2. Model Initialization
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    configs = Config(args)

    if args.model == "DLinear":
        model = DLinear.Model(configs).to(device)
    elif args.model == "TiDE":
        model = TiDE.Model(configs).to(device)
    elif args.model == "TimesNet":
        model = TimesNet.Model(configs).to(device)
    else:
        raise ValueError(f"Unknown model: {args.model}")

    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=args.learning_rate)

    # 3. Training Loop
    print("Starting training...")
    best_loss = float("inf")

    for epoch in range(args.epochs):
        model.train()
        train_loss = []

        progress_bar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{args.epochs}")

        for batch_x, batch_y in progress_bar:
            batch_x = batch_x.to(device)
            batch_y = batch_y.to(device)

            optimizer.zero_grad()

            # Model forward

            # Construct dummy marks
            B, L, C = batch_x.shape
            x_mark_enc = torch.zeros(B, L, 4).to(device)  # 4 time features usually
            x_dec = torch.zeros(B, args.pred_len, C).to(device)
            x_mark_dec = torch.zeros(B, args.pred_len, 4).to(device)

            if args.model == "DLinear":
                outputs = model(batch_x, x_mark_enc, x_dec, x_mark_dec)
            elif args.model == "TiDE":
                # TiDE expects batch_y_mark
                outputs = model(batch_x, x_mark_enc, x_dec, x_mark_dec)
            elif args.model == "TimesNet":
                outputs = model(batch_x, x_mark_enc, x_dec, x_mark_dec)

            # Outputs shape: [B, Pred_Len, C]

            loss = criterion(outputs, batch_y)
            train_loss.append(loss.item())

            loss.backward()
            optimizer.step()

            progress_bar.set_postfix({"loss": loss.item()})

        avg_train_loss = np.mean(train_loss)

        # Validation
        model.eval()
        test_loss = []
        with torch.no_grad():
            for batch_x, batch_y in test_loader:
                batch_x = batch_x.to(device)
                batch_y = batch_y.to(device)

                B, L, C = batch_x.shape
                x_mark_enc = torch.zeros(B, L, 4).to(device)
                x_dec = torch.zeros(B, args.pred_len, C).to(device)
                x_mark_dec = torch.zeros(B, args.pred_len, 4).to(device)

                outputs = model(batch_x, x_mark_enc, x_dec, x_mark_dec)
                loss = criterion(outputs, batch_y)
                test_loss.append(loss.item())

        avg_test_loss = np.mean(test_loss)
        print(
            f"Epoch {epoch+1}: Train Loss: {avg_train_loss:.4f}, Test Loss: {avg_test_loss:.4f}"
        )

        if avg_test_loss < best_loss:
            best_loss = avg_test_loss
            # Save model
            save_path = os.path.join(args.save_dir, f"{args.model}_best.pth")
            torch.save(model.state_dict(), save_path)
            print(f"Saved best model to {save_path}")

    # 4. Future Prediction
    print("Generating future predictions...")
    model.load_state_dict(
        torch.load(os.path.join(args.save_dir, f"{args.model}_best.pth"))
    )
    model.eval()

    last_windows = data_provider.get_last_window()
    future_predictions = []

    with torch.no_grad():
        for station_id, window_info in last_windows.items():
            window = window_info["data"]
            last_timestamp = window_info["last_timestamp"]

            # window: [Seq_Len, C]
            x = torch.FloatTensor(window).unsqueeze(0).to(device)  # [1, Seq_Len, C]

            B, L, C = x.shape
            x_mark_enc = torch.zeros(B, L, 4).to(device)
            x_dec = torch.zeros(B, args.pred_len, C).to(device)
            x_mark_dec = torch.zeros(B, args.pred_len, 4).to(device)

            outputs = model(x, x_mark_enc, x_dec, x_mark_dec)
            # outputs: [1, Pred_Len, C]

            # Inverse transform demand (index 0)
            pred_demand = outputs[0, :, 0].cpu().numpy()

            real_demand = data_provider.inverse_transform(pred_demand)

            # Round to integer
            real_demand = np.round(real_demand).astype(int)

            # Generate timestamps
            future_timestamps = data_provider.generate_future_timestamps(
                last_timestamp, args.pred_len
            )

            # Format output
            station_preds = []
            for t, d in zip(future_timestamps, real_demand):
                station_preds.append({"timestamp": t, "demand": int(d)})

            future_predictions.append(
                {"station_id": int(station_id), "predictions": station_preds}
            )

    # 5. Save Results
    # Save hyperparameters
    params = vars(args)
    with open(os.path.join(args.save_dir, f"{args.model}_params.json"), "w") as f:
        json.dump(params, f, indent=4)

    # Save predictions
    with open(os.path.join(args.save_dir, f"{args.model}_future.json"), "w") as f:
        json.dump(future_predictions, f, indent=4)

    print("Training and prediction completed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Time Series Forecasting Training")

    # Model selection
    parser.add_argument(
        "--model",
        type=str,
        required=True,
        default="DLinear",
        help="Model name: DLinear, TiDE, TimesNet",
    )

    # Data paths
    parser.add_argument(
        "--data_path",
        type=str,
        default="../../../data/api_demands.json",
        help="Path to data json",
    )
    parser.add_argument(
        "--save_dir",
        type=str,
        default="./checkpoints",
        help="Directory to save model and results",
    )

    # Hyperparameters
    parser.add_argument("--seq_len", type=int, default=96, help="Input sequence length")
    parser.add_argument(
        "--pred_len", type=int, default=24, help="Prediction sequence length"
    )
    parser.add_argument("--enc_in", type=int, default=6, help="Input feature dimension")
    parser.add_argument("--c_out", type=int, default=6, help="Output feature dimension")
    parser.add_argument("--d_model", type=int, default=64, help="Model dimension")
    parser.add_argument("--d_ff", type=int, default=128, help="FFN dimension")
    parser.add_argument("--e_layers", type=int, default=2, help="Num of encoder layers")
    parser.add_argument("--d_layers", type=int, default=1, help="Num of decoder layers")
    parser.add_argument("--dropout", type=float, default=0.1, help="Dropout")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size")
    parser.add_argument("--epochs", type=int, default=10, help="Train epochs")
    parser.add_argument(
        "--learning_rate", type=float, default=0.001, help="Learning rate"
    )

    args = parser.parse_args()

    if not os.path.exists(args.save_dir):
        os.makedirs(args.save_dir)

    train(args)
