from nvflare import FedJob
from nvflare.app_common.workflows.fedavg import FedAvg
from nvflare.app_opt.pt.file_model_persistor import PTFileModelPersistor
from nvflare.job_config.script_runner import ScriptRunner
from pathlib import Path
import os
import sys
from deepchem_simulation_train import ClassificationModel
from config import *

## First configure all of the simulation components, orchestrators, and executors
# Job configuration
job_name = "NVFlare_DeepChem_Simulation"

# Configure the FedAvg controller
num_clients = 3
num_rounds = 30

# Configure model persistor
# This is where the global model weights will be saved to disk at the end of each round
persistor_global_file_name = Path(f"{Path.cwd()}/../saved_models/local_simulation.pt")
# Ensure the output directory exists
persistor_global_file_name.parent.mkdir(parents=True, exist_ok=True)
# This is the initial architecture the persistor will use to store weights
model_object = ClassificationModel()
# Configure the script runner (client executor)
script_location = "deepchem_simulation_train.py"

## Next create the job and add the components to the server
# Create the federated job
job = FedJob(
    name=job_name
)

# Create the FedAvg controller
controller = FedAvg(
    num_clients=num_clients,
    num_rounds=num_rounds
)

# Add controller to the server
job.to_server(controller)

# Create the persistor
persistor = PTFileModelPersistor(
    model=model_object,
    global_model_file_name=str(persistor_global_file_name),
    allow_numpy_conversion=False
)

# Add persistor to the server
job.to_server(persistor, id="persistor")

## Finally add the script executor to the clients
# Create the script executor
runner = ScriptRunner(
            script=script_location,
            server_expected_format="pytorch"
        )

# Add executor to all clients
job.to_clients(runner, tasks=["train"])

## Export the job and run the simulation
job.export_job("../simulation")

job.simulator_run("../simulation/workdir", n_clients=num_clients)