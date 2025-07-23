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

from nvflare.client.api import init, is_running, receive, send, FLModel
from nvflare.client.tracking import SummaryWriter
from nvflare.apis.shareable import Shareable
from nvflare.apis.fl_constant import ReturnCode
from nvflare.apis.fl_context import FLContext

from custom.pneumonia_trainer_class import PneumoniaTrainer


def execute(task_name: str, shareable: Shareable, fl_ctx: FLContext, abort_signal) -> Shareable:
    # Initialize NVFlare client API context
    ctx = init()

    # Log metrics
    writer = SummaryWriter()

    # Initialize trainer
    trainer = PneumoniaTrainer(lr=0.01, epochs=5, test_set_percentage=20.0, writer=writer)

    while is_running(ctx):
        # 1. Receive global model
        input_model = receive(ctx)
        if input_model is None:
            print("[Client] No input model received. Exiting training loop.")
            break

        current_round = input_model.current_round
        print(f"[Client] Round {current_round}: received global model.")

        trainer.set_weights(input_model.params)

        # 2. Train locally
        trainer.local_train(global_round=current_round)

        # 3. Validate locally
        val_loss = trainer.local_valid(global_round=current_round)
        print(f"[Client] Round {current_round}: validation loss = {val_loss}")

        # 4. Prepare output model
        output_model = FLModel(
            params=trainer.get_weights(),
            metrics={"val_loss": val_loss},
            meta={"format": "pytorch"},
        )

        # 5. Send model
        send(output_model, ctx)

    # Finalize logs
    writer.flush()
    writer.close()

    # Return dummy Shareable
    result = Shareable()
    result.set_return_code(ReturnCode.OK)
    return result