# Copyright (c) 2024, Rhino HealthTech, Inc.
# Original file modified by Rhino Health to adapt it to the Rhino Health Federated Computing Platform.

# Copyright (c) 2021, NVIDIA CORPORATION.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from rhino_health.client import Client
from pneumonia_trainer import PneumoniaTrainer

# Step 1: Connect to Rhino FL client
client = Client()
client.set_run_context()

# Step 2: Initialize the trainer and prepare data
trainer = PneumoniaTrainer(lr=0.01, epochs=5, test_split=0.2)
trainer.prepare_data()

# Step 3: Get global weights from server and load into model
global_weights = client.get_parameters()
trainer.set_weights(global_weights)

# Step 4: Optional pre-training evaluation
initial_loss = trainer.evaluate()
client.log_metric("initial_validation_loss", initial_loss)

# Step 5: Local training
trainer.train()

# Step 6: Post-training evaluation
final_loss = trainer.evaluate()
client.log_metric("final_validation_loss", final_loss)

# Step 7: Submit updated weights to the server
updated_weights = trainer.get_weights()
client.submit_parameters(updated_weights)
