# Introduction to NVFlare
> Last validated: 2026-10-26

This tutorial demonstrates how to convert existing PyTorch code into a federated learning workflow using NVIDIA FLARE (NVFlare), an open-source framework for secure, production-ready federated learning.

## Resources
- `notebooks/`
  - `NVFlare_Simulation.ipynb` - Builds an NVFlare job (FedAvg controller, model persistor, script runner), exports it and runs it in the NVFlare simulator
- `src/`
  - `train.py` - Client training script using the NVFlare Client API (`import nvflare.client as flare`); runs on each simulated site
  - `utils/`
    - `train_util.py` - Model (`SimpleClassifier`), trainer (`ClassificationTrainer`), synthetic per-site datasets (`get_datasets`) and logger setup
    - `log_config.json` - NVFlare logging configuration used by the simulator to keep console output readable
- `README.md` - This file

Running the notebook creates `output/` (the final global model, `global_model.pt`) and `simulation/` (the exported job and simulator workdir). These are generated and not committed.

## Tutorial Structure

This tutorial is divided into two parts:

### Part 1: Converting Code to NVFlare
Learn how to adapt your existing machine learning code to work with the NVFlare framework. We'll build on the federated learning concepts from the previous tutorial, converting our simple classifier into an NVFlare-compatible application.

### Part 2: Running Simulated Federated Learning
Use NVFlare's simulator to test your federated learning workflow locally before deploying to production. You'll learn how to configure jobs, run multiple clients, and analyze results.

---

## Part 1: Converting to NVFlare

### Overview

In the previous tutorial, we manually implemented federated learning by:
- Creating client and server classes
- Managing weight transfers
- Implementing the FedAvg algorithm

NVFlare automates this infrastructure, letting you focus on your model and training logic.

### The Training Script

The core of any NVFlare application is the training script. Here's `train.py`:

<div style="display: flex; gap: 20px;">

<div style="flex: 1;">

### Local Training
```python
from utils.train_util import get_datasets, SimpleClassifier, ClassificationTrainer

def train():
    # Load local data
    train_loader, test_loader = get_datasets(site_name)
    # Initialize local model
    trainer = ClassificationTrainer(SimpleClassifier())

    # Local learning loop
    for epoch in range(epochs):
        
        # Train for one epoch on local data
        trainer.train(dataloader=train_loader, epochs=1)

        # Evaluate local model on local data
        local_accuracy = trainer.evaluate(test_loader)
    

if __name__ == "__main__":
    train() 
```

</div>

<div style="flex: 1;">

### NVFlare Federated Training
```python
# (1) Import the NVFlare client
import nvflare.client as flare
from utils.train_util import get_datasets, SimpleClassifier, ClassificationTrainer

def train():
    # (2) Initialize NVFlare client
    flare.init()
    
    # Load local data
    train_loader, test_loader = get_datasets(site_name)
    # Initialize local model
    trainer = ClassificationTrainer(SimpleClassifier())

    # (3) Federated learning loop
    while flare.is_running():
        # (4) Receive global model from server
        global_model = flare.receive()
        
        # (5) Update local model with global weights
        trainer.model.load_state_dict(global_model.params)

        # (6) Evaluate global model on local data
        global_model_local_accuracy = trainer.evaluate(test_loader)
        
        # (7) Train for one epoch on local data
        trainer.train(dataloader=train_loader, epochs=1)

        # (8) Package updated model and metrics
        output_model = flare.FLModel(
            params=trainer.model.state_dict(),
            metrics={"global_accuracy": global_model_local_accuracy}
        )
      
        # (9) Send updated model back to server
        flare.send(output_model)
    

if __name__ == "__main__":
    train() 
```

</div>

</div>

### Key NVFlare Components

#### 1. **Import client API**
```python
import nvflare.client as flare
```
#### 2. **Initialize NVFlare Client**
```python
flare.init()
site_name = flare.get_site_name()
```
- Sets up secure communication channels with NVFlare server
- Must be called before any other NVFlare operations

#### 3. **Training Loop**
```python
while flare.is_running():
```
- NVFlare manages the federated learning rounds
- Loop continues until the job completes (configured number of rounds)

#### 4. **Receive the Global Model**
```python
global_model = flare.receive()
```
- Receive the aggregated model from the server
- Blocks the script until a model is received

#### 5. **Load Global Weights**
```python
trainer.model.load_state_dict(global_model.params)
```
- Update the local model with the global parameters

#### 6. **Evaluate Global Model**
```python
trainer.evaluate(test_loader)
```
- Evaluate the global model on the local test set
- Evaluation occurs before training while all clients have the same weights
- Global model metrics can be sent to server for aggregation 

#### 7. **Train Local Model**
```python
trainer.train(dataloader=train_loader, epochs=1)
```
- Train the global model on local training set

#### 8. **Package Updates**
```python
output_model = flare.FLModel(
    params=trainer.model.state_dict(),
    metrics={"global_accuracy": global_model_local_accuracy}
)
```
- Package the updated model weights and metrics

#### 9. **Send Updates**
```python
flare.send(output_model)
```
- Send the weights and metrics to the server

### What Changed from the Previous Tutorial?

| Manual Implementation | NVFlare Implementation |
|----------------------|------------------------|
| Custom `Client` class | `flare.init()` |
| Custom `Server` class | Handled by NVFlare server |
| Manual weight transfer | `flare.receive()` / `flare.send()` |
| Manual aggregation | Configured in job settings |
| Round management | `while flare.is_running()` |

### Benefits of Using NVFlare

✅ **Less Boilerplate**: No need to implement client-server communication  
✅ **Production-Ready**: Built-in security, authentication, and monitoring  
✅ **Flexible**: Easily swap aggregation algorithms without changing training code  
✅ **Scalable**: Supports many clients and large models  
✅ **Standard**: Industry-standard framework used in real deployments  

---

## Part 2: Running Simulated Federated Learning

Now that you understand how to structure an NVFlare training script, proceed to **Part 2** where you'll:
- Configure NVFlare jobs
- Run simulated federated learning locally
- Analyze training metrics and model performance
- Understand the complete federated learning workflow

**Continue to:** `notebooks/NVFlare_Simulation.ipynb`

### Expected Output
The simulation runs 10 rounds across 3 sites. Each round, every site evaluates the global model on its local test data. Accuracy should rise from about 0.58 to about 0.65 by round 10.

At the end you will see `END_RUN received` and `request to stop the job` messages. These are normal and mean the job finished.

The notebook creates these folders (they are not committed):
- `output/global_model.pt`: the final global model
- `simulation/`: the exported job and simulator workdir

## Next Steps

In the next tutorial, you'll learn how to deploy these same configuration files to a real federated learning platform (Rhino FCP) and run distributed training across actual remote sites using real data and a real model.

**Continue to:** `Tutorial_3_Deploying_Federated_Learning`

## Getting Help

For additional support, check out [RhinoDocs](https://docs.rhinofcp.com/) or reach out to [support@rhinofcp.com](mailto:support@rhinofcp.com).