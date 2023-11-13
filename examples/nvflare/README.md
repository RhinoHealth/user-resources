# Rhino Health Examples - NVIDIA FLARE
This folder contains examples for using Rhino Health's integration with NVIDIA FLARE for federated training of models
<br>

# Table of Contents
- [hello-numpy-sag-rhino](./hello-numpy-sag-rhino/README.md) - Use the NVIDIA FLARE `Hello Numpy Scatter and Gather` example and apply the necessary changes for it to run on FCP. Add an `infer.py` script to perform inference on the trained model 
- [hello-pt-rhino](./hello-pt-rhino/README.md) - Use the NVIDIA FLARE `Hello PyTorch` example and apply the necessary changes for it to run on FCP. Add an `infer.py` script to perform inference on the trained model
- [mimic-cxr](./mimic-cxr/README.md) - Train a pneumonia detection model from Chest XRays using PyTorch code adapted to NVIDIA FLARE v2.0, and apply the necessary changes for it to run on FCP
- [mimic-cxr-nvflare-v2.2](./mimic-cxr-nvflare-v2.2/README.md) - Same as the `mimic-cxr` example, but using NVIDIA FLARE v2.2
- [monai-zoo-spleen](./monai-zoo-spleen/README.md) - Use NVIDIA FLARE v2.2 to perform federated training of a spleen CT segmentation model from the [Monai Model Zoo](https://monai.io/model-zoo.html) adapted to run on FCP
- [regression-logistic-linear](./regression-logistic-linear/README.md) - Use NVIDIA FLARE v2.3 to fit logistic and linear regression models using FCP
- [regression-poisson](./regression-poisson/README.md) - Use NVIDIA FLARE v2.3 to fit a poisson regression model using FCP
- [regression-quantile](./regression-quantile/README.md) - Use NVIDIA FLARE v2.3 to fit a quantile regression model using FCP
- [glm-coeff-optimization](./glm-coeff-optimization/README.md) - Use NVIDIA FLARE v2.3 to train a GLM model to estimate coefficients for a regression model using FCP
- [xgboost](./xgboost/README.md) - Use NVIDIA FLARE v2.3 to train an XGBoost model using FCP
- [split-learning](./split-learning/README.md) - Adapts NVIDIA's [Split Learning](https://github.com/NVIDIA/NVFlare/tree/2.3/examples/advanced/vertical_federated_learning) NVIDIA FLARE v2.3 example to run on FCP
- [encrypted-model-code-and-weights](./encrypted-model-code-and-weights/README.md) - Locally encrypt your model code and build a container image using just the encrypted code (and not the source code). Set up the model to encrypt the model parameters so that they are stored in an encrypted manner on FCP. Add an `infer.py` script to perform inference on the trained model, decrypting the model parameters during inference using a key provided during run time
<br><br>

# Getting Help
For additional support, please reach out to [support@rhinohealth.com](mailto:support@rhinohealth.com).
