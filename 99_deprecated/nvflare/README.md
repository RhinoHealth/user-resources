# Rhino FCP Examples - NVIDIA FLARE
This folder contains examples for using Rhino's Federated Computing Platform (FCP) integration with NVIDIA FLARE (NVFlare) for federated training of models
<br>

# Table of Contents
- [hello-numpy-sag-rhino](./hello-numpy-sag-rhino/README.md) - Use the NVFlare `Hello Numpy Scatter and Gather` example and apply the necessary changes for it to run on FCP. Add an `infer.py` script to perform inference on the trained model 
- [hello-pt-rhino](./hello-pt-rhino/README.md) - Use the NVFlare `Hello PyTorch` example and apply the necessary changes for it to run on FCP. Add an `infer.py` script to perform inference on the trained model
- [hello-flower](./hello-flower/README.md) - Use Flower with NVFlare v2.5 on FCP
- [mimic-cxr](./mimic-cxr/README.md) - Train a pneumonia detection model from Chest XRays using PyTorch code adapted to NVFlare v2.0, and apply the necessary changes for it to run on FCP
- [mimic-cxr-nvflare-v2.2](./mimic-cxr-nvflare-v2.2/README.md) - Same as the `mimic-cxr` example, but using NVFlare v2.2
- [mimic-cxr-nvflare-v2.3](./mimic-cxr-nvflare-v2.3/README.md) - Same as the `mimic-cxr` example, but using NVFlare v2.3
- [mimic-cxr-nvflare-v2.4](./mimic-cxr-nvflare-v2.4/mimic-cxr-fedavg/README.md) - Same as the `mimic-cxr` example, but using NVFlare v2.4
- [mimic-cxr-nvflare-v2.5](./mimic-cxr-nvflare-v2.5/mimic-cxr-fedavg/README.md) - Same as the `mimic-cxr` example, but using NVFlare v2.5
- [regression-logistic-linear](./regression-logistic-linear/README.md) - Use NVFlare v2.3 to fit logistic and linear regression models using FCP
- [regression-poisson](./regression-poisson/README.md) - Use NVFlare v2.3 to fit a poisson regression model using FCP
- [regression-quantile](./regression-quantile/README.md) - Use NVFlare v2.3 to fit a quantile regression model using FCP
- [regression-glm-coeff](./regression-glm-coeff/README.md) - Fit a federated Generalized Linear Model (GLM) using FCP with NVFlare 2.3
- [regression-glm-coeff-with-aic](./regression-glm-coeff-with-aic/README.md) - Fit a federated Generalized Linear Model (GLM) and perform Akaike Information Criterion (AIC)-based feature selection using FCP with NVFlare 2.3
- [encrypted-model-code-and-weights](./encrypted-model-code-and-weights/README.md) - Locally encrypt your model code and build a container image using just the encrypted code (and not the source code). Set up the model to encrypt the model parameters so that they are stored in an encrypted manner on FCP. Add an `infer.py` script to perform inference on the trained model, decrypting the model parameters during inference using a key provided during run time
- [xgboost](./xgboost/README.md) - Use NVFlare v2.3 to train an XGBoost model using FCP
- [monai-zoo-spleen](./monai-zoo-spleen/README.md) - Use NVFlare v2.2 to perform federated training of a spleen CT segmentation model from the [Monai Model Zoo](https://monai.io/model-zoo.html) adapted to run on FCP
- [llm-federated-fine-tuning-bionemo](./llm-federated-fine-tuning-bionemo/README.md) - Use NVFlare v2.4 and BioNeMo to perform federated fine-tuning of a protein language model using FCP
- [split-learning](./split-learning/README.md) - Adapts NVIDIA's [Split Learning](https://github.com/NVIDIA/NVFlare/tree/2.3/examples/advanced/vertical_federated_learning) NVFlare v2.3 example to run on FCP
<br><br>

# Getting Help
For additional support, please reach out to [support@rhinofcp.com](mailto:support@rhinofcp.com).
