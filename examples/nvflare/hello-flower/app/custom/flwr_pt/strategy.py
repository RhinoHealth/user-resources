import flwr as fl
from flwr.server.client_proxy import ClientProxy
from flwr.common import FitRes, Parameters, Scalar
import torch
import numpy as np
from pathlib import Path
from typing import Optional, Union
from collections import OrderedDict
from .task import Net, DEVICE


class SaveModelStrategy(fl.server.strategy.FedAvg):

    def aggregate_fit(
        self,
        server_round: int,
        results: list[tuple[ClientProxy, FitRes]],
        failures: list[Union[tuple[ClientProxy, FitRes], BaseException]],
    ) -> tuple[Optional[Parameters], dict[str, Scalar]]:
        """Aggregate model weights using weighted average and store checkpoint"""

        net = Net().to(DEVICE)

        # Call aggregate_fit from base class (FedAvg) to aggregate parameters and metrics
        aggregated_parameters, aggregated_metrics = super().aggregate_fit(
            server_round, results, failures
        )


        save_dir = Path( "/output/model_parameters/")
        save_dir.mkdir(parents=True, exist_ok=True)  # Ensure directory exists

        if aggregated_parameters is not None:
            print(f"Saving round {server_round} aggregated_parameters...")

            # Convert `Parameters` to `list[np.ndarray]`
            aggregated_ndarrays: list[np.ndarray] = fl.common.parameters_to_ndarrays(
                aggregated_parameters
            )

            # Convert `list[np.ndarray]` to PyTorch `state_dict`
            params_dict = zip(net.state_dict().keys(), aggregated_ndarrays)
            state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
            net.load_state_dict(state_dict, strict=True)

            # Save per-round checkpoint
            round_path = save_dir / f"model_round_{server_round}.pth"
            torch.save(net.state_dict(), round_path)
            print(f"Saved round {server_round} aggregated_parameters to {round_path}.")

        return aggregated_parameters, aggregated_metrics
